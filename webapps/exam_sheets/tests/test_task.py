from webapps.exam_sheets.models import UserProfile, ExamSheet, Task, Exam
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import exam_sheet_tasks_url, exam_url, exam_tasks_url


class TaskPermittedUser(APITestCase):

    def setUp(self):
        self.not_hashed_password = 'testuje'

        self.examinator_owner = UserProfile.objects.create_user(
            username='HavePerms9',
            email='testowysobie3@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )
        self.examinator_not_owner = UserProfile.objects.create_user(
            username='HavePerms91',
            email='testowysobie31@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )
        self.user = UserProfile.objects.create_user(
            username='HaveNotPerms911',
            email='testowysobie311@mail.pl',
            password=self.not_hashed_password,
            is_examinator=False
        )

        self.user_2 = UserProfile.objects.create_user(
            username='HaveNot3Perms911',
            email='testowyso1bie311@mail.pl',
            password=self.not_hashed_password,
            is_examinator=False
        )

        self.client.force_login(self.examinator_owner)

        self.exam_sheet = ExamSheet.objects.create(
            id=1,
            title="Test sheet",
            user=self.examinator_owner
        )

    def test_examinator_can_create_task_to_his_exam(self):
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF?",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(201, test_task.status_code)


    def test_examinator_cant_create_task_to_sheet_which_does_not_belong_to_him(self):
        # Re-log to not owner
        self.client.force_login(self.examinator_not_owner)
        # Try to create task to exam_sheet which belong to examinator_owner
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(403, test_task.status_code)

    def test_user_cant_create_task(self):
        # login normal user
        self.client.force_login(self.user)
        # Create test task
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(403, test_task.status_code)

    def test_user_cant_see_task_from_exam_sheet_route(self):
        # Create test task
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(201, test_task.status_code)

        # login normal user
        self.client.force_login(self.user)

        # retrieve this task
        retrieve_task_as_user = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id,
                                                                    task_id=test_task.data['id'])
                                               )
        self.assertEqual(403, retrieve_task_as_user.status_code)

    def test_examinator_but_not_owner_cant_retrieve_task(self):
        # Create test_task
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(201, test_task.status_code)

        # Re-log to not owner
        self.client.force_login(self.user)

        get_task = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=test_task.data['id']))
        self.assertEqual(403, get_task.status_code)

    def test_examinator_and_owner_can_retrieve_task(self):
        # Create test_task
        test_task = self.client.post(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.id
        })
        self.assertEqual(201, test_task.status_code)

        test_task_2 = Task.objects.create(question="DUPA?", max_points=10, exam_sheet=self.exam_sheet)

        get_task = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=test_task.data['id']))
        self.assertEqual(200, get_task.status_code)

    def test_all_tasks_assigned_to_exam_sheet_are_visible_only_by_sheet_owner(self):
        Task.objects.create(question="Testuje?", max_points=5, exam_sheet=self.exam_sheet)
        Task.objects.create(question="Testujemy?", max_points=5, exam_sheet=self.exam_sheet)

        self.client.force_login(self.examinator_not_owner)
        get_tasks = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''))
        self.assertEqual(403, get_tasks.status_code)

        self.client.force_login(self.user)
        get_tasks = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=''))
        self.assertEqual(403, get_tasks.status_code)

    def test_only_task_owner_can_get_into_single_task_id(self):
        test_task = Task.objects.create(question="Testuje?", max_points=5, exam_sheet=self.exam_sheet)

        get_examinator = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=test_task.pk))
        self.assertEqual(200, get_examinator.status_code)

        self.client.force_login(self.examinator_not_owner)
        get_tasks = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=test_task.pk))
        self.assertEqual(403, get_tasks.status_code)

        self.client.force_login(self.user)
        get_tasks = self.client.get(exam_sheet_tasks_url(sheet_id=self.exam_sheet.id, task_id=test_task.pk))
        self.assertEqual(403, get_tasks.status_code)

    def test_user_see_task_from_exam_route(self):
        self.client.force_login(self.user)
        Task.objects.create(question="Testuje?", max_points=5, exam_sheet=self.exam_sheet)
        exam = Exam.objects.create(exam_sheet=self.exam_sheet, user=self.user)
        get_tasks = self.client.get(exam_tasks_url(exam_id=exam.pk, task_id=''))
        self.assertEqual(200, get_tasks.status_code)

    def test_user_cant_see_tasks_from_exam_route_when_exam_does_not_belong_to_him(self):
        exam = Exam.objects.create(exam_sheet=self.exam_sheet, user=self.user)
        self.client.force_login(self.user_2)
        get_exam = self.client.get(exam_url(exam_id=exam.pk))
        self.assertEqual(403, get_exam.status_code)

    def test_user_cant_add_task_from_exam_route(self):
        self.client.force_login(self.user)
        exam = Exam.objects.create(exam_sheet=self.exam_sheet, user=self.user)
        test_task = self.client.post(exam_tasks_url(exam_id=exam.pk, task_id=''), {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.exam_sheet.pk
        })
        self.assertEqual(403, test_task.status_code)


