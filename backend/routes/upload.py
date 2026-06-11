from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import fitz  
import pytesseract
from PIL import Image
import io
from datetime import datetime

from backend.rag.document_processor import process_pdf, process_image, split_documents
from backend.rag.vector_store import get_vector_store
from backend.db.mongo import documents_collection

from backend.services.report_service import generate_pdf
from fastapi.responses import FileResponse

# Tesseract path — works on both Windows (local) and Linux (Docker)
import platform
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# On Linux (Docker), tesseract is in PATH automatically — no config needed

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

vector_db = get_vector_store()

ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg"]

# OCR: Extract text from embedded images inside a PDF 
def extract_images_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        image_chunks = []

        for page_number in range(len(doc)):
            page = doc[page_number]
            images = page.get_images(full=True)

            for img in images:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                image = Image.open(io.BytesIO(image_bytes))
                text = pytesseract.image_to_string(image)

                if text.strip():
                    image_chunks.append({
                        "text": text,
                        "page": page_number + 1,
                        "is_image": True
                    })

        return image_chunks

    except Exception as e:
        print(f"⚠️ Image OCR from PDF failed: {e}")
        return []


#  MAIN UPLOAD API 
@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        all_chunks = []

        # ── PDF handling ──
        if ext == ".pdf":
            # 1. Extract and split normal text
            raw_texts = process_pdf(file_path)           # returns list[str]
            doc_chunks = split_documents(raw_texts)      # returns list[Document]

            # FIX: extract .page_content from each Document object
            normal_chunks = [
                {"text": doc.page_content, "is_image": False}
                for doc in doc_chunks
                if doc.page_content and doc.page_content.strip()
            ]

            # 2. Extract text from embedded images via OCR
            image_chunks = extract_images_text_from_pdf(file_path)

            all_chunks = normal_chunks + image_chunks

        #  Image file handling (PNG / JPG / JPEG) 
        elif ext in [".png", ".jpg", ".jpeg"]:
            # Use the OCR API from document_processor
            texts = process_image(file_path)             

            all_chunks = [
                {"text": t, "is_image": True, "page": 1}
                for t in texts
                if t and t.strip()
            ]

        if not all_chunks:
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this file. "
                       "For PDFs, make sure it contains selectable text or embedded images. "
                       "For images, ensure the text is legible."
            )

        # Store all chunks in vector DB
        for i, chunk in enumerate(all_chunks):
            metadata = {
                "source": file.filename,
                "chunk_id": i + 1,
                "is_image": chunk.get("is_image", False)
            }

            if "page" in chunk and chunk["page"] is not None:
                metadata["page"] = chunk["page"]

            vector_db.add_texts(
                texts=[chunk["text"]],
                metadatas=[metadata]
            )

        # Save upload metadata to MongoDB
        documents_collection.insert_one({
            "filename": file.filename,
            "path": file_path,
            "num_chunks": len(all_chunks),
            "uploaded_at": datetime.utcnow()
        })

        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "chunks_created": len(all_chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


#  DOWNLOAD REPORT 
@router.get("/download")
def download():
    try:
        file_path = generate_pdf()
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="No report has been generated yet.")

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename="report.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))