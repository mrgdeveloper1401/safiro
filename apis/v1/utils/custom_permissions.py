from rest_framework import permissions

from apis.v1.utils.custom_exceptions import AuthenticationFailed


class AsyncRemoveAuthenticationPermissions(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise AuthenticationFailed()
        return True
