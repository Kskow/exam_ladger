from webapps.exam_sheets.models import UserProfile, ExamSheet
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import exam_sheet_url, exam_sheet_tasks_url


class ExamSheetsPermitedUser(APITestCase):

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

        self.client.force_login(self.examinator)

        self.exam_sheet = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "Test sheet"
            })

        self.assertEqual(201, self.exam_sheet.status_code)
        self.test_sheet_id = str(self.exam_sheet.data['id']) + '/'

    def test_examinator_can_create_exam_sheet(self):
        # Create new sheet when logged as examinator
        test_sheet = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "test exam sheet",
        })
        self.assertEqual(201, test_sheet.status_code)

    def test_user_cant_create_exam_sheet(self):
        # Login to normal user
        self.client.force_login(self.test_user)

        # Try to post new sheet
        test_sheet = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "test exam sheet",
        })
        self.assertEqual(403, test_sheet.status_code)

    def test_examinator_cant_access_sheet_if_he_is_not_author(self):
        # Examinator create sheet
        test_sheet = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "test exam sheet",
        })
        self.assertEqual(201, test_sheet.status_code)

        get_author = self.client.get(exam_sheet_url(sheet_id=test_sheet.data['id']))
        self.assertEqual(200, get_author.status_code)

        # Re-log to examinator but not sheet owner.
        not_author = UserProfile.objects.create_user(
            username='HavePerms91',
            email='testowysobie31@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )
        self.client.force_login(not_author)

        # Try to enter sheet which not_author is not owner
        get_sheet = self.client.get(exam_sheet_url(sheet_id=test_sheet.data['id']))
        self.assertEqual(404, get_sheet.status_code)

    def test_examinator_cant_see_list_with_other_examinators_exams(self):
        # Examinator create two sheets
        test_sheet_1 = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "test exam sheet",
        })
        self.assertEqual(201, test_sheet_1.status_code)

        test_sheet_2 = self.client.post(exam_sheet_url(sheet_id=''), {
            "title": "test exam sheet2",
        })

        self.assertEqual(201, test_sheet_2.status_code)
        # Re-log to examinator but not owner
        not_author = UserProfile.objects.create_user(
            username='HavePerms91',
            email='testowysobie31@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )
        self.client.force_login(not_author)

        get_sheets = self.client.get(exam_sheet_url(sheet_id=''))
        self.assertEqual(200, get_sheets.status_code)
        self.assertEqual(0, len(get_sheets.data))

    def test_added_points_to_max_points_after_creating_task(self):
        exam_sheet = ExamSheet.objects.create(
            id=999,
            title="Test sheeet",
            user=self.examinator
        )
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=exam_sheet.id, task_id=''), {
            "question": "WTF?",
            "max_points": 5,
            "exam_sheet": exam_sheet.id
        })
        self.assertEqual(201, test_task.status_code)

        exam_sheet = ExamSheet.objects.get(pk=exam_sheet.id)
        self.assertEqual(5, exam_sheet.max_points)

    def test_max_points_changed_properly_after_edited_task(self):
        exam_sheet = ExamSheet.objects.create(
            id=998,
            title="Test sh1t",
            user=self.examinator
        )
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=exam_sheet.id, task_id=''), {
            "question": "WTF?",
            "max_points": 5,
            "exam_sheet": exam_sheet.id
        })

        test_task_two = self.client.post(exam_sheet_tasks_url(sheet_id=exam_sheet.id, task_id=''), {
            "question": "WTF!?",
            "max_points": 5,
            "exam_sheet": exam_sheet.id
        })

        edited_task = self.client.put(exam_sheet_tasks_url(sheet_id=exam_sheet.id, task_id=test_task.data['id']), {
            "question": test_task.data['question'],
            "max_points": 3,
            "exam_sheet": exam_sheet.id
        })

        exam_sheet = ExamSheet.objects.get(pk=exam_sheet.id)
        self.assertEqual(8, exam_sheet.max_points)
