from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import upload, research, history
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="ResearchMind - AI Research Agent")

#  CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  API Routes
app.include_router(upload.router)
app.include_router(research.router)
app.include_router(history.router)

# Serve frontend folder as static files 
app.mount("/static", StaticFiles(directory="frontend"), name="static")

#  Root → opens UI directly in browser 
@app.get("/")
def home():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}