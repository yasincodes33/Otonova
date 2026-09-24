from django.test import TestCase
from django.urls import reverse


class AnasayfaTestCase(TestCase):
    def test_index_200(self):
        response = self.client.get(reverse('pages:index'))
        self.assertEqual(response.status_code, 200)

    def test_hakkimizda_200(self):
        response = self.client.get(reverse('pages:hakkimizda'))
        self.assertEqual(response.status_code, 200)
