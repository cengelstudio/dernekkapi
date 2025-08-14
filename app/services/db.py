import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from flask import current_app
from app.models import User, Association, Member, Receipt, AdminUser

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Veritabanını başlat ve tabloları oluştur"""
    conn = get_db_connection()

    # Users tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            lastLoginDate TEXT NOT NULL
        )
    ''')

    # AdminUsers tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT NOT NULL
        )
    ''')

    # Associations tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS associations (
            id TEXT PRIMARY KEY,
            governmentId TEXT NOT NULL,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            last_login TEXT NOT NULL,
            typeCode TEXT,
            typeCodeDescription TEXT,
            subTypeCode TEXT,
            subTypeCodeDescription TEXT,
            oldLegalEntityNumber TEXT,
            newLegalEntityNumber TEXT
        )
    ''')

    # Members tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id TEXT PRIMARY KEY,
            identityNumber TEXT NOT NULL,
            nationality TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            middleName TEXT,
            birthSurname TEXT,
            gender TEXT,
            birthPlace TEXT,
            motherName TEXT,
            birthDate TEXT,
            fatherName TEXT,
            district TEXT,
            neighborhood TEXT,
            street TEXT,
            buildingNameOrNumber TEXT,
            doorNumber TEXT,
            apartmentNumber TEXT,
            phoneNumber TEXT,
            gsm TEXT,
            association TEXT NOT NULL,
            membershipYear TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            updated_at TEXT,
            approved_by TEXT,
            approved_at TEXT,
            rejection_reason TEXT,
            FOREIGN KEY (association) REFERENCES associations (id)
        )
    ''')

    # Receipts tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            memberId TEXT NOT NULL,
            associationId TEXT NOT NULL,
            uploadPath TEXT NOT NULL,
            uploadDate TEXT NOT NULL,
            FOREIGN KEY (memberId) REFERENCES members (id),
            FOREIGN KEY (associationId) REFERENCES associations (id)
        )
    ''')

    # Varsayılan admin kullanıcısı oluştur
    try:
        admin_user = User("admin", "admin123", "admin")
        create_user(admin_user)
    except:
        pass  # Zaten varsa hata verme

    # Varsayılan yönetici kullanıcısı oluştur
    try:
        default_admin = AdminUser("admin", "admin123", "Sistem Yöneticisi", "Yönetici", "admin@avfed.org")
        create_admin_user(default_admin)
    except:
        pass  # Zaten varsa hata verme

    conn.commit()
    conn.close()

    # Mevcut members tablosuna eksik sütunları ekle
    add_missing_columns_to_members()

def add_missing_columns_to_members():
    """Mevcut members tablosuna eksik sütunları ekle"""
    try:
        conn = get_db_connection()

        # Sütunların var olup olmadığını kontrol et ve ekle
        columns_to_add = [
            ('status', 'TEXT DEFAULT "pending"'),
            ('created_at', 'TEXT'),
            ('updated_at', 'TEXT'),
            ('approved_by', 'TEXT'),
            ('approved_at', 'TEXT'),
            ('rejection_reason', 'TEXT')
        ]

        for column_name, column_def in columns_to_add:
            try:
                conn.execute(f'ALTER TABLE members ADD COLUMN {column_name} {column_def}')
                print(f"Added column {column_name} to members table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists")
                else:
                    print(f"Error adding column {column_name}: {e}")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error in add_missing_columns_to_members: {e}")

# User işlemleri
def create_user(user: User) -> bool:
    """Yeni kullanıcı oluştur"""
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (id, username, password, role, lastLoginDate) VALUES (?, ?, ?, ?, ?)',
            (user.id, user.username, user.password, user.role, user.lastLoginDate)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"User creation error: {e}")
        return False

def get_user_by_username(username: str) -> Optional[User]:
    """Kullanıcı adına göre kullanıcı getir"""
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user_data:
        return User.from_dict(dict(user_data))
    return None

def update_user_login(user_id: str):
    """Kullanıcının son giriş tarihini güncelle"""
    from datetime import datetime
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET lastLoginDate = ? WHERE id = ?',
        (str(int(datetime.now().timestamp())), user_id)
    )
    conn.commit()
    conn.close()

# AdminUser işlemleri
def create_admin_user(admin_user: AdminUser) -> bool:
    """Yeni yönetici kullanıcısı oluştur"""
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO admin_users (id, username, password, full_name, role, email, is_active, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (admin_user.id, admin_user.username, admin_user.password, admin_user.full_name, admin_user.role, admin_user.email, admin_user.is_active, admin_user.created_at, admin_user.last_login)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Admin user creation error: {e}")
        return False

def get_admin_user_by_username(username: str) -> Optional[AdminUser]:
    """Kullanıcı adına göre yönetici kullanıcısı getir"""
    conn = get_db_connection()
    admin_data = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if admin_data:
        return AdminUser.from_dict(dict(admin_data))
    return None

def update_admin_user_login(admin_user_id: str):
    """Yönetici kullanıcının son giriş tarihini güncelle"""
    from datetime import datetime
    conn = get_db_connection()
    conn.execute(
        'UPDATE admin_users SET last_login = ? WHERE id = ?',
        (str(int(datetime.now().timestamp())), admin_user_id)
    )
    conn.commit()
    conn.close()

def get_all_admin_users() -> List[AdminUser]:
    """Tüm yönetici kullanıcıları getir"""
    conn = get_db_connection()
    admin_users_data = conn.execute('SELECT * FROM admin_users ORDER BY created_at DESC').fetchall()
    conn.close()

    return [AdminUser.from_dict(dict(user_data)) for user_data in admin_users_data]

def get_admin_user_by_id(admin_user_id: str) -> Optional[AdminUser]:
    """ID'ye göre yönetici kullanıcısı getir"""
    conn = get_db_connection()
    admin_data = conn.execute('SELECT * FROM admin_users WHERE id = ?', (admin_user_id,)).fetchone()
    conn.close()

    if admin_data:
        return AdminUser.from_dict(dict(admin_data))
    return None

