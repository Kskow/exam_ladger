# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from webapps.exam_sheets.models import UserProfile
from rest_framework.test import APITestCase
from django.urls import reverse


class TaskPermittedUser(APITestCase):
    login = 'http://testserver/api/login/'
    logout = 'http://testserver/api/logout/'
    sheets = reverse('exam_sheets')
    task = reverse('task')

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

        login_resp = self.client.post(self.login, {
            "username": self.examinator_owner.username,
            "email": self.examinator_owner.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        self.exam_sheet = self.client.post(self.sheets, {
            "title": "Test sheet"
        })

        self.assertEqual(201, self.exam_sheet.status_code)
        self.test_sheet_id = str(self.exam_sheet.data['id']) + '/'

        self.test_task = self.client.post(self.task, {
            "question": "Test question",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, self.test_task.status_code)
        self.task_id = str(self.test_task.data['id']) + '/'

    def test_examinator_can_create_task_to_his_exam(self):
        test_task = self.client.post(self.task, {
            "question": "WTF?",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, test_task.status_code)

    def test_examinator_cant_create_task_to_sheet_which_does_not_belong_to_him(self):
        # Re-log to not owner
        login_not_owner = self.client.post(self.login, {
            "username": self.examinator_not_owner.username,
            "email": self.examinator_not_owner.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_not_owner.status_code)
        self.assertNotEqual(self.exam_sheet.data['user'], self.examinator_not_owner.username)
        # Try to create task to exam_sheet which belong to examinator_owner
        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(403, test_task.status_code)

    def test_user_cant_create_task(self):
        # login normal user
        login_resp = self.client.post(self.login, {
            "username": self.user.username,
            "email": self.user.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        # Create test task
        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(403, test_task.status_code)

    def test_user_can_see_task(self):
        # Create test task
        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, test_task.status_code)

        # login normal user
        login_resp = self.client.post(self.login, {
            "username": self.user.username,
            "email": self.user.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        # retrive this task
        retrive_task_as_user = self.client.get(self.task + str(test_task.data['id']) + '/')
        self.assertEqual(200, retrive_task_as_user.status_code)

    def test_user_cant_update_and_delete_task(self):
        # Create test task
        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, test_task.status_code)

        # login normal user
        login_resp = self.client.post(self.login, {
            "username": self.user.username,
            "email": self.user.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        # try to update/delete task
        update_task = self.client.put(self.task + str(test_task.data['id']) + '/', {
            "question": "DUPA",
            "max_points": 10,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(403, update_task.status_code)

        delete_task = self.client.delete(self.task + str(test_task.data['id']) + '/')
        self.assertEqual(403, delete_task.status_code)

    def test_owner_can_update_and_delete_task(self):
        # create test_task
        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, test_task.status_code)

        # try to update task and delete task
        update_task = self.client.put(self.task + str(test_task.data['id']) + '/', {
            "question": "DUPA",
            "max_points": 10,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(200, update_task.status_code)

        delete_task = self.client.delete(self.task + str(test_task.data['id']) + '/')
        self.assertEqual(204, delete_task.status_code)

    def test_examinator_but_not_owner_cant_update_delete_task(self):
        #Create test_task

        test_task = self.client.post(self.task, {
            "question": "WTF??",
            "max_points": 5,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(201, test_task.status_code)

        # Re-log to not owner
        login_resp = self.client.post(self.login, {
            "username": self.examinator_not_owner.username,
            "email": self.examinator_not_owner.email,
            "password": self.not_hashed_password
        })
        self.assertEqual(200, login_resp.status_code)

        # Update/Delete task
        update_task = self.client.put(self.task + str(test_task.data['id']) + '/', {
            "question": "DUPA",
            "max_points": 10,
            "exam_sheet": self.test_sheet_id.rsplit('/', 1)[0]
        })
        self.assertEqual(403, update_task.status_code)

        delete_task = self.client.delete(self.task + str(test_task.data['id']) + '/')
        self.assertEqual(403, delete_task.status_code)
