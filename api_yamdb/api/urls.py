from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from .views import CommentViewSet, ReviewViewSet, TitleViewSet

router = routers.DefaultRouter()

router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='comment')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review')


urlpatterns = [
    path('v1/', include(router.urls),),
]
