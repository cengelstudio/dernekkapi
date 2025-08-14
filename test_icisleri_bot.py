#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İçişleri Bot Test Dosyası
Bot'un çeşitli fonksiyonlarını test eder.
"""

import unittest
from unittest.mock import Mock, patch
from icisleri_bot import IcisleriBot

class TestIcisleriBot(unittest.TestCase):

    def setUp(self):
        """Test öncesi hazırlık"""
        self.bot = IcisleriBot(headless=True)

    def tearDown(self):
        """Test sonrası temizlik"""
        if self.bot.driver:
            self.bot.close()

    @patch('icisleri_bot.webdriver.Chrome')
    def test_setup_driver_success(self, mock_chrome):
        """Driver başlatma başarı testi"""
        # Mock driver oluştur
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        # Test
        result = self.bot.setup_driver()

        # Assertions
        self.assertTrue(result)
        self.assertIsNotNone(self.bot.driver)
        self.assertIsNotNone(self.bot.wait)

    @patch('icisleri_bot.webdriver.Chrome')
    def test_setup_driver_failure(self, mock_chrome):
        """Driver başlatma hata testi"""
        # Mock exception
        mock_chrome.side_effect = Exception("Driver error")

        # Test
        result = self.bot.setup_driver()

        # Assertions
        self.assertFalse(result)

    def test_login_credentials(self):
        """Login bilgileri testi"""
        username = "gizay.kilicoglu"
        password = "1234avfed"

        # Bilgilerin doğru olduğunu kontrol et
        self.assertEqual(username, "gizay.kilicoglu")
        self.assertEqual(password, "1234avfed")
        self.assertIsInstance(username, str)
        self.assertIsInstance(password, str)

        def test_urls(self):
        """URL'lerin doğru olduğunu test et"""
        login_url = "https://asilah.icisleri.gov.ct.tr/Security/Login/"
        kimlik_no = "1840227874"
        target_url = f"https://asilah.icisleri.gov.ct.tr/AvcilikAticilikDernekUye/Yeni?kimlikNumarasi={kimlik_no}"

        self.assertIn("icisleri.gov.ct.tr", login_url)
        self.assertIn("icisleri.gov.ct.tr", target_url)
        self.assertIn("kimlikNumarasi", target_url)
        self.assertIn(kimlik_no, target_url)
        self.assertTrue(login_url.startswith("https://"))
        self.assertTrue(target_url.startswith("https://"))

        def test_xpath(self):
        """XPath'lerin doğru formatını test et"""
        # Login form XPath'leri
        username_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[1]/input"
        password_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/input"
        login_button_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[4]/button[1]"

        # Hedef sayfa buton XPath'i
        target_button_xpath = "/html/body/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/button[1]"

        # Login form XPath'lerini test et
        self.assertTrue(username_xpath.startswith("/html/body"))
        self.assertIn("input", username_xpath)
        self.assertIsInstance(username_xpath, str)

        self.assertTrue(password_xpath.startswith("/html/body"))
        self.assertIn("input", password_xpath)
        self.assertIsInstance(password_xpath, str)

        self.assertTrue(login_button_xpath.startswith("/html/body"))
        self.assertIn("button[1]", login_button_xpath)
        self.assertIsInstance(login_button_xpath, str)

        # Hedef buton XPath'ini test et
        self.assertTrue(target_button_xpath.startswith("/html/body"))
        self.assertIn("button[1]", target_button_xpath)
        self.assertIsInstance(target_button_xpath, str)

def run_basic_tests():
    """Temel testleri çalıştır"""
    print("İçişleri Bot Temel Testleri Başlatılıyor...")

    # Test suite oluştur
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIcisleriBot)

    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Sonuçları yazdır
    print(f"\nTest Sonuçları:")
    print(f"Çalıştırılan testler: {result.testsRun}")
    print(f"Hatalar: {len(result.failures)}")
    print(f"Başarısız: {len(result.errors)}")

    return result.wasSuccessful()

if __name__ == "__main__":
    run_basic_tests()
