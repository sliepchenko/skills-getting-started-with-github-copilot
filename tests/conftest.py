import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a fresh TestClient for each test.
    This ensures test isolation with a clean app state.
    """
    return TestClient(app)
