from webapps.exam_sheets.models import UserProfile, ExamSheet, Answer, Exam
from django.urls import reverse

# URL'S


def exam_sheet_url(sheet_id):
    if sheet_id == '':
        return 'http://testserver/api/exam_sheets/'
    return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/'

def exam_sheet_tasks_url(sheet_id, task_id):
    if task_id == '':
        return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/tasks/'
    return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/tasks/' + str(task_id) + '/'



