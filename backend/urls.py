from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('shop.urls')),  # Если у вас есть приложение shop
    # Другие маршруты...
]