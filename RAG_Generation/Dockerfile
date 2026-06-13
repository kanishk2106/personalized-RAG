FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Snowflake/snowflake-arctic-embed-s')"
ENV EMBEDDING_MODEL_PATH=Snowflake/snowflake-arctic-embed-s
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY RAG_Generation/ ./RAG_Generation/

EXPOSE 8000

CMD ["uvicorn", "RAG_Generation.main:app", "--host", "0.0.0.0", "--port", "8000"]
