from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import CustomUsersViewSet, TokenView

app_name = 'users'

router = DefaultRouter()

router.register('users', CustomUsersViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', TokenView.as_view(), name='signup'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='signout'),
]
