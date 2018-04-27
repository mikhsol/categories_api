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


class RetreiveCategoryBaseTestCase(APITestCase):
    def setUp(self):
        self.url_name = 'categories-app:category-details'


class RetreiveCategoryErrorTestCase(RetreiveCategoryBaseTestCase):
    def test_get_not_allowed(self):
        url = reverse(self.url_name, args=['0'])
        response = self.client.get(url[:len(url)-2])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_404(self):
        url = reverse(self.url_name, args=['0'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RetreiveCategoryTestCase(RetreiveCategoryBaseTestCase):
    def setUp(self):
        super().setUp()
        self.c1 = Category.objects.create(name='Category 1')

    def test_get_simple_category(self):
        url = reverse(self.url_name, args=['1'])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.c1.pk)
        self.assertEqual(response.data['name'], self.c1.name)

    def test_get_category_with_child(self):
        c11 = Category.objects.create(name='Category 1.1')
        self.c1.kids.add(c11)

        url = reverse(self.url_name, args=['1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], self.c1.pk)
        self.assertEqual(response.data['name'], self.c1.name)
        self.assertEqual(len(response.data['children']), 1)
        self.assertEqual(response.data['children'][0]['id'], c11.pk)
        self.assertEqual(response.data['children'][0]['name'], c11.name)

    def test_get_category_with_parents(self):
        c11 = Category.objects.create(name='Category 1.1')
        c111 = Category.objects.create(name='Category 1.1.1')
        self.c1.kids.add(c11)
        c11.kids.add(c111)

        url = reverse(self.url_name, args=['3'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], c111.pk)
        self.assertEqual(response.data['name'], c111.name)
        self.assertEqual(len(response.data['parents']), 2)
        self.assertEqual(response.data['parents'][0]['id'], c11.pk)
        self.assertEqual(response.data['parents'][0]['name'], c11.name)
        self.assertEqual(response.data['parents'][1]['id'], self.c1.pk)
        self.assertEqual(response.data['parents'][1]['name'], self.c1.name)

    def test_get_category_with_siblings(self):
        c11 = Category.objects.create(name='Category 1.1')
        c12 = Category.objects.create(name='Category 1.2')
        self.c1.kids.add(c11, c12)
        c12.siblings.add(c11)

        url = reverse(self.url_name, args=['2'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], c11.pk)
        self.assertEqual(response.data['name'], c11.name)
        self.assertEqual(len(response.data['parents']), 1)
        self.assertEqual(response.data['parents'][0]['id'], self.c1.pk)
        self.assertEqual(response.data['parents'][0]['name'], self.c1.name)
        self.assertEqual(response.data['siblings'][0]['id'], c12.pk)
        self.assertEqual(response.data['siblings'][0]['name'], c12.name)




class TaskEndToEndTestCase(APITestCase):
    def test_post(self):
        url = reverse('categories-app:category-create')
        data = {
            'name': 'Category 1',
            'children': [
                {
                    'name': 'Category 1.1',
                    'children': [
                        {
                            'name': 'Category 1.1.1',
                            'children': [
                                {'name': 'Category 1.1.1.1'},
                                {'name': 'Category 1.1.1.2'},
                                {'name': 'Category 1.1.1.3'}
                            ]
                        },
                        {
                            'name': 'Category 1.1.2',
                            'children': [
                                {'name': 'Category 1.1.2.1'},
                                {'name': 'Category 1.1.2.2'},
                                {'name': 'Category 1.1.2.3'}
                            ]
                        }
                    ]
                },
                {
                    'name': 'Category 1.2',
                    'children': [
                        {'name':  'Category 1.2.1'},
                        {
                            'name': 'Category 1.2.2',
                            'children': [
                                {'name': 'Category 1.2.2.1'},
                                {'name': 'Category 1.2.2.2'}
                            ]
                        }
                    ]
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(Category.objects.all()), 15)

        c1 = Category.objects.get(name='Category 1')
        self.assertEqual(len(c1.child_of.all()), 0)
        c1_kids = c1.kids.all()
        self.assertEqual(len(c1_kids), 2)

        c11 = Category.objects.get(name='Category 1.1')
        c12 = Category.objects.get(name='Category 1.2')
        self.assertIn(c11, c1_kids)
        self.assertIn(c12, c1_kids)

        self.assertEqual(len(c11.child_of.all()), 1)
        self.assertIn(c1, c11.child_of.all())

        self.assertEqual(len(c12.child_of.all()), 1)
        self.assertIn(c1, c12.child_of.all())

        self.assertEqual(len(c11.siblings.all()), 1)
        self.assertEqual(len(c12.siblings.all()), 1)

        self.assertIn(c12, c11.siblings.all())
        self.assertIn(c11, c12.siblings.all())

        c111 = Category.objects.get(name='Category 1.1.1')
        self.assertEqual(len(c111.child_of.all()),1)
        self.assertIn(c11, c111.child_of.all())

        self.assertEqual(len(c111.kids.all()), 3)

        c1111 = Category.objects.get(name='Category 1.1.1.1')
        c1112 = Category.objects.get(name='Category 1.1.1.2')
        c1113 = Category.objects.get(name='Category 1.1.1.3')

        self.assertIn(c1111, c111.kids.all())
        self.assertIn(c1112, c111.kids.all())
        self.assertIn(c1113, c111.kids.all())

        self.assertEqual(len(c1111.siblings.all()), 2)
        self.assertEqual(len(c1112.siblings.all()), 2)
        self.assertEqual(len(c1113.siblings.all()), 2)

        self.assertIn(c1113, c1111.siblings.all())
        self.assertIn(c1112, c1111.siblings.all())

        self.assertIn(c1111, c1112.siblings.all())
        self.assertIn(c1113, c1112.siblings.all())

        self.assertIn(c1111, c1113.siblings.all())
        self.assertIn(c1112, c1113.siblings.all())
