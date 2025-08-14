import time
import json
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IcisleriBot:
    """İçişleri Bakanlığı sitesinden kimlik bilgilerini çeken bot"""

    def __init__(self, headless=True):
        self.driver = None
        self.is_logged_in = False
        self.headless = headless
        self.wait_timeout = 10

    def setup_driver(self):
        """Chrome driver'ı hazırla"""
        try:
            logger.info("🔧 ChromeDriver başlatılıyor...")
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
                logger.info("🌐 Headless mod aktif")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            # Önce sistem ChromeDriver'ını dene
            try:
                logger.info("🔍 Sistem ChromeDriver deneniyor...")
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✅ Sistem ChromeDriver başarıyla başlatıldı")
            except:
                # Sistem ChromeDriver yoksa WebDriver Manager kullan
                logger.info("📥 WebDriver Manager ile ChromeDriver indiriliyor...")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✅ WebDriver Manager ile ChromeDriver başlatıldı")

            self.driver.implicitly_wait(5)
            logger.info("🚀 ChromeDriver hazır")
            return True
        except Exception as e:
            logger.error(f"❌ Driver setup hatası: {e}")
            return False

    def login_to_icisleri(self, username: str, password: str) -> bool:
        """İçişleri Bakanlığı sitesine giriş yap"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False

            logger.info("🌐 İçişleri Bakanlığı sitesine bağlanılıyor...")
            # Giriş sayfasına git
            self.driver.get("https://asilah.icisleri.gov.ct.tr/Security/Login/")
            logger.info("📄 Giriş sayfası yüklendi")

            logger.info("👤 Kullanıcı adı giriliyor...")
            # Username input
            username_input = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[1]/input"))
            )
            username_input.clear()
            username_input.send_keys(username)
            logger.info("✅ Kullanıcı adı girildi")

            logger.info("🔒 Şifre giriliyor...")
            # Password input
            password_input = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/input")
            password_input.clear()
            password_input.send_keys(password)
            logger.info("✅ Şifre girildi")

            logger.info("🚪 Giriş yapılıyor...")
            # Login button
            login_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[4]/button[1]")
            login_button.click()
            logger.info("⏳ Giriş işlemi bekleniyor...")

            # Giriş başarılı mı kontrol et
            time.sleep(3)
            if "Login" not in self.driver.current_url:
                self.is_logged_in = True
                logger.info("✅ İçişleri Bakanlığı sistemine başarıyla giriş yapıldı")
                return True
            else:
                logger.error("❌ Giriş başarısız - Login sayfasında kaldı")
                return False

        except Exception as e:
            logger.error(f"❌ İçişleri giriş hatası: {e}")
            return False

    def get_member_info(self, identity_number: str) -> Dict[str, Any]:
        """Kimlik numarasından üye bilgilerini çek"""
        try:
            if not self.is_logged_in:
                return {"error": "Giriş yapılmamış"}

            logger.info(f"🔍 Kimlik numarası {identity_number} için bilgiler aranıyor...")
            # Üye ekleme sayfasına git
            url = f"https://asilah.icisleri.gov.ct.tr/AvcilikAticilikDernekUye/Yeni?kimlikNumarasi={identity_number}"
            self.driver.get(url)
            logger.info("📄 Üye bilgi sayfası yüklendi")

            # Sayfanın yüklenmesini bekle
            logger.info("⏳ Sayfa yüklenmesi bekleniyor...")
            time.sleep(3)

            # Bilgileri çek
            member_info = {}
            logger.info("📋 Bilgiler çekiliyor...")

            def get_field_info(xpath, field_name):
                """Alan bilgilerini ve readonly durumunu çek"""
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    value = element.get_attribute('value') or ""
                    readonly = element.get_attribute('readonly') is not None or element.get_attribute('disabled') is not None
                    logger.info(f"✅ {field_name}: {value} (Readonly: {readonly})")
                    return value, readonly
                except:
                    logger.warning(f"⚠️ {field_name} bilgisi çekilemedi")
                    return "", False

            def get_select_info(xpath, field_name):
                """Select elementi bilgilerini çek"""
                try:
                    select_element = self.driver.find_element(By.XPATH, xpath)
                    selected_value = select_element.get_attribute('value') or ""
                    readonly = select_element.get_attribute('disabled') is not None

                    # Tüm option'ları al
                    options = []
                    option_elements = select_element.find_elements(By.TAG_NAME, "option")

                    for option in option_elements:
                        option_value = option.get_attribute('value') or ""
                        option_text = option.text.strip()
                        option_id = option.get_attribute('data-select2-id') or ""

                        options.append({
                            'value': option_value,
                            'text': option_text,
                            'id': option_id
                        })

                    logger.info(f"✅ {field_name}: {selected_value} (Readonly: {readonly}, {len(options)} seçenek)")
                    return selected_value, readonly, options
                except:
                    logger.warning(f"⚠️ {field_name} bilgisi çekilemedi")
                    return "", False, []

            # Tüm alanları çek
            fields = [
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[5]/div[1]/input", "firstName", "İsim"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[5]/div[2]/input", "lastName", "Soyisim"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[6]/div[1]/input", "middleName", "İkinci isim"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[6]/div[2]/input", "birthSurname", "Doğum soyismi"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[7]/div/input", "gender", "Cinsiyet"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[8]/div[1]/input", "birthPlace", "Doğum yeri"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[9]/div[1]/input", "motherName", "Anne adı"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[9]/div[2]/input", "fatherName", "Baba adı"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[8]/div[2]/input", "birthDate", "Doğum tarihi"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[3]/div/div/input", "phoneNumber", "Telefon"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[1]/div/input", "gsmCountryCode", "GSM Alan kodu"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[2]/input", "gsmOperatorCode", "GSM Operatör kodu"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[3]/input", "gsmNumber", "GSM Numarası"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[3]/div[2]/input", "neighborhood", "Mahalle"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[4]/div[1]/input", "street", "Cadde"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[4]/div[2]/input", "buildingNameOrNumber", "Bina"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[5]/div[1]/input", "doorNumber", "Dış kapı no"),
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[5]/div[2]/input", "apartmentNumber", "İç kapı no")
            ]

            # Select alanları
            select_fields = [
                ("/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[3]/div[1]/select", "district", "İlçe")
            ]

            for xpath, field_name, display_name in fields:
                logger.info(f"👤 {display_name} bilgisi çekiliyor...")
                value, readonly = get_field_info(xpath, display_name)
                member_info[field_name] = value
                member_info[f'{field_name}_readonly'] = readonly

            # Select alanlarını çek
            for xpath, field_name, display_name in select_fields:
                logger.info(f"🏛️ {display_name} bilgisi çekiliyor...")
                selected_value, readonly, options = get_select_info(xpath, display_name)
                member_info[field_name] = selected_value
                member_info[f'{field_name}_readonly'] = readonly
                member_info[f'{field_name}_options'] = options

            # Kimlik numarasını ekle
            member_info['identityNumber'] = identity_number
            member_info['nationality'] = "KT"

            logger.info("🎉 Tüm bilgiler başarıyla çekildi!")
            return member_info

        except Exception as e:
            logger.error(f"❌ Bilgi çekme hatası: {e}")
            return {"error": f"Bilgi çekme hatası: {str(e)}"}

    def close(self):
        """Driver'ı kapat"""
        try:
            if self.driver:
                logger.info("🔒 ChromeDriver kapatılıyor...")
                self.driver.quit()
                logger.info("✅ ChromeDriver kapatıldı")
        except:
            pass

def fetch_member_info_from_icisleri(identity_number: str) -> Dict[str, Any]:
    """İçişleri Bakanlığı sitesinden üye bilgilerini çek"""
    logger.info(f"🚀 Kimlik numarası {identity_number} için bilgi çekme işlemi başlatılıyor...")
    bot = IcisleriBot(headless=True)

    try:
        # Giriş yap
        logger.info("🔐 İçişleri Bakanlığı sistemine giriş yapılıyor...")
        if not bot.login_to_icisleri("gizay.kilicoglu", "1234avfed"):
            logger.error("❌ Giriş başarısız")
            return {"error": "İçişleri Bakanlığı sitesine giriş başarısız"}

        # Bilgileri çek
        logger.info("📋 Üye bilgileri çekiliyor...")
        member_info = bot.get_member_info(identity_number)

        logger.info("✅ Bilgi çekme işlemi tamamlandı")
        return member_info

    except Exception as e:
        logger.error(f"❌ İşlem hatası: {str(e)}")
        return {"error": f"İşlem hatası: {str(e)}"}

    finally:
        bot.close()
