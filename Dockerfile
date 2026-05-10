FROM python:3.12-slim
WORKDIR /app

COPY job_analyzer/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY job_analyzer/ ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]