from webapps.exam_sheets.models import UserProfile, ExamSheet, Task, Exam, Answer
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import exam_url


class ExamTests(APITestCase):

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

    def test_cant_create_exam_if_exam_sheet_does_not_contain_any_task(self):
        self.test_task.delete()
        self.client.force_login(self.test_user)
        generate_exam = self.client.post(exam_url(exam_id=''), {
            "exam_sheet": self.test_sheet.pk
        })

        self.assertEqual(400, generate_exam.status_code)

    def test_user_cant_delete_already_generated_exam(self):
        self.client.force_login(self.test_user)
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)
        delete_exam = self.client.delete(exam_url(exam_id=test_exam.pk))

        self.assertEqual(403, delete_exam.status_code)

    def test_user_cant_edit_already_generated_exam(self):
        self.client.force_login(self.test_user)
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)
        update_exam = self.client.put(exam_url(exam_id=test_exam.pk), {
            "achieved_points": 10
        })

        self.assertEqual(403, update_exam.status_code)

    def test_examinator_cant_check_exam_if_not_answers_are_checked(self):
        test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.test_user)
        Answer.objects.create(
            answer="test_answer!",
            exam=test_exam,
            task=self.test_task,
            user=self.test_user,
            is_checked=False
        )

        update_exam = self.client.put(exam_url(exam_id=test_exam.pk), {
            "is_checked": True,
            "exam_sheet": self.test_sheet.pk
        })

        self.assertEqual(400, update_exam.status_code)

    def test_user_reached_passed_to_exam_percent_value(self):
        self.test_sheet.max_points = 5
        self.test_sheet.save()

        test_exam = Exam.objects.create(
            exam_sheet=self.test_sheet,
            user=self.test_user,
            achieved_points=4,
            percent_to_pass=60
        )

        Answer.objects.create(
            answer="test_answer!",
            exam=test_exam,
            task=self.test_task,
            user=self.test_user,
            assigned_points=4,
            is_checked=True
        )

        update_exam = self.client.put(exam_url(exam_id=test_exam.pk), {
            "is_checked": True,
            "exam_sheet": self.test_sheet.pk
        })

        self.assertEqual(200, update_exam.status_code)

        exam = Exam.objects.get(pk=test_exam.pk)
        self.assertEqual(True, exam.is_checked)
        self.assertEqual('PASSED', exam.is_passed)

    def test_user_not_reached_percent_to_pass_value(self):
        self.test_sheet.max_points = 5
        self.test_sheet.save()

        test_exam = Exam.objects.create(
            exam_sheet=self.test_sheet,
            user=self.test_user,
            achieved_points=2,
            percent_to_pass=60
        )

        Answer.objects.create(
            answer="test_answer!",
            exam=test_exam,
            task=self.test_task,
            user=self.test_user,
            assigned_points=4,
            is_checked=True
        )

        self.client.put(exam_url(exam_id=test_exam.pk), {
            "is_checked": True,
            "exam_sheet": self.test_sheet.pk
        })

        exam = Exam.objects.get(pk=test_exam.pk)
        self.assertEqual(True, exam.is_checked)
        self.assertEqual('NOT PASSED', exam.is_passed)
