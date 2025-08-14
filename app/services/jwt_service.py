import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app
from app.models import User, Association

def create_token(user_data: Dict[str, Any], user_type: str = "admin") -> str:
    """JWT token oluştur"""
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'user_type': user_type,  # 'admin' veya 'association'
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT token doğrula"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Token'dan kullanıcı bilgilerini al"""
    payload = verify_token(token)
    if not payload:
        return None

    return {
        'user_id': payload['user_id'],
        'username': payload['username'],
        'user_type': payload['user_type']
    }

def create_admin_token(user) -> str:
    """Admin kullanıcısı için token oluştur"""
    if hasattr(user, 'to_dict'):
        return create_token(user.to_dict(), "admin")
    else:
        # user is already a dictionary
        return create_token(user, "admin")

def create_association_token(association) -> str:
    """Dernek için token oluştur"""
    if hasattr(association, 'to_dict'):
        return create_token(association.to_dict(), "association")
    else:
        # association is already a dictionary
        return create_token(association, "association")
