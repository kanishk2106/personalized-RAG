import logging
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pdf_extractor.pipeline import run_batch 
from pydantic import BaseModel
from typing import Optional
import uvicorn


app = FastAPI()

def setup_env_and_logging():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

setup_env_and_logging()
logger = logging.getLogger("pdf_extraction")
class WebhookPayload(BaseModel):
    filename: Optional[str] = None
@app.post("/")
async def handle_webhook(request: WebhookPayload, background_tasks: BackgroundTasks):
    try:
        filename = request.filename

        if not filename:
            logger.warning("No filename in webhook, running full batch scan.")
        
        background_tasks.add_task(run_batch, filename=filename)

        return {"status": "accepted", "processing_file": filename}

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)





