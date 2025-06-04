from rest_framework import permissions
#
# class OwnerPermission(permissions.IsAuthenticated):
#     def has_object_permission(self, request, view, obj):
#         # Kiểm tra xem người dùng yêu cầu có phải là chủ sở hữu của đối tượng này không
#         return request.user == obj

# class OwnerPermission(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user

class OwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Nếu object là chính user
        if isinstance(obj, request.user.__class__):
            return obj == request.user
        # Nếu object có thuộc tính user
        return hasattr(obj, 'user') and obj.user == request.user


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 0

class Exerciser_Self_HelpPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 1

class Exerciser_With_CoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 2

class CoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 3