def update_admin_user(admin_user: AdminUser) -> bool:
    """Yönetici kullanıcısını güncelle"""
    try:
        conn = get_db_connection()
        conn.execute(
            '''UPDATE admin_users
               SET username = ?, password = ?, full_name = ?, role = ?, email = ?, is_active = ?
               WHERE id = ?''',
            (admin_user.username, admin_user.password, admin_user.full_name,
             admin_user.role, admin_user.email, admin_user.is_active, admin_user.id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Admin user update error: {e}")
        return False

def delete_admin_user(admin_user_id: str) -> bool:
    """Yönetici kullanıcısını sil"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM admin_users WHERE id = ?', (admin_user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Admin user deletion error: {e}")
        return False

# Association işlemleri
def create_association(association: Association) -> bool:
    """Yeni dernek oluştur"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO associations
            (id, governmentId, name, username, password, last_login, typeCode, typeCodeDescription,
             subTypeCode, subTypeCodeDescription, oldLegalEntityNumber, newLegalEntityNumber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            association.id, association.governmentId, association.name, association.username,
            association.password, association.last_login, association.typeCode,
            association.typeCodeDescription, association.subTypeCode, association.subTypeCodeDescription,
            association.oldLegalEntityNumber, association.newLegalEntityNumber
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Association creation error: {e}")
        return False

def get_association_by_username(username: str) -> Optional[Association]:
    """Kullanıcı adına göre dernek getir"""
    conn = get_db_connection()
    assoc_data = conn.execute('SELECT * FROM associations WHERE username = ?', (username,)).fetchone()
    conn.close()

    if assoc_data:
        return Association.from_dict(dict(assoc_data))
    return None

def get_association_by_id(association_id: str) -> Optional[Association]:
    """ID'ye göre dernek getir"""
    conn = get_db_connection()
    assoc_data = conn.execute('SELECT * FROM associations WHERE id = ?', (association_id,)).fetchone()
    conn.close()

    if assoc_data:
        return Association.from_dict(dict(assoc_data))
    return None

def get_all_associations() -> List[Association]:
    """Tüm dernekleri getir"""
    conn = get_db_connection()
    assoc_data = conn.execute('SELECT * FROM associations').fetchall()
    conn.close()

    return [Association.from_dict(dict(row)) for row in assoc_data]

def update_association_login(association_id: str):
    """Derneğin son giriş tarihini güncelle"""
    from datetime import datetime
    conn = get_db_connection()
    conn.execute(
        'UPDATE associations SET last_login = ? WHERE id = ?',
        (str(int(datetime.now().timestamp())), association_id)
    )
    conn.commit()
    conn.close()

# Member işlemleri
def create_member(member: Member) -> bool:
    """Yeni üye oluştur"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO members
            (id, identityNumber, nationality, firstName, lastName, middleName, birthSurname,
             gender, birthPlace, motherName, birthDate, fatherName, district, neighborhood,
             street, buildingNameOrNumber, doorNumber, apartmentNumber, phoneNumber, gsm,
             association, membershipYear, status, created_at, updated_at, approved_by, approved_at, rejection_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            member.id, member.identityNumber, member.nationality, member.firstName,
            member.lastName, member.middleName, member.birthSurname, member.gender,
            member.birthPlace, member.motherName, member.birthDate, member.fatherName,
            member.district, member.neighborhood, member.street, member.buildingNameOrNumber,
            member.doorNumber, member.apartmentNumber, member.phoneNumber, json.dumps(member.gsm),
            member.association, member.membershipYear, member.status, member.created_at,
            member.updated_at, member.approved_by, member.approved_at, member.rejection_reason
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Member creation error: {e}")
        return False

def get_members_by_association(association_id: str) -> List[Member]:
    """Derneğe ait üyeleri getir"""
    conn = get_db_connection()
    member_data = conn.execute('SELECT * FROM members WHERE association = ?', (association_id,)).fetchall()
    conn.close()

    members = []
    for row in member_data:
        member_dict = dict(row)
        member_dict['gsm'] = json.loads(member_dict['gsm'])
        members.append(Member.from_dict(member_dict))

    return members

def get_member_by_id(member_id: str) -> Optional[Member]:
    """ID'ye göre üye getir"""
    conn = get_db_connection()
    member_data = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    conn.close()

    if member_data:
        member_dict = dict(member_data)
        member_dict['gsm'] = json.loads(member_dict['gsm'])
        return Member.from_dict(member_dict)
    return None

def get_member_by_identity_and_association(identity_number: str, association_id: str) -> Optional[Member]:
    """Kimlik numarası ve dernek ID'sine göre üye getir"""
    conn = get_db_connection()
    member_data = conn.execute('SELECT * FROM members WHERE identityNumber = ? AND association = ?',
                              (identity_number, association_id)).fetchone()
    conn.close()

    if member_data:
        member_dict = dict(member_data)
        member_dict['gsm'] = json.loads(member_dict['gsm'])
        return Member.from_dict(member_dict)
    return None

def update_member(member: Member) -> bool:
    """Üye bilgilerini güncelle"""
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE members
            SET identityNumber = ?, nationality = ?, firstName = ?, lastName = ?, middleName = ?,
                birthSurname = ?, gender = ?, birthPlace = ?, motherName = ?, birthDate = ?,
                fatherName = ?, district = ?, neighborhood = ?, street = ?, buildingNameOrNumber = ?,
                doorNumber = ?, apartmentNumber = ?, phoneNumber = ?, gsm = ?, membershipYear = ?,
                status = ?, updated_at = ?
            WHERE id = ?
        ''', (
            member.identityNumber, member.nationality, member.firstName, member.lastName,
            member.middleName, member.birthSurname, member.gender, member.birthPlace,
            member.motherName, member.birthDate, member.fatherName, member.district,
            member.neighborhood, member.street, member.buildingNameOrNumber, member.doorNumber,
            member.apartmentNumber, member.phoneNumber, json.dumps(member.gsm), member.membershipYear,
            member.status, member.updated_at, member.id
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Member update error: {e}")
        return False

def delete_member(member_id: str) -> bool:
    """Üyeyi sil"""
    try:
        conn = get_db_connection()
        # Önce üyeye ait makbuzları sil
        conn.execute('DELETE FROM receipts WHERE memberId = ?', (member_id,))
        # Sonra üyeyi sil
        conn.execute('DELETE FROM members WHERE id = ?', (member_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Member deletion error: {e}")
        return False

# Receipt işlemleri
def create_receipt(receipt: Receipt) -> bool:
    """Yeni makbuz oluştur"""
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO receipts (id, memberId, associationId, uploadPath, uploadDate) VALUES (?, ?, ?, ?, ?)',
            (receipt.id, receipt.memberId, receipt.associationId, receipt.uploadPath, receipt.uploadDate)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Receipt creation error: {e}")
        return False

def get_receipts_by_association(association_id: str) -> List[Receipt]:
    """Derneğe ait makbuzları getir"""
    conn = get_db_connection()
    receipt_data = conn.execute('SELECT * FROM receipts WHERE associationId = ?', (association_id,)).fetchall()
    conn.close()

    return [Receipt.from_dict(dict(row)) for row in receipt_data]

def get_receipts_by_member(member_id: str) -> List[Receipt]:
    """Üyeye ait makbuzları getir"""
    conn = get_db_connection()
    receipt_data = conn.execute('SELECT * FROM receipts WHERE memberId = ?', (member_id,)).fetchall()
    conn.close()

    return [Receipt.from_dict(dict(row)) for row in receipt_data]

def get_receipt_by_id(receipt_id: str) -> Optional[Receipt]:
    """ID'ye göre makbuz getir"""
    conn = get_db_connection()
    receipt_data = conn.execute('SELECT * FROM receipts WHERE id = ?', (receipt_id,)).fetchone()
    conn.close()

    if receipt_data:
        return Receipt.from_dict(dict(receipt_data))
    return None

def has_receipt_for_current_year(member_id: str, current_year: str) -> bool:
    """Üyenin bu yıl için makbuzu var mı kontrol et"""
    conn = get_db_connection()
    # Üyenin bu yıl için makbuzu var mı kontrol et
    receipt_data = conn.execute('''
        SELECT r.* FROM receipts r
        JOIN members m ON r.memberId = m.id
        WHERE r.memberId = ? AND m.membershipYear = ?
    ''', (member_id, current_year)).fetchone()
    conn.close()

    return receipt_data is not None

def check_member_receipt_status(member: Member) -> str:
    """Üyenin makbuz durumunu kontrol et ve uygun status döndür"""
    from datetime import datetime

    current_year = str(datetime.now().year)

    # Eğer üye bu yıl için değilse, makbuz kontrolü yapma
    if member.membershipYear != current_year:
        return member.status

    # Bu yıl için makbuz var mı kontrol et
    has_receipt = has_receipt_for_current_year(member.id, current_year)

    if member.status == "pending" and not has_receipt:
        return "receipt_pending"
    elif member.status == "receipt_pending" and has_receipt:
        return "pending"

    return member.status
