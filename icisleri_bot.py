#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İçişleri Bakanlığı Bot
Selenium kullanarak İçişleri Bakanlığı sitesine giriş yapar ve belirli işlemleri gerçekleştirir.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('icisleri_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IcisleriBot:
    def __init__(self, headless=False):
        """
        Bot başlatıcı

        Args:
            headless (bool): Tarayıcıyı görünmez modda çalıştır
        """
        self.driver = None
        self.wait = None
        self.headless = headless

    def setup_driver(self):
        """Chrome driver'ı konfigüre eder ve başlatır"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless")

            # Tarayıcı ayarları
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # SSL sertifika hatalarını görmezden gel
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)

            logger.info("Chrome driver başarıyla başlatıldı")
            return True

        except Exception as e:
            logger.error(f"Driver başlatılırken hata oluştu: {e}")
            return False

    def login(self, username, password):
        """
        İçişleri Bakanlığı sitesine giriş yapar

        Args:
            username (str): Kullanıcı adı
            password (str): Şifre
        """
        try:
            # Login sayfasına git
            login_url = "https://asilah.icisleri.gov.ct.tr/Security/Login/"
            logger.info(f"Login sayfasına gidiliyor: {login_url}")
            self.driver.get(login_url)

            # Sayfanın yüklenmesini bekle
            time.sleep(3)

                        # Username alanını bul ve doldur
            username_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[1]/input"
            username_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, username_xpath))
            )
            username_field.clear()
            username_field.send_keys(username)
            logger.info("Kullanıcı adı girildi")

            # Password alanını bul ve doldur
            password_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/input"
            password_field = self.driver.find_element(By.XPATH, password_xpath)
            password_field.clear()
            password_field.send_keys(password)
            logger.info("Şifre girildi")

            # Login butonunu bul ve tıkla
            login_button_xpath = "/html/body/div[2]/div/div/div/div/div[2]/form/div[4]/button[1]"
            login_button = self.driver.find_element(By.XPATH, login_button_xpath)
            login_button.click()
            logger.info("Login butonuna tıklandı")

            # Login işleminin tamamlanmasını bekle
            time.sleep(5)

            # Login başarılı mı kontrol et
            if "Login" not in self.driver.current_url:
                logger.info("Login başarılı!")
                return True
            else:
                logger.error("Login başarısız!")
                return False

        except TimeoutException:
            logger.error("Login sayfası yüklenirken zaman aşımı")
            return False
        except Exception as e:
            logger.error(f"Login sırasında hata oluştu: {e}")
            return False

    def navigate_to_target_page(self):
        """
        Hedef sayfaya gider ve belirtilen butona tıklar
        """
        try:
            # Hedef sayfaya git (kimlik numarası ile)
            kimlik_no = "1840227874"  # Test için kimlik numarası
            target_url = f"https://asilah.icisleri.gov.ct.tr/AvcilikAticilikDernekUye/Yeni?kimlikNumarasi={kimlik_no}"
            logger.info(f"Hedef sayfaya gidiliyor: {target_url}")
            self.driver.get(target_url)

            # Sayfanın yüklenmesini bekle
            time.sleep(5)

            # Belirtilen butonu bul ve tıkla
            button_xpath = "/html/body/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/button[1]"
            logger.info(f"Buton aranıyor: {button_xpath}")

            button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )

            # Butona tıkla
            button.click()
            logger.info("Butona başarıyla tıklandı!")

            # İşlemin tamamlanmasını bekle
            time.sleep(3)

            return True

        except TimeoutException:
            logger.error("Buton bulunamadı veya tıklanamadı")
            return False
        except Exception as e:
            logger.error(f"Hedef sayfa işlemi sırasında hata oluştu: {e}")
            return False

    def take_screenshot(self, filename="screenshot.png"):
        """Ekran görüntüsü alır"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Ekran görüntüsü alındı: {filename}")
        except Exception as e:
            logger.error(f"Ekran görüntüsü alınırken hata: {e}")

    def close(self):
        """Tarayıcıyı kapatır"""
        if self.driver:
            self.driver.quit()
            logger.info("Tarayıcı kapatıldı")

def main():
    """Ana fonksiyon"""
    # Bot başlat
    bot = IcisleriBot(headless=False)  # Test için görünür modda çalıştır

    try:
        # Driver'ı başlat
        if not bot.setup_driver():
            logger.error("Bot başlatılamadı!")
            return

        # Login bilgilerini oku
        username = "gizay.kilicoglu"
        password = "1234avfed"

        # Login ol
        if not bot.login(username, password):
            logger.error("Login başarısız, işlem durduruluyor!")
            return

        # Hedef sayfaya git ve butona tıkla
        if not bot.navigate_to_target_page():
            logger.error("Hedef sayfa işlemi başarısız!")
            return

        # Ekran görüntüsü al
        bot.take_screenshot("test_screenshot.png")

        logger.info("Bot işlemi başarıyla tamamlandı!")

    except Exception as e:
        logger.error(f"Ana işlem sırasında hata oluştu: {e}")

    finally:
        # Tarayıcıyı kapat
        bot.close()

if __name__ == "__main__":
    main()
