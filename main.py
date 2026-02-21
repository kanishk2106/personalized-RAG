import logging
import os

def main() -> None:
    # Optional for local dev:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    from pdf_extractor.pipeline import run_batch
    run_batch()

if __name__ == "__main__":
    main()
