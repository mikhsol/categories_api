from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from categories.serializers import (
    CategoryCreateSerializer,
    CategoryRetrieveSerializer
)
from categories.models import Category


class CategoryCreateView(CreateAPIView):
    serializer_class = CategoryCreateSerializer


class CategoryRetrieveView(RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        pk = fetch_pk(self.kwargs)
        obj = get_object_or_404(Category, pk=pk)
        data = {'id': obj.pk, 'name': obj.name}

        kids = obj.kids.all()
        if len(kids) > 0:
            data['children'] = kids

        if len(obj.child_of.all()) > 0:
            # Based on task assume that only one direct parent.
            data['parents'] = fetch_parents(obj)

        siblings = obj.siblings.all()
        if len(siblings) > 0:
            data['siblings'] = siblings

        serializer = CategoryRetrieveSerializer(data)

        return Response(data=serializer.data)


def fetch_pk(kwargs):
    try:
        return kwargs['pk']
    except AttributeError:
        raise ParseError()

def fetch_parents(obj):
    parent = obj.child_of.first()
    if parent:
        return [parent] + fetch_parents(parent)
    return []
