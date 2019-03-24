from webapps.exam_sheets.models import UserProfile, ExamSheet, Task, Exam
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import exam_url


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

        self.test_user_2 = UserProfile.objects.create_user(
            username="Testow2y",
            password=self.not_hashed_password,
            email="k11@mail.pl",
            is_examinator=False
        )

        self.client.force_login(self.examinator)

        self.test_sheet = ExamSheet.objects.create(
            id=1,
            title="Test sheet",
            user=self.examinator
        )

        self.test_task = Task.objects.create(
            question="Testuje?",
            max_points=5,
            exam_sheet=self.test_sheet
        )

    def test_user_can_generate_exam(self):
        self.client.force_login(self.test_user)
        generate_exam = self.client.post(exam_url(exam_id=''), {
            "exam_sheet": self.test_sheet.pk
        })
        self.assertEqual(201, generate_exam.status_code)

    def test_not_owner_normal_user_cant_get_into_other_user_exam(self):
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)
        self.client.force_login(self.test_user_2)
        get_exam = self.client.get(exam_url(exam_id=test_exam.pk))
        self.assertEqual(403, get_exam.status_code)

    # def test_points_assigned_dynamically_after_examinator_check_answer(self):
    #     login_resp = self.client.post(self.login, {
    #         "username": self.test_user.username,
    #         "email": self.test_user.email,
    #         "password": self.not_hashed_password
    #     })
    #     self.assertEqual(200, login_resp.status_code)
    #
    #     generate_exam = self.client.post(self.exams, {
    #         "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
    #     })
    #
    #     self.assertEqual(201, generate_exam.status_code)
    #
    #     test_answer = self.client.post(self.answer, {
    #         "answer": "test_answer",
    #         "task": self.task_id.rsplit('/', 1)[0]
    #     })
    #     self.assertEqual(201, test_answer.status_code)
    #
    #     login_resp = self.client.post(self.login, {
    #         "username": self.examinator.username,
    #         "email": self.examinator.email,
    #         "password": self.not_hashed_password
    #     })
    #     self.assertEqual(200, login_resp.status_code)
    #
    #     update_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
    #         "assigned_points": 1
    #     })
    #     self.assertEqual(200, update_answer.status_code)
    #
    #     login_resp = self.client.post(self.login, {
    #         "username": self.test_user.username,
    #         "email": self.test_user.email,
    #         "password": self.not_hashed_password
    #     })
    #     self.assertEqual(200, login_resp.status_code)
    #
    #     get_exam = self.client.get(self.exams + str(generate_exam.data['id']))
    #     print(get_exam.data)
    #     self.assertEqual(200, get_exam.status_code)
    #     print(get_exam.data)
    #     self.assertEqual(1, get_exam.data['achieved_points'])
