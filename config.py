# İçişleri Bakanlığı Sistemi Konfigürasyonu
# Bu dosya hassas bilgiler içerdiği için .gitignore'a eklenmiştir

# İçişleri Bakanlığı Sistemi Bilgileri
ICISLERI_CONFIG = {
    'login_url': 'https://asilah.icisleri.gov.ct.tr/Security/Login/',
    'username': 'gizay.kilicoglu',
    'password': '1234avfed'
}

# Bot Konfigürasyonu
BOT_CONFIG = {
    'headless': False,  # Headless mod (True/False) - Debug için False
    'wait_timeout': 10,  # Saniye cinsinden bekleme süresi
    'implicit_wait': 5,  # Saniye cinsinden implicit bekleme
    'window_size': '1920,1080',  # Pencere boyutu
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Log Konfigürasyonu
LOG_CONFIG = {
    'log_directory': './logs',
    'log_filename': 'icisleri_bot.log',
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Uygulama Konfigürasyonu
APP_CONFIG = {
    'debug': True,
    'host': '0.0.0.0',
    'port': 5504,
    'secret_key': 'your-secret-key-here'  # Güvenlik için değiştirin
}
