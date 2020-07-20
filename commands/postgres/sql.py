from django.conf import settings
from django.contrib.auth.hashers import make_password


def insert_django_user_statement(username, raw_password, is_edushare=False):
    settings.configure()
    hash_password = make_password(raw_password)
    escaped_password = hash_password.replace("$", r"\$")
    user_table = "users_user" if is_edushare else "auth_user"
    return (
        f'INSERT INTO {user_table} '
        f'(password, is_superuser, is_staff, is_active, username, first_name, last_name, email, date_joined) '
        f'VALUES (\'{escaped_password}\', true, true, true, \'{username}\', \'\', \'\', \'\', NOW())'
    )
