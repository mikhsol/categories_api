from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    JSONField,
    ValidationError,
)

from categories.models import Category


class CategorySerializer(ModelSerializer):
    children = JSONField(required=False)

    class Meta:
        model = Category
        fields = ('name', 'children')

    def create(self, validated_data):
        name = self.get_name(validated_data)
        parent = Category.objects.create(name=name)
        children = self.get_children(validated_data)

        if len(children) > 0:
            self.process_kids(parent, children)
        return parent

    @staticmethod
    def get_name(validated_data):
        try:
            return validated_data.pop('name')
        except KeyError:
            raise ValidationError({'name': '"name" field is required.'})

    @staticmethod
    def get_children(validated_data):
        try:
            return validated_data.pop('children')
        except KeyError:
            return []

    @staticmethod
    def process_kids(parent, children):
        kids = []
        for child in children:
            kids.append(CategorySerializer.retreive_kid(child))
        parent.kids.add(*kids)
        CategorySerializer.set_siblings(kids)

    @staticmethod
    def retreive_kid(child):
        serializer = CategorySerializer(data=child)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)

    @staticmethod
    def set_siblings(kids):
        if len(kids) > 0:
            for i, kid in enumerate(kids):
                kid.siblings.add(*kids[i+1:])
