from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(AbstractUser):
    is_examinator = models.BooleanField(default=False)


class ExamSheet(models.Model):
    title = models.CharField(max_length=100, blank=False, unique=True)
    max_points = models.IntegerField(default=0)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def update_exam_sheet_achieved_points(self, actual_answer_points, updated_answer_points):
        """
        Updating achieved points which depends from answer.assigned_points updates

        """
        self.max_points = self.max_points - actual_answer_points + updated_answer_points
        self.save()

    def check_that_exam_sheet_has_any_task_assigned(self):
        if len(self.tasks.all()) <= 0:
            return False
        return True


class Exam(models.Model):
    IS_PASSED_CHOICES = (
        ('PASSED', 'Passed'),
        ('NOT PASSED', 'Not passed'),
        ('PENDING', 'pending')
    )

    achieved_points = models.IntegerField(default=0)
    is_passed = models.CharField(max_length=30, choices=IS_PASSED_CHOICES, default='PENDING')
    percent_to_pass = models.IntegerField(default=0,
                                          validators=[
                                              MinValueValidator(0),
                                              MaxValueValidator(100)
                                            ]
                                          )
    is_checked = models.BooleanField(default=False)
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def update_exam_achieved_points(self, actual_answer_points, updated_answer_points):
        """
        Updating achieved points which depends from answer.assigned_points updates

        """
        self.achieved_points = self.achieved_points - actual_answer_points + updated_answer_points
        self.save()

    def is_exam_passed(self):
        """
        Checking that percents from exam.achieved_points/exam_sheet.max_points are higher from percent_to_pass
        and change properly is_passed field if all answers are already checked
        """

        achieved_percents = 100 * (self.achieved_points/self.exam_sheet.max_points)
        if achieved_percents > 0 and achieved_percents > self.percent_to_pass:
            self.is_passed = 'PASSED'
            return self.save()
        self.is_passed = 'NOT PASSED'
        self.save()

    def check_that_all_answers_assigned_to_exam_are_checked(self):
        """
        If examinator will try to update is_checked to True and not all answers will have is_checked=True than
        properly error will be shown, else percent_to_pass will be correctly calculated and is_passed status will
        be changed.
        """
        for answer in self.answers.all():
            if not answer.is_checked:
                return False
        return True
        # self.is_exam_passed() -> do perform_update()

    def on_update(self):
        """
        Actions performing after updating, when is_checked is set to True than check that user pass exam
        """
        if self.is_checked:
            self.is_exam_passed()


class Task(models.Model):
    question = models.CharField(max_length=150)
    max_points = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    exam_sheet = models.ForeignKey(ExamSheet, on_delete=models.CASCADE, related_name='tasks')

    def points_before_update(self):
        """
        Get points before .save() while updating
        """
        task_before_update = Task.objects.get(pk=self.pk)
        return task_before_update.max_points

    def on_create(self, points_to_add):
        """
        Add assigned to task max_points to Exam Sheet
        """
        self.exam_sheet.update_exam_sheet_achieved_points(0, points_to_add)

    def on_update(self, points_to_update):
        """
        Re-assign points from task to Exam Sheet
        """
        self.exam_sheet.update_exam_sheet_achieved_points(self.exam_sheet.max_points, points_to_update)

    def on_delete(self):
        """
        Deduct points from sheet and exam before deleting Task
        """

        self.exam_sheet.update_exam_sheet_achieved_points(self.max_points, 0)
        for answer in Answer.objects.filter(task=self):
            exam = Exam.objects.get(pk=answer.exam.pk)
            exam.update_exam_achieved_points(answer.assigned_points, 0)
        return


class Answer(models.Model):
    answer = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tasks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='answers')
    assigned_points = models.IntegerField(default=0,
                                          validators=[
                                              MinValueValidator(0),
                                            ]
                                          )
    is_checked = models.BooleanField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def points_before_update(self):
        """
        Get points before .save() while updating
        :return:
        """
        answer_before_update = Answer.objects.get(pk=self.pk)
        return answer_before_update.assigned_points

    def on_examinator_update(self, points_before_update, points_to_update):
        """
        On update check that current user is examiantor than assign/reassign points to exam
        """
        return self.exam.update_exam_achieved_points(points_before_update, points_to_update)

    def on_delete(self):
        """
        Deduct points from exam when answer is deleted.
        """
        self.exam.update_exam_achieved_points(self.assigned_points, 0)
        return
