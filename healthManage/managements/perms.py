from rest_framework import permissions

class OwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        obj = view.get_object()  # Đối tượng bạn muốn kiểm tra quyền
        # Kiểm tra nếu request.user là đối tượng của chính người dùng hoặc người dùng khác
        return super().has_permission(request, view) and obj == request.user

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