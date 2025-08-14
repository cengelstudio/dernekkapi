import unittest
from datetime import datetime
from app import create_app
from app.services.db import create_member, get_members_by_association, create_association
from app.models import Member, Association

class MemberTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Test derneği oluştur
        self.test_association = Association("TEST001", "Test Derneği", "testdernek", "testpass")
        create_association(self.test_association)

    def tearDown(self):
        self.app_context.pop()

    def test_create_member(self):
        """Üye oluşturmanın başarılı olduğunu test et"""
        member = Member("12345678901", "Test", "User", self.test_association.id)
        member.phoneNumber = "02121234567"
        member.gsm = {"countryCode": "+90", "operatorCode": "533", "number": "1234567"}

        result = create_member(member)
        self.assertTrue(result)

    def test_get_members_by_association(self):
        """Derneğe ait üyelerin getirildiğini test et"""
        # Test üyesi oluştur
        member = Member("12345678901", "Test", "User", self.test_association.id)
        create_member(member)

        # Derneğin üyelerini al
        members = get_members_by_association(self.test_association.id)
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].firstName, "Test")
        self.assertEqual(members[0].lastName, "User")

    def test_member_data_integrity(self):
        """Üye verilerinin doğru şekilde saklandığını test et"""
        member = Member("12345678901", "Test", "User", self.test_association.id)
        member.middleName = "Middle"
        member.birthSurname = "BirthSurname"
        member.gender = "Erkek"
        member.birthPlace = "İstanbul"
        member.motherName = "Anne"
        member.birthDate = "1990-01-01"
        member.fatherName = "Baba"
        member.district = "Kadıköy"
        member.neighborhood = "Test Mahalle"
        member.street = "Test Sokak"
        member.buildingNameOrNumber = "Test Bina"
        member.doorNumber = "1"
        member.apartmentNumber = "A"
        member.phoneNumber = "02121234567"
        member.gsm = {"countryCode": "+90", "operatorCode": "533", "number": "1234567"}
        member.membershipYear = str(datetime.now().year)

        create_member(member)

        # Üyeyi geri al ve verileri kontrol et
        members = get_members_by_association(self.test_association.id)
        retrieved_member = members[0]

        self.assertEqual(retrieved_member.identityNumber, "12345678901")
        self.assertEqual(retrieved_member.firstName, "Test")
        self.assertEqual(retrieved_member.lastName, "User")
        self.assertEqual(retrieved_member.middleName, "Middle")
        self.assertEqual(retrieved_member.birthSurname, "BirthSurname")
        self.assertEqual(retrieved_member.gender, "Erkek")
        self.assertEqual(retrieved_member.birthPlace, "İstanbul")
        self.assertEqual(retrieved_member.motherName, "Anne")
        self.assertEqual(retrieved_member.birthDate, "1990-01-01")
        self.assertEqual(retrieved_member.fatherName, "Baba")
        self.assertEqual(retrieved_member.district, "Kadıköy")
        self.assertEqual(retrieved_member.neighborhood, "Test Mahalle")
        self.assertEqual(retrieved_member.street, "Test Sokak")
        self.assertEqual(retrieved_member.buildingNameOrNumber, "Test Bina")
        self.assertEqual(retrieved_member.doorNumber, "1")
        self.assertEqual(retrieved_member.apartmentNumber, "A")
        self.assertEqual(retrieved_member.phoneNumber, "02121234567")
        self.assertEqual(retrieved_member.gsm["countryCode"], "+90")
        self.assertEqual(retrieved_member.gsm["operatorCode"], "533")
        self.assertEqual(retrieved_member.gsm["number"], "1234567")
        self.assertEqual(retrieved_member.membershipYear, str(datetime.now().year))

if __name__ == '__main__':
    unittest.main()
