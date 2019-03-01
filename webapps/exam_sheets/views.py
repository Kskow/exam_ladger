# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile
from webapps.exam_sheets.serializers import ExamSheetSerializer, ExamSerializer, TaskSerializer, AnswerUserSerializer, \
    UserProfileSerializer, AnswerExaminatorSerializer
from rest_framework import generics
from django.http import HttpResponse
from webapps.exam_sheets.permissions import IsExamiantorOrSheetOwner, IsExaminatorAndTaskOwner, \
    IsExaminatorOrAnswerOwner
from rest_framework.permissions import IsAuthenticated

def health_check(request):
    return HttpResponse()


class UserList(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

class ExamSheetCreate(generics.CreateAPIView):
    """
    View where examinator can create new sheet
    """
    permission_classes = (IsAuthenticated, IsExamiantorOrSheetOwner, )

    serializer_class = ExamSheetSerializer


    def perform_create(self, serializer):
        """
        Create new exam_sheet which will be assigned to current user which have examinator permissions.
        """

        user = self.request.user
        serializer.save(user=user)

class ExamSheetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View where examinator can get,put and delete examsheet
    """
    permission_classes = (IsAuthenticated, IsExamiantorOrSheetOwner,)

    queryset = ExamSheet.objects.all()
    serializer_class = ExamSheetSerializer

class TaskCreate(generics.CreateAPIView):
    """
    View where Examinator can add tasks
    """

    permission_classes = (IsAuthenticated, IsExaminatorAndTaskOwner,)

    serializer_class = TaskSerializer

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View where Examiantor can check/update/delete task details
    """
    permission_classes = (IsAuthenticated, IsExaminatorAndTaskOwner,)

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class ExamDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class AnswerCreate(generics.CreateAPIView):
    """
    View where exam_sheet author can see all answers assigned to task which belongs to his sheet
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrAnswerOwner,)

    serializer_class = AnswerUserSerializer

    def perform_create(self, serializer):
        """
        Answer is created by already logged in user
        """
        user = self.request.user
        answer = serializer.save(user=user)



class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View where user can retrive/update his answer, and exam_sheet author can assigne points.
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrAnswerOwner,)

    queryset = Answer.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_examinator:
            return AnswerExaminatorSerializer
        return AnswerUserSerializer
