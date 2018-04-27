from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
)

from categories.models import Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)

    def create(self, validated_data):
        category = Category.objects.create(**validated_data)
        return validated_data