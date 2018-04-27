from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from categories.models import Category


class CreateBaseTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('categories-app:category-create')
        self.data = {'name': 'Category 1'}


class BadRequestTestCase(CreateBaseTestCase):
    def test_bad_request(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateSimpleCategoryTestCase(CreateBaseTestCase):
    def tearDown(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, 'Category 1')

    def test_create_simple_category(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_with_existed_name(self):
        Category.objects.create(name='Category 1')

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateNestedCategoryTestCase(CreateBaseTestCase):
    def setUp(self):
        super().setUp()
        self.data['children'] = [
                {'name': 'Category 1.1'}
            ]

    def test_create_category_with_one_child(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

        p = Category.objects.get(name='Category 1')
        c = Category.objects.get(name='Category 1.1')
        self.assertEqual(len(p.child_of.all()), 0)
        self.assertEqual(len(p.kids.all()), 1)

        self.assertIn(c, p.kids.all())

        self.assertEqual(len(c.child_of.all()), 1)
        self.assertIn(p, c.child_of.all())

        self.assertEqual(len(p.siblings.all()), 0)
        self.assertEqual(len(c.siblings.all()), 0)

    def test_create_category_kid_with_sibling(self):
        self.data['children'].append({'name': 'Category 1.2'})

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

        p = Category.objects.get(name='Category 1')
        c1 = Category.objects.get(name='Category 1.1')
        c2 = Category.objects.get(name='Category 1.2')
        self.assertEqual(len(p.child_of.all()), 0)
        self.assertEqual(len(p.kids.all()), 2)

        self.assertEqual(len(c1.siblings.all()), 1)
        self.assertEqual(len(c1.siblings.all()), len(c2.siblings.all()))
        self.assertEqual(c1.siblings.all()[0], c2)
        self.assertEqual(c2.siblings.all()[0], c1)

        self.assertIn(c1, p.kids.all())
        self.assertIn(c2, p.kids.all())
