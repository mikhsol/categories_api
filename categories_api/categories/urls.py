from django.urls import path

from categories.views import (
    CategoryCreateView,
    CategoryRetrieveView,
)


app_name = 'categories-app'

urlpatterns = [
    path('categories/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', CategoryRetrieveView.as_view(), name='category-details'),
]
