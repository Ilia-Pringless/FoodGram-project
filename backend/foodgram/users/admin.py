from django.contrib import admin

from foodgram.settings import EMPTY_VALUE_DISPLAY
from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'is_superuser')
    list_filter = ('username', 'email', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id', 'username', 'email')
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY
