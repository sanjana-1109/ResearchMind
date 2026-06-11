import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Reads from env — works both locally (localhost) and in Docker (mongo service)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["research_agent"]
history_collection = db["history"]


def save_user_name(session_id, name):
    from backend.db.mongo import chat_collection
    chat_collection.update_one(
        {"session_id": session_id},
        {"$set": {"user_name": name}},
        upsert=True
    )


def get_user_name(session_id):
    from backend.db.mongo import chat_collection
    user = chat_collection.find_one({"session_id": session_id})
    if user and "user_name" in user:
        return user["user_name"]
    return None


from backend.db.mongo import chat_collection

def save_chat(session_id, query, answer, sources, is_report=False):
    chat_collection.insert_one({
        "session_id": session_id,
        "query": query,
        "answer": answer,
        "sources": sources,
        "is_report": is_report,
        "timestamp": datetime.utcnow()
    })


def get_chat_history(session_id):
    chats = chat_collection.find(
        {"session_id": session_id}
    ).sort("timestamp", 1)

    history = []
    for c in chats:
        history.append({
            "query": c.get("query", ""),
            "answer": c.get("answer", "")
        })

    return history