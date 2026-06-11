from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["research_agent_db"]

chat_collection = db["chat_history"]
documents_collection = db["documents"]

