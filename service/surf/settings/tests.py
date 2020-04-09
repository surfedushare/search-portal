from .local import *

INSTALLED_APPS += [
    'test_without_migrations'
]
TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

NOSE_ARGS = ['--nocapture',
             '--nologcapture',
             ]
