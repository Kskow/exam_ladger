# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
#
# from webapps.exam_sheets.models import UserProfile, Task, ExamSheet
# from rest_framework.test import APITestCase
# from django.urls import reverse
#
#
# class UserAnswer(APITestCase):
#     login = 'http://testserver/api/login/'
#     logout = 'http://testserver/api/logout/'
#     sheets = reverse('exam_sheets')
#     task = reverse('task')
#     answer = reverse('answer')
#
#     id = 100
#     def _generate_id(self):
#         self.id += 1
#         return self.id
#
#     def setUp(self):
#         self.not_hashed_password = 'testuje'
#
#         # Create task as permitted user
#         self.examinator = UserProfile.objects.create_user(
#             username='HavePerms9',
#             email='testowysobie3@mail.pl',
#             password=self.not_hashed_password,
#             is_examinator=True
#         )
#
#         self.user_one = UserProfile.objects.create_user(
#             username='NoPerms',
#             email='test3@mail.pl',
#             password=self.not_hashed_password,
#             is_examinator=False
#         )
#
#         self.user_two = UserProfile.objects.create_user(
#             username='NoPerms1',
#             email='test4@mail.pl',
#             password=self.not_hashed_password,
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
#         })
#
#         self.assertEqual(201, self.test_sheet.status_code)
#         self.test_sheet_id = str(self.test_sheet.data['id']) + '/'
#
#     def tearDown(self):
#         logout = self.client.post(self.logout)
#         self.assertEqual(200, logout.status_code)
#
#     def test_user_can_add_answer(self):
#         # Login user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet= ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#         # Create test answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#
#         self.assertEqual(201, test_answer.status_code)
#
#     def test_same_user_cant_create_two_answers_to_one_task(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first answer
#         test_answer_two = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer_two.status_code)
#
#         # Try to create second answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer1",
#             "task": test_task.id
#         })
#         self.assertEqual(400, test_answer.status_code)
#
#     def test_user_cant_retrive__update_delete_other_users_answers(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login first user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first user answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         # Re-log to second user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_two.username,
#             "email": self.user_two.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Retrive/update/delete first user answer
#         retrive_answer = self.client.get(self.answer + str(test_answer.data['id']) + '/')
#         self.assertEqual(403, retrive_answer.status_code)
#
#         update_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
#             "answer": "changed",
#             "task": test_task.id
#         })
#         self.assertEqual(403, update_answer.status_code)
#
#         delete_answer = self.client.delete(self.answer + str(test_answer.data['id']) + '/')
#         self.assertEqual(403, delete_answer.status_code)
#
#     def test_user_can_retrive_update_delete_his_answers(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login first user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first user answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         # Retrive/update/del user answer
#         retrive_answer = self.client.get(self.answer + str(test_answer.data['id']) + '/')
#         self.assertEqual(200, retrive_answer.status_code)
#
#         update_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
#             "answer": "changed",
#             "task": test_task.id
#         })
#         self.assertEqual(200, update_answer.status_code)
#
#         delete_answer = self.client.delete(self.answer + str(test_answer.data['id']) + '/')
#         self.assertEqual(204, delete_answer.status_code)
#
#     def test_examinator_can_assign_points_to_user_answer(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login first user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first user answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         # Login to examinator
#         login_resp = self.client.post(self.login, {
#             "username": self.examinator.username,
#             "email": self.examinator.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Assign points to user answer
#         update_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
#             "assigned_points": 1
#         })
#         self.assertEqual(200, update_answer.status_code)
#
#     def test_examinator_can_retrive_user_answer(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login first user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first user answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         # Login to examinator
#         login_resp = self.client.post(self.login, {
#             "username": self.examinator.username,
#             "email": self.examinator.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Retrive user answer
#         retrive_answer = self.client.get(self.answer + str(test_answer.data['id']) + '/')
#         self.assertEqual(200, retrive_answer.status_code)
#
#     def test_cant_assign_more_points_than_max(self):
#         # Create test task
#         test_task = Task.objects.create(
#             id=self._generate_id(),
#             max_points=5,
#             exam_sheet=ExamSheet.objects.create(id=self._generate_id(), title='dupa', user=self.examinator)
#         )
#
#         # Login first user
#         login_resp = self.client.post(self.login, {
#             "username": self.user_one.username,
#             "email": self.user_one.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Create first user answer
#         test_answer = self.client.post(self.answer, {
#             "answer": "test_answer",
#             "task": test_task.id
#         })
#         self.assertEqual(201, test_answer.status_code)
#
#         # Login to examinator
#         login_resp = self.client.post(self.login, {
#             "username": self.examinator.username,
#             "email": self.examinator.email,
#             "password": self.not_hashed_password
#         })
#         self.assertEqual(200, login_resp.status_code)
#
#         # Retrive user answer
#         retrive_answer = self.client.put(self.answer + str(test_answer.data['id']) + '/', {
#             "assigned_points": test_task.max_points + 1
#         })
#         self.assertEqual(400, retrive_answer.status_code)