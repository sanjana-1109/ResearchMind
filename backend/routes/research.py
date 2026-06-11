from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.workflow import build_graph
from backend.rag.vector_store import get_vector_store
from backend.rag.hybrid_retriever import BM25Retriever
from backend.db.mongo import chat_collection
from datetime import datetime

router = APIRouter(prefix="/research", tags=["research"])


class QueryRequest(BaseModel):
    query: str
    session_id: str


# INIT
vector_db = get_vector_store()

try:
    bm25 = BM25Retriever([])
except:
    bm25 = None

graph = build_graph()


# CHAT API
@router.post("/chat")
def chat(request: QueryRequest):
    try:
        result = graph.invoke({
            "query": request.query,
            "session_id": request.session_id,
            "mode": "chat",
            "vector_db": vector_db,
            "bm25": bm25
        })

        return {
            "answer": str(result.get("answer", "")),
            "sources": result.get("sources", []),
            "is_report": result.get("is_report", False)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# REPORT API
@router.post("/report")
def report(request: QueryRequest):
    try:
        result = graph.invoke({
            "query": request.query,
            "session_id": request.session_id,
            "mode": "report",
            "vector_db": vector_db,
            "bm25": bm25
        })

        return {
            "answer": str(result.get("answer", "")),
            "sources": result.get("sources", []),
            "is_report": True
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))