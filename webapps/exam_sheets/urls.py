from django.urls import path
from . import views
from webapps.exam_sheets.views import ExamSheetViewSet, TaskViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter


urlpatterns = [
    path('health_check', views.health_check, name='health_check'),
]


router = ExtendedSimpleRouter()
# Nested urls
exam_sheets_routes = router.register(r'exam_sheets', ExamSheetViewSet, base_name='exam_sheet')
exam_sheets_routes.register(r'tasks', TaskViewSet, 'exam_sheets-task', parents_query_lookups=['exam_sheet'])
urlpatterns += router.urls



