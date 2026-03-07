FROM python:3.10-slim
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx && \
    apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["python3", "main.py"]