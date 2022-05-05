from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.settings import api_settings


class CustomJWTAuthentication(authentication.JWTAuthentication):

    def authenticate(self, request):
        try:
            header = self.get_header(request)
            raw_token = self.get_raw_token(header)
            validated_token = self.get_validated_token(raw_token)

            return self.get_user(validated_token), validated_token
        except (AttributeError, AuthenticationFailed):
            return None

    def get_validated_token(self, raw_token):
        """
        Override this method so that we do not return 500 to the client instead we return 403
        """
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError:
                pass

        raise AuthenticationFailed()
