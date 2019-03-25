from webapps.exam_sheets.models import UserProfile, Task, ExamSheet, Exam, Answer
from rest_framework.test import APITestCase
from webapps.exam_sheets.tests.data import answers_url


class UserAnswer(APITestCase):

    def setUp(self):
        self.not_hashed_password = 'testuje'

        # Create task as permitted user
        self.examinator = UserProfile.objects.create_user(
            username='HavePerms9',
            email='testowysobie3@mail.pl',
            password=self.not_hashed_password,
            is_examinator=True
        )

        self.user_one = UserProfile.objects.create_user(
            username='NoPerms',
            email='test3@mail.pl',
            password=self.not_hashed_password,
            is_examinator=False
        )

        self.user_two = UserProfile.objects.create_user(
            username='NoPerms1',
            email='test4@mail.pl',
            password=self.not_hashed_password,
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

        self.test_exam = Exam.objects.create(exam_sheet=self.test_sheet, user=self.user_one)

    def test_user_can_add_answer(self):
        self.client.force_login(self.user_one)

        answer = self.client.post(answers_url(exam_id=self.test_exam.pk, task_id=self.test_task.pk, answer_id=''), {
            "answer": "Testowa",
        })
        self.assertEqual(201, answer.status_code)

    def test_same_user_cant_create_two_answers_to_one_task(self):

        # Login user
        self.client.force_login(self.user_one)

        # Create first answer
        test_answer_one = self.client.post(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
            "answer": "test_answer",
        })
        self.assertEqual(201, test_answer_one.status_code)

        # Try to create second answer
        test_answer_two = self.client.post(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
            "answer": "test_answer2",
        })
        self.assertEqual(400, test_answer_two.status_code)

    def test_user_cant_retrive_update_delete_other_users_answers(self):
        # Login first user
        self.client.force_login(self.user_one)

        # Create first user answer
        test_answer = Answer(pk=1000, exam=self.test_exam, task=self.test_task, user=self.user_one, answer='TEST')

        # Re-log to second user
        self.client.force_login(self.user_two)

        # Retrive/update/delete first user answer
        retrive_answer = self.client.get(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.pk))
        self.assertEqual(404, retrive_answer.status_code)

        update_answer = self.client.put(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.pk), {
            "answer": "changed",
        })

        self.assertEqual(404, update_answer.status_code)

        delete_answer = self.client.delete(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.pk))
        self.assertEqual(404, delete_answer.status_code)

    def test_examinator_can_assign_points_to_user_answer(self):
        # Login first user
        self.client.force_login(self.user_one)

        # Create first user answer
        test_answer = self.client.post(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
                "answer": "test_answer",
            })
        self.assertEqual(201, test_answer.status_code)
        # Login to examinator
        self.client.force_login(self.examinator)

        # Assign points to user answer
        update_answer = self.client.put(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.data['id']), {
            "assigned_points": "3",
        })
        self.assertEqual(200, update_answer.status_code)

    def test_cant_assign_more_points_than_max(self):
        # Login first user
        self.client.force_login(self.user_one)

        # Create first user answer
        test_answer = self.client.post(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
                "answer": "test_answer",
            })
        self.assertEqual(201, test_answer.status_code)
        # Login to examinator
        self.client.force_login(self.examinator)

        # Assign points to user answer
        update_answer = self.client.put(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=test_answer.data['id']), {
            "assigned_points": self.test_task.max_points + 1,
        })

        self.assertEqual(400, update_answer.status_code)