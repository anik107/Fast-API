from datetime import timedelta
from .utils import *
from ..routers.users import get_current_user, get_db
from ..routers.auth import (
    authenticate_user,
    authenticate_user,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)
from jose import jwt
from ..main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_authenticated_user(test_user):
    db = TestingSessionLocal()

    authenticated_user_result = authenticate_user(
        username=test_user.username,
        password="password", # Use the plain text password
        db=db
    )
    assert authenticated_user_result is not None
    assert authenticated_user_result.username == test_user.username

    non_authenticated_user_result = authenticate_user(
        username="nonexistentuser",
        password="wrongpassword",
        db=db
    )
    assert non_authenticated_user_result is False

    wrong_password_result = authenticate_user(
        username=test_user.username,
        password="wrongpassword",
        db=db
    )
    assert wrong_password_result is False

def test_create_access_token(test_user):
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.username == test_user.username).first()
    expires_delta = timedelta(minutes=30)
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=expires_delta
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user.username
    assert payload["id"] == user.id
    assert payload["role"] == user.role