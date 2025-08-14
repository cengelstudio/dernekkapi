# İçişleri Bakanlığı Bot

Bu bot, İçişleri Bakanlığı web sitesine otomatik giriş yapar ve belirli işlemleri gerçekleştirir.

## Özellikler

- ✅ Otomatik login işlemi
- ✅ Hedef sayfaya navigasyon
- ✅ Belirtilen butona otomatik tıklama
- ✅ Ekran görüntüsü alma
- ✅ Detaylı loglama
- ✅ Hata yönetimi

## Gereksinimler

### Python Kütüphaneleri
```bash
pip install -r requirements.txt
```

### Chrome WebDriver
Bot Chrome tarayıcısını kullanır. Chrome'un yüklü olduğundan emin olun.

**macOS için:**
```bash
brew install --cask google-chrome
```

**ChromeDriver otomatik yönetimi için:**
```bash
pip install webdriver-manager
```

## Kullanım

### 1. Temel Kullanım
```bash
python icisleri_bot.py
```

### 2. Test Çalıştırma
```bash
python test_icisleri_bot.py
```

### 3. Headless Mod (Görünmez)
Bot dosyasında `headless=True` yaparak görünmez modda çalıştırabilirsiniz.

## Konfigürasyon

### Login Bilgileri
Login bilgileri `icisleri.txt` dosyasından okunur:
```
Username: gizay.kilicoglu
Password: 1234avfed
```

### URL'ler
- **Login URL:** `https://asilah.icisleri.gov.ct.tr/Security/Login/`
- **Hedef URL:** `https://asilah.icisleri.gov.ct.tr/AvcilikAticilikDernekUye/Yeni?kimlikNumarasi=1840227874`

### XPath'ler

#### Login Form XPath'leri:
```xpath
# Kullanıcı adı alanı
/html/body/div[2]/div/div/div/div/div[2]/form/div[1]/input

# Şifre alanı
/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/input

# Login butonu
/html/body/div[2]/div/div/div/div/div[2]/form/div[4]/button[1]
```

#### Hedef Sayfa XPath'i:
```xpath
# Hedef buton
/html/body/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/button[1]
```

## Dosya Yapısı

```
├── icisleri_bot.py          # Ana bot dosyası
├── test_icisleri_bot.py     # Test dosyası
├── icisleri.txt             # Login bilgileri
├── requirements.txt          # Python bağımlılıkları
├── icisleri_bot.log         # Log dosyası (otomatik oluşur)
└── test_screenshot.png      # Ekran görüntüsü (otomatik oluşur)
```

## Loglama

Bot tüm işlemleri detaylı olarak loglar:
- Konsol çıktısı
- `icisleri_bot.log` dosyası

## Hata Yönetimi

Bot aşağıdaki durumları yönetir:
- ✅ Network bağlantı hataları
- ✅ Element bulunamama durumları
- ✅ Zaman aşımı hataları
- ✅ Login başarısızlığı

## Güvenlik

⚠️ **Önemli:** Login bilgilerini güvenli tutun ve paylaşmayın.

## Geliştirme

### Yeni Özellik Ekleme
1. `IcisleriBot` sınıfına yeni metod ekleyin
2. Test dosyasına test case ekleyin
3. README'yi güncelleyin

### Debug Modu
Bot'u debug modunda çalıştırmak için:
```python
bot = IcisleriBot(headless=False)  # Görünür mod
```

## Sorun Giderme

### ChromeDriver Hatası
```bash
# ChromeDriver'ı manuel yükleyin
brew install chromedriver
```

### SSL Sertifika Hatası
Bot otomatik olarak SSL hatalarını görmezden gelir.

### Element Bulunamama
XPath'i kontrol edin ve sayfanın tamamen yüklendiğinden emin olun.

## Lisans

Bu proje test amaçlı geliştirilmiştir.

## İletişim

Sorularınız için proje sahibi ile iletişime geçin.
