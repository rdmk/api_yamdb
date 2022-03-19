from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (AdminOnly, AuthorAdminModeratorOrReadOnly,
                             IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             CreateUserSerializer, GenreSerializer,
                             GetTokenSerializer, ReviewSerializer,
                             TitleSerializer, UserSerializer,
                             TitleCreateSerializer)
from api.viewsets import FilteredAdminOrReadOnlyListCreateDestroyViewSet
from api_yamdb.settings import PROJECT_EMAIL
from reviews.models import Category, Genre, Review, Title, User

WRONG_CONFIRMATION_CODE = 'Ошибочный код подтверждения'


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_user(request):
    """Creates user and sends email containing confirmation code"""
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, created = User.objects.get_or_create(
            username=username,
            email=email.lower()
        )
    except IntegrityError:
        return Response(
            {'message': 'Имя пользователя или почта уже используются.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    token = default_token_generator.make_token(user)
    send_mail(
        'Confirmation code',
        f'Your confirmation code is {token}',
        PROJECT_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token_for_user(request):
    """Generates and returns token for created user"""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    token = serializer.validated_data['confirmation_code']
    if not default_token_generator.check_token(user, token):
        return Response(
            WRONG_CONFIRMATION_CODE, status=status.HTTP_400_BAD_REQUEST
        )
    refresh = str(RefreshToken.for_user(user).access_token)
    return Response(
        {"token": refresh},
        status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes((IsAuthenticated,))
def users_me(request):
    """Lets user obtain and update his personal data"""
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(role=user.role)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AdminOnly,)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(FilteredAdminOrReadOnlyListCreateDestroyViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(FilteredAdminOrReadOnlyListCreateDestroyViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TitleSerializer
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score'))
    ordering_fields = ['name']
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleCreateSerializer
        return TitleSerializer
