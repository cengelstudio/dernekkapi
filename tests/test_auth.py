import unittest
from app import create_app
from app.services.db import get_user_by_username, create_user
from app.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_login_page(self):
        """Giriş sayfasının yüklendiğini test et"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DernekKap', response.data)

    def test_admin_login_success(self):
        """Admin girişinin başarılı olduğunu test et"""
        # Test admin kullanıcısı oluştur
        test_user = User("testadmin", "testpass", "admin")
        create_user(test_user)

        response = self.client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpass',
            'user_type': 'admin'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_admin_login_failure(self):
        """Yanlış admin girişinin başarısız olduğunu test et"""
        response = self.client.post('/auth/login', data={
            'username': 'wronguser',
            'password': 'wrongpass',
            'user_type': 'admin'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ge\xc3\xa7ersiz', response.data)

    def test_logout(self):
        """Çıkış işleminin çalıştığını test et"""
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DernekKap', response.data)

if __name__ == '__main__':
    unittest.main()
