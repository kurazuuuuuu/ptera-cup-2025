from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app


# Helper to get auth token
def get_auth_headers(client):
    # 1. Register
    email = "test_timeline@example.com"
    password = "password123"
    try:
        client.post("/v1/auth/register", json={
            "email": email,
            "password": password,
            "username": "timeline_tester"
        })
        # Ignore 400 if already exists
    except Exception:
        pass

    # 2. Login
    login_res = client.post("/v1/auth/jwt/login", data={
        "username": email,
        "password": password
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_timeline_lifecycle():
    with TestClient(app) as client:
        headers = get_auth_headers(client)
        
        # 1. Create a post (Need a dummy Event ID?)
        # First, create an event
        event_data = {
            "title": "Timeline Test Event",
            "category": "Test",
            "start_date": "2025-12-25T10:00:00",
            "end_date": "2025-12-25T12:00:00"
        }
        event_res = client.post("/v1/events/", json=event_data, headers=headers)
        
        assert event_res.status_code == 201, f"Create event failed: {event_res.text}"
        event_id = event_res.json()["id"]

        post_data = {
            "event_id": event_id,
            "content": "This is a test post from pytest"
        }
        response = client.post("/v1/timeline/posts", json=post_data, headers=headers)
        assert response.status_code == 200, f"Create post failed: {response.text}"
        data = response.json()
        assert data["content"] == post_data["content"]
        assert "id" in data
        post_id = data["id"]
        print(f"Created post with ID: {post_id}")

        # 2. Get timeline and verify post exists
        response = client.get("/v1/timeline/posts", headers=headers)
        assert response.status_code == 200
        posts = response.json()
        assert len(posts) > 0
        # Check if our created post is in the list
        found = False
        for post in posts:
            if post["id"] == post_id:
                assert post["content"] == post_data["content"]
                found = True
                break
        assert found, f"Post with ID {post_id} not found in timeline"

        # 3. Delete the post
        response = client.delete(f"/v1/timeline/posts/{post_id}", headers=headers)
        assert response.status_code == 204
        
        # 4. Verify post is gone
        response = client.get("/v1/timeline/posts", headers=headers)
        assert response.status_code == 200
        posts = response.json()
        found = False
        for post in posts:
            if post["id"] == post_id:
                found = True
                break
        assert not found, f"Post with ID {post_id} should have been deleted"
        print("Test passed successfully!")
