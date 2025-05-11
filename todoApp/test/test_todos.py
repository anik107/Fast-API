from fastapi import status
from ..routers.todos import get_current_user, get_db
from ..main import app
from .utils import *
from ..models import TodoItem

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert response.json() == [{
        "title": "Test Todo",
        "description": "This is a test todo item",
        "priority": 5,
        "completed": False,
        "owner_id": 1,
        "id": 1
    }]

def test_read_one_authenticated(test_todo):
    response = client.get(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Test Todo",
        "description": "This is a test todo item",
        "priority": 5,
        "completed": False,
        "owner_id": 1,
        "id": test_todo.id
    }
    assert response.json()["id"] == test_todo.id

def test_create_todo_authenticated(test_todo):
    request_body = {
        "title": "New Todo",
        "description": "This is a new todo item",
        "priority": 3,
        "completed": False
    }
    response = client.post("/todos/todo", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(TodoItem).filter(TodoItem.id == response.json()["id"]).first()

    for key, value in request_body.items():
        assert getattr(model, key) == value

def test_update_todo_authenticated(test_todo):
    request_body = {
        "title": "Updated Todo",
        "description": "This is an updated todo item",
        "priority": 5,
        "completed": False
    }
    response = client.put(f"/todos/todo/{test_todo.id}", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(TodoItem).filter(TodoItem.id == test_todo.id).first()

    for key, value in request_body.items():
        assert getattr(model, key) == value

def test_delete_todo_authenticated(test_todo):
    response = client.delete(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(TodoItem).filter(TodoItem.id == test_todo.id).first()
    assert model is None