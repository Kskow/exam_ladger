# URL'S


def exam_sheet_url(sheet_id):
    if sheet_id == '':
        return 'http://testserver/api/exam_sheets/'
    return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/'


def exam_sheet_tasks_url(sheet_id, task_id):
    if task_id == '':
        return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/tasks/'
    return 'http://testserver/api/exam_sheets/' + str(sheet_id) + '/tasks/' + str(task_id) + '/'


def exam_url(exam_id):
    if exam_id == '':
        return 'http://testserver/api/exams/'
    return 'http://testserver/api/exams/' + str(exam_id) + '/'


def exam_tasks_url(exam_id, task_id):
    if task_id == '':
        return 'http://testserver/api/exams/' + str(exam_id) + '/tasks/'
    return 'http://testserver/api/exams/' + str(exam_id) + '/tasks/' + str(task_id) + '/'


def answers_url(exam_id, task_id, answer_id):
    if answer_id == '':
        return 'http://testserver/api/exams/' + str(exam_id) + '/tasks/' + str(task_id) + '/answers/'
    return 'http://testserver/api/exams/' + str(exam_id) + '/tasks/' + str(task_id) + '/answers/' + str(answer_id) + '/'
