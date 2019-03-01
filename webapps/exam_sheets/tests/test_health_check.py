# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from django.urls import reverse


class HealthCheck(APITestCase):
    url = reverse('health_check')

    def test_health_check(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
