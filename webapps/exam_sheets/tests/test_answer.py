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
            "task": self.test_task.pk,
            "exam": self.test_exam.pk
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
            "task": self.test_task.pk,
            "exam": self.test_exam.pk
        })
        self.assertEqual(201, test_answer_one.status_code)

        # Try to create second answer
        test_answer_two = self.client.post(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=''),
            {
            "answer": "test_answer2",
            "task": self.test_task.pk,
            "exam": self.test_exam.pk
        })
        self.assertEqual(400, test_answer_two.status_code)

    def test_user_cant_retrive_update_delete_other_users_answers(self):
        # Login first user
        self.client.force_login(self.user_one)

        # Create first user answer
        test_answer = Answer(
            pk=1000,
            exam=self.test_exam,
            task=self.test_task,
            user=self.user_one,
            answer='TEST'
        )

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
            "task": self.test_task.pk,
            "exam": self.test_exam.pk
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
                "task": self.test_task.pk,
                "exam": self.test_exam.pk
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
                "task": self.test_task.pk,
                "exam": self.test_exam.pk
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

    def test_answer_points_assign_correctly_to_exam_after_examinator_check_and_is_checked_equal_to_true(self):
        answer = Answer.objects.create(
            answer="TESTOWA",
            task=self.test_task,
            exam=self.test_exam,
            user=self.user_one
        )

        self.client.force_login(self.examinator)

        update_answer = self.client.put(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=answer.pk), {
            "assigned_points": 3
        })

        self.assertEqual(True, update_answer.data['is_checked'])
        exam = Exam.objects.get(pk=self.test_exam.pk)
        self.assertEqual(3, exam.achieved_points)

    def test_answer_points_are_deducted_from_exam_after_deleting_answer_by_examinator(self):
        answer = Answer.objects.create(
            answer="TESTOWA",
            task=self.test_task,
            exam=self.test_exam,
            user=self.user_one,
            assigned_points=self.test_task.max_points
        )
        self.test_exam.achieved_points = 5
        self.test_exam.save()

        self.client.delete(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=answer.pk))

        exam = Exam.objects.get(pk=self.test_exam.pk)
        self.assertEqual(0, exam.achieved_points)

    def test_user_cant_delete_his_answer_if_answer_is_already_checked(self):
        answer = Answer.objects.create(
            answer="TESTOWA",
            task=self.test_task,
            exam=self.test_exam,
            user=self.user_one,
            assigned_points=self.test_task.max_points,
            is_checked=True
        )

        self.client.force_login(self.user_one)

        delete_answer = self.client.delete(answers_url(
            exam_id=self.test_exam.pk,
            task_id=self.test_task.pk,
            answer_id=answer.pk)
        )

        self.assertEqual(403, delete_answer.status_code)
