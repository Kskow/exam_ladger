from exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile
from exam_sheets.serializers import ExamSheetSerializer, ExamSerializer, TaskSerializer, AnswerUserSerializer, \
    UserProfileSerializer, AnswerExaminatorSerializer
from django.http import HttpResponse
from exam_sheets.permissions import IsExamiantorOrSheetOwner, IsExaminatorAndTaskOwner, \
    IsExaminatorOrOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin


def health_check(response):
    return HttpResponse()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class ExamSheetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    retrieve:
    Return given exam_sheet details if owner calls for it

    list:
    Return a list of all existing exam_sheets created by already logged in examinator

    create:
    Create a new exam_sheet instance if you are examinator

    update:
    Update exam_sheet data if sheet owner calls for it

    delete:
    Examiantor, owner of sheet is able to delete his sheet
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
    retrieve:
    Examinator can see his task detail, user can see task if he already generate exam instance from sheet which these
    task belongs to

    list:
    Examinator can see his task list, user can see task list if he already generate exam instance from sheet which these
    task belongs to

    create:
    Examinator can create task and assign him to exam_sheet

    update:
    Examinator can update data of these task

    delete:
    Examinator, owner is able to delete task
    """
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsExaminatorAndTaskOwner)

    def get_queryset(self):
        exam_sheet_id = int(self.request.parser_context['kwargs']['parent_lookup_exam_sheet'])
        return Task.objects.filter(exam_sheet=exam_sheet_id)

    def perform_create(self, serializer):
        """
        On create task max points will be added to exam_sheet max points value
        """
        serializer.save()
        serializer.instance.on_create(serializer.data['max_points'])

    def perform_update(self, serializer):
        """
        On update when max points assigned to task will be updated by exam owner than max points of exam sheet will be
        updated also.
        """
        serializer.save()
        serializer.instance.on_update(serializer.data['max_points'])

    def perform_destroy(self, instance):
        """
        On delete max points assigned to task will be deducted from exam_sheet max points value and
        each answer achieved points which are assigned to these task will be deducted from exams which has these task.
        """
        instance.on_delete()
        instance.delete()


class ExamViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    retrieve:
    Examinator and exam owner can retrive exam details

    list:
    Examinator see list of exams which are assigned to his sheets, user can see list of his generated exam instances

    create:
    User can create exam instance to already create exam sheet

    update:
    Examinator can check exam if all answers assigned to tasks which belongs to these exam are already checked

    delete:
    Examinator is able to delete these exam
    """

    serializer_class = ExamSerializer
    queryset = Exam.objects.all()
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save()
        if self.request.user.is_examinator:
            serializer.instance.on_update()


class AnswerViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    retrieve:
    Owner and examinator can retrieve details of answer

    create:
    User is able to create answer for exam task

    Update:
    User is able to update his answer if examinator did not already checked these answer
    Examinator is able to check annswer and assign points to these answer

    Delete:
    Examinator is able to delete answer
    """
    permission_classes = (IsAuthenticated, IsExaminatorOrOwner,)

    def get_queryset(self):
        task_id = int(self.request.parser_context['kwargs']['parent_lookup_exam__task'])
        return Answer.objects.filter(task=task_id)

    def get_serializer_class(self):
        if self.request.user.is_examinator:
            return AnswerExaminatorSerializer
        return AnswerUserSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Answer is created by already logged in user, and if examinator is person who update(check) answer than
        points are assigned/reassigned to exam automatically and is_checked field is set to True
        """
        user = self.request.user
        if user.is_examinator:
            points_before_update = serializer.instance.assigned_points
            serializer.save(user=user, is_checked=True)
            serializer.instance.on_examinator_update(points_before_update, serializer.data['assigned_points'])
            return
        serializer.save(user=user)

    def perform_destroy(self, instance):
        """
        After deleting points from answer will be correctly deducted from exam.
        """
        instance.delete()
        instance.on_delete()
