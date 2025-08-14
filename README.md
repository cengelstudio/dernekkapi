# DernekKapı

Derneklerin AVFED sistemine açılan dijital kapısı.

## Proje Hakkında

DernekKapı, derneklerin üye yönetimini kolaylaştırmak ve AVFED sistemine entegrasyonu sağlamak amacıyla geliştirilmiş bir web uygulamasıdır. Sistem, derneklerin üye bilgilerini yönetmelerine, makbuz yüklemelerine ve AVFED sistemine otomatik form doldurma işlemlerini gerçekleştirmelerine olanak tanır.

## Özellikler

### Yönetim (AVFED) Paneli
- Tüm derneklerin üye ve makbuz istatistiklerini görüntüleme
- Dernek bazında detaylı raporlama
- Sistem geneli üye ve makbuz takibi
- Dernek aktivitelerini izleme

### Dernek Paneli
- Üye oluşturma ve yönetimi
- Üye listesi görüntüleme
- CSV ve Excel formatında dışa aktarma
- Makbuz yükleme ve takibi
- AVFED sistemine otomatik entegrasyon

## Teknolojiler

- **Backend:** Python 3.8+, Flask
- **Template Engine:** Jinja2
- **Veritabanı:** SQLite
- **Kimlik Doğrulama:** JWT
- **Frontend:** Bootstrap 5, Font Awesome
- **Dosya İşleme:** Pillow, pandas, openpyxl

## Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım Adım Kurulum

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd dernekkapi
```

2. **Sanal ortam oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı çalıştırın:**
```bash
python run.py
```

5. **Tarayıcınızda açın:**
```
http://localhost:5000
```

## Kullanım

### İlk Giriş
- **Yönetim Paneli:** admin / admin123
- **Dernek Paneli:** Henüz dernek oluşturulmadı

### Yönetim Paneli
1. Yönetim olarak giriş yapın
2. Dashboard'da tüm derneklerin istatistiklerini görün
3. Dernek detaylarını inceleyin
4. Sistem geneli raporları görüntüleyin

### Dernek Paneli
1. Dernek olarak giriş yapın
2. Yeni üye ekleyin
3. Üye listesini görüntüleyin
4. Makbuz yükleyin
5. Verileri CSV/Excel formatında dışa aktarın

## Veritabanı Şeması

### Users (Yönetim)
- id: Benzersiz kimlik
- username: Kullanıcı adı
- password: Şifre (plain text)
- role: Rol (admin, user, moderator)
- lastLoginDate: Son giriş tarihi

### Associations (Dernekler)
- id: Benzersiz kimlik
- governmentId: Devlet ID
- name: Dernek adı
- username: Giriş kullanıcı adı
- password: Şifre
- last_login: Son giriş tarihi
- typeCode: Tür kodu
- subTypeCode: Alt tür kodu
- oldLegalEntityNumber: Eski tüzel numara
- newLegalEntityNumber: Yeni tüzel numara

### Members (Üyeler)
- id: Benzersiz kimlik
- identityNumber: Kimlik numarası
- firstName, lastName: Ad soyad
- nationality: Uyruk
- birthDate: Doğum tarihi
- address: Adres bilgileri
- phoneNumber: Telefon
- gsm: GSM bilgileri (JSON)
- association: Dernek ID
- membershipYear: Üyelik yılı

### Receipts (Makbuzlar)
- id: Benzersiz kimlik
- memberId: Üye ID
- associationId: Dernek ID
- uploadPath: Dosya yolu
- uploadDate: Yükleme tarihi

## API Endpoints

### Kimlik Doğrulama
- `GET /auth/login` - Giriş sayfası
- `POST /auth/login` - Giriş işlemi
- `GET /auth/logout` - Çıkış işlemi

### Yönetim Paneli
- `GET /admin/` - Admin dashboard
- `GET /admin/association/<id>` - Dernek detayı
- `GET /admin/members` - Tüm üyeler
- `GET /admin/receipts` - Tüm makbuzlar

### Dernek Paneli
- `GET /dashboard/` - Dernek dashboard
- `GET /dashboard/profile` - Dernek profili

### Üye İşlemleri
- `GET /members/create` - Üye oluşturma sayfası
- `POST /members/create` - Üye oluşturma
- `GET /members/list` - Üye listesi
- `GET /members/<id>` - Üye detayı
- `POST /members/<id>/receipt` - Makbuz yükleme
- `GET /members/export/csv` - CSV dışa aktarma
- `GET /members/export/excel` - Excel dışa aktarma

## Test

Testleri çalıştırmak için:

```bash
# Tüm testleri çalıştır
python -m unittest discover tests

# Belirli test dosyasını çalıştır
python -m unittest tests.test_auth
python -m unittest tests.test_member
python -m unittest tests.test_bot
```

## Geliştirme

### Proje Yapısı
```
dernekkapi/
├── app/                    # Ana uygulama
│   ├── models/            # Veri modelleri
│   ├── services/          # İş mantığı servisleri
│   ├── routes/            # Route tanımları
│   ├── templates/         # HTML şablonları
│   └── static/            # Statik dosyalar
├── db/                    # Veritabanı dosyaları
├── tests/                 # Test dosyaları
├── run.py                 # Uygulama başlatıcı
└── requirements.txt       # Python bağımlılıkları
```

### Yeni Özellik Ekleme
1. Model tanımlarını `app/models/` altında oluşturun
2. Veritabanı işlemlerini `app/services/db.py` altında ekleyin
3. Route'ları `app/routes/` altında tanımlayın
4. Template'leri `app/templates/` altında oluşturun
5. Testleri `tests/` altında yazın

## Güvenlik

### Production Ortamında
- Şifreleri hash'leyin (bcrypt, werkzeug.security)
- JWT secret key'i güçlü bir değerle değiştirin
- HTTPS kullanın
- Rate limiting ekleyin
- Input validation güçlendirin
- SQL injection koruması ekleyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Proje hakkında sorularınız için: [email@example.com]

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun
