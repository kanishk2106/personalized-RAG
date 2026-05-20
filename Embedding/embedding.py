# Embedding/embed_and_upsert.py
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from tqdm import tqdm

from .database import SessionLocal, DBChunk, Document

load_dotenv()

logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "rag")
MODEL_PATH = os.environ["EMBEDDING_MODEL_PATH"]
EMBED_BATCH = 64
UPSERT_BATCH = 100
METADATA_TEXT_CAP = 2000
NAMESPACE = ""

_MODEL: SentenceTransformer | None = None
_INDEX = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_PATH)
        dim = _MODEL.get_sentence_embedding_dimension()
        assert dim == 384, f"Expected 384-dim model, got {dim}"
    return _MODEL


def _get_index():
    global _INDEX
    if _INDEX is None:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        _INDEX = pc.Index(PINECONE_INDEX)
    return _INDEX


def sync_document_embeddings(
    doc_id: str,
    old_chunk_ids: list[str] | None = None,
) -> None:
    model = _get_model()
    index = _get_index()

    if old_chunk_ids:
        logger.info(
            "Deleting %d existing Pinecone vectors for doc_id=%s",
            len(old_chunk_ids), doc_id,
        )
        for i in range(0, len(old_chunk_ids), UPSERT_BATCH):
            batch = old_chunk_ids[i : i + UPSERT_BATCH]
            try:
                index.delete(ids=batch, namespace=NAMESPACE)
            except Exception as e:
                if "Namespace not found" in str(e):
                    logger.info("Namespace not found (fresh index); skipping delete")
                    break
                raise
    else:
        logger.info("No existing vectors to delete for doc_id=%s", doc_id)

    with SessionLocal() as session:
        rows = session.execute(
            select(
                DBChunk.chunk_id,
                DBChunk.text,
                Document.doc_id,
            )
            .join(Document, DBChunk.document_id == Document.id)
            .where(Document.doc_id == doc_id)
            .order_by(DBChunk.chunk_index)
        ).all()

    if not rows:
        logger.warning("No chunks found for doc_id=%s; nothing to embed", doc_id)
        return

    logger.info("Embedding %d chunks for doc_id=%s", len(rows), doc_id)

    for batch_start in tqdm(range(0, len(rows), EMBED_BATCH), desc=f"Embed {doc_id}"):
        batch = rows[batch_start:batch_start + EMBED_BATCH]

        texts = [r.text for r in batch]
        embeddings = model.encode(
            texts,
            batch_size=EMBED_BATCH,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        vectors = []
        for r, emb in zip(batch, embeddings):
            vectors.append({
                "id": r.chunk_id,
                "values": emb.tolist(),
                "metadata": {
                    "doc_id": r.doc_id
                },
            })

        for i in range(0, len(vectors), UPSERT_BATCH):
            index.upsert(
                vectors=vectors[i:i + UPSERT_BATCH],
                namespace=NAMESPACE,
            )

    logger.info("Synced doc_id=%s: %d vectors in Pinecone", doc_id, len(rows))