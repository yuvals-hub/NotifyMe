from django.urls import path
from .views import traffic

urlpatterns = [
    path('', traffic, name= 'traffic'),
]