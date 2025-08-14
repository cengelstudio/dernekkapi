#!/usr/bin/env python3
import json
import random
import string
import sys
import os

# Flask app context'i için
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.db import create_association, get_all_associations
from app.models.schema import Association

def generate_username():
    """6 haneli rastgele username oluştur"""
    return ''.join(random.choices(string.digits, k=6))

def generate_password():
    """12 haneli rastgele şifre oluştur (harf ve rakam karışık)"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=12))

def import_associations():
    """associations.json dosyasından verileri okuyup veritabanına işle"""

    # Flask app context'i oluştur
    app = create_app()

    with app.app_context():
        # Mevcut dernekleri kontrol et
        existing_associations = get_all_associations()
        existing_usernames = {assoc.username for assoc in existing_associations}

        print(f"Mevcut dernek sayısı: {len(existing_associations)}")

        # associations.json dosyasını oku
        with open('db/associations.json', 'r', encoding='utf-8') as f:
            associations_data = json.load(f)

        print(f"JSON dosyasındaki dernek sayısı: {len(associations_data)}")

        # Benzersiz username'ler oluştur
        used_usernames = set()

        for i, assoc_data in enumerate(associations_data):
            # Benzersiz 6 haneli username oluştur
            while True:
                username = generate_username()
                if username not in existing_usernames and username not in used_usernames:
                    used_usernames.add(username)
                    break

            # 12 haneli şifre oluştur
            password = generate_password()

            # Association objesi oluştur
            association = Association(
                government_id=assoc_data['ID'],
                name=assoc_data['ISIM'],
                username=username,
                password=password
            )

            # Ek bilgileri doldur
            association.typeCode = assoc_data.get('TUZEL_TUR_KOD', '')
            association.typeCodeDescription = assoc_data.get('TUZEL_TUR_KOD_TANIM', '')
            association.subTypeCode = assoc_data.get('TUZEL_TIP_KOD', '')
            association.subTypeCodeDescription = assoc_data.get('TUZEL_TIP_KOD_TANIM', '')
            association.oldLegalEntityNumber = assoc_data.get('ESKI_TUZEL_NUMARASI', '')
            association.newLegalEntityNumber = assoc_data.get('E_TUZEL_NUMARASI', '')

            # Veritabanına kaydet
            success = create_association(association)

            if success:
                print(f"[{i+1:3d}/{len(associations_data)}] ✅ {assoc_data['ISIM'][:50]:<50} | Username: {username} | Şifre: {password}")
            else:
                print(f"[{i+1:3d}/{len(associations_data)}] ❌ {assoc_data['ISIM'][:50]:<50} | HATA!")

        # Son durumu kontrol et
        final_associations = get_all_associations()
        print(f"\n✅ İşlem tamamlandı!")
        print(f"Toplam dernek sayısı: {len(final_associations)}")

                # Username ve şifre listesini markdown dosyasına kaydet
        with open('association_credentials.md', 'w', encoding='utf-8') as f:
            f.write("# DERNEK KULLANICI ADI VE ŞİFRELERİ\n\n")
            f.write("| Sıra | Dernek Adı | Username | Şifre | Eski Tüzel No | Yeni Tüzel No |\n")
            f.write("|------|------------|----------|-------|----------------|---------------|\n")

            for i, assoc in enumerate(final_associations, 1):
                f.write(f"| {i:3d} | {assoc.name} | {assoc.username} | {assoc.password} | {assoc.oldLegalEntityNumber} | {assoc.newLegalEntityNumber} |\n")

        print(f"Kullanıcı adı ve şifreler 'association_credentials.md' dosyasına kaydedildi.")

if __name__ == "__main__":
    import_associations()
