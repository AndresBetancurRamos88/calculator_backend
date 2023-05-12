from rest_framework import serializers
from .models import Record, Operation


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ["id", "type"]

class RecordSerializer(serializers.ModelSerializer):
    operation_type = serializers.StringRelatedField(source='operation.type')

    class Meta:
        model = Record
        fields = ["id", "creation_date", "amount", "user_balance", "operation_response", "operation_type"]
