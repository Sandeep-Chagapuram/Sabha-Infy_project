import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["product"] == "Sabha AI"
    assert "qualcomm_cloud_ai" in data
    assert "models_ready" in data["qualcomm_cloud_ai"]
    assert "Qualcomm Cloud AI Playground is the exclusive LLM provider" in data["qualcomm_cloud_ai"]["notice"]

def test_full_api_workflow_e2e():
    # 1. Register User
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "architect@sabha.ai",
        "password": "Password123!",
        "full_name": "Priya Sharma",
        "workspace_name": "Test Engineering Workspace"
    })
    assert reg_resp.status_code in [200, 400]

    # 2. Login User
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "architect@sabha.ai",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    auth_data = login_resp.json()
    token = auth_data["access_token"]
    ws_id = auth_data["default_workspace_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Live Meeting
    meet_resp = client.post(f"/api/v1/workspaces/{ws_id}/meetings", headers=headers, json={
        "title": "Architecture Sync",
        "input_source": "live_meeting",
        "project_context": "v1.0 release planning"
    })
    assert meet_resp.status_code == 200
    meeting_id = meet_resp.json()["id"]

    # 4. Generate LiveKit Token
    lk_resp = client.post(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/livekit-token", headers=headers)
    assert lk_resp.status_code == 200
    assert "token" in lk_resp.json()

    # 5. Add Live Transcript Segment
    seg_resp = client.post(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/segments", headers=headers, json={
        "sequence_number": 0,
        "speaker_name": "Vikram",
        "text": "I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday.",
        "start_time": 10.5
    })
    assert seg_resp.status_code == 200
    assert seg_resp.json()["text"] == "I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday."

    # 6. Analyze Meeting via Shared Pipeline
    analyze_resp = client.post(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/analyze", headers=headers, json={
        "depth": "full",
        "force_recompute": True
    })
    assert analyze_resp.status_code == 200
    analysis = analyze_resp.json()
    assert analysis["meeting_id"] == meeting_id
    assert "executive_summary" in analysis

    # 7. List Tasks
    tasks_resp = client.get(f"/api/v1/workspaces/{ws_id}/tasks?meeting_id={meeting_id}", headers=headers)
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()
    assert len(tasks) > 0

    # 8. Update Task & Report Blocker
    task_id = tasks[0]["id"]
    patch_resp = client.patch(f"/api/v1/workspaces/{ws_id}/tasks/{task_id}", headers=headers, json={
        "status": "blocked",
        "blocker_reason": "Waiting on upstream database migration"
    })
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "blocked"

    # 9. Get Dashboards
    personal_dash = client.get(f"/api/v1/workspaces/{ws_id}/dashboard/personal", headers=headers)
    assert personal_dash.status_code == 200

    team_dash = client.get(f"/api/v1/workspaces/{ws_id}/dashboard/team", headers=headers)
    assert team_dash.status_code == 200
    assert "task_metrics" in team_dash.json()
    assert "workload_by_member" in team_dash.json()

    # 10. Export Meeting Report (Markdown, CSV, JSON)
    exp_md = client.get(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/export?format=markdown", headers=headers)
    assert exp_md.status_code == 200
    assert "# Sabha AI Meeting Intelligence Report" in exp_md.text

    exp_csv = client.get(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/export?format=csv", headers=headers)
    assert exp_csv.status_code == 200

    exp_json = client.get(f"/api/v1/workspaces/{ws_id}/meetings/{meeting_id}/export?format=json", headers=headers)
    assert exp_json.status_code == 200
    assert exp_json.json()["meeting_id"] == meeting_id
