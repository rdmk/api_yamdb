from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (CurrentUserDefault, FloatField,
                                        ModelSerializer, ValidationError)
from reviews.models import Category, Comment, Genre, Review, Title


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        exclude = ['id']


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        exclude = ['id']


class TitleSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title
        read_only_fields = ['id', 'rating']


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', read_only=True, default=CurrentUserDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'pub_date')


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
