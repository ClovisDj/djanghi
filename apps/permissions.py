from rest_framework.permissions import BasePermission

from apps.utils import is_valid_uuid


class IsNesterUserRouteMixin:
    @staticmethod
    def is_user_nested_route(request):
        return 'user_pk' in request.parser_context['kwargs']


class IsUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.profiles.models import User

        if isinstance(request.user, User) and \
                request.user == obj and \
                request.method.lower() != 'delete':
            return True

        if request.user.is_admin:
            return True

        return False


class IsFullAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.profiles.models import User

        if isinstance(request.user, User):
            return request.user.is_full_admin

        return False


class AdminAccessPolicyPermission(BasePermission):
    def has_permission(self, request, view):
        from apps.profiles.models import User

        allowed_roles = getattr(view, 'allowed_admin_roles', [])
        if allowed_roles and request.user.is_admin:
            return (
                (isinstance(request.user, User) and request.user.has_min_one_role(*allowed_roles)) or
                (request.method.lower() == 'get')
            )

        return True


class RegularUserActionPermissions(BasePermission):
    def has_permission(self, request, view):
        from apps.profiles.models import User

        allowed_actions = getattr(view, 'regular_user_allowed_actions', [])

        if isinstance(request.user, User) and not request.user.is_admin:
            if not allowed_actions:
                return False

            if allowed_actions:
                return request.method.upper() in list(map(str.upper, allowed_actions))

        return True


class NestedUserRoutePermission(IsNesterUserRouteMixin, BasePermission):

    def has_permission(self, request, view):
        from apps.profiles.models import User

        user_pk = request.parser_context.get('kwargs', {}).get('user_pk')
        if isinstance(request.user, User) and self.is_user_nested_route(request) and is_valid_uuid(user_pk):
            return request.user.association.users.filter(id=user_pk).exists()

        return True


class RegularUserNestedRoutePermission(IsNesterUserRouteMixin, BasePermission):

    def has_permission(self, request, view):
        from apps.profiles.models import User

        if isinstance(request.user, User) and not request.user.is_admin and self.is_user_nested_route(request):
            return request.parser_context['kwargs']['user_pk'] == str(request.user.id)

        return True


class PasswordResetPermission(BasePermission):
    def has_permission(self, request, view):
        from apps.profiles.models import User

        if request.method.lower() != 'post':
            return False

        association_label = request.data.get('association_label')
        email = request.data.get('email')
        if not association_label or not email:
            return False

        user_qs = User.objects.get_actives().filter(
            association__label__iexact=association_label,
            email__iexact=email,
            is_registered=True
        )

        if not user_qs.exists():
            return False

        return True
