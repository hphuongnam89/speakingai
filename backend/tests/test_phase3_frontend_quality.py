import re
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_profile_name_xss_payload_handled_safely():
    # Register user
    reg = client.post("/api/v1/auth/register", json={"email": "xss-test@example.com", "password": "secure-pwd-12345"})
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile with XSS payload (within 50 chars limit)
    xss_payload = '<script>alert("xss")</script>'
    res = client.post("/api/v1/profiles", headers=headers, json={"name": xss_payload})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == xss_payload

    # Fetch profile
    get_res = client.get(f"/api/v1/profiles/{data['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == xss_payload


def test_app_js_uses_escape_html_for_dynamic_insertions():
    app_js_path = Path(__file__).resolve().parent.parent / "web" / "app.js"
    assert app_js_path.exists()
    content = app_js_path.read_text(encoding="utf-8")

    # Verify escapeHtml function is defined
    assert "function escapeHtml" in content

    # Verify critical dynamic variables are passed through escapeHtml
    assert "escapeHtml(p.name)" in content
    assert "escapeHtml(c.original)" in content
    assert "escapeHtml(c.corrected)" in content
    assert "escapeHtml(profile.name)" in content
    assert "escapeHtml(examinerVerdict)" in content
    assert "escapeHtml(pronFeedback)" in content

    # Verify focus trap & modal accessibility handlers exist
    assert "trapModalFocus" in content
    assert "openModal" in content
    assert "closeModal" in content
    assert 'e.key === "Escape"' in content
    assert 'e.key === "Tab"' in content


def test_app_js_syntax_passes_node_check():
    app_js_path = Path(__file__).resolve().parent.parent / "web" / "app.js"
    res = subprocess.run(["node", "-c", str(app_js_path)], capture_output=True, text=True)
    assert res.returncode == 0, f"Node syntax check failed: {res.stderr}"


def test_web_index_serves_security_headers():
    res = client.get("/")
    assert res.status_code == 200
    # Check security headers
    headers = res.headers
    assert "x-content-type-options" in headers
    assert headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in headers
