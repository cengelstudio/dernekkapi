from flask import Flask, redirect, url_for
from app.config import Config
from app.services.db import init_db
from app.routes import auth, dashboard, admin, members
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Jinja2 filter'ları ekle
    @app.template_filter('datetime')
    def format_datetime(timestamp):
        """Unix timestamp'i okunabilir tarihe çevir"""
        try:
            if isinstance(timestamp, str):
                timestamp = int(timestamp)
            return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
        except:
            return timestamp

    # Blueprint'leri kaydet
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(members.bp)

    # Ana sayfa route'u
    @app.route('/')
    def index():
        """Ana sayfa - giriş sayfasına yönlendir"""
        return redirect(url_for('auth.login'))

    # Uygulama context'i içinde veritabanını başlat
    with app.app_context():
        init_db()

    return app
