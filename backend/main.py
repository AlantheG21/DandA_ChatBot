import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from retriever import retrieve_chunks
from llm import ask_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dand-a-chat-bot.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        chunks = retrieve_chunks(request.query)
        response = ask_llm(request.query, chunks)
    except Exception:
        logger.exception("Failed to handle /chat request for query: %r", request.query)
        raise HTTPException(
            status_code=502,
            detail="Failed to generate a response. Please try again.",
        )
    return {"response": response}