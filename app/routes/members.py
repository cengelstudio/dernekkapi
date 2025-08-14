from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file
from app.services.db import create_member, get_members_by_association, get_member_by_id, create_receipt, get_receipts_by_member
from app.services.file_upload import save_receipt_file, get_file_path
from app.services.jwt_service import get_user_from_token
from app.models import Member, Receipt
import pandas as pd
import io
from datetime import datetime

bp = Blueprint('members', __name__, url_prefix='/members')

def login_required(f):
    """Giriş kontrolü decorator'ı"""
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Lütfen önce giriş yapın', 'error')
            return redirect(url_for('auth.login'))

        user_data = get_user_from_token(session['token'])
        if not user_data:
            flash('Geçersiz oturum', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni üye oluştur"""
    if request.method == 'POST':
        # Form verilerini al
        identity_number = request.form.get('identityNumber')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        nationality = request.form.get('nationality', 'KT')
        middle_name = request.form.get('middleName', '')
        birth_surname = request.form.get('birthSurname', '')
        gender = request.form.get('gender', '')
        birth_place = request.form.get('birthPlace', '')
        mother_name = request.form.get('motherName', '')
        birth_date = request.form.get('birthDate', '')
        father_name = request.form.get('fatherName', '')
        district = request.form.get('district', '')
        neighborhood = request.form.get('neighborhood', '')
        street = request.form.get('street', '')
        building_name = request.form.get('buildingNameOrNumber', '')
        door_number = request.form.get('doorNumber', '')
        apartment_number = request.form.get('apartmentNumber', '')
        phone_number = request.form.get('phoneNumber', '')

        # GSM bilgileri
        gsm_country_code = request.form.get('gsmCountryCode', '+90')
        gsm_operator_code = request.form.get('gsmOperatorCode', '533')
        gsm_number = request.form.get('gsmNumber', '0000000')

        membership_year = request.form.get('membershipYear', str(datetime.now().year))

        # Zorunlu alanları kontrol et
        if not identity_number or not first_name or not last_name:
            flash('Kimlik numarası, ad ve soyad zorunludur', 'error')
            return render_template('member_create.html')

        # Üye oluştur
        association_id = session.get('user_id')
        member = Member(identity_number, first_name, last_name, association_id)

        # Diğer bilgileri doldur
        member.nationality = nationality
        member.middleName = middle_name
        member.birthSurname = birth_surname
        member.gender = gender
        member.birthPlace = birth_place
        member.motherName = mother_name
        member.birthDate = birth_date
        member.fatherName = father_name
        member.district = district
        member.neighborhood = neighborhood
        member.street = street
        member.buildingNameOrNumber = building_name
        member.doorNumber = door_number
        member.apartmentNumber = apartment_number
        member.phoneNumber = phone_number
        member.gsm = {
            "countryCode": gsm_country_code,
            "operatorCode": gsm_operator_code,
            "number": gsm_number
        }
        member.membershipYear = membership_year

        # Veritabanına kaydet
        if create_member(member):
            flash('Üye başarıyla oluşturuldu', 'success')
            return redirect(url_for('members.list'))
        else:
            flash('Üye oluşturulurken hata oluştu', 'error')

    return render_template('member_create.html', current_year=datetime.now().year)

@bp.route('/list')
@login_required
def list():
    """Üye listesi"""
    association_id = session.get('user_id')
    members = get_members_by_association(association_id)

    return render_template('member_list.html', members=members, current_year=datetime.now().year)

@bp.route('/<member_id>')
@login_required
def detail(member_id):
    """Üye detay sayfası"""
    member = get_member_by_id(member_id)
    if not member:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    # Üyenin makbuzlarını al
    receipts = get_receipts_by_member(member_id)

    return render_template('member_detail.html', member=member, receipts=receipts)

@bp.route('/<member_id>/receipt', methods=['POST'])
@login_required
def upload_receipt(member_id):
    """Üye için makbuz yükle"""
    member = get_member_by_id(member_id)
    if not member:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    # Dosya kontrolü
    if 'receipt_file' not in request.files:
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('members.detail', member_id=member_id))

    file = request.files['receipt_file']
    if file.filename == '':
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('members.detail', member_id=member_id))

    # Dosyayı kaydet
    file_path = save_receipt_file(file, member_id)
    if not file_path:
        flash('Dosya yüklenirken hata oluştu', 'error')
        return redirect(url_for('members.detail', member_id=member_id))

    # Makbuz kaydını oluştur
    association_id = session.get('user_id')
    receipt = Receipt(member_id, association_id, file_path)

    if create_receipt(receipt):
        flash('Makbuz başarıyla yüklendi', 'success')
    else:
        flash('Makbuz kaydedilirken hata oluştu', 'error')

    return redirect(url_for('members.detail', member_id=member_id))

@bp.route('/export/csv')
@login_required
def export_csv():
    """Üyeleri CSV formatında dışa aktar"""
    association_id = session.get('user_id')
    members = get_members_by_association(association_id)

    # DataFrame oluştur
    data = []
    for member in members:
        data.append({
            'Kimlik No': member.identityNumber,
            'Ad': member.firstName,
            'Soyad': member.lastName,
            'İkinci Ad': member.middleName,
            'Doğum Soyadı': member.birthSurname,
            'Cinsiyet': member.gender,
            'Doğum Yeri': member.birthPlace,
            'Anne Adı': member.motherName,
            'Doğum Tarihi': member.birthDate,
            'Baba Adı': member.fatherName,
            'İlçe': member.district,
            'Mahalle': member.neighborhood,
            'Cadde/Sokak': member.street,
            'Bina': member.buildingNameOrNumber,
            'Dış Kapı No': member.doorNumber,
            'İç Kapı No': member.apartmentNumber,
            'Telefon': member.phoneNumber,
            'GSM': f"{member.gsm['countryCode']}{member.gsm['operatorCode']}{member.gsm['number']}",
            'Üyelik Yılı': member.membershipYear
        })

    df = pd.DataFrame(data)

    # CSV dosyası oluştur
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'uyeler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@bp.route('/export/excel')
@login_required
def export_excel():
    """Üyeleri Excel formatında dışa aktar"""
    association_id = session.get('user_id')
    members = get_members_by_association(association_id)

    # DataFrame oluştur
    data = []
    for member in members:
        data.append({
            'Kimlik No': member.identityNumber,
            'Ad': member.firstName,
            'Soyad': member.lastName,
            'İkinci Ad': member.middleName,
            'Doğum Soyadı': member.birthSurname,
            'Cinsiyet': member.gender,
            'Doğum Yeri': member.birthPlace,
            'Anne Adı': member.motherName,
            'Doğum Tarihi': member.birthDate,
            'Baba Adı': member.fatherName,
            'İlçe': member.district,
            'Mahalle': member.neighborhood,
            'Cadde/Sokak': member.street,
            'Bina': member.buildingNameOrNumber,
            'Dış Kapı No': member.doorNumber,
            'İç Kapı No': member.apartmentNumber,
            'Telefon': member.phoneNumber,
            'GSM': f"{member.gsm['countryCode']}{member.gsm['operatorCode']}{member.gsm['number']}",
            'Üyelik Yılı': member.membershipYear
        })

    df = pd.DataFrame(data)

    # Excel dosyası oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Üyeler')

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'uyeler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
