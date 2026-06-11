from fastapi import APIRouter, HTTPException
from backend.db.mongo import chat_collection

router = APIRouter(prefix="/history", tags=["history"])


# Get full chat history (all sessions)
@router.get("/")
def get_history():
    try:
        chats = list(chat_collection.find(
            {"query": {"$exists": True}}   
        ).sort("timestamp", -1))

        for chat in chats:
            chat["_id"] = str(chat["_id"])

            if "timestamp" in chat:
                chat["timestamp"] = str(chat["timestamp"])
        return {
                "count": len(chats),
                "history": chats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get messages for a specific session — used by "Continue Chat"
@router.get("/session/{session_id}")
def get_session_history(session_id: str):
    try:
        chats = list(chat_collection.find(
            {
                "session_id": session_id,
                "query": {"$exists": True}
            }
        ).sort("timestamp", 1))

        for chat in chats:
            chat["_id"] = str(chat["_id"])

            if "timestamp" in chat:
                chat["timestamp"] = str(chat["timestamp"])

        return {
            "session_id": session_id,
            "count": len(chats),
            "messages": chats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Clear all history
@router.delete("/")
def clear_history():
    try:
        chat_collection.delete_many({})
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))