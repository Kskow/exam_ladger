from rest_framework import serializers
from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile


class ExamSheetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ExamSheet
        fields = ('id', 'title', 'user')


class ExamSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Exam
        fields = ('id', 'achieved_points', 'exam_sheet', 'user', 'is_passed')
        read_only_fields = ('achieved_points', 'is_passed')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('exam_sheet', 'user'),
            )
        ]


class TaskSerializer(serializers.ModelSerializer):
    # exam_sheet = serializers.SlugRelatedField(
    #     queryset=ExamSheet.objects.all(),
    #     slug_field='id'
    # )
    class Meta:
        model = Task
        fields = ('id', 'question', 'max_points', 'exam_sheet')

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('question', 'exam_sheet'),
            )
        ]


class AnswerUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user')
        read_only_fields = ('assigned_points', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'task'),
            )
        ]


class AnswerExaminatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user')
        read_only_fields = ('user', 'answer', 'task')

    def validate(self, attrs):
        max_points = self.instance.task.max_points
        points = attrs['assigned_points']

        if points > max_points:
            raise serializers.ValidationError(
                f"Assigned points {points} can not be higher than max points {max_points}!"
            )
        return super().validate(attrs)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'password', 'is_examinator')
