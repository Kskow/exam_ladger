from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError


class UserProfile(AbstractUser):
    is_examinator = models.BooleanField(default=False)


class ExamSheet(models.Model):
    title = models.CharField(max_length=100, blank=False, unique=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class Exam(models.Model):
    IS_PASSED_CHOICES = (
        ('PASSED', 'Passed'),
        ('NOT PASSED', 'Not passed'),
        ('PENDING', 'pending')
    )

    achieved_points = models.IntegerField(default=0)
    is_passed = models.CharField(max_length=30, choices=IS_PASSED_CHOICES, default='PENDING')
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class Task(models.Model):
    question = models.CharField(max_length=150)
    max_points = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE, related_name='tasks')


class Answer(models.Model):
    answer = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='answers')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    assigned_points = models.IntegerField(default=0,
                                          validators=[
                                              MinValueValidator(0),
                                            ]
                                          )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
