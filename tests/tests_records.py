import json
import math
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.records.models import Operation, Record


@pytest.mark.django_db
def test_addition(get_bearer_token, client, data_operations):
    Operation.objects.create(type="Addition", cost=10)
    data_operations["operation"] = 1
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": 4}


@pytest.mark.django_db
def test_subtraction(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Subtraction", cost=20)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": 0}


@pytest.mark.django_db
def test_multiplication(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Multiplication", cost=30)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": 4}


@pytest.mark.django_db
def test_division(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Division", cost=40)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": 1}

    data_operations["num2"] = 0
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.json() == {"error": "Division by zero not allowed"}


@pytest.mark.django_db
def test_square_root(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Square root", cost=50)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )
    expeted = {"result": round(math.sqrt(data_operations["num1"]), 2)}

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expeted


@pytest.mark.django_db
def test_random_string(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Random string", cost=60)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"]


@pytest.mark.django_db
def test_random_string_mock(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Random string", cost=60)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    with patch("apps.records.views.requests.get") as mock_get:
        mock_get.return_value.status_code = status.HTTP_200_OK
        mock_get.return_value.text = "randomstring"
        response = client.post(
            reverse("record-list"),
            data=json_data,
            HTTP_AUTHORIZATION=get_bearer_token,
            content_type="application/json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"] == "randomstring"


@pytest.mark.django_db
def test_bad_request(get_bearer_token, client, data_operations):
    Operation.objects.create(type="Random string", cost=60)
    del data_operations["username"]
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "User Id or Operation Id missing!"}

    data_operations["user"] = get_user_model().objects.select_related().first().id
    del data_operations["operation"]
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "User Id or Operation Id missing!"}

    del data_operations["user"]
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "User Id or Operation Id missing!"}


@pytest.mark.django_db
def test_not_found(get_bearer_token, client, data_operations):
    Operation.objects.create(type="Random string", cost=60)
    data_operations["username"] = 1000
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"error": "User does not exits!"}

    data_operations["username"] = get_user_model().objects.select_related().first().username
    data_operations["operation"] = 10000
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"error": "Operation does not exits!"}


@pytest.mark.django_db
def test_insufficient_balance(get_bearer_token, client, data_operations):
    operation = Operation.objects.create(type="Random string", cost=210)
    data_operations["operation"] = operation.id
    data_operations["user"] = get_user_model().objects.select_related().first().id
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "Insufficient balance"}


@pytest.mark.django_db
def test_wrong_data_type(get_bearer_token, client, data_operations):
    data_operations["num1"] = "a"
    data_operations["num2"] = "b"
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "num1 and num2 must be integers or floats"}


@pytest.mark.django_db
def test_wrong_data_type_random_string(get_bearer_token, client, data_operations):
    data_operations["operation"] = 6
    data_operations["num1"] = 1.2
    data_operations["num2"] = 2.1
    json_data = json.dumps(data_operations)

    response = client.post(
        reverse("record-list"),
        data=json_data,
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error": "For random string, num1 and num2 must be integers"
    }


@pytest.mark.django_db
@pytest.mark.parametrize("user_operation", [("Random string", 60)], indirect=True)
def test_record_list(get_bearer_token, client, user_operation):
    Record.objects.create(
        user=user_operation["user"],
        operation=user_operation["operation"],
        amount=10,
        user_balance=190,
        operation_response=user_operation["operation"].cost,
    )

    response = client.get(
        reverse("record-list"),
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["operation_response"] == "60"


@pytest.mark.django_db
@pytest.mark.parametrize("user_operation", [("Random string", 60)], indirect=True)
def test_destroy(get_bearer_token, client, user_operation):
    record = Record.objects.create(
        user=user_operation["user"],
        operation=user_operation["operation"],
        amount=10,
        user_balance=190,
        operation_response=user_operation["operation"].cost,
    )

    response = client.delete(
        reverse("record-detail", kwargs={"pk": record.id}),
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Record deleted"}


@pytest.mark.django_db
def test_destroy_not_found(get_bearer_token, client):
    response = client.delete(
        reverse("record-detail", kwargs={"pk": 1000}),
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "Not found record"}


@pytest.mark.django_db
def test_operation_list(get_bearer_token, client):
    Operation.objects.create(
        type="suma",
        cost=100,
    )

    response = client.get(
        reverse("operation-list"),
        HTTP_AUTHORIZATION=get_bearer_token,
        content_type="application/json",
    )
    pytest.set_trace()
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["type"]== "suma"