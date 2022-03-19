from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор'),
]


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=254,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        max_length=max(len(role) for _, role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )

    def is_admin(self):
        return (
            self.role == ADMIN
            or self.is_staff
        )

    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class GenreAndCategory(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Идентификатор',
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class Genre(GenreAndCategory):
    class Meta(GenreAndCategory.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(GenreAndCategory):
    class Meta(GenreAndCategory.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    def year_validator(self):
        if self > date.today().year:
            raise ValidationError(
                ('Нельзя добавить произведение из будущего.'),
                params={'value': self},
            )
    name = models.TextField(verbose_name='Название произведения')
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания произведения',
        validators=[year_validator],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
    )

    class Meta:
        ordering = ('-year', 'name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class ReviewAndComment(models.Model):
    text = models.TextField(
        verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )

    class Meta:
        abstract = True


class Review(ReviewAndComment):
    """Модель отзывов к произведениям."""
    title = models.ForeignKey(
        to=Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MaxValueValidator(
                10, 'Оценка не может быть более 10.'),
            MinValueValidator(
                1, 'Оценка не может быть менее 1.'),
        ),
    )

    class Meta:
        """Дополнительная информация по управлению моделью Review."""
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (models.UniqueConstraint(
            fields=['title', 'author'],
            name='unique_review_by_author'
        ),)

    def __str__(self):
        return f'{self.author}: {self.text[:33]}'


class Comment(ReviewAndComment):
    """Модель комментариев к отзывам."""
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв')
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор')

    class Meta:
        """Дополнительная информация по управлению моделью Comment."""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author}: {self.text[:33]}'
