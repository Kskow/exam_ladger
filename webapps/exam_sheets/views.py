from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile
from webapps.exam_sheets.serializers import ExamSheetSerializer, ExamSerializer, TaskSerializer, AnswerUserSerializer, \
    UserProfileSerializer, AnswerExaminatorSerializer
from django.http import HttpResponse
from webapps.exam_sheets.permissions import IsExamiantorOrSheetOwner, IsExaminatorAndTaskOwner, \
    IsExaminatorOrOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin


def health_check(Response):
    return HttpResponse()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class ExamSheetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    View where examinator can create new sheet and see exam sheets which belongs to him
    """
    # TODO: Add points to max points field after adding task
    serializer_class = ExamSheetSerializer
    permission_classes = (IsAuthenticated, IsExamiantorOrSheetOwner,)

    def get_queryset(self):
        return ExamSheet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create new exam_sheet which will be assigned to current user which have examinator permissions.
        """

        user = self.request.user
        serializer.save(user=user)


class TaskViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    View where Examinator can add tasks to his exam and see list of his tasks, if url is nested then
    examinator see list of tasks filtered by exam_sheet in url, user will see only tasks by exams which he try to
    retrive.
    """
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsExaminatorAndTaskOwner)

    def get_queryset(self):
        exam_sheet_id = int(self.request.parser_context['kwargs']['parent_lookup_exam_sheet'])
        return Task.objects.filter(exam_sheet=exam_sheet_id)


class ExamViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    View where user can create instance of exam_sheet which belongs to him and list all his exams
    """
    # TODO: when all answers has been checked and points over 50%
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class AnswerViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    View where exam_sheet author can see all answers assigned to task which belongs to his sheet
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner,)

    def get_queryset(self):
        task_id = int(self.request.parser_context['kwargs']['parent_lookup_task'])
        return Answer.objects.filter(task=task_id)

    def get_serializer_class(self):
        if self.request.user.is_examinator:
            return AnswerExaminatorSerializer
        return AnswerUserSerializer

    def perform_create(self, serializer):
        """
        Answer is created by already logged in user
        """

        user = self.request.user
        serializer.save(user=user)
