from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(
        self,
        username: str,
        is_staff: bool,
        is_superuser: bool,
        password: str,
        **extra_fields,
    ):
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, False, False, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        return self._create_user(username, True, True, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    balance = models.IntegerField(default=200)
    status = models.CharField(max_length=10, default="active")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"{self.username}"
