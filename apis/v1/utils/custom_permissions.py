from rest_framework import permissions

from apis.v1.utils.custom_exceptions import AuthenticationFailed, NotDriverException


class AsyncRemoveAuthenticationPermissions(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise AuthenticationFailed()
        return True


class SyncRemoveAuthenticationPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise AuthenticationFailed()
        return True


class NotAuthenticated(permissions.BasePermission):
    message = "کاربر لاگین شده نمیتواند دسترسی پیدا کند"

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsDriverAccount(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_driver:
            raise NotDriverException()
        return True


class IsOwnerProductComment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.id != obj.user.id:
            return False
        return True
