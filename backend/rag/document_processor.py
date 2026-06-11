from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import requests
import os

#  PROCESS PDF
def process_pdf(file_path):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        texts = [doc.page_content for doc in docs if doc.page_content]

        return texts if texts else []

    except Exception as e:
        print("❌ PDF processing error:", e)
        return []



#  OCR USING API (NO TESSERACT)

def process_image(file_path):
    try:
        url = "https://api.ocr.space/parse/image"

        payload = {
            "apikey": "161aa2e02888957",  
            "language": "eng"
        }

        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                files={"file": f},
                data=payload
            )

        result = response.json()

        if result.get("IsErroredOnProcessing"):
            print("❌ OCR API Error:", result)
            return []

        text = result["ParsedResults"][0]["ParsedText"]

        return [text] if text.strip() else []

    except Exception as e:
        print("❌ Image processing error:", e)
        return []



#  UNIFIED PROCESSOR

def process_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return process_pdf(file_path)

    elif ext in [".png", ".jpg", ".jpeg"]:
        return process_image(file_path)

    else:
        print(f"⚠️ Unsupported file type: {ext}")
        return []



# SPLIT DOCUMENTS

def split_documents(texts):
    try:
        if not texts:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        documents = splitter.create_documents(texts)

        return documents

    except Exception as e:
        print("❌ Splitting error:", e)
        return []