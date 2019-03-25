from webapps.exam_sheets.models import UserProfile, ExamSheet, Task, Exam
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import exam_url, answers_url


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

    def test_points_assigned_to_exam_when_examiantor_check_answer(self):
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)

        # Login first user
        self.client.force_login(self.test_user)

        # Create first user answer
        test_answer = self.client.post(answers_url(
            exam_id=test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
                "answer": "test_answer",
            })
        self.assertEqual(201, test_answer.status_code)

        # Login to examinator
        self.client.force_login(self.examinator)

        # Assign points to user answer
        self.client.put(answers_url(
            exam_id=test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.data['id']), {
            "assigned_points": self.test_task.max_points,
        })

        exam = Exam.objects.get(pk=test_exam.pk)
        self.assertEqual(exam.achieved_points, self.test_task.max_points)

    def test_assigned_points_check_correctly_after_examinator_change_points(self):
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)

        # Login first user
        self.client.force_login(self.test_user)
        # Create first user answer

        test_answer = self.client.post(answers_url(
            exam_id=test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
                "answer": "test_answer",
            })

        # Login to examinator
        self.client.force_login(self.examinator)

        # Assign points to user answer
        self.client.put(answers_url(
            exam_id=test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.data['id']), {
            "assigned_points": self.test_task.max_points,
        })

        # Re-assign points to user answer
        points_to_re_assign = 2
        self.client.put(answers_url(
            exam_id=test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.data['id']), {
            "assigned_points": points_to_re_assign,
        })

        exam = Exam.objects.get(pk=test_exam.pk)
        self.assertEqual(exam.achieved_points, points_to_re_assign)
