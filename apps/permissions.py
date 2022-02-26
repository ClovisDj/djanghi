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


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class AdminAccessPolicyPermission(BasePermission):
    def has_permission(self, request, view):
        from apps.profiles.models import User

        allowed_roles = getattr(view, 'allowed_admin_roles', [])
        if allowed_roles and request.user.is_admin:
            return isinstance(request.user, User) and request.user.has_min_one_role(*allowed_roles)

        return True


class RegularUserActionPermissions(BasePermission):
    def has_permission(self, request, view):
        from apps.profiles.models import User

        allowed_actions = getattr(view, 'regular_user_allowed_actions', [])

        if allowed_actions and isinstance(request.user, User) and not request.user.is_admin:
            return request.method.upper() in list(map(str.upper, allowed_actions))

        return True
