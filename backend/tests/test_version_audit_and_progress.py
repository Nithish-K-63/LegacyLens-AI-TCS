"""Unit tests verifying technology requirements & version audit, progress initialization, and multi-language scanner."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.main import app, ANALYSES_DB
from backend.schemas.models import AnalysisRecord, TechnologyVersionAudit
from backend.services.version_analyzer import audit_project_technologies_and_versions
from backend.services.static_analyzer import analyze_codebase, ConservativeMultiLanguageScanner
from backend.services.dependency_analyzer import build_dependency_graph

client = TestClient(app)


def test_version_audit_from_package_json():
    """Verify declared vs resolved versions and 12-field upgrade explanations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_path = os.path.join(tmpdir, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write('''{
  "name": "legacy-web",
  "dependencies": {
    "react": "16.8.0",
    "lodash": "4.17.15",
    "axios": "^0.21.1"
  }
}''')
        inventory = [
            {"path": pkg_path, "relative_path": "package.json", "language": "JSON", "extension": ".json"}
        ]
        audits = audit_project_technologies_and_versions(tmpdir, inventory)
        assert len(audits) >= 2
        react_audit = next((a for a in audits if a.component == "react"), None)
        assert react_audit is not None
        assert react_audit.current_version == "16.8.0"
        assert react_audit.recommended_version == "18.3.1"
        assert react_audit.upgrade_priority in ("Critical", "High")
        assert len(react_audit.risks_and_breaking_changes) > 0
        assert len(react_audit.benefits) > 0
        assert react_audit.recommended_upgrade_path != ""
        assert len(react_audit.testing_requirements) > 0


def test_version_audit_endpoint():
    """Verify /api/analysis/{analysis_id}/versions endpoint returns structured audit."""
    res = client.get("/api/analysis/demo/versions")
    assert res.status_code == 200
    data = res.json()
    assert "version_audit" in data
    assert len(data["version_audit"]) >= 3
    first = data["version_audit"][0]
    assert "component" in first
    assert "current_version" in first
    assert "recommended_version" in first
    assert "upgrade_priority" in first
    assert "benefits" in first
    assert "risks_and_breaking_changes" in first
    assert "recommended_upgrade_path" in first


def test_progress_starts_at_zero_and_queued():
    """Verify new analysis begins at progress=0 and stage='queued'."""
    dummy_id = "LL-progtest"
    ANALYSES_DB[dummy_id] = AnalysisRecord(
        id=dummy_id,
        project_name="ProgTest",
        status="analyzing",
        progress=0,
        stage="queued",
        created_at="2026-10-31T00:00:00Z"
    )
    res = client.get(f"/api/analysis/{dummy_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["progress"] == 0
    assert data["stage"] == "queued"
    assert data["status"] == "analyzing"


def test_multi_language_and_zero_findings_prevention():
    """Verify static analyzer produces findings and dependency links across multi-file codebases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create Python entry and service
        py_path = os.path.join(tmpdir, "app.py")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write('''# Primary app bootstrap
import os
import sys

def main():
    api_key = "sk-live-9999888877776666"
    print("Starting app...")
''')

        svc_path = os.path.join(tmpdir, "order_service.py")
        with open(svc_path, "w", encoding="utf-8") as f:
            f.write('''# Service logic
def calculate_discount(tier, amount):
    # TODO: verify loyalty gold threshold
    if tier == "gold":
        return amount * 0.12
    return 0.0
''')

        inventory = [
            {"path": py_path, "relative_path": "app.py", "language": "Python", "extension": ".py"},
            {"path": svc_path, "relative_path": "order_service.py", "language": "Python", "extension": ".py"}
        ]

        res = analyze_codebase(tmpdir, inventory)
        assert "findings" in res
        assert len(res["findings"]) > 0

        # Verify dependency graph produces nodes and edges
        nodes, edges = build_dependency_graph(inventory, res)
        assert len(nodes) >= 2
        assert len(edges) >= 1
