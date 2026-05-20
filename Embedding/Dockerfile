FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Snowflake/snowflake-arctic-embed-s')"
ENV EMBEDDING_MODEL_PATH=Snowflake/snowflake-arctic-embed-s

COPY pdf_extractor/ ./pdf_extractor/
COPY Embedding/ ./Embedding/

CMD ["uvicorn", "Embedding.main:app", "--host", "0.0.0.0", "--port", "8080"]
