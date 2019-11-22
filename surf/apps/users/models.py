from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models as django_models
from django.contrib.sessions.models import Session
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from rest_framework.authtoken.models import Token

from surf.vendor.surfconext.models import DataGoalPermission
from surf.apps.communities.models import Community
from surf.apps.core.models import UUIDModel


class SessionToken(Token):
    sessions = models.ManyToManyField(Session, verbose_name=_("sessions"))


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

    def clear_all_data_goal_permissions(self):
        DataGoalPermission.objects.filter(user=self).delete()

    def get_all_user_data(self):
        communities = Community.objects.filter(team__user=self)
        if communities:
            communities = f"User is member of the following communities:<br>" \
                f"{'<br>'.join([community.name for community in communities])}<br>"
        else:
            communities = "User is not a member of any communities<br>"

        return f"================= START USER EXPORT =================<br>" \
            f"<br>"\
            f"================= USER ACCOUNT INFO =================<br>" \
            f"Username: {escape(self.username)}<br>" \
            f"First name: {escape(self.first_name) if self.first_name else 'unknown'}<br>" \
            f"Last name: {escape(self.last_name) if self.last_name else 'unknown'}<br>" \
            f"Email address: {escape(self.email) if self.email else 'unknown'}<br>" \
            f"Last login: {self.last_login}<br>" \
            f"Date joined: {self.date_joined}<br>" \
            f"================= USER ACCOUNT INFO =================<br>" \
            f"<br>"\
            f"================== USER COMMUNITIES ==================<br>" \
            f"{communities}" \
            f"================== USER COMMUNITIES ==================<br>" \
            f"<br>"\
            f"================== END USER EXPORT =================="


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
