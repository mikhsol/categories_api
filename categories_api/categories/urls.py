from django.urls import path

from categories.views import CategoryCreateView


app_name = 'categories-app'

urlpatterns = [
    path('categories/', CategoryCreateView.as_view(), name='category-create')
]
