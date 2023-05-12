import math

import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Operation, Record
from .serializers import OperationSerializer, RecordSerializer


class RecordViewset(GenericViewSet):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = RecordSerializer
    queryset = Record.objects.filter(status=True).select_related("user", "operation")

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Operation id to perform",
                    },
                    "creation_date": {
                        "type": "date",
                        "description": "Creation date",
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Price of each operation",
                    },
                    "user_balance": {
                        "type": "integer",
                        "description": "Available user credits",
                    },
                    "operation_response": {
                        "type": "string",
                        "description": "Operation result",
                    },
                    "operation_type": {
                        "type": "string",
                        "description": "Operation description",
                    },
                },
            }
        },
        responses={
            200: RecordSerializer,
        },
        examples=[
            OpenApiExample(
                name="Common Example",
                value=[
                    {
                    "id": 13,
                    "creation_date": "2023-04-16T15:10:58.377953",
                    "amount": 10,
                    "user_balance": 10,
                    "operation_response": "3",
                    "operation_type": "Addition"
                    },
                    {
                    "id": 11,
                    "creation_date": "2023-04-16T14:58:14.016401",
                    "amount": 50,
                    "user_balance": 80,
                    "operation_response": "1",
                    "operation_type": "Square root"
                    }
                ],
            ),
        ],
        summary="Records for each user operation",
        description="Lists all the records operations per user",
    )
    def list(self, request, *args, **kwargs):
        record_serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(record_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "integer", "description": "Unique user"},
                    "operation": {
                        "type": "integer",
                        "description": "Operation id to perform",
                    },
                    "num1": {
                        "type": "number",
                        "description": "First numerical input for the operation",
                        "default": 0,
                        "minimum": 0,
                    },
                    "num2": {
                        "type": "number",
                        "description": "Second numerical input for the operation",
                        "default": 0,
                        "minimum": 0,
                    },
                },
                "required": ["num1", "num2"],
            }
        },
        responses={
            200: RecordSerializer,
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Bad Request"}
                },
            },
            404: {
                "type": "object",
                "properties": {"error": {"type": "string", "description": "Not Found"}},
            },
        },
        examples=[
            OpenApiExample(
                name="Common Example",
                value={"operation": 1, "username": "admin", "num1": 1, "num2": 2},
            ),
        ],
        summary="Performs a mathematical or string operation for a user and creates a record of the operation",
        description="Takes a `user`, `operation`, `num1` (required), and `num2` (required). `operation` can be set to one of the following values: `addition`, `subtraction`, `multiplication`, `division`, `square_root`, `random_string`.",
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        operation_type = request.data.get("operation")
        num1 = request.data.get("num1")
        num2 = request.data.get("num2")
        cache.clear()

        if operation_type == 6 and (
            not isinstance(num1, int) or not isinstance(num2, int)
        ):
            return Response(
                {"error": "For random string, num1 and num2 must be integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (isinstance(num1, float) | isinstance(num1, int)) or not (
            isinstance(num2, float) | isinstance(num2, int)
        ):
            return Response(
                {"error": "num1 and num2 must be integers or floats"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not all([username, operation_type]):
            return Response(
                {"error": "User Id or Operation Id missing!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()
        try:
            user = cache.get(f"user_{username}")
            if user is None:
                user = User.objects.filter(status="active").get(username=username)
                cache.set(f"user_{username}", user)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exits!"}, status=status.HTTP_404_NOT_FOUND
            )

        operation = cache.get(f"operation_{operation_type}")
        if operation is None:
            try:
                operation = Operation.objects.get(
                    id=operation_type,
                )
                cache.set(f"operation_{operation_type}", operation)
            except Operation.DoesNotExist:
                return Response(
                    {"error": "Operation does not exits!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if operation.type.lower() == "division" and num2 == 0:
            return Response(
                {"error": "Division by zero not allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.balance < operation.cost:
            return Response(
                {"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST
            )

        operations = {
            "Addition": lambda x, y: x + y,
            "Subtraction": lambda x, y: x - y,
            "Multiplication": lambda x, y: x * y,
            "Division": lambda x, y: x / y,
            "Square root": lambda x, y: round(math.sqrt(x), 2),
            "Random string": lambda x, y: self.get_random_string(x, y),
        }

        if operation.type not in operations:
            return Response(
                {"error": f'Operation "{operation.type}" not supported.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = operations[operation.type](num1, num2)
        user.balance -= operation.cost
        user.save()

        Record.objects.create(
            operation=operation,
            user=user,
            amount=operation.cost,
            user_balance=user.balance,
            operation_response=result,
        )

        return Response({"result": result}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        record = self.get_queryset().filter(id=pk).first()
        if record:
            record.status = False
            record.save()
            return Response({"message": "Record deleted"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Not found record"}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def get_random_string(num_strings: int, string_length: int):
        url = f"https://www.random.org/strings/?num={num_strings}&len={string_length}&digits=on&upperalpha=on&loweralpha=on&unique=on&format=plain&rnd=new"
        response = requests.get(url)
        if response.status_code != 200:
            Response({"error": response.reason}, status=status.HTTP_404_NOT_FOUND)
        return response.text


class OperationViewset(GenericViewSet):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = OperationSerializer
    queryset = Operation.objects.all()

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Operation id to perform",
                    },
                    "type": {
                        "type": "string",
                        "description": "Operation name",
                    },
                },
            }
        },
        responses={
            200: RecordSerializer,
        },
        examples=[
            OpenApiExample(
                name="Common Example",
                value=[
                    {"id": 1, "type": "Addition"},
                    {"id": 2, "type": "Subtraction"}
                ],
            ),
        ],
        summary="lists all defined operations",
        description="lists all the operations defined, so that the frontend is aligned with the backend",
    )

    def list(self, request, *args, **kwargs):
        operation_serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(operation_serializer.data, status=status.HTTP_200_OK)
