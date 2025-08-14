from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.services.db import get_all_associations, get_members_by_association, get_receipts_by_association
from app.services.db import get_all_admin_users, create_admin_user, get_admin_user_by_id, get_admin_user_by_username, update_admin_user, delete_admin_user, get_association_by_username
from app.services.jwt_service import get_user_from_token, create_association_token
from app.models import AdminUser
from datetime import datetime

def format_last_login(last_login):
    """Unix timestamp'i okunabilir tarihe çevir"""
    if not last_login or last_login == 'Hiç giriş yapmamış':
        return 'Hiç giriş yapmamış'
    try:
        if isinstance(last_login, str):
            timestamp = int(last_login)
        else:
            timestamp = last_login
        return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
    except:
        return last_login

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Admin kontrolü decorator'ı"""
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Lütfen önce giriş yapın', 'error')
            return redirect(url_for('auth.login'))

        user_data = get_user_from_token(session['token'])
        if not user_data or user_data['user_type'] != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def manager_required(f):
    """Yönetici kontrolü decorator'ı - sadece Yönetici rolündeki kullanıcılar"""
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Lütfen önce giriş yapın', 'error')
            return redirect(url_for('auth.login'))

        user_data = get_user_from_token(session['token'])
        if not user_data or user_data['user_type'] != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok', 'error')
            return redirect(url_for('auth.login'))

        # Yönetici kullanıcısını kontrol et
        admin_user = get_admin_user_by_username(user_data['username'])
        if not admin_user or admin_user.role != "Yönetici":
            flash('Bu işlem için Yönetici yetkisi gereklidir', 'error')
            return redirect(url_for('admin.dashboard'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@admin_required
def dashboard():
    """Admin ana sayfası"""
    # Tüm dernekleri al
    associations = get_all_associations()

    # Her dernek için üye ve makbuz sayılarını hesapla
    association_stats = []
    total_members = 0
    total_receipts = 0
    total_pending_members = 0

    for association in associations:
        members = get_members_by_association(association.id)
        receipts = get_receipts_by_association(association.id)

        member_count = len(members)
        receipt_count = len(receipts)
        pending_count = len([m for m in members if m.status == 'pending'])

        total_members += member_count
        total_receipts += receipt_count
        total_pending_members += pending_count

        # Last login formatlaması
        formatted_last_login = format_last_login(association.last_login)

        association_stats.append({
            'association': association,
            'member_count': member_count,
            'receipt_count': receipt_count,
            'pending_count': pending_count,
            'formatted_last_login': formatted_last_login
        })

    return render_template('admin.jinja2',
                         associations=association_stats,
                         total_members=total_members,
                         total_receipts=total_receipts,
                         total_pending_members=total_pending_members)

@bp.route('/association/<association_id>')
@admin_required
def association_detail(association_id):
    """Dernek detay sayfası"""
    # Dernek bilgilerini al
    associations = get_all_associations()
    association = None

    for assoc in associations:
        if assoc.id == association_id:
            association = assoc
            break

    if not association:
        flash('Dernek bulunamadı', 'error')
        return redirect(url_for('admin.dashboard'))

    # Derneğin üyelerini al
    members = get_members_by_association(association_id)

    # Derneğin makbuzlarını al
    receipts = get_receipts_by_association(association_id)

    return render_template('association_detail.jinja2',
                         association=association,
                         members=members,
                         receipts=receipts)

@bp.route('/members')
@admin_required
def all_members():
    """Tüm üyeleri listele"""
    associations = get_all_associations()
    all_members = []

    for association in associations:
        members = get_members_by_association(association.id)
        for member in members:
            all_members.append({
                'member': member,
                'association': association
            })

    # Onay bekleyen üyeleri üstte göster
    all_members.sort(key=lambda x: (x['member'].status != 'pending', x['member'].created_at))

    return render_template('all_members.jinja2', members=all_members)

@bp.route('/members/<member_id>/approve', methods=['POST'])
@admin_required
def approve_member(member_id):
    """Üyeyi onayla ve İçişleri Bakanlığı sistemine kaydet"""
    from app.services.db import get_member_by_id, update_member, get_association_by_id
    from app.services.icisleri_submit_bot import IcisleriSubmitBot

    member = get_member_by_id(member_id)
    if not member:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('admin.all_members'))

    # Dernek bilgilerini al
    association = get_association_by_id(member.association)
    if not association:
        flash('Dernek bilgileri bulunamadı', 'error')
        return redirect(url_for('admin.all_members'))

    # Admin kullanıcısını al
    user_data = get_user_from_token(session['token'])
    admin_user = get_admin_user_by_username(user_data['username'])

    # Progress callback fonksiyonu
    def progress_callback(message, progress):
        # Bu fonksiyon gerçek zamanlı güncelleme için kullanılacak
        # Şimdilik sadece log yazıyoruz
        print(f"Progress: {progress}% - {message}")

    # Config'den bilgileri al
    try:
        from config import ICISLERI_CONFIG
    except ImportError:
        flash('Konfigürasyon dosyası bulunamadı', 'error')
        return redirect(url_for('admin.all_members'))

    # İçişleri Bakanlığı sistemine kaydet
    bot = IcisleriSubmitBot(headless=True, progress_callback=progress_callback)  # Headless mod
    try:
        # Giriş yap
        if not bot.login_to_icisleri(ICISLERI_CONFIG['username'], ICISLERI_CONFIG['password']):
            flash('İçişleri Bakanlığı sistemine giriş yapılamadı', 'error')
            return redirect(url_for('admin.all_members'))

        # Üyeyi sisteme kaydet
        member_data = member.to_dict()
        association_data = association.to_dict()

        result = bot.submit_member_to_icisleri(member_data, association_data)

        if result['success']:
            # Üye durumunu güncelle
            member.status = 'approved'
            member.approved_by = admin_user.full_name if admin_user else 'Bilinmeyen'
            member.approved_at = str(int(datetime.now().timestamp()))
            member.updated_at = str(int(datetime.now().timestamp()))

            if update_member(member):
                # Mesaj türüne göre renklendirme
                modal_message = result.get("message", "")
                if "Yeni Kayıt Yapıldı" in modal_message:
                    message_type = "success"
                    message_title = "✅ Başarılı"
                else:
                    message_type = "warning"
                    message_title = "⚠️ Uyarı"

                success_message = f'{member.firstName} {member.lastName} başarıyla onaylandı ve İçişleri Bakanlığı sistemine kaydedildi.'

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': success_message,
                        'modal_message': modal_message,
                        'message_type': message_type,
                        'message_title': message_title
                    })
                else:
                    flash(success_message, message_type)
            else:
                error_message = 'Üye onaylanırken hata oluştu'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': error_message})
                else:
                    flash(error_message, 'error')
        else:
            error_message = f'İçişleri Bakanlığı sistemine kayıt başarısız: {result["message"]}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': error_message})
            else:
                flash(error_message, 'error')

    except Exception as e:
        error_message = f'İçişleri Bakanlığı sistemi hatası: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': error_message})
        else:
            flash(error_message, 'error')
    finally:
        bot.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'message': 'Bilinmeyen hata'})

    return redirect(url_for('admin.all_members'))

