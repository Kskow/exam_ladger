from django.urls import path
from . import views
from webapps.exam_sheets.views import ExamSheetViewSet, TaskViewSet, ExamViewSet, AnswerViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter


urlpatterns = [
    path('health_check', views.health_check, name='health_check'),
]


router = ExtendedSimpleRouter()
# Nested urls
exam_sheets_routes = router.register(r'exam_sheets', ExamSheetViewSet, base_name='exam_sheet')
exam_sheets_routes.register(r'tasks', TaskViewSet, 'exam_sheets-task', parents_query_lookups=['exam_sheet'])

(
    router.register(r'exams', ExamViewSet, base_name='exam')
          .register(r'tasks',
                    TaskViewSet,
                    base_name='exams-task',
                    parents_query_lookups=['exam_sheet'])
          .register(r'answers',
                    AnswerViewSet,
                    base_name='exams-tasks-answer',
                    parents_query_lookups=['task', 'exam_sheet__task'])
)

urlpatterns += router.urls



