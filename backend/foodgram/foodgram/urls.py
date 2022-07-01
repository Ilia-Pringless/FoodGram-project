from django.contrib import admin
from django.urls import include, path

api = [
    path('', include('api.urls')),
    path('', include('users.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api)),
]
