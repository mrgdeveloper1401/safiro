from rest_framework import permissions

from apis.v1.utils.custom_exceptions import AuthenticationFailed, NotActiveAccount


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


class IsActiveAccount(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.is_active is False:
            raise NotActiveAccount()
        return True
