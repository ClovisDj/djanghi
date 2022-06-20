from .base import ENVIRONMENT, DEBUG, ENV


DEFAULT_RENDERER_CLASSES = (
    'rest_framework_json_api.renderers.JSONRenderer',
)

REST_FRAMEWORK = {
    'PAGE_SIZE': ENV.int('PAGE_SIZE'),
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'apps.extensions.backend.CustomJsonApiPageNumberPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_json_api.parsers.JSONParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.custom_authentications.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'apps.permissions.AdminAccessPolicyPermission',
        'apps.permissions.RegularUserActionPermissions',
        'apps.permissions.RegularUserNestedRoutePermission',
        'apps.permissions.NestedUserRoutePermission',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_json_api.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'apps.extensions.backend.AssociationFilterBackend',
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework_json_api.filters.OrderingFilter',
        'rest_framework_json_api.django_filters.DjangoFilterBackend',

    ),
    'SEARCH_PARAM': 'search',

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'COERCE_DECIMAL_TO_STRING': False,
}

if ENVIRONMENT.lower() == 'local' and DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework_json_api.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
