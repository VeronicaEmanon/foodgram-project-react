from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        help_text="Введите имя"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="Введите фамилию"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Юзернейм"
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Электронная почта",
        help_text="Введите электронную почту"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Подписка на автора"
        verbose_name_plural = "Подписка на авторов"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_author_for_user",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписался на {self.author}"
