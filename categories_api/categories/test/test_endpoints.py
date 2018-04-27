from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from categories.models import Category


class SimpleCreateCategoryTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('categories-app:category-create')

    def test_create_simple_category(self):
        data = {'name': 'Category'}

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_with_existed_name(self):
        Category.objects.create(name='Category')
        data = {'name': 'Category'}

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, 'Category')
