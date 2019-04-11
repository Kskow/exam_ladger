# URL'S


def exam_sheet_url(sheet_id):
    if sheet_id == '':
        return 'http://testserver/api/exam_sheets/'
    return f"http://testserver/api/exam_sheets/{sheet_id}/"


def exam_sheet_tasks_url(sheet_id, task_id):
    if task_id == '':
        return f"http://testserver/api/exam_sheets/{sheet_id}/tasks/"
    return f"http://testserver/api/exam_sheets/{sheet_id}/tasks/{task_id}/"


def exam_url(exam_id):
    if exam_id == '':
        return 'http://testserver/api/exams/'
    return f"http://testserver/api/exams/{exam_id}/"


def exam_tasks_url(exam_id, task_id):
    if task_id == '':
        return f"http://testserver/api/exams/{exam_id}/tasks/"
    return f"http://testserver/api/exams/{exam_id}/tasks/{task_id}/"


def answers_url(exam_id, task_id, answer_id):
    if answer_id == '':
        return f"http://testserver/api/exams/{exam_id}/tasks/{task_id}/answers/"
    return f"http://testserver/api/exams/{exam_id}/tasks/{task_id}/answers/{answer_id}/"
