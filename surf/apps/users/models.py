from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models as django_models

from surf.apps.core.models import UUIDModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, None, password, **extra_fields)


class User(AbstractUser):
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("username",)


class SurfConextAuth(UUIDModel):
    user = django_models.ForeignKey(User,
                                    related_name='surfconext_auth',
                                    on_delete=django_models.CASCADE)

    display_name = django_models.CharField(max_length=100)
    external_id = django_models.CharField(max_length=255)
    access_token = django_models.CharField(max_length=255)

    @staticmethod
    def update_or_create_user(display_name, external_id, access_token):
        rv = SurfConextAuth.objects.filter(external_id=external_id).first()
        if not rv:
            u, _ = User.objects.get_or_create(
                username=external_id,
                defaults=dict(username=external_id, first_name=display_name))

            rv = u.surfconext_auth
            if rv:
                rv.external_id = external_id
                rv.display_name = display_name
                rv.access_token = access_token
                rv.save()

            else:
                rv = SurfConextAuth.objects.create(user_id=u.id,
                                                   external_id=external_id,
                                                   display_name=display_name,
                                                   access_token=access_token)
        else:
            rv.access_token = access_token
            rv.display_name = display_name
            rv.save()

        return rv

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "SurfConext Auth"
        verbose_name_plural = "SurfConext Auths"
        ordering = ("display_name",)
