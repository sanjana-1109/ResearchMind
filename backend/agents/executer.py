import re
from backend.services.db_service import save_chat, get_chat_history, get_user_name, save_user_name
from backend.rag.hybrid_retriever import hybrid_retrieval
from backend.services.qa_service import generate_answer, generate_answer_with_context
from backend.services.report_service import generate_report


def has_documents(vector_db) -> bool:
    """Check if any documents have been uploaded to the vector store."""
    try:
        # Try fetching at least 1 doc — if something exists, return True
        results = vector_db.similarity_search("test", k=1)
        return len(results) > 0
    except Exception:
        return False


def executor_node(state):

    query = state["query"]
    session_id = state.get("session_id")
    mode = state.get("mode", "chat")

    vector_db = state.get("vector_db")
    bm25 = state.get("bm25")

    user_name = get_user_name(session_id)

    #  GREETING 
    if query.lower().strip() in ["hi", "hello", "hey"]:
        return {
            "answer": f"👋 Hello {user_name or ''}! How can I help you?",
            "sources": [],
            "is_report": False
        }

    #  NAME DETECTION 
    name_patterns = [
        r"i am\s+([a-zA-Z]+)",
        r"my name is\s+([a-zA-Z]+)"
    ]

    for pattern in name_patterns:
        match = re.search(pattern, query.lower())
        if match:
            name = match.group(1).capitalize()
            save_user_name(session_id, name)
            return {
                "answer": f"Nice to meet you {name}! 😊",
                "sources": [],
                "is_report": False
            }

    #  DETECT REPORT REQUEST 
    query_lower = query.lower()

    report_keywords = [
        "report",
        "detailed report",
        "full report",
        "analysis",
        "deep dive",
        "structured report"
    ]

    is_report_request = any(word in query_lower for word in report_keywords)

    #  REPORT MODE 
    if is_report_request or mode == "report":
        docs = hybrid_retrieval(query, vector_db, bm25) or []

        context = "\n".join([d.get("content", "") for d in docs])

        sources = []
        for d in docs:
            if d.get("is_image"):
                label = f"📷 Image Source (Page {d.get('page', '?')})"
            else:
                label = f"📄 {d.get('source')} (Chunk {d.get('chunk_id', '?')})"
            sources.append(label)

        sources = list(set(sources))

        answer = generate_report(query, context, sources)

        save_chat(session_id, query, answer, sources, is_report=True)

        return {
            "answer": answer,
            "sources": sources,
            "is_report": True
        }

    #  CHAT MODE 
    # Always try RAG first — fall back to general LLM if no docs exist
    history = get_chat_history(session_id)[-3:]
    history_text = "\n".join([
        h.get("query", "") + " " + h.get("answer", "")
        for h in history
    ])

    docs_available = has_documents(vector_db)

    if docs_available:
        # Retrieve relevant chunks from uploaded documents
        docs = hybrid_retrieval(query, vector_db, bm25) or []

        context = "\n".join([d.get("content", "") for d in docs])

        # Build sources with chunk info
        sources = []
        for d in docs:
            if d.get("is_image"):
                label = f"📷 Image Source (Page {d.get('page', '?')})"
            else:
                label = f"📄 {d.get('source')} (Chunk {d.get('chunk_id', '?')})"
            sources.append(label)

        sources = list(set(sources))

        # Answer using document context + chat history
        answer = generate_answer_with_context(query, context, history_text)

    else:
        # No documents uploaded — answer from general knowledge
        docs = []
        sources = []
        answer = generate_answer(query, history_text)

    save_chat(session_id, query, answer, sources, is_report=False)

    return {
        "answer": answer,
        "sources": sources,
        "is_report": False
    }