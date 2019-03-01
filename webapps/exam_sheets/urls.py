from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('health_check', views.health_check, name='health_check'),
    path('exam_sheets/', views.ExamSheetCreate.as_view(), name='exam_sheets'),
    path('exam_sheets/<int:pk>/', views.ExamSheetDetail.as_view(), name='detail_view'),
    path('task/', views.TaskCreate.as_view(), name='task'),
    path('task/<int:pk>/', views.TaskDetail.as_view()),
    path('answer/', views.AnswerCreate.as_view(), name='answer'),
    path('answer/<int:pk>/', views.AnswerDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('exams/', views.ExamDetail.as_view(), name='exams'),
    path('exams/<int:pk>', views.ExamDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)


