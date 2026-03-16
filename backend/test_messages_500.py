from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User

client = TestClient(app)

def test_messages():
    db = SessionLocal()
    # Find any 2 users
    users = db.query(User).limit(2).all()
    if len(users) < 2:
        return
    u1, u2 = users[0], users[1]
    
    # We will just hack dependencies using dependency_overrides
    from dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: u1

    # Try fetching messages
    print(f"Fetching messages between {u1.user_id} and {u2.user_id}")
    res = client.get(f"/api/messages/{u1.user_id}/{u2.user_id}")
    print("GET STATUS:", res.status_code)
    print("GET BODY:", res.text)
    
    # Try posting message
    print("\nPosting message")
    res2 = client.post("/api/messages", json={"receiver_id": str(u2.user_id), "content": "hello test"})
    print("POST STATUS:", res2.status_code)
    print("POST BODY:", res2.text)

if __name__ == "__main__":
    test_messages()
