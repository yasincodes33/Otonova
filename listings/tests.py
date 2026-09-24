from django.test import TestCase


class ArabalarTest(TestCase):
    def test_arabalar_200(self):
        r = self.client.get('/arabalar/')
        self.assertEqual(r.status_code, 200)
