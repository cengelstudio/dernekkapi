import unittest
from app import create_app
from app.services.bot import AVFEDBot, process_member_registration
from app.models import Member

class BotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.bot = AVFEDBot()

    def tearDown(self):
        self.app_context.pop()

    def test_bot_initialization(self):
        """Bot'un doğru şekilde başlatıldığını test et"""
        self.assertFalse(self.bot.is_logged_in)
        self.assertIsNone(self.bot.session)

    def test_login_to_avfed(self):
        """AVFED sistemine giriş işlemini test et"""
        result = self.bot.login_to_avfed("testuser", "testpass")
        self.assertTrue(result)
        self.assertTrue(self.bot.is_logged_in)

    def test_fill_member_form(self):
        """Üye formu doldurma işlemini test et"""
        # Önce giriş yap
        self.bot.login_to_avfed("testuser", "testpass")

        # Test üyesi oluştur
        member = Member("12345678901", "Test", "User", "test-association-id")
        member.phoneNumber = "02121234567"
        member.gsm = {"countryCode": "+90", "operatorCode": "533", "number": "1234567"}

        result = self.bot.fill_member_form(member)
        self.assertTrue(result)

    def test_upload_receipt(self):
        """Makbuz yükleme işlemini test et"""
        # Önce giriş yap
        self.bot.login_to_avfed("testuser", "testpass")

        result = self.bot.upload_receipt("test_receipt.jpg", "test-member-id")
        self.assertTrue(result)

    def test_logout(self):
        """Çıkış işlemini test et"""
        # Önce giriş yap
        self.bot.login_to_avfed("testuser", "testpass")
        self.assertTrue(self.bot.is_logged_in)

        # Çıkış yap
        result = self.bot.logout()
        self.assertTrue(result)
        self.assertFalse(self.bot.is_logged_in)

    def test_process_member_registration(self):
        """Üye kayıt işlemini test et"""
        # Test üyesi oluştur
        member = Member("12345678901", "Test", "User", "test-association-id")
        member.phoneNumber = "02121234567"
        member.gsm = {"countryCode": "+90", "operatorCode": "533", "number": "1234567"}

        # AVFED kimlik bilgileri
        avfed_credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }

        result = process_member_registration(member, avfed_credentials)

        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertIn('member_id', result)
        self.assertEqual(result['member_id'], member.id)
        self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main()
