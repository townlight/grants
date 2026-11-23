import tomllib
from pathlib import Path

from fastapi.testclient import TestClient

import townlight_grants
from townlight_grants.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_package_version() -> None:
    assert townlight_grants.__version__ == "0.3.0"


def test_pyproject_pins_townlight_core() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]

    assert "townlight-core==1.3.0.dev2" in dependencies


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "CivicGrants"
    assert payload["version"] == "0.3.0"
    assert payload["status"] == "grant support foundation plus grant persistence"
    assert "staff review queues" in payload["message"]
    assert "Townlight Records grant context packets" in payload["message"]
    assert "official eligibility decisions" in payload["message"]
    assert "not implemented" in payload["message"]
    assert payload["next_step"].startswith("Configure CIVICGRANTS_GRANT_DB_URL")


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "civicgrants"
    assert payload["version"] == "0.3.0"
    assert payload["civiccore_version"] == "1.3.0.dev2"


def test_release_gate_prefers_native_unix_python_before_windows_launcher() -> None:
    script = (ROOT / "scripts" / "verify-release.sh").read_text(encoding="utf-8")

    python3_probe = "command -v python3"
    python_probe = "command -v python)"
    assert python3_probe in script
    assert python_probe in script
    assert script.index(python3_probe) < script.index(python_probe)
