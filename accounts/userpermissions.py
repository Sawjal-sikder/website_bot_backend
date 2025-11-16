from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    Allow only superuser to update.
    """
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            return request.user.is_superuser
        return True   # Allow GET for everyone who has normal permissions
