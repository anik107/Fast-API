from fastapi import status
from .utils import *
from ..routers.admin import get_current_user, get_db
from ..main import app
from ..models import TodoItem

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    response_data = response.json()
    assert len(response_data) == 1
    todo_data = response_data[0]

    for key, value in todo_data.items():
        assert key in ["title", "description", "priority", "completed", "owner_id", "id"]
        assert value == test_todo.__getattribute__(key)

def test_admin_delete_todo_authenticated(test_todo):
    response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Todo deleted successfully"}

    db = TestingSessionLocal()
    model = db.query(TodoItem).filter(TodoItem.id == test_todo.id).first()
    assert model is None

def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}

def test_admin_delete_todo_unauthorized():
    app.dependency_overrides[get_current_user] = lambda: None
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
    app.dependency_overrides[get_current_user] = override_get_current_user