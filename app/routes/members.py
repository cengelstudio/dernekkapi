from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file, jsonify
from app.services.db import create_member, get_members_by_association, get_member_by_id, create_receipt, get_receipts_by_member, update_member, delete_member, get_member_by_identity_and_association
from app.services.file_upload import save_receipt_file, get_file_path
from app.services.jwt_service import get_user_from_token
from app.services.icisleri_bot import fetch_member_info_from_icisleri
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
            return render_template('member_create.jinja2')

        # Aynı kimlik numarasına sahip üye var mı kontrol et
        association_id = session.get('user_id')
        existing_member = get_member_by_identity_and_association(identity_number, association_id)

        if existing_member:
            # Mevcut üyeyi güncelle
            existing_member.nationality = nationality
            existing_member.firstName = first_name
            existing_member.lastName = last_name
            existing_member.middleName = middle_name
            existing_member.birthSurname = birth_surname
            existing_member.gender = gender
            existing_member.birthPlace = birth_place
            existing_member.motherName = mother_name
            existing_member.birthDate = birth_date
            existing_member.fatherName = father_name
            existing_member.district = district
            existing_member.neighborhood = neighborhood
            existing_member.street = street
            existing_member.buildingNameOrNumber = building_name
            existing_member.doorNumber = door_number
            existing_member.apartmentNumber = apartment_number
            existing_member.phoneNumber = phone_number
            existing_member.gsm = {
                "countryCode": gsm_country_code,
                "operatorCode": gsm_operator_code,
                "number": gsm_number
            }
            existing_member.membershipYear = membership_year
            existing_member.status = "pending"  # Onay bekliyor
            existing_member.updated_at = str(int(datetime.now().timestamp()))

            member = existing_member
            is_update = True
        else:
            # Yeni üye oluştur
            member = Member(identity_number, first_name, last_name, association_id)
            is_update = False

        # Yeni üye ise diğer bilgileri doldur
        if not is_update:
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
            member.status = "pending"  # Onay bekliyor

        # Veritabanına kaydet
        if is_update:
            # Güncelleme işlemi
            success = update_member(member)
            if success:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': 'Üye bilgileri başarıyla güncellendi ve onay için bekliyor',
                        'member_id': member.id
                    })
                else:
                    flash('Üye bilgileri başarıyla güncellendi ve onay için bekliyor', 'success')
                    return redirect(url_for('members.list'))
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Üye güncellenirken hata oluştu'
                    }), 400
                else:
                    flash('Üye güncellenirken hata oluştu', 'error')
        else:
            # Yeni üye oluşturma
            if create_member(member):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': 'Üye başarıyla oluşturuldu ve onay için bekliyor',
                        'member_id': member.id
                    })
                else:
                    flash('Üye başarıyla oluşturuldu ve onay için bekliyor', 'success')
                    return redirect(url_for('members.list'))
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Üye oluşturulurken hata oluştu'
                    }), 400
                else:
                    flash('Üye oluşturulurken hata oluştu', 'error')

    return render_template('member_create.jinja2', current_year=datetime.now().year)

@bp.route('/fetch-info', methods=['POST'])
@login_required
def fetch_info():
    """İçişleri Bakanlığı sitesinden kimlik bilgilerini çek"""
    try:
        data = request.get_json()
        identity_number = data.get('identity_number')

        if not identity_number:
            return jsonify({'error': 'Kimlik numarası gerekli'}), 400

        # İçişleri Bakanlığı sitesinden bilgileri çek
        member_info = fetch_member_info_from_icisleri(identity_number)

        if 'error' in member_info:
            return jsonify({'error': member_info['error']}), 400

        return jsonify(member_info)

    except Exception as e:
        return jsonify({'error': f'İşlem hatası: {str(e)}'}), 500

@bp.route('/list')
@login_required
def list():
    """Üye listesi"""
    association_id = session.get('user_id')
    members = get_members_by_association(association_id)
    current_year = datetime.now().year

    # Bu yıl makbuz yüklenmeyen üyeleri hesapla
    members_without_receipts = []
    for member in members:
        # Üyenin makbuzlarını al
        receipts = get_receipts_by_member(member.id)

        # Bu yıl yüklenen makbuz var mı kontrol et
        has_receipt_this_year = False
        for receipt in receipts:
            receipt_date = datetime.fromtimestamp(int(receipt.uploadDate))
            if receipt_date.year == current_year:
                has_receipt_this_year = True
                break

        # Bu yıl makbuz yüklenmemişse listeye ekle
        if not has_receipt_this_year:
            members_without_receipts.append(member)

    # Makbuz durumunu kontrol et ve status'ları güncelle
    from app.services.db import check_member_receipt_status
    for member in members:
        member.status = check_member_receipt_status(member)

    return render_template('member_list.jinja2',
                         members=members,
                         members_without_receipts=members_without_receipts,
                         current_year=current_year)

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

    return render_template('member_detail.jinja2', member=member, receipts=receipts)

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
        # Makbuz yüklendikten sonra üye status'unu güncelle
        from app.services.db import check_member_receipt_status
        member.status = check_member_receipt_status(member)
        update_member(member)

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

@bp.route('/<member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(member_id):
    """Üye düzenleme"""
    association_id = session.get('user_id')
    member = get_member_by_id(member_id)

    if not member or member.association != association_id:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    if request.method == 'POST':
        # Form verilerini al
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
        gsm_country_code = request.form.get('gsmCountryCode', '+90')
        gsm_operator_code = request.form.get('gsmOperatorCode', '533')
        gsm_number = request.form.get('gsmNumber', '0000000')
        membership_year = request.form.get('membershipYear', str(datetime.now().year))

        # Zorunlu alanları kontrol et
        if not first_name or not last_name:
            flash('Ad ve soyad zorunludur', 'error')
            return render_template('member_edit.jinja2', member=member, current_year=datetime.now().year)

        # Üye bilgilerini güncelle
        member.firstName = first_name
        member.lastName = last_name
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
        member.updated_at = str(int(datetime.now().timestamp()))

        # Veritabanına kaydet
        if update_member(member):
            flash('Üye başarıyla güncellendi', 'success')
            return redirect(url_for('members.detail', member_id=member.id))
        else:
            flash('Üye güncellenirken hata oluştu', 'error')

    return render_template('member_edit.jinja2', member=member, current_year=datetime.now().year)

@bp.route('/<member_id>/delete', methods=['POST'])
@login_required
def delete(member_id):
    """Üye silme"""
    association_id = session.get('user_id')
    member = get_member_by_id(member_id)

    if not member or member.association != association_id:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    if delete_member(member_id):
        flash('Üye başarıyla silindi', 'success')
    else:
        flash('Üye silinirken hata oluştu', 'error')

    return redirect(url_for('members.list'))

@bp.route('/<member_id>/print')
@login_required
def print_member(member_id):
    """Üye yazdırma sayfası"""
    association_id = session.get('user_id')
    member = get_member_by_id(member_id)

    if not member or member.association != association_id:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    return render_template('member_print.jinja2', member=member, current_time=current_time)

@bp.route('/<member_id>/pdf')
@login_required
def pdf_member(member_id):
    """Üye PDF indirme"""
    association_id = session.get('user_id')
    member = get_member_by_id(member_id)

    if not member or member.association != association_id:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('members.list'))

    # Basit HTML to PDF dönüşümü için HTML içeriği oluştur
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Üye Bilgileri - {member.firstName} {member.lastName}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .section {{ margin-bottom: 20px; }}
            .section h3 {{ color: #333; border-bottom: 1px solid #ccc; }}
            .info-row {{ margin: 5px 0; }}
            .label {{ font-weight: bold; display: inline-block; width: 150px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Üye Bilgileri</h1>
            <h2>{member.firstName} {member.lastName}</h2>
        </div>

        <div class="section">
            <h3>Kimlik Bilgileri</h3>
            <div class="info-row"><span class="label">Kimlik No:</span> {member.identityNumber}</div>
            <div class="info-row"><span class="label">Uyruk:</span> {member.nationality}</div>
            <div class="info-row"><span class="label">Ad:</span> {member.firstName}</div>
            <div class="info-row"><span class="label">Soyad:</span> {member.lastName}</div>
            {f'<div class="info-row"><span class="label">İkinci Ad:</span> {member.middleName}</div>' if member.middleName else ''}
            {f'<div class="info-row"><span class="label">Doğum Soyadı:</span> {member.birthSurname}</div>' if member.birthSurname else ''}
            {f'<div class="info-row"><span class="label">Cinsiyet:</span> {member.gender}</div>' if member.gender else ''}
            {f'<div class="info-row"><span class="label">Doğum Tarihi:</span> {member.birthDate}</div>' if member.birthDate else ''}
            {f'<div class="info-row"><span class="label">Doğum Yeri:</span> {member.birthPlace}</div>' if member.birthPlace else ''}
        </div>

        <div class="section">
            <h3>Aile Bilgileri</h3>
            {f'<div class="info-row"><span class="label">Anne Adı:</span> {member.motherName}</div>' if member.motherName else ''}
            {f'<div class="info-row"><span class="label">Baba Adı:</span> {member.fatherName}</div>' if member.fatherName else ''}
        </div>

        <div class="section">
            <h3>İletişim Bilgileri</h3>
            {f'<div class="info-row"><span class="label">Telefon:</span> {member.phoneNumber}</div>' if member.phoneNumber else ''}
            {f'<div class="info-row"><span class="label">GSM:</span> {member.gsm["countryCode"]}{member.gsm["operatorCode"]}{member.gsm["number"]}</div>' if member.gsm["number"] != '0000000' else ''}
            <div class="info-row"><span class="label">Üyelik Yılı:</span> {member.membershipYear}</div>
        </div>

        {f'''
        <div class="section">
            <h3>Adres Bilgileri</h3>
            <div class="info-row"><span class="label">Adres:</span> {member.district or ''} {member.neighborhood or ''} {member.street or ''} {member.buildingNameOrNumber or ''} No: {member.doorNumber or ''} {member.apartmentNumber or ''}</div>
        </div>
        ''' if any([member.district, member.neighborhood, member.street, member.buildingNameOrNumber, member.doorNumber, member.apartmentNumber]) else ''}

        <div class="section">
            <h3>Durum Bilgileri</h3>
            <div class="info-row"><span class="label">Durum:</span> {member.status}</div>
            <div class="info-row"><span class="label">Oluşturulma Tarihi:</span> {datetime.fromtimestamp(int(member.created_at)).strftime('%d.%m.%Y %H:%M') if member.created_at else 'Bilinmiyor'}</div>
        </div>
    </body>
    </html>
    """

    return send_file(
        io.BytesIO(html_content.encode('utf-8')),
        mimetype='text/html',
        as_attachment=True,
        download_name=f'uye_{member.identityNumber}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jinja2'
    )
