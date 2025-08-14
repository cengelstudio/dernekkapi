from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.services.db import get_members_by_association, get_receipts_by_association
from app.services.jwt_service import get_user_from_token
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    """Giriş kontrolü decorator'ı"""
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Lütfen önce giriş yapın', 'error')
            return redirect(url_for('auth.login'))

        user_data = get_user_from_token(session['token'])
        if not user_data or user_data['user_type'] != 'association':
            flash('Bu sayfaya erişim yetkiniz yok', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@login_required
def index():
    """Dernek ana sayfası"""
    association_id = session.get('user_id')
    association_name = session.get('association_name', 'Dernek')

    # Üye sayısını al
    members = get_members_by_association(association_id)
    member_count = len(members)

    # Makbuz sayısını al
    receipts = get_receipts_by_association(association_id)
    receipt_count = len(receipts)

    return render_template('dashboard.jinja2',
                         association_name=association_name,
                         member_count=member_count,
                         receipt_count=receipt_count,
                         current_year=datetime.now().year)

@bp.route('/profile')
@login_required
def profile():
    """Dernek profil sayfası"""
    association_name = session.get('association_name', 'Dernek')
    return render_template('profile.jinja2', association_name=association_name)
