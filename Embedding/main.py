import logging
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from wordsegment import load as ws_load

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
ws_load()
logger = logging.getLogger("embedding")


class WebhookPayload(BaseModel):
    json_filenames: Optional[list[str]] = None


@app.post("/")
async def handle_webhook(request: WebhookPayload, background_tasks: BackgroundTasks):
    try:
        from .pipeline import run_chunk_batch

        filenames = request.json_filenames

        if not filenames:
            logger.warning("No json_filenames in webhook, running full batch scan.")

        background_tasks.add_task(run_chunk_batch, json_filenames=filenames)

        return {"status": "accepted", "processing_files": filenames}

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)