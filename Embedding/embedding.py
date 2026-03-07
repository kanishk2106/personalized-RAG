import os
import json
import logging
import io
import boto3
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
S3_BUCKET = os.getenv("MY_CLOUD_BUCKET")
REGION = "us-east-1"
s3_client = boto3.client('s3', region_name=REGION)

logger = logging.getLogger(__name__)

def get_embedding_model():
    """Syncs model between Local and Cloud."""
    model_name = "all-MiniLM-L6-v2"
    local_path = os.path.join(os.getcwd(), "models", model_name)
    s3_key = f"models/{model_name}/weights.bin"

    if os.path.exists(local_path):
        return SentenceTransformer(local_path)
    
    # Logic to download from HF and then BACKUP to Cloud
    model = SentenceTransformer(model_name)
    model.save(local_path)
    
    # Backup to cloud (simplified upload of main weight file)
    with open(f"{local_path}/pytorch_model.bin", "rb") as f:
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=f)
    logger.info("✅ Model saved locally and backed up to Cloud.")
    return model

def run_ingestor_production():
    """Phase 3: Ingests lean vectors to Pinecone and heavy text to Cloud."""
    
    model = get_embedding_model()
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

    # 1. Pull cleaned JSON list from Cloud
    prefix = "data/scrubbed_json/"
    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix).get('Contents', [])

    for obj in objects:
        file_key = obj['Key']
        if not file_key.endswith('.json'): continue

        # Load from Cloud
        file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
        data = json.loads(file_obj['Body'].read().decode('utf-8'))
        doc_meta = data['doc']
        
        # We will store two different payloads
        pinecone_vectors = []
        cloud_lookup_table = {}

        for page in data.get("pages", []):
            chunks = splitter.split_text(page['text'])
            for i, chunk in enumerate(chunks):
                vector_id = f"{doc_meta['doc_id']}#p{page['page']}#c{i}"
                embedding = model.encode(chunk).tolist()

                # A. LEAN PINECONE PAYLOAD (No Text)
                pinecone_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "doc_id": doc_meta['doc_id'],
                        "page": page['page'],
                        "s3_lookup_key": f"data/lookup/{doc_meta['doc_id']}.json"
                    }
                })

                # B. HEAVY CLOUD PAYLOAD (Text + Embeddings backup)
                cloud_lookup_table[vector_id] = {
                    "text": chunk,
                    "embedding": embedding, # Backup in case of image/DB failure
                    "metadata": doc_meta
                }

        # 2. Save Heavy Text to Cloud Lookup (JSON per Document)
        lookup_key = f"data/lookup/{doc_meta['doc_id']}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=lookup_key,
            Body=json.dumps(cloud_lookup_table)
        )

        # 3. Upsert Lean Vectors to Pinecone
        if pinecone_vectors:
            index.upsert(vectors=pinecone_vectors, namespace="portfolio")
            logger.info(f"✨ Ingested {doc_meta['doc_id']}: Vectors in DB, Text in Cloud.")

# --- RETRIEVAL LOGIC ---

def retrieve_context(query, top_k=3):
    """How the retrieval looks now: 2-step lookup."""
    model = get_embedding_model()
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    # 1. Search Pinecone for IDs
    query_vec = model.encode(query).tolist()
    results = index.query(vector=query_vec, top_k=top_k, include_metadata=True, namespace="portfolio")

    final_context = []
    # 2. Fetch Text from Cloud using IDs
    for match in results['matches']:
        vector_id = match['id']
        lookup_key = match['metadata']['s3_lookup_key']
        
        # In a real app, you'd cache this S3 object in memory/Redis
        lookup_file = s3_client.get_object(Bucket=S3_BUCKET, Key=lookup_key)
        full_data = json.loads(lookup_file['Body'].read().decode('utf-8'))
        
        final_context.append(full_data[vector_id]['text'])

    return final_context