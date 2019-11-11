from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models as django_models
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models

from rest_framework.authtoken.models import Token

from surf.apps.core.models import UUIDModel


class TokenSession(AbstractBaseSession):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def get_session_store_class(cls):
        return TokenSessionStore


class TokenSessionStore(DBStore):

    @classmethod
    def get_model_class(cls):
        return TokenSession


class UserManager(BaseUserManager):
    """
    Implementation of User manager class.
    """

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Implements user creation by his `username`, `email`, `password`
        :param username:
        :param email:
        :param password:
        :param extra_fields:
        :return: created user
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Creates user by his `username`, `email`, `password`
        :param username:
        :param email:
        :param password:
        :param extra_fields:
        :return: created user
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates superuser by his `username`, `password`
        :param username:
        :param password:
        :param extra_fields:
        :return: created superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, None, password, **extra_fields)


class User(AbstractUser):
    """
    Unfortunately the Django User was replaced with a custom User for no particular reason.
    It's hard to remove the custom User, so we're going to be stuck with it for a while.
    """
    pass


class SurfConextAuth(UUIDModel):
    """
    Implementation of SURFconext User model.
    """

    # related Django user
    user = django_models.OneToOneField(User,
                                       related_name='surfconext_auth',
                                       on_delete=django_models.CASCADE)

    # field `preferred_username` of SURFconext user
    display_name = django_models.CharField(max_length=100)

    # field `edu_person_targeted_id` of SURFconext user
    external_id = django_models.CharField(max_length=255)

    # SURFconext user access token
    access_token = django_models.TextField()

    @staticmethod
    def update_or_create_user(display_name, external_id, access_token):
        """
        Updates SURFconext user data or creates new if the user does not exist.
        :param display_name: SURFconext user preferred username
        :param external_id: SURFconext user identifier
        :param access_token: SURFconext user access token
        :return: created/updated user instance
        """

        rv = SurfConextAuth.objects.filter(external_id=external_id).first()
        if rv:
            # SURFconext user DB instance exists, so we should only update it
            rv.access_token = access_token
            rv.display_name = display_name
            rv.save()

        else:
            # SURFconext user DB instance does not exist,
            # so we should create it
            u, _ = User.objects.get_or_create(
                username=external_id,
                defaults=dict(first_name=display_name))

            if getattr(u, "surfconext_auth", None):
                rv = u.surfconext_auth
                rv.external_id = external_id
                rv.display_name = display_name
                rv.access_token = access_token
                rv.save()

            else:
                rv = SurfConextAuth.objects.create(user_id=u.id,
                                                   external_id=external_id,
                                                   display_name=display_name,
                                                   access_token=access_token)

        return rv

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "SurfConext Auth"
        verbose_name_plural = "SurfConext Auths"
        ordering = ("display_name",)
