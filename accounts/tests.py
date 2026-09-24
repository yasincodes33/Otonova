from django.test import TestCase
from django.contrib.auth.models import User
from .models import ProfilModel


class ProfilSignalTest(TestCase):
    def test_profil_olusturulur(self):
        user = User.objects.create_user('test@test.com', 'test@test.com', 'sifre1234')
        self.assertTrue(ProfilModel.objects.filter(kullanici=user).exists())


class AuthViewTest(TestCase):
    def test_kayit_200(self):
        r = self.client.get('/kayit/')
        self.assertEqual(r.status_code, 200)

    def test_giris_200(self):
        r = self.client.get('/giris/')
        self.assertEqual(r.status_code, 200)
