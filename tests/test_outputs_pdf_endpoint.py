from fastapi import FastAPI
from fastapi.testclient import TestClient

from labs import router as lab_router


def test_get_outputs_pdf_returns_service_payload(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(lab_router.outputs_router)

    class _ServiceStub:
        def list_pdf_outputs(self):
            return {
                "items": [{"filename": "post.pdf", "path": "public/pdf/post.pdf"}],
                "count": 1,
            }

    monkeypatch.setattr(lab_router, "service", _ServiceStub())

    with TestClient(app) as client:
        response = client.get("/outputs/pdf")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{"filename": "post.pdf", "path": "public/pdf/post.pdf"}],
        "count": 1,
    }
