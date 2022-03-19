from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, create_user,
                       get_token_for_user, users_me)

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review')

auth_urls = [
    path('signup/', create_user),
    path('token/', get_token_for_user),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/users/me/', users_me),
    path('v1/', include(router_v1.urls)),
]
