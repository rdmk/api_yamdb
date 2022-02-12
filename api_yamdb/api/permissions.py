from rest_framework import permissions


class AuthorStaffOrReadOnly(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in 'GET'
            or request.user.is_moderator or request.user.is_admin
            or request.user == obj.author
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Требуются права администратора'

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_superuser)
