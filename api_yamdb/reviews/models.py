from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    USER = 'US'
    MODERATOR = 'MO'
    ADMIN = 'AD'
    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        max_length=2,
        choices=ROLE_CHOICES,
        default=USER,
    )


class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='ЧПУ URL жанра',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='ЧПУ URL категории',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания произведения',
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
        ordering = ('-year',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов к произведениям."""
    MARKS = [(i, str(i)) for i in range(1, 11)]

    title = models.ForeignKey(
        to=Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения'
    )
    text = models.TextField(
        verbose_name='Текст отзыва')
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва')
    score = models.CharField(
        max_length=1,
        choices=MARKS,
        verbose_name='Оценка произведения',
        validators=(
            MaxValueValidator(
                10, 'Оценка не может быть более 10.'),
            MinValueValidator(
                1, 'Оценка не может быть менее 1.'),
        ),
        blank=False,
        null=False,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отзыва'
    )

    class Meta:
        """Дополнительная информация по управлению моделью Review."""
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-title', '-id')

    def __str__(self):
        return f'{self.author}: {self.text[:33]}'


class Comment(models.Model):
    """Модель комментариев к отзывам."""
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв')
    text = models.TextField(
        verbose_name='Текст комментария')
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментирования')

    class Meta:
        """Дополнительная информация по управлению моделью Comment."""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-review', '-id',)

    def __str__(self):
        return f'{self.author}: {self.text[:33]}'
