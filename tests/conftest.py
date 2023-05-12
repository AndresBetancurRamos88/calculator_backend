import base64
import binascii
import json
import os

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from oauth2_provider.models import Application
from rest_framework.test import APIClient

from apps.records.models import Operation


@pytest.fixture
def secrets():
    return {
        "client_id": "1c276c1f131463996ca3bffef3387d3c7b7f24a32d3b25cf8ae5951981da",
        "client_secret": "d53aae99f17836e17e4cd37bef6c7feebdcccc71715c40448dfcca667bfc",
    }


@pytest.fixture
def header_auth_basic(secrets):
    bytes_to_encode = f'{secrets["client_id"]}:{secrets["client_secret"]}'.encode()
    encoded_bytes = base64.b64encode(bytes_to_encode)
    return f"Basic {encoded_bytes.decode()}"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture(autouse=True)
@pytest.mark.django_db
def create_aplication(secrets):
    user = get_user_model().objects.create_user(username="admin", password="123456")
    client_id = secrets["client_id"]
    client_secret = secrets["client_secret"]

    Application.objects.create(
        client_id=client_id,
        redirect_uris="http://localhost:8000/",
        client_type="confidential",
        authorization_grant_type="password",
        client_secret=client_secret,
        name="calculator",
        user_id=user.id,
        skip_authorization=False,
    )


@pytest.mark.django_db
@pytest.fixture
def get_bearer_token(client, header_auth_basic):
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
    return f"Bearer {response.json()['access_token']}"


@pytest.fixture
def data_operations():
    return {"operation": 2, "username": "admin", "num1": 2, "num2": 2}


@pytest.fixture
def user_operation(request):
    return {
        "operation": Operation.objects.create(
            type=request.param[0], cost=request.param[1]
        ),
        "user": get_user_model().objects.select_related().first(),
    }
