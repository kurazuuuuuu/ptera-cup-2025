from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
import pytest

client = TestClient(app)

def test_timeline_lifecycle():
    # 1. Create a post
    post_data = {"username": "testuser_pytest", "content": "This is a test post from pytest"}
    response = client.post("/posts", json=post_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == post_data["username"]
    assert data["content"] == post_data["content"]
    assert "id" in data
    post_id = data["id"]
    print(f"Created post with ID: {post_id}")

    # 2. Get timeline and verify post exists
    response = client.get("/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) > 0
    # Check if our created post is in the list
    found = False
    for post in posts:
        if post["id"] == post_id:
            assert post["username"] == post_data["username"]
            assert post["content"] == post_data["content"]
            found = True
            break
    assert found, f"Post with ID {post_id} not found in timeline"

    # 3. Delete the post
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json() == {"message": f"ID {post_id} の投稿を削除しました。"}

    # 4. Verify post is gone
    response = client.get("/posts")
    assert response.status_code == 200
    posts = response.json()
    found = False
    for post in posts:
        if post["id"] == post_id:
            found = True
            break
    assert not found, f"Post with ID {post_id} should have been deleted"
    print("Test passed successfully!")
