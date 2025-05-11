import pytest
from starlette.testclient import TestClient
from todoApp.main import app
from fastapi import FastAPI, status

client = TestClient(app)

def test_return_helth_check():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}