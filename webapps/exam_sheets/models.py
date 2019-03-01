# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError

class UserProfile(AbstractUser):
    is_examinator = models.BooleanField(default=False)


class ExamSheet(models.Model):
    title = models.CharField(max_length=100, blank=False, unique=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class Exam(models.Model):
    final_grade = models.IntegerField(default=0)
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class Task(models.Model):
    question = models.CharField(max_length=150)
    max_points = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE)

class Answer(models.Model):
    answer = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_points = models.IntegerField(default=0,
                                          validators=[
                                              MinValueValidator(0),
                                            ]
                                          )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)