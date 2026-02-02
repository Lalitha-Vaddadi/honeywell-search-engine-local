from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


celery_app = Celery(
    "pdf_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# IMPORTANT: Explicit imports so tasks are registered
import app.worker.tasks          # registers process_pdf
import app.worker.tasks_embedding  # registers embed_pdf
