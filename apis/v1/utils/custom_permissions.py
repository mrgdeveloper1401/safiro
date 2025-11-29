from rest_framework import permissions

from apis.v1.utils.custom_exceptions import AuthenticationFailed


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
