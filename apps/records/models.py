from django.db import models

from apps.users.models import User


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(
        verbose_name="Creation date", auto_now=False, auto_now_add=True
    )
    status = models.BooleanField("Status", default=True)

    class Meta:
        abstract = True
        verbose_name = "Base model"
        verbose_name_plural = "Base models"


class Operation(BaseModel):
    type = models.CharField(
        verbose_name="Operation type", blank=False, null=False, max_length=15
    )
    cost = models.IntegerField(verbose_name="Operation cost", blank=False, null=False)

    class Meta:
        verbose_name = "Operation"
        verbose_name_plural = "Operations"

    def __str__(self) -> str:
        return f"{self.type} cost is {self.cost}"


class Record(BaseModel):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name="Amount", blank=False, null=False)
    user_balance = models.IntegerField(
        verbose_name="User balance", blank=False, null=False
    )
    operation_response = models.CharField(
        verbose_name="Operation Response", blank=False, null=False, max_length=15
    )

    class Meta:
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self) -> str:
        return f"User balance is {self.user_balance}"
