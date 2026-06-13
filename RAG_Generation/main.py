
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pinecone import Pinecone
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .embeddings import embed_query
from .generation import aclose_client, stream_chat
from .prompt import SYSTEM_PROMPT, build_user_message
from .reranking import rerank
from .retrieval import Candidate, hybrid_retrieve

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "rag")
RETRIEVE_K = int(os.environ.get("RETRIEVE_K", "20"))
RERANK_TOP_N = int(os.environ.get("RERANK_TOP_N", "2"))


_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
_Session = async_sessionmaker(_engine, expire_on_commit=False)
_state: dict = {}  

@asynccontextmanager
async def lifespan(app: FastAPI):  
    pc = Pinecone(api_key=PINECONE_API_KEY)
    _state["pc_index"] = pc.Index(PINECONE_INDEX)
    try:
        async with _Session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
    except Exception as db_warmup_err:
        print(f"Database warmup failed: {db_warmup_err}")
    embed_query("warmup")  
    rerank("warmup", [Candidate(chunk_id="0", doc_id="0", text="warmup")], top_n=1)
    yield
    await aclose_client()
    await _engine.dispose()


async def get_session():  
    async with _Session() as session:
        yield session
app = FastAPI(title="RAG Chatbot API", lifespan=lifespan)
class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
class RetrieveResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
async def _retrieve_and_rerank(
    query: str, session: AsyncSession
) -> list[Candidate]:
    query_vec = embed_query(query)
    candidates = await hybrid_retrieve(
        pc_index=_state["pc_index"],
        session=session,
        query=query,
        query_vec=query_vec,
        top_k=RETRIEVE_K,
    )
    return rerank(query, candidates, top_n=RERANK_TOP_N)

@app.post("/chat")
async def chat(
    body: ChatRequest,
) -> StreamingResponse:
    try:
        async with _Session() as session:
            top_chunks = await _retrieve_and_rerank(body.query,session)
    except Exception as db_err:
        print(f"Database Error: {db_err}")
        top_chunks=[]
    user_msg = build_user_message(
        question=body.query,
        chunks=top_chunks,
    )
    return StreamingResponse(
        stream_chat(system=SYSTEM_PROMPT, user=user_msg),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(
    body: ChatRequest,
) -> RetrieveResponse:
    try:
        async with _Session() as session:
            top_chunks = await _retrieve_and_rerank(body.query,session)
    except Exception as db_err:
        print(f"Database Error: {db_err}")
    return RetrieveResponse(
        query=body.query,
        chunks=[
            RetrievedChunk(chunk_id=c.chunk_id, doc_id=c.doc_id, text=c.text)
            for c in top_chunks
        ],
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
