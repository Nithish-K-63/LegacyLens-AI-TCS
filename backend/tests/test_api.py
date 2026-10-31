"""API and security tests for LegacyLens AI FastAPI application."""
import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.security import validate_github_url, safe_extract_zip, redact_secrets

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns status, version, and model info."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "gemini_configured" in data
    assert "timestamp" in data


def test_demo_analysis_retrieval():
    """Verify default demo analysis returns completed status and full dataset."""
    response = client.get("/api/analysis/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "demo"
    assert data["status"] == "completed"
    assert data["record"] is not None
    assert len(data["record"]["findings"]) >= 5
    assert len(data["record"]["rules"]) >= 4
    assert len(data["record"]["modules"]) >= 5


def test_demo_graph_endpoint():
    """Verify graph endpoint returns nodes and edges."""
    response = client.get("/api/analysis/demo/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 5
    assert len(data["edges"]) >= 5


def test_demo_heatmap_endpoint():
    """Verify heatmap endpoint returns module risks and matrix."""
    response = client.get("/api/analysis/demo/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data
    assert "layer_scores" in data


def test_demo_report_endpoints():
    """Verify report export in JSON and Markdown formats."""
    res_json = client.get("/api/analysis/demo/report?format=json")
    assert res_json.status_code == 200
    assert "project_name" in res_json.json()

    res_md = client.get("/api/analysis/demo/report?format=markdown")
    assert res_md.status_code == 200
    assert "# OmniStrat Modernization Report" in res_md.text


def test_github_url_validation_safety():
    """Verify GitHub URL validator blocks unsafe hosts, protocols, and credentials."""
    # Valid
    valid, url = validate_github_url("https://github.com/torvalds/linux")
    assert valid is True
    assert "github.com/torvalds/linux.git" in url

    # Invalid scheme
    valid, err = validate_github_url("http://github.com/user/repo")
    assert valid is False

    # SSRF / local address
    valid, err = validate_github_url("https://127.0.0.1/repo")
    assert valid is False

    # Embedded credentials
    valid, err = validate_github_url("https://user:pass@github.com/org/repo")
    assert valid is False
    assert "credentials" in err.lower()

    # Non-GitHub host
    valid, err = validate_github_url("https://gitlab.com/org/repo")
    assert valid is False


def test_zip_slip_protection(tmp_path):
    """Verify Zip Slip path traversal is caught and rejected."""
    bad_zip_path = tmp_path / "evil.zip"
    dest_dir = tmp_path / "extracted"
    dest_dir.mkdir()

    # Create zip with directory traversal entry
    with zipfile.ZipFile(bad_zip_path, "w") as zf:
        zf.writestr("../../etc/passwd", "evil content")

    success, msg, count = safe_extract_zip(str(bad_zip_path), str(dest_dir))
    assert success is False
    assert "Illegal file path" in msg


def test_secret_redaction():
    """Verify API keys and passwords are redacted from snippets."""
    sample = 'DATABASE_PASSWORD = "SuperSecretPassword123!"\nAPI_KEY = "AIzaSyD-fakeKey1234567890abcdef"'
    redacted = redact_secrets(sample)
    assert "SuperSecretPassword123!" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_upload_and_pipeline_execution(tmp_path):
    """Verify ZIP upload starts analysis pipeline and completes with findings."""
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("src/order/discount.py", "def calc(loyalty_tier):\n    if loyalty_tier == 'Gold': return 0.12\n")
        zf.writestr("src/auth/policy.py", "def check(role):\n    if role == 'ADMIN_OVERRIDE': return True\n")
        zf.writestr("legacy/schema.sql", "CREATE TABLE CUSTOMER_CREDIT (ID INT, BAL DECIMAL(10,2));\n")

    zip_buf.seek(0)
    response = client.post(
        "/api/analyze/upload",
        files={"file": ("sample.zip", zip_buf.getvalue(), "application/zip")},
        data={"project_name": "Test Upload Project"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "analysis_id" in res_data
    assert res_data["status"] == "analyzing"

    # Status check
    analysis_id = res_data["analysis_id"]
    status_res = client.get(f"/api/analysis/{analysis_id}")
    assert status_res.status_code == 200


def test_gemini_settings_and_test_endpoints(monkeypatch):
    """Verify Gemini settings retrieval and connection testing endpoints."""
    # 1. Get settings
    settings_res = client.get("/api/settings/gemini")
    assert settings_res.status_code == 200
    data = settings_res.json()
    assert data["provider"] == "Google Gemini"
    assert "supported_models" in data
    assert "setup_url" in data

    # 2. Test with empty key
    test_res = client.post("/api/settings/gemini/test", json={"api_key": ""})
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["success"] is False
    assert "No API key" in test_data["message"]

    # 3. Configure with empty key returns 400
    bad_cfg = client.post("/api/settings/gemini/configure", json={"api_key": ""})
    assert bad_cfg.status_code == 400

    # 4. Test error handling when connection fails
    from backend.services.gemini_service import gemini_service
    monkeypatch.setattr(
        gemini_service,
        "test_connection",
        lambda api_key=None, model_name=None: {
            "success": False,
            "message": "Connection failed: Invalid API key or unauthorized project.",
            "model": "gemini-2.5-flash",
            "timestamp": "2026-10-31T00:00:00Z"
        }
    )
    test_res_bad = client.post("/api/settings/gemini/test", json={"api_key": "AIzaSyFakeKeyInvalidForTesting1234567890"})
    assert test_res_bad.status_code == 200
    bad_data = test_res_bad.json()
    assert bad_data["success"] is False
    assert "Invalid API key" in bad_data["message"]
    assert "AIzaSyFakeKeyInvalidForTesting1234567890" not in bad_data["message"]


def test_database_analysis_endpoint():
    """Verify database analysis endpoint returns tables, shared writers, and stored procs."""
    db_res = client.get("/api/analysis/demo/database")
    assert db_res.status_code == 200
    db_data = db_res.json()
    assert "tables" in db_data
    assert "shared_tables" in db_data
    assert "stored_procedures" in db_data
    assert len(db_data["shared_tables"]) >= 1
    assert "CUSTOMER_CREDIT" in db_data["tables"]


def test_pipeline_and_product_endpoints():
    """Verify dedicated pipeline, module tree, token usage, and product profile endpoints."""
    # 1. Pipeline
    pipe_res = client.get("/api/analysis/demo/pipeline")
    assert pipe_res.status_code == 200
    pipe_data = pipe_res.json()
    assert "pipelines" in pipe_data
    assert len(pipe_data["pipelines"]) >= 1
    p1 = pipe_data["pipelines"][0]
    assert "stages" in p1
    assert len(p1["stages"]) >= 2
    assert "responsibility" in p1["stages"][0]

    # 2. Module Tree
    tree_res = client.get("/api/analysis/demo/modules")
    assert tree_res.status_code == 200
    tree_data = tree_res.json()
    assert "module_tree" in tree_data
    assert len(tree_data["module_tree"]) >= 1

    # 3. Token Usage
    token_res = client.get("/api/analysis/demo/tokens")
    assert token_res.status_code == 200
    token_data = token_res.json()
    assert "token_usage" in token_data
    assert token_data["token_usage"]["total_tokens"] >= 0

    # 4. Product Profile
    prof_res = client.get("/api/analysis/demo/profile")
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    assert "profile" in prof_data
    assert "product_type" in prof_data["profile"]


def test_nested_wrapper_zip_detection():
    """Verify detect_project_root correctly unwraps a single nested directory in an archive."""
    import tempfile
    import os
    from backend.services.ingestion import detect_project_root

    with tempfile.TemporaryDirectory() as td:
        nested = os.path.join(td, "my-repo-master")
        os.makedirs(nested)
        with open(os.path.join(nested, "package.json"), "w") as f:
            f.write('{"name": "calculator"}')
        
        detected_root = detect_project_root(td)
        assert detected_root == nested
        assert os.path.exists(os.path.join(detected_root, "package.json"))
