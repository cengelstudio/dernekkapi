from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.services.db import get_user_by_username, get_association_by_username, update_user_login, update_association_login
from app.services.db import get_admin_user_by_username, update_admin_user_login
from app.services.jwt_service import create_admin_token, create_association_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'admin')

        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir', 'error')
            return render_template('login.html')

        if user_type == 'admin':
            # Önce admin_users tablosunda ara
            admin_user = get_admin_user_by_username(username)
            if admin_user and admin_user.password == password and admin_user.is_active:
                # Admin kullanıcısı girişi
                token = create_admin_token({
                    'id': admin_user.id,
                    'username': admin_user.username,
                    'role': admin_user.role,
                    'full_name': admin_user.full_name,
                    'user_type': 'admin'
                })
                session['token'] = token
                session['user_type'] = 'admin'
                session['user_id'] = admin_user.id
                session['username'] = admin_user.username
                session['admin_role'] = admin_user.role
                session['full_name'] = admin_user.full_name

                update_admin_user_login(admin_user.id)
                flash('Başarıyla giriş yaptınız', 'success')
                return redirect(url_for('admin.dashboard'))

            # Eski admin kullanıcısı kontrolü (geriye uyumluluk için)
            user = get_user_by_username(username)
            if user and user.password == password:
                token = create_admin_token(user)
                session['token'] = token
                session['user_type'] = 'admin'
                session['user_id'] = user.id
                session['username'] = user.username
                session['admin_role'] = 'Yönetici'  # Varsayılan rol

                update_user_login(user.id)
                flash('Başarıyla giriş yaptınız', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Geçersiz kullanıcı adı veya şifre', 'error')
        else:
            # Dernek girişi
            association = get_association_by_username(username)
            if association and association.password == password:  # Production'da hash kontrolü yapılmalı
                token = create_association_token(association)
                session['token'] = token
                session['user_type'] = 'association'
                session['user_id'] = association.id
                session['username'] = association.username
                session['association_name'] = association.name

                update_association_login(association.id)
                flash('Başarıyla giriş yaptınız', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('Geçersiz kullanıcı adı veya şifre', 'error')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Çıkış işlemi"""
    session.clear()
    flash('Başarıyla çıkış yaptınız', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    """Ana sayfa - giriş sayfasına yönlendir"""
    return redirect(url_for('auth.login'))
