from rest_framework.generics import CreateAPIView

from categories.serializers import CategorySerializer
from categories.models import Category


class CategoryCreateView(CreateAPIView):
    serializer_class = CategorySerializer

