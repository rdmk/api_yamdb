from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User


class CreateUserSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(required=True, max_length=254)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не допустимо!'
            )
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']
        model = User
        lookup_field = 'username'


class GetTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(required=True)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['id']
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'year', 'rating', 'description',
                  'genre', 'category']
        model = Title
        read_only_fields = ['name', 'year', 'rating', 'description',
                            'genre', 'category']


class TitleCreateSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'description',
                  'genre', 'category']


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        user = self.context['request'].user
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError('Вы уже написали отзыв.')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
