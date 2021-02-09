from django.test import TestCase

from django.contrib.auth import get_user_model


class UserManagerTests(TestCase):
    
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(phone_number='08130165966', email="smartyleey@gmail.com", password='chi11111')
        self.assertEqual(user.phone_number, '08130165966')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(phone_number='08130165966')
        with self.assertRaises(TypeError):
            User.objects.create_user(phone_number='08130165966', email="smartyleey@gmail.com", password='chi11111')
            
        def test_create_superuser(self):
            User = get_user_model()
            admin_user = User.objectes.create_superuser('08130165966', 'smartyleey@gmail.com', 'chi11111')
            self.assertEqual(admin_user.phone_number, '08130165966')
            self.assertTrue(admin_user.is_active)
            self.assertTrue(admin_user.is_staff)
            self.assertTrue(admin_user.is_superuser)
            try:
                self.assertIsNone(admin_user.username)
            except AttributeError:
                pass
            with self.assertRaises(ValueError):
                User.objects.create_superuser(phone_number='08130165966', email='smartyleey@gmail.com', password='chi11111', is_superuser=False)