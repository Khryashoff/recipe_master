from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import EMAIL, USERNAME_NAME, USERNAME_SURNAME


class User(AbstractUser):
    """
    Класс, представляющий пользователя.
    """
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=EMAIL,
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        max_length=USERNAME_NAME,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USERNAME_NAME
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=USERNAME_SURNAME
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    """
    Класс, представляющий подписку пользователя на автора рецептов.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписался на {self.author} '
