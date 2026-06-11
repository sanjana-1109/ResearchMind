# ─── Base image ───
FROM python:3.11-slim

# ─── System dependencies (Tesseract OCR + build tools) ───
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    gcc \
    g++ \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ─── FIX: Python build tools for pip dependencies ───
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ─── Working directory ───a
WORKDIR /app

# ─── Upgrade pip ───
RUN pip install --upgrade pip

# ─── Install dependencies ───
COPY requirements.txt .
RUN pip install --default-timeout=100 --retries 10 --no-cache-dir -r requirements.txt

# ─── Copy entire project ───
COPY . .

# ─── Create required folders ───
RUN mkdir -p data chroma_db frontend

# ─── Single port for everything ───
EXPOSE 8000

# ─── Start FastAPI — serves both API and frontend UI ───
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]