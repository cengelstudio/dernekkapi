from flask import Flask, redirect, url_for
from app.config import Config
from app.services.db import init_db
from app.routes import auth, dashboard, admin, members
from datetime import datetime
import os
from jinja2 import FileSystemLoader, Environment, ChoiceLoader

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Özel template loader oluştur (.jinja2 uzantısını destekler)
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')

    # .jinja2 uzantılı dosyalar için loader
    jinja2_loader = FileSystemLoader(template_dir, followlinks=True)

    # Flask'ın varsayılan template engine'ini özelleştir
    app.jinja_env.loader = jinja2_loader
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

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