@bp.route('/members/<member_id>/reject', methods=['POST'])
@admin_required
def reject_member(member_id):
    """Üyeyi reddet"""
    from app.services.db import get_member_by_id, update_member

    member = get_member_by_id(member_id)
    if not member:
        flash('Üye bulunamadı', 'error')
        return redirect(url_for('admin.all_members'))

    rejection_reason = request.form.get('rejection_reason', '')

    # Admin kullanıcısını al
    user_data = get_user_from_token(session['token'])
    admin_user = get_admin_user_by_username(user_data['username'])

    # Üye durumunu güncelle
    member.status = 'rejected'
    member.approved_by = admin_user.full_name if admin_user else 'Bilinmeyen'
    member.approved_at = str(int(datetime.now().timestamp()))
    member.rejection_reason = rejection_reason
    member.updated_at = str(int(datetime.now().timestamp()))

    if update_member(member):
        flash(f'{member.firstName} {member.lastName} reddedildi', 'success')
    else:
        flash('Üye reddedilirken hata oluştu', 'error')

    return redirect(url_for('admin.all_members'))

@bp.route('/receipts')
@admin_required
def all_receipts():
    """Tüm makbuzları listele"""
    associations = get_all_associations()
    all_receipts = []

    for association in associations:
        receipts = get_receipts_by_association(association.id)
        for receipt in receipts:
            all_receipts.append({
                'receipt': receipt,
                'association': association
            })

    return render_template('all_receipts.jinja2', receipts=all_receipts)

# Yönetici Kullanıcı Yönetimi
@bp.route('/users')
@admin_required
def users():
    """Yönetici kullanıcıları listele"""
    admin_users = get_all_admin_users()
    return render_template('admin_users.jinja2', admin_users=admin_users)

