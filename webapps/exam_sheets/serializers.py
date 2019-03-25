from rest_framework import serializers
from webapps.exam_sheets.models import ExamSheet, Exam, Task, Answer, UserProfile


class ExamSheetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ExamSheet
        fields = ('id', 'title', 'user', 'max_points')
        read_only_fields = ('max_points',)
    # TODO: max points assigned only with tasks, set default to tasks points
    # TODO: max points can't be lower than 0


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
    # TODO: can't create instance if 0 task assigned to exam_sheet
    # TODO: not possible to achieve more points than max exam_sheet points
    # TODO: archieved points can't be lower than 0

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
    # TODO: max_points can't be lower than 0
    def create(self, validated_data):
        exam_sheet = ExamSheet.objects.get(pk=validated_data['exam_sheet'].pk)
        exam_sheet.max_points += validated_data['max_points']
        exam_sheet.save()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        exam_sheet_id = self.instance.exam_sheet_id

        actual_max_points = self.instance.max_points
        self.instance.actual_max_points = self.validated_data['max_points']

        exam_sheet = ExamSheet.objects.get(pk=exam_sheet_id)
        exam_sheet.max_points = exam_sheet.max_points - actual_max_points + self.instance.actual_max_points
        exam_sheet.save()

        instance.save()
        return instance


class AnswerUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    task = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )
    exam = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user', 'exam')
        read_only_fields = ('assigned_points', 'task', 'exam')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'task', 'exam')
            )
        ]

    def to_internal_value(self, data):
        data = data.copy()
        request = self.context['request']
        task_id = request.parser_context['kwargs']['parent_lookup_task']
        task = Task.objects.get(pk=task_id)
        data['task'] = task

        exam_sheet = ExamSheet.objects.get(pk=task.exam_sheet.pk)
        exam = Exam.objects.get(exam_sheet=exam_sheet, user=self.context['request'].user)
        data['exam'] = exam
        return data


class AnswerExaminatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'answer', 'assigned_points', 'task', 'user')
        read_only_fields = ('user', 'answer', 'task')
    # TODO: can't assigne points lower than 0

    def validate(self, attrs):
        max_points = self.instance.task.max_points
        points = attrs['assigned_points']

        if points > max_points:
            raise serializers.ValidationError(
                f"Assigned points {points} can not be higher than max points {max_points}!"
            )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        exam_id = self.instance.exam_id

        actual_answer_points = self.instance.assigned_points
        self.instance.assigned_points = self.validated_data['assigned_points']

        exam = Exam.objects.get(pk=exam_id)
        exam.achieved_points = exam.achieved_points - actual_answer_points + self.instance.assigned_points
        exam.save()

        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'password', 'is_examinator')
