from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser

from apps.utils import extract_user_from_request_token


class CustomAuthenticationMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        super().process_request(request)

        if isinstance(request.user, AnonymousUser):
            user_from_token = extract_user_from_request_token(request)
            if user_from_token:
                request.user = user_from_token
