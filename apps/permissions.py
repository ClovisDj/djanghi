from rest_framework.permissions import BasePermission


class IsUserOrFullAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.profiles.models import User

        if isinstance(request.user, User) and \
                request.user == obj and \
                request.method.lower() != 'delete':
            return True

        if request.user.is_full_admin:
            return True

        return False
