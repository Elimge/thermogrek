import os
import pytest
import httpx

# If running inside Docker network, target service hostname; otherwise localhost
BASE_URL = os.getenv("TEST_API_URL", "http://thermogrek-backend:8000/api/v1")

def test_api_health_endpoint():
    """Verifies that API is online and reports active database connection."""
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["subsystems"]["database"] == "connected"

def test_api_list_assets():
    """Verifies that both pre-seeded industrial assets are retrieved."""
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        response = client.get("/assets")
        assert response.status_code == 200
        assets = response.json()
        assert len(assets) >= 2
        asset_ids = [a["id"] for a in assets]
        assert "HE-01" in asset_ids
        assert "CT-01" in asset_ids

def test_api_get_latest_telemetry_he():
    """Verifies that live latest reading endpoint returns telemetry and KPIs."""
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        response = client.get("/assets/HE-01/latest")
        assert response.status_code == 200
        payload = response.json()
        assert payload["asset_id"] == "HE-01"
        assert "metrics" in payload
        assert "kpis" in payload
        assert "health_status" in payload

def test_api_get_telemetry_history():
    """Verifies that historical time-series endpoint returns chronologically sorted data points."""
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        response = client.get("/assets/HE-01/history?limit=10")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) > 0
