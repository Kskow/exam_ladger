# from __future__ import unicode_literals
#
# from webapps.exam_sheets.models import UserProfile
# from rest_framework.test import APITestCase
# from django.urls import reverse
#
#
# class ExamSheetsPermitedUser(APITestCase):
#     login = 'http://testserver/api/login/'
#     logout = 'http://testserver/api/logout/'
#     sheets = reverse('exam_sheets')
#     exams = reverse('exams')
#     answer = reverse('answer')
#     task = reverse('task')
#
#     def setUp(self):
#         self.not_hashed_password = 'testuje'
#
#         self.examinator = UserProfile.objects.create_user(
#             username='HavePerms9',
#             email='testowysobie3@mail.pl',
#             password=self.not_hashed_password,
#             is_examinator=True
#         )
#
#         self.test_user = UserProfile.objects.create_user(
#             username="Testowy",
#             password=self.not_hashed_password,
#             email="k1@mail.pl",
#             is_examinator=False
#         )
#
#         login_resp = self.client.post(self.login, {
#             "username": self.examinator.username,
#             "email": self.examinator.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         self.test_sheet = self.client.post(self.sheets, {
#             "title": "Test sheet"
#             })
#
#         self.assertEqual(201, self.test_sheet.status_code)
#         self.test_sheet_id = str(self.test_sheet.data['id']) + '/'
#
#         self.test_task = self.client.post(self.task, {
#             "question": "Test question",
#             "max_points": 5,
#             "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
#         })
#         self.assertEqual(201, self.test_task.status_code)
#         self.task_id = str(self.test_task.data['id']) + '/'
#
#     def _test_user_can_generate_exam(self):
#         login_resp = self.client.post(self.login, {
#             "username": self.test_user.username,
#             "email": self.test_user.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         generate_exam = self.client.post(self.exams, {
#             "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
#         })
#
#         self.assertEqual(201, generate_exam.status_code)
#
#     def test_points_assigned_dynamically_after_examinator_check_answer(self):
#         login_resp = self.client.post(self.login, {
#             "username": self.test_user.username,
#             "email": self.test_user.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         generate_exam = self.client.post(self.exams, {
#             "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
#         })
#
#         self.assertEqual(201, generate_exam.status_code)
#
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": self.task_id.rsplit('/', 1)[0]
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         login_resp = self.client.post(self.login, {
#             "username": self.examinator.username,
#             "email": self.examinator.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         update_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
#             "assigned_points": 1
#         })
#         self.assertEqual(200, update_answer.status_code)
#
#         login_resp = self.client.post(self.login, {
#             "username": self.test_user.username,
#             "email": self.test_user.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         get_exam = self.client.get(self.exams + str(generate_exam.data['id']))
#         print(get_exam.data)
#         self.assertEqual(200, get_exam.status_code)
#         print(get_exam.data)
#         self.assertEqual(1, get_exam.data['achieved_points'])