@bp.route('/users/create', methods=['GET', 'POST'])
@manager_required
def create_user():
    """Yeni yönetici kullanıcısı oluştur"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        email = request.form.get('email')

        if not all([username, password, full_name, role]):
            flash('Tüm alanları doldurun', 'error')
            return render_template('admin_user_create.jinja2')

        if role not in ['Yönetici', 'Moderatör']:
            flash('Geçersiz rol', 'error')
            return render_template('admin_user_create.jinja2')

        # Kullanıcı adı kontrolü
        existing_user = get_admin_user_by_username(username)
        if existing_user:
            flash('Bu kullanıcı adı zaten kullanılıyor', 'error')
            return render_template('admin_user_create.jinja2')

        # Yeni admin kullanıcısı oluştur
        admin_user = AdminUser(username, password, full_name, role, email)

        if create_admin_user(admin_user):
            flash('Yönetici kullanıcısı başarıyla oluşturuldu', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('Kullanıcı oluşturulurken hata oluştu', 'error')

    return render_template('admin_user_create.jinja2')

@bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@manager_required
def edit_user(user_id):
    """Yönetici kullanıcısını düzenle"""
    admin_user = get_admin_user_by_id(user_id)
    if not admin_user:
        flash('Kullanıcı bulunamadı', 'error')
        return redirect(url_for('admin.users'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        email = request.form.get('email')
        is_active = request.form.get('is_active') == 'on'

        if not all([username, full_name, role]):
            flash('Gerekli alanları doldurun', 'error')
            return render_template('admin_user_edit.jinja2', admin_user=admin_user)

        if role not in ['Yönetici', 'Moderatör']:
            flash('Geçersiz rol', 'error')
            return render_template('admin_user_edit.jinja2', admin_user=admin_user)

        # Kullanıcı adı kontrolü (kendisi hariç)
        existing_user = get_admin_user_by_username(username)
        if existing_user and existing_user.id != user_id:
            flash('Bu kullanıcı adı zaten kullanılıyor', 'error')
            return render_template('admin_user_edit.jinja2', admin_user=admin_user)

        # Kullanıcıyı güncelle
        admin_user.username = username
        admin_user.full_name = full_name
        admin_user.role = role
        admin_user.email = email
        admin_user.is_active = is_active

        if password:  # Şifre değiştirilmişse
            admin_user.password = password

        if update_admin_user(admin_user):
            flash('Kullanıcı başarıyla güncellendi', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('Kullanıcı güncellenirken hata oluştu', 'error')

    return render_template('admin_user_edit.jinja2', admin_user=admin_user)

@bp.route('/users/<user_id>/delete', methods=['POST'])
@manager_required
def delete_user(user_id):
    """Yönetici kullanıcısını sil"""
    admin_user = get_admin_user_by_id(user_id)
    if not admin_user:
        flash('Kullanıcı bulunamadı', 'error')
        return redirect(url_for('admin.users'))

    # Kendini silmeye çalışıyorsa engelle
    current_user_data = get_user_from_token(session['token'])
    if current_user_data and current_user_data['username'] == admin_user.username:
        flash('Kendinizi silemezsiniz', 'error')
        return redirect(url_for('admin.users'))

    if delete_admin_user(user_id):
        flash('Kullanıcı başarıyla silindi', 'success')
    else:
        flash('Kullanıcı silinirken hata oluştu', 'error')

    return redirect(url_for('admin.users'))

@bp.route('/login-as-association/<association_id>')
@manager_required
def login_as_association(association_id):
    """Yönetici olarak dernek adına giriş yap"""
    # Dernek bilgilerini al
    associations = get_all_associations()
    association = None

    for assoc in associations:
        if assoc.id == association_id:
            association = assoc
            break

    if not association:
        flash('Dernek bulunamadı', 'error')
        return redirect(url_for('admin.dashboard'))

    # Dernek için token oluştur
    token = create_association_token(association)

    # Session'ı dernek bilgileriyle güncelle
    session['token'] = token
    session['user_type'] = 'association'
    session['user_id'] = association.id
    session['username'] = association.username
    session['association_name'] = association.name

    flash(f'"{association.name}" derneği adına giriş yapıldı. Admin paneline dönmek için çıkış yapıp tekrar giriş yapmanız gerekiyor.', 'success')
    return redirect(url_for('dashboard.index'))


