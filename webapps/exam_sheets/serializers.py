from rest_framework import serializers
from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile


class ExamSheetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ExamSheet
        fields = ('id', 'title', 'user', 'max_points')
        read_only_fields = ('max_points',)


class ExamSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Exam
        fields = ('id', 'achieved_points', 'exam_sheet', 'user', 'is_passed', 'percent_to_pass', 'is_checked')
        read_only_fields = ('achieved_points', 'is_passed', 'percent_to_pass', 'user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('exam_sheet', 'user'),
            )
        ]

    def validate_exam_sheet(self, exam_sheet):
        """
        Exam sheet must have more than 0 tasks to give user posibility to generate exam
        """
        is_task_assigned = exam_sheet.check_that_exam_sheet_has_any_task_assigned()
        if not is_task_assigned:
            raise serializers.ValidationError('These exam does not have any tasks assigned!')
        return exam_sheet

    def validate_is_checked(self, is_checked):
        if self.instance != is_checked and self.instance:
            are_task_checked = self.instance.check_that_all_answers_assigned_to_exam_are_checked()
            if not are_task_checked:
                raise serializers.ValidationError('Not all answers has been checked!')
        return is_checked


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'question', 'max_points', 'exam_sheet')

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('question', 'exam_sheet'),
            )
        ]

    def validate_exam_sheet(self, exam_sheet):
        """
        Tasks can be assigned only be exam_sheet owner.
        """
        exam_sheet = ExamSheet.objects.get(pk=exam_sheet.pk)
        current_user = self.context['request'].user.pk

        if exam_sheet.user.pk == current_user:
            return exam_sheet

        raise serializers.ValidationError('You are not these exam_sheet owner!')


class AnswerUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user', 'exam')
        read_only_fields = ('assigned_points', 'user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'task', 'exam')
            )
        ]


class AnswerExaminatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user', 'is_checked', 'exam')
        read_only_fields = ('user', 'answer', 'task', 'exam')

    def validate_assigned_points(self, assigned_points):
        """
        Examinator cant assign more points to answer than task max points
        """
        max_points = self.instance.task.max_points
        if assigned_points > max_points:
            raise serializers.ValidationError(
                f"Assigned points {assigned_points} can not be higher than max points {max_points}!"
            )
        return assigned_points


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'password', 'is_examinator')
