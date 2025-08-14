import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Optional

def allowed_file(filename: str) -> bool:
    """Dosya uzantısının izinli olup olmadığını kontrol et"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_receipt_file(file, member_id: str) -> Optional[str]:
    """Makbuz dosyasını kaydet"""
    if file and allowed_file(file.filename):
        # Güvenli dosya adı oluştur
        filename = secure_filename(file.filename)

        # Benzersiz dosya adı oluştur
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{member_id}_{uuid.uuid4().hex}.{file_extension}"

        # Upload klasörünü oluştur (yoksa)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Dosyayı kaydet
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Veritabanında saklanacak yolu döndür
        return f"uploads/{unique_filename}"

    return None

def delete_receipt_file(file_path: str) -> bool:
    """Makbuz dosyasını sil"""
    try:
        if file_path.startswith('uploads/'):
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path[8:])
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        return False
    except Exception as e:
        print(f"File deletion error: {e}")
        return False

def get_file_path(file_path: str) -> str:
    """Dosya yolunu tam yol olarak döndür"""
    if file_path.startswith('uploads/'):
        return os.path.join(current_app.config['UPLOAD_FOLDER'], file_path[8:])
    return file_path
