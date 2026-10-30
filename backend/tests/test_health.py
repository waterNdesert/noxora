from sqlalchemy.exc import OperationalError

from src.core.database import get_db_session
from src.main import app


async def test_health_endpoints_report_api_and_database_status(client):
    live = await client.get("/api/health/live")
    ready = await client.get("/api/health/ready")
    version = await client.get("/api/version")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json() == {
        "status": "ready",
        "dependencies": {"database": "available"},
    }
    assert version.status_code == 200
    assert version.json()["name"] == "Nexora API"


async def test_readiness_reports_database_failure(client):
    class BrokenSession:
        async def execute(self, _statement):
            raise OperationalError("SELECT 1", {}, OSError("database unavailable"))

    async def failed_session():
        yield BrokenSession()

    app.dependency_overrides[get_db_session] = failed_session
    response = await client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {"database": "unavailable"},
    }
