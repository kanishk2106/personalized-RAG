
from __future__ import annotations
from functools import lru_cache
import os
from sentence_transformers import SentenceTransformer
EMBEDDING_MODEL_PATH = os.environ["EMBEDDING_MODEL_PATH"]
_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    model = SentenceTransformer(EMBEDDING_MODEL_PATH)
    return model


def embed_query(text: str) -> list[float]:
    model = _load_model()
    vec = model.encode(
        _QUERY_PREFIX + text,
        normalize_embeddings=True,  
    )
    return vec.tolist()
