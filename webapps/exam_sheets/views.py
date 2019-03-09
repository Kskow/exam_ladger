from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile
from webapps.exam_sheets.serializers import ExamSheetSerializer, ExamSerializer, TaskSerializer, AnswerUserSerializer, \
    UserProfileSerializer, AnswerExaminatorSerializer
from rest_framework import generics
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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsExaminatorAndTaskOwner)


class ExamViewSet(viewsets.ModelViewSet):
    """
    View where user can create instance of exam_sheet which belongs to him and list all his exams
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner)

    serializer_class = ExamSerializer
    queryset = Exam.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class AnswerViewSet(viewsets.ModelViewSet):
    """
    View where exam_sheet author can see all answers assigned to task which belongs to his sheet
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner,)
    serializer_class = AnswerUserSerializer
    queryset = Answer.objects.all()

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


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View where user can retrive/update his answer, and exam_sheet author can assigne points.
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner,)

    queryset = Answer.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_examinator:
            return AnswerExaminatorSerializer
        return AnswerUserSerializer
