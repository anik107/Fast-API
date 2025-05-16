from .utils import *
from ..routers.users import get_current_user, get_db
from ..main import app
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    respose = client.get("/user")
    assert respose.status_code == status.HTTP_200_OK
    assert isinstance(respose.json(), dict)
    assert respose.json()['username'] == test_user.username
    assert respose.json()['email'] == test_user.email
    assert respose.json()['first_name'] == test_user.first_name
    assert respose.json()['last_name'] == test_user.last_name
    assert respose.json()['id'] == test_user.id
    assert respose.json()['role'] == test_user.role
    assert respose.json()['hashed_password'] == test_user.hashed_password
    assert respose.json()['phone_number'] == test_user.phone_number
    assert respose.json()['id'] == test_user.id

def test_update_password(test_user):
    response = client.put(
        "/user/password",
        json={
            "password": "password",
            "new_password": "new_password"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password updated successfully"}

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert bcrypt_context.verify("new_password", model.hashed_password)

def test_update_password_invalid(test_user):
    response = client.put(
        "/user/password",
        json={
            "password": "wrong_password",
            "new_password": "new_password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid password"}
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert bcrypt_context.verify("password", model.hashed_password)
    assert not bcrypt_context.verify("new_password", model.hashed_password)
    assert model.hashed_password != "new_password"

def test_change_phone_number(test_user):
    response = client.put(
        f"/user/phonenumber/{test_user.phone_number}",
        json={
            "phone_number": "0987654321"
        }
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert model.phone_number == "1234567890"
    assert model.phone_number == test_user.phone_number

def test_change_phone_number_invalid(test_user):
    response = client.put(
        f"/user/phonenumber/{test_user.phone_number}",
        json={
            "phone_number": "123"
        }
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

