import environ

ENV = environ.Env()

log_level = ENV.str('DJANGO_LOG_LEVEL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'timestamp': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': ENV.str('LOG_FILE_PATH'),
            'formatter': 'timestamp',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': True,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': ENV.str('DJANGO_LOG_LEVEL'),
            'propagate': True,
        },
    },
}