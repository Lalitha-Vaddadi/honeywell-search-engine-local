import io
import uuid
import sys
import pathlib

# Ensure backend package is importable when running pytest from backend/
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from unittest import mock
from fastapi.testclient import TestClient

# Mock out Celery before it gets imported transitively
sys.modules["celery"] = mock.MagicMock()
sys.modules["worker.celery_app"] = mock.MagicMock()
sys.modules["worker.tasks_embedding"] = mock.MagicMock()

from app.main import app
from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings
from app.routers import upload_router

# Stop mocks after import
mock.patch.stopall()


class DummyUser(User):
    def __init__(self):
        # Minimal stand-in; SQLA Base init not required for dependency override
        self.id = uuid.uuid4()
        self.email = "test@example.com"
        self.name = "Test User"


def fake_current_user():
    return DummyUser()


def noop_delay(*args, **kwargs):
    # Stub for Celery delay to avoid needing a running worker in tests
    return None


@pytest.fixture(autouse=True)
def override_deps(monkeypatch):
    # Override auth dependency
    app.dependency_overrides[get_current_user] = fake_current_user
    # Stub Celery task trigger
    monkeypatch.setattr(upload_router.process_pdf, "delay", noop_delay)
    yield
    app.dependency_overrides.clear()


def test_upload_pdf_round_trip():
    # Ensure bucket exists before calling API
    upload_router.ensure_bucket_exists()

    client = TestClient(app)

    # Minimal PDF content
    pdf_bytes = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    files = {
        "files": (
            "sample.pdf",
            io.BytesIO(pdf_bytes),
            "application/pdf",
        )
    }

    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_uploaded"] == 1
    uploaded = data["data"]["uploaded"][0]
    assert uploaded["filename"] == "sample.pdf"
    assert uploaded["status"] == "pending"

    # Verify MinIO object key was returned
    assert "object_key" in uploaded and uploaded["object_key"]

    # Test passes - upload worked
    print(f"Upload successful: doc_id={uploaded['id']}")
