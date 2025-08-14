import uuid
import json
from datetime import datetime
from typing import Dict, Any

class User:
    def __init__(self, username: str, password: str, role: str = "admin"):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password  # Plain text, production'da hash'lenmeli
        self.role = role
        self.lastLoginDate = str(int(datetime.now().timestamp()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "lastLoginDate": self.lastLoginDate
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        user = cls(data["username"], data["password"], data["role"])
        user.id = data["id"]
        user.lastLoginDate = data["lastLoginDate"]
        return user

class AdminUser:
    def __init__(self, username: str, password: str, full_name: str, role: str = "Yönetici", email: str = ""):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password  # Plain text, production'da hash'lenmeli
        self.full_name = full_name
        self.role = role  # "Yönetici" veya "Moderatör"
        self.email = email
        self.is_active = True
        self.created_at = str(int(datetime.now().timestamp()))
        self.last_login = str(int(datetime.now().timestamp()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminUser':
        admin_user = cls(
            data["username"],
            data["password"],
            data["full_name"],
            data.get("role", "Yönetici"),
            data.get("email", "")
        )
        admin_user.id = data["id"]
        admin_user.is_active = data.get("is_active", True)
        admin_user.created_at = data.get("created_at", str(int(datetime.now().timestamp())))
        admin_user.last_login = data.get("last_login", str(int(datetime.now().timestamp())))
        return admin_user

    def can_create_users(self) -> bool:
        """Sadece Yönetici rolündeki kullanıcılar yeni kullanıcı oluşturabilir"""
        return self.role == "Yönetici"

class Association:
    def __init__(self, government_id: str, name: str, username: str, password: str):
        self.id = str(uuid.uuid4())
        self.governmentId = government_id
        self.name = name
        self.username = username
        self.password = password  # Plain text, production'da hash'lenmeli
        self.last_login = str(int(datetime.now().timestamp()))
        self.typeCode = ""
        self.typeCodeDescription = ""
        self.subTypeCode = ""
        self.subTypeCodeDescription = ""
        self.oldLegalEntityNumber = ""
        self.newLegalEntityNumber = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "governmentId": self.governmentId,
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "last_login": self.last_login,
            "typeCode": self.typeCode,
            "typeCodeDescription": self.typeCodeDescription,
            "subTypeCode": self.subTypeCode,
            "subTypeCodeDescription": self.subTypeCodeDescription,
            "oldLegalEntityNumber": self.oldLegalEntityNumber,
            "newLegalEntityNumber": self.newLegalEntityNumber
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Association':
        assoc = cls(data["governmentId"], data["name"], data["username"], data["password"])
        assoc.id = data["id"]
        assoc.last_login = data["last_login"]
        assoc.typeCode = data.get("typeCode", "")
        assoc.typeCodeDescription = data.get("typeCodeDescription", "")
        assoc.subTypeCode = data.get("subTypeCode", "")
        assoc.subTypeCodeDescription = data.get("subTypeCodeDescription", "")
        assoc.oldLegalEntityNumber = data.get("oldLegalEntityNumber", "")
        assoc.newLegalEntityNumber = data.get("newLegalEntityNumber", "")
        return assoc

class Member:
    def __init__(self, identity_number: str, first_name: str, last_name: str, association_id: str):
        self.id = str(uuid.uuid4())
        self.identityNumber = identity_number
        self.nationality = "KT"
        self.firstName = first_name
        self.lastName = last_name
        self.middleName = ""
        self.birthSurname = ""
        self.gender = ""
        self.birthPlace = ""
        self.motherName = ""
        self.birthDate = ""
        self.fatherName = ""
        self.district = ""
        self.neighborhood = ""
        self.street = ""
        self.buildingNameOrNumber = ""
        self.doorNumber = ""
        self.apartmentNumber = ""
        self.phoneNumber = ""
        self.gsm = {
            "countryCode": "+90",
            "operatorCode": "533",
            "number": "0000000"
        }
        self.association = association_id
        self.membershipYear = str(datetime.now().year)
        self.status = "pending"  # "pending", "approved", "rejected"
        self.created_at = str(int(datetime.now().timestamp()))
        self.updated_at = str(int(datetime.now().timestamp()))
        self.approved_by = ""
        self.approved_at = ""
        self.rejection_reason = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "identityNumber": self.identityNumber,
            "nationality": self.nationality,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "middleName": self.middleName,
            "birthSurname": self.birthSurname,
            "gender": self.gender,
            "birthPlace": self.birthPlace,
            "motherName": self.motherName,
            "birthDate": self.birthDate,
            "fatherName": self.fatherName,
            "district": self.district,
            "neighborhood": self.neighborhood,
            "street": self.street,
            "buildingNameOrNumber": self.buildingNameOrNumber,
            "doorNumber": self.doorNumber,
            "apartmentNumber": self.apartmentNumber,
            "phoneNumber": self.phoneNumber,
            "gsm": self.gsm,
            "association": self.association,
            "membershipYear": self.membershipYear,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "rejection_reason": self.rejection_reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Member':
        member = cls(data["identityNumber"], data["firstName"], data["lastName"], data["association"])
        member.id = data["id"]
        member.nationality = data.get("nationality", "KT")
        member.middleName = data.get("middleName", "")
        member.birthSurname = data.get("birthSurname", "")
        member.gender = data.get("gender", "")
        member.birthPlace = data.get("birthPlace", "")
        member.motherName = data.get("motherName", "")
        member.birthDate = data.get("birthDate", "")
        member.fatherName = data.get("fatherName", "")
        member.district = data.get("district", "")
        member.neighborhood = data.get("neighborhood", "")
        member.street = data.get("street", "")
        member.buildingNameOrNumber = data.get("buildingNameOrNumber", "")
        member.doorNumber = data.get("doorNumber", "")
        member.apartmentNumber = data.get("apartmentNumber", "")
        member.phoneNumber = data.get("phoneNumber", "")
        member.gsm = data.get("gsm", {"countryCode": "+90", "operatorCode": "533", "number": "0000000"})
        member.membershipYear = data.get("membershipYear", str(datetime.now().year))
        member.status = data.get("status", "pending")
        member.created_at = data.get("created_at", str(int(datetime.now().timestamp())))
        member.updated_at = data.get("updated_at", str(int(datetime.now().timestamp())))
        member.approved_by = data.get("approved_by", "")
        member.approved_at = data.get("approved_at", "")
        member.rejection_reason = data.get("rejection_reason", "")
        return member

class Receipt:
    def __init__(self, member_id: str, association_id: str, upload_path: str):
        self.id = str(uuid.uuid4())
        self.memberId = member_id
        self.associationId = association_id
        self.uploadPath = upload_path
        self.uploadDate = str(int(datetime.now().timestamp()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "memberId": self.memberId,
            "associationId": self.associationId,
            "uploadPath": self.uploadPath,
            "uploadDate": self.uploadDate
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Receipt':
        receipt = cls(data["memberId"], data["associationId"], data["uploadPath"])
        receipt.id = data["id"]
        receipt.uploadDate = data["uploadDate"]
        return receipt
