from rest_framework import permissions

from apis.v1.utils.custom_exceptions import AuthenticationFailed, NotActiveAccount, NotDriverException


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


class IsActiveDriverAccount(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_driver:
            raise NotDriverException()
        return True
