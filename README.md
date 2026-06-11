# 🔬 ResearchMind — Autonomous Research & Report Generation Agent

An AI-powered research assistant built with **FastAPI**, **LangGraph**, **RAG (Hybrid Retrieval)**, and **Groq LLM**. Upload documents, ask questions, and generate structured research reports automatically.

---

## ✨ Features

- 💬 **Chat / QA** — Ask questions answered from uploaded documents or general knowledge
- 📋 **Report Generator** — Generate structured research reports with sources
- 📂 **Document Upload** — PDF and image (PNG/JPG) support with OCR
- 🔍 **Hybrid Retrieval** — Vector search (ChromaDB) + BM25 keyword search
- 🕓 **Chat History** — Sessions saved in MongoDB, resumable anytime
- ⬇ **PDF Download** — Export generated reports as PDF

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11 |
| Agent Framework | LangGraph (Planner → Executor) |
| LLM | Groq (LLaMA 3.3 70B) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB |
| Keyword Search | BM25 (rank-bm25) |
| Database | MongoDB |
| OCR | Tesseract + PyMuPDF |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
├── backend/
│   ├── agents/
│   │   ├── executer.py       # Executor node (RAG + answer generation)
│   │   ├── planner.py        # Planner node (task decomposition)
│   │   ├── state.py          # LangGraph state definition
│   │   └── workflow.py       # LangGraph workflow builder
│   ├── db/
│   │   └── mongo.py          # MongoDB connection
│   ├── rag/
│   │   ├── document_processor.py   # PDF + image text extraction
│   │   ├── hybrid_retriever.py     # Vector + BM25 hybrid search
│   │   └── vector_store.py         # ChromaDB setup
│   ├── routes/
│   │   ├── history.py        # Chat history endpoints
│   │   ├── research.py       # Chat + Report endpoints
│   │   └── upload.py         # File upload endpoint
│   └── services/
│       ├── db_service.py     # Database helper functions
│       ├── intent_service.py # Intent detection
│       ├── qa_service.py     # Answer generation
│       └── report_service.py # Report + PDF generation
├── frontend/
│   └── index.html            # Frontend UI
├── backend/main.py           # FastAPI entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example              # Environment variable template
```

---

## 🚀 Getting Started

### Option A — Run with Docker (Recommended)

**1. Clone the repo**
```bash
git clone https://github.com/sanjana-1109/ResearchMind.git
cd ResearchMind
```

**2. Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

**3. Start all services**
```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| App + Frontend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

### Option B — Run Locally (Without Docker)

**1. Clone the repo**
```bash
git clone https://github.com/sanjana-1109/ResearchMind.git
cd ResearchMind
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

**5. Start MongoDB** (must be running locally)
```bash
net start MongoDB            # Windows
brew services start mongodb-community  # Mac
```

**6. Run the backend**
```bash
uvicorn backend.main:app --reload --port 8000
```

**7. Open the app**

Visit `http://localhost:8000` in your browser.

---

## 🔑 Environment Variables

Create a `.env` file based on `.env.example`:

```env
GROQ_API_KEY=your_groq_api_key_here
MONGO_URI=mongodb://localhost:27017/     # local
# MONGO_URI=mongodb://research_mongo:27017/   # Docker
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/` | Upload PDF or image |
| GET | `/upload/download` | Download generated report as PDF |
| POST | `/research/chat` | Chat / QA |
| POST | `/research/report` | Generate structured report |
| GET | `/history/` | Get all chat history |
| GET | `/history/session/{id}` | Get messages for a session |
| DELETE | `/history/` | Clear all history |

---

## 👤 Author

**Sanjana Savarkar**
- GitHub: [@sanjana-1109](https://github.com/sanjana-1109)
