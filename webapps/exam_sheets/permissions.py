from rest_framework import permissions
from webapps.exam_sheets.models import ExamSheet


class IsExamiantorOrSheetOwner(permissions.BasePermission):
    """
    Check that current user is examinator and sheet owner if he try to retrive/edit/delete sheet
    """
    message = 'You are not allowed to see these page!'

    def has_permission(self, request, view):
        return request.user.is_examinator

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user and request.user.is_examinator

class IsExaminatorAndTaskOwner(permissions.BasePermission):
    """
    Permission which allows Task owner to edit/delete/retrive
    """
    message = 'You are not allowed to enter here!'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            exam_sheet_id = request.data['exam_sheet']
            exam_sheet = ExamSheet.objects.get(pk=exam_sheet_id)
            return exam_sheet.user == request.user
        except Exception:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.id == obj.exam_sheet.user.pk

class IsExaminatorOrAnswerOwner(permissions.BasePermission):

    message = 'You are not allowed to enter here!'

    def has_object_permission(self, request, view, obj):
        if request.user.is_examinator:
            return True
        if request.user.id != obj.user.pk:
            return False
        return True

