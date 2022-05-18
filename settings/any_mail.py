from .base import ENV

EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'

ANYMAIL = {
    'SENDGRID_API_KEY': ENV.str('SENDGRID_API_KEY')
}

DEFAULT_FROM_EMAIL = ENV.str('DEFAULT_FROM_EMAIL')
