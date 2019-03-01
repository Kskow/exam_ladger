from __future__ import unicode_literals

from webapps.exam_sheets.models import UserProfile
from rest_framework.test import APITestCase
from django.urls import reverse


class ExamSheetsPermitedUser(APITestCase):
    login = 'http://testserver/api/login/'
    logout = 'http://testserver/api/logout/'
    sheets = reverse('exam_sheets')

    def setUp(self):
        self.not_hashed_password = 'testuje'

        self.examinator = UserProfile.objects.create_user(
            username='HavePerms9',
            email='testowysobie3@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )

        self.test_user = UserProfile.objects.create_user(
            username="Testowy",
            password=self.not_hashed_password,
            email="k1@mail.pl",
            is_examinator=False
        )

        login_resp = self.client.post(self.login, {
            "username": self.examinator.username,
            "email": self.examinator.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        self.exam_sheet = self.client.post(self.sheets, {
            "title": "Test sheet"
            })

        self.assertEqual(201, self.exam_sheet.status_code)
        self.test_sheet_id = str(self.exam_sheet.data['id']) + '/'

    def tearDown(self):
        logout = self.client.post(self.logout)
        self.assertEqual(200, logout.status_code)

    def test_examinator_can_create_exam_sheet(self):
        # Create new sheet when logged as examinator
        test_sheet = self.client.post(self.sheets, {
            "title": "test exam sheet",
        })
        self.assertEqual(201, test_sheet.status_code)

    def test_user_cant_create_exam_sheet(self):
        # Login to normal user
        login_user = self.client.post(self.login, {
            "username": self.test_user.username,
            "email": self.test_user.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_user.status_code)

        # Try to post new sheet
        test_sheet = self.client.post(self.sheets, {
            "title": "test exam sheet",
        })
        self.assertEqual(403, test_sheet.status_code)

    def test_examinator_cant_access_sheet_if_he_is_not_author(self):
        # Examinator create sheet
        test_sheet = self.client.post(self.sheets, {
            "title": "test exam sheet",
        })
        get_author = self.client.get(self.sheets + str(test_sheet.data['id']) + '/')
        self.assertEqual(200, get_author.status_code)
        self.assertEqual(201, test_sheet.status_code)

        # Re-log to examinator but not sheet owner.
        not_author = UserProfile.objects.create_user(
            username='HavePerms91',
            email='testowysobie31@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )
        login_user = self.client.post(self.login, {
            "username": not_author.username,
            "email": not_author.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_user.status_code)
        #Try to enter sheet which not_author is not owner
        get_sheet = self.client.get(self.sheets + str(test_sheet.data['id']) + '/')
        self.assertEqual(403, get_sheet.status_code)