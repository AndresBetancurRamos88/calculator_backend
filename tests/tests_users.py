import base64
import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login(client, header_auth_basic):
    data = {
        "username": "admin",
        "password": "123456",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=header_auth_basic,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.django_db
def test_login_not_auth_header(client):
    data = {
        "username": "admin",
        "password": "123465",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Authorization Header missing"}


@pytest.mark.django_db
def test_login_invalid_application(client):
    bytes_to_encode = "123:456".encode()
    encoded_bytes = base64.b64encode(bytes_to_encode)
    encoded_string = encoded_bytes.decode()
    auth_header = f"Basic {encoded_string}"

    data = {
        "username": "admin",
        "password": "123456",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=auth_header,
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json() == {"error": "Invalid application"}


@pytest.mark.django_db
def test_login_not_credentials(client, header_auth_basic):
    data = {
        "username": "",
        "password": "",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=header_auth_basic,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Please provide both username and password"}


@pytest.mark.django_db
def test_login_not_password(client, header_auth_basic):
    data = {
        "username": "admin",
        "password": "",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=header_auth_basic,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Please provide both username and password"}


@pytest.mark.django_db
def test_login_not_user(client, header_auth_basic):
    data = {
        "username": "",
        "password": "123456",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=header_auth_basic,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Please provide both username and password"}


@pytest.mark.django_db
def test_login_invalid_credentials(client, header_auth_basic):
    data = {
        "username": "admin",
        "password": "aaaaaa",
        "grant_type": "password",
    }
    json_data = json.dumps(data)

    response = client.post(
        reverse("login"),
        data=json_data,
        HTTP_AUTHORIZATION=header_auth_basic,
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json() == {"error": "Invalid Credentials"}


@pytest.mark.django_db
def test_logout_invalid_token(client):
    auth_header = "Bearer 123456"
    response = client.post(
        reverse("logout"),
        HTTP_AUTHORIZATION=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid access token"}


@pytest.mark.django_db
def test_logout(get_bearer_token, client):
    response = client.post(
        reverse("logout"),
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}
