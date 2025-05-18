from rest_framework import permissions

class OwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Kiểm tra xem người dùng yêu cầu có phải là chủ sở hữu của đối tượng này không
        return request.user == obj


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 0


class ExerciserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 1

class CoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 2