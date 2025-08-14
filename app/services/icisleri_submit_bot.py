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
import os

# Config'den log ayarlarını al
try:
    from config import LOG_CONFIG
    log_dir = LOG_CONFIG.get('log_directory', './logs')
    log_filename = LOG_CONFIG.get('log_filename', 'icisleri_bot.log')
    log_level = getattr(logging, LOG_CONFIG.get('log_level', 'INFO'))
    log_format = LOG_CONFIG.get('log_format', '%(asctime)s - %(levelname)s - %(message)s')

    # Log dizinini oluştur
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_filename)

    # File handler ekle
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Console handler ekle
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)

    # Logger'ı yapılandır
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

except ImportError:
    # Config dosyası yoksa varsayılan ayarları kullan
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

class IcisleriSubmitBot:
    """İçişleri Bakanlığı sistemine üye kaydetme botu"""

    def __init__(self, headless=True, progress_callback=None):  # Headless modu varsayılan olarak açık
        self.driver = None
        self.is_logged_in = False
        self.headless = headless
        self.progress_callback = progress_callback

        # Config'den ayarları al
        try:
            from config import BOT_CONFIG
            self.wait_timeout = BOT_CONFIG.get('wait_timeout', 10)
        except ImportError:
            self.wait_timeout = 10

    def safe_input_fill(self, xpath, value, field_name):
        """Güvenli input doldurma fonksiyonu"""
        try:
            element = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            # Readonly kontrolü
            if not element.get_attribute('readonly'):
                element.clear()
                time.sleep(0.5)  # Kısa bekleme
                element.send_keys(value)
                logger.info(f"✅ {field_name} girildi")
                if self.progress_callback:
                    self.progress_callback(f"{field_name} girildi", 70)
                time.sleep(0.3)  # Input sonrası kısa bekleme
            else:
                logger.info(f"ℹ️ {field_name} alanı readonly, atlandı")
                if self.progress_callback:
                    self.progress_callback(f"{field_name} alanı readonly, atlandı", 70)
            return True
        except Exception as e:
            logger.warning(f"⚠️ {field_name} alanı hatası: {e}")
            if self.progress_callback:
                self.progress_callback(f"{field_name} alanı hatası: {e}", 70)
            return False

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

            # Geliştirme için ek ayarlar
            if not self.headless:
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)

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

            if self.progress_callback:
                self.progress_callback("İçişleri Bakanlığı sitesine bağlanılıyor...", 10)
            logger.info("🌐 İçişleri Bakanlığı sitesine bağlanılıyor...")
            # Giriş sayfasına git
            self.driver.get("https://asilah.icisleri.gov.ct.tr/Security/Login/")
            logger.info("📄 Giriş sayfası yüklendi")

            if self.progress_callback:
                self.progress_callback("Kullanıcı adı giriliyor...", 15)
            logger.info("👤 Kullanıcı adı giriliyor...")
            # Username input
            username_input = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[1]/input"))
            )
            username_input.clear()
            username_input.send_keys(username)
            logger.info("✅ Kullanıcı adı girildi")

            if self.progress_callback:
                self.progress_callback("Şifre giriliyor...", 20)
            logger.info("🔒 Şifre giriliyor...")
            # Password input
            password_input = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/input")
            password_input.clear()
            password_input.send_keys(password)
            logger.info("✅ Şifre girildi")

            if self.progress_callback:
                self.progress_callback("Giriş yapılıyor...", 25)
            logger.info("🚪 Giriş yapılıyor...")
            # Login button
            login_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/form/div[4]/button[1]")
            login_button.click()
            logger.info("⏳ Giriş işlemi bekleniyor...")

            # Giriş başarılı mı kontrol et
            time.sleep(3)
            if "Login" not in self.driver.current_url:
                self.is_logged_in = True
                if self.progress_callback:
                    self.progress_callback("İçişleri Bakanlığı sistemine başarıyla giriş yapıldı", 30)
                logger.info("✅ İçişleri Bakanlığı sistemine başarıyla giriş yapıldı")
                return True
            else:
                if self.progress_callback:
                    self.progress_callback("Giriş başarısız oldu", 30)
                logger.error("❌ Giriş başarısız oldu")
                return False

        except Exception as e:
            logger.error(f"❌ Giriş hatası: {e}")
            return False

    def submit_member_to_icisleri(self, member_data: Dict[str, Any], association_data: Dict[str, Any]) -> Dict[str, Any]:
        """Üyeyi İçişleri Bakanlığı sistemine kaydet"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Önce giriş yapılmalı")
                return {"success": False, "message": "Sisteme giriş yapılmamış"}

            if self.progress_callback:
                self.progress_callback("Üye kayıt sayfasına gidiliyor...", 35)
            logger.info("📝 Üye kayıt sayfasına gidiliyor...")
            # Üye ekleme sayfasına git
            url = f"https://asilah.icisleri.gov.ct.tr/AvcilikAticilikDernekUye/Yeni?kimlikNumarasi={member_data['identityNumber']}"
            self.driver.get(url)
            logger.info("📄 Üye kayıt sayfası yüklendi")

            # Sayfanın yüklenmesini bekle
            time.sleep(3)

            if self.progress_callback:
                self.progress_callback("Dernek seçimi yapılıyor...", 40)
            logger.info("🏢 Dernek seçimi yapılıyor...")
            # Dernek seçim modal butonuna tıkla
            dernek_button = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[4]/div[3]/div/div/button"))
            )

            # Element'in tıklanabilir olmasını bekle
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[4]/div[3]/div/div/button"))
            )

            # JavaScript ile tıkla (daha güvenilir)
            self.driver.execute_script("arguments[0].click();", dernek_button)
            logger.info("✅ Dernek seçim modal butonuna tıklandı")

            # Modal'ın açılmasını bekle
            time.sleep(2)
            logger.info("⏳ Modal açılması bekleniyor...")

            # Dernek listesi tablosunu bul
            try:
                table_body = WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[2]/div[2]/div[4]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div[2]/table/tbody"))
                )
                logger.info("✅ Dernek listesi tablosu bulundu")
            except TimeoutException:
                logger.error("❌ Dernek listesi tablosu bulunamadı")
                return {
                    "success": False,
                    "message": "Dernek listesi tablosu bulunamadı. XPath kontrol edilmeli."
                }
            except Exception as e:
                logger.error(f"❌ Dernek listesi tablosu hatası: {e}")
                return {
                    "success": False,
                    "message": f"Dernek listesi tablosu hatası: {str(e)}"
                }

                        # Tablo satırlarını al
            try:
                table_rows = table_body.find_elements(By.XPATH, "tr")
                logger.info(f"📋 {len(table_rows)} adet dernek bulundu")

                if len(table_rows) == 0:
                    logger.error("❌ Tablo satırı bulunamadı")
                    return {
                        "success": False,
                        "message": "Dernek tablosunda satır bulunamadı"
                    }
            except Exception as e:
                logger.error(f"❌ Tablo satırları okuma hatası: {e}")
                return {
                    "success": False,
                    "message": f"Tablo satırları okuma hatası: {str(e)}"
                }

            # Aranacak dernek adı
            target_dernek_name = association_data.get('name', '')
            logger.info(f"🔍 Aranan dernek: {target_dernek_name}")

            if self.progress_callback:
                self.progress_callback(f"Dernek aranıyor: {target_dernek_name}", 45)

            # Dernek adını tabloda ara
            dernek_found = False
            for i, row in enumerate(table_rows):
                try:
                    # İlk td'deki dernek adını al
                    first_td = row.find_element(By.XPATH, "td[1]")
                    dernek_name_in_table = first_td.text.strip()

                    logger.info(f"📝 Satır {i+1} - Tablo dernek adı: {dernek_name_in_table}")

                    # Dernek adını karşılaştır (tam eşleşme)
                    if target_dernek_name.strip() == dernek_name_in_table.strip():
                        if self.progress_callback:
                            self.progress_callback(f"Eşleşen dernek bulundu: {dernek_name_in_table}", 50)
                        logger.info(f"✅ Eşleşen dernek bulundu: {dernek_name_in_table}")

                        # TR'ye tıkla
                        row.click()
                        logger.info("✅ Dernek satırına tıklandı")

                        # 2 saniye bekle
                        time.sleep(2)
                        logger.info("⏳ 2 saniye beklendi")

                        dernek_found = True
                        break

                except Exception as e:
                    logger.warning(f"⚠️ Satır {i+1} okuma hatası: {e}")
                    continue

            if not dernek_found:
                logger.error(f"❌ Dernek bulunamadı: {target_dernek_name}")
                return {
                    "success": False,
                    "message": f"Dernek bulunamadı: {target_dernek_name}. Mevcut dernekler kontrol edilmeli."
                }

            # Dernek seçimini kaydet butonuna tıkla
            logger.info("💾 Dernek seçimini kaydet butonuna tıklanıyor...")
            save_dernek_button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div[2]/div[4]/div/div/div[3]/button[1]")
            save_dernek_button.click()
            logger.info("✅ Dernek seçimi kaydedildi")

            # Form alanlarının yüklenmesini bekle
            time.sleep(3)  # Daha uzun bekleme süresi

            # Form alanlarını doldur
            if self.progress_callback:
                self.progress_callback("Form alanları dolduruluyor...", 55)
            logger.info("📋 Form alanları dolduruluyor...")

            # Telefon numarası
            if member_data.get('phoneNumber'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[3]/div/div/input",
                    member_data['phoneNumber'],
                    "Telefon numarası"
                )

            # GSM bilgileri
            if member_data.get('gsm'):
                gsm_data = member_data['gsm']

                # GSM Alan kodu
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[1]/div/input",
                    gsm_data.get('countryCode', '+90'),
                    "GSM alan kodu"
                )

                # GSM Kodu
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[2]/input",
                    gsm_data.get('operatorCode', '533'),
                    "GSM kodu"
                )

                # GSM Numara
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[3]/div[4]/div[3]/input",
                    gsm_data.get('number', '0000000'),
                    "GSM numarası"
                )

            # Adres bilgileri
            if member_data.get('neighborhood'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[3]/div[2]/input",
                    member_data['neighborhood'],
                    "Mahalle/Köy"
                )

            if member_data.get('street'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[4]/div[1]/input",
                    member_data['street'],
                    "Cadde/Sokak"
                )

            if member_data.get('buildingNameOrNumber'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[4]/div[2]/input",
                    member_data['buildingNameOrNumber'],
                    "Bina"
                )

            if member_data.get('doorNumber'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[5]/div[1]/input",
                    member_data['doorNumber'],
                    "Dış kapı no"
                )

            if member_data.get('apartmentNumber'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[2]/div[5]/div[2]/input",
                    member_data['apartmentNumber'],
                    "İç kapı no"
                )

            # Kişisel bilgiler
            if member_data.get('firstName'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[5]/div[1]/input",
                    member_data['firstName'],
                    "İsim"
                )

            if member_data.get('lastName'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[5]/div[2]/input",
                    member_data['lastName'],
                    "Soyisim"
                )

            if member_data.get('middleName'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[6]/div[1]/input",
                    member_data['middleName'],
                    "İkinci isim"
                )

            if member_data.get('birthSurname'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[6]/div[2]/input",
                    member_data['birthSurname'],
                    "Doğum soyismi"
                )

            if member_data.get('gender'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[7]/div/input",
                    member_data['gender'],
                    "Cinsiyet"
                )

            if member_data.get('birthPlace'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[8]/div[1]/input",
                    member_data['birthPlace'],
                    "Doğum yeri"
                )

            if member_data.get('motherName'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[9]/div[1]/input",
                    member_data['motherName'],
                    "Anne adı"
                )

            if member_data.get('fatherName'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[9]/div[2]/input",
                    member_data['fatherName'],
                    "Baba adı"
                )

            if member_data.get('birthDate'):
                self.safe_input_fill(
                    "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div/div[1]/div[8]/div[2]/input",
                    member_data['birthDate'],
                    "Doğum tarihi"
                )

                        if self.progress_callback:
                self.progress_callback("Kaydet butonuna tıklanıyor...", 80)
            logger.info("💾 Kaydet butonuna tıklanıyor...")
            # Kaydet butonu
            try:
                save_button = WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div[2]/div[2]/div[3]/div/div/div/div[2]/div/form/div[2]/button"))
                )

                # JavaScript ile tıkla (daha güvenilir)
                self.driver.execute_script("arguments[0].click();", save_button)
                if self.progress_callback:
                    self.progress_callback("Kaydetme işlemi bekleniyor...", 85)
                logger.info("⏳ Kaydetme işlemi bekleniyor...")
            except Exception as e:
                logger.error(f"❌ Kaydet butonu hatası: {e}")
                return {
                    "success": False,
                    "message": f"Kaydet butonu hatası: {str(e)}"
                }

            # POST işleminin tamamlanmasını bekle
            time.sleep(5)
            logger.info("⏳ POST işlemi tamamlandı, modal bekleniyor...")

            # Modal'ın açılmasını bekle (daha uzun süre)
            modal_found = False
            max_attempts = 10
            attempt = 0

            while attempt < max_attempts and not modal_found:
                try:
                    if self.progress_callback:
                        self.progress_callback(f"Modal aranıyor... (Deneme {attempt + 1}/{max_attempts})", 90)
                    logger.info(f"🔍 Modal aranıyor... (Deneme {attempt + 1}/{max_attempts})")

                    # Modal'ı bulmaya çalış
                    modal = self.driver.find_element(By.XPATH, "/html/body/div[8]/div")

                    if modal.is_displayed():
                        if self.progress_callback:
                            self.progress_callback("Modal bulundu ve görünür", 95)
                        logger.info("✅ Modal bulundu ve görünür")
                        modal_found = True
                        break
                    else:
                        logger.info("⚠️ Modal bulundu ama görünür değil")

                except NoSuchElementException:
                    logger.info(f"⏳ Modal henüz yüklenmedi... (Deneme {attempt + 1}/{max_attempts})")
                    time.sleep(2)  # 2 saniye bekle
                    attempt += 1
                except Exception as e:
                    logger.warning(f"⚠️ Modal arama hatası: {e}")
                    time.sleep(2)
                    attempt += 1

            if not modal_found:
                logger.error("❌ Modal bulunamadı")
                return {
                    "success": False,
                    "message": "Modal bulunamadı, işlem başarısız olabilir"
                }

            # Modal mesajını al
            try:
                if self.progress_callback:
                    self.progress_callback("Modal mesajı okunuyor...", 98)
                logger.info("📢 Modal mesajı okunuyor...")
                modal_message = self.driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div[1]")
                message_text = modal_message.text
                logger.info(f"📢 Modal mesajı: {message_text}")

                # Modal butonuna tıkla
                if self.progress_callback:
                    self.progress_callback("Modal butonuna tıklanıyor...", 99)
                logger.info("🔘 Modal butonuna tıklanıyor...")
                modal_button = self.driver.find_element(By.XPATH, "/html/body/div[8]/div/div[3]/button[1]")
                modal_button.click()
                logger.info("✅ Modal kapatıldı")

                return {
                    "success": True,
                    "message": message_text,
                    "modal_message": message_text
                }

            except Exception as e:
                logger.error(f"❌ Modal işlemi hatası: {e}")
                return {
                    "success": False,
                    "message": f"Modal işlemi hatası: {str(e)}"
                }

        except Exception as e:
            logger.error(f"❌ Üye kaydetme hatası: {e}")
            return {
                "success": False,
                "message": f"Üye kaydetme hatası: {str(e)}"
            }

    def close(self):
        """Driver'ı kapat"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Driver kapatıldı")
