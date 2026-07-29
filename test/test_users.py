from .utils import *
from database import get_db
from routers.auth import get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK

    assert response.json()['username'] == 'vivi'
    assert response.json()['email'] == 'vivi@gmail.com'
    assert response.json()['first_name'] == 'viviana'
    assert response.json()['last_name'] == 'zuniga'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '7821211866'

def test_change_password_success(test_user):
    response = client.put("/user/password", json={"password": "testpassword", "new_password": "testnewpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"password": "wrooong_password", "new_password": "testnewpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on change password'}

def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber", json={"phone_number": "7821115486"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
