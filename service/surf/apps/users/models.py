from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from rest_framework.authtoken.models import Token

from surf.vendor.surfconext.models import DataGoalPermission
from surf.apps.communities.models import Community


class SessionToken(Token):
    sessions = models.ManyToManyField(Session, verbose_name=_("sessions"))


class User(AbstractUser):

    def clear_all_data_goal_permissions(self):
        DataGoalPermission.objects.filter(user=self).delete()

    def get_all_user_data(self):
        communities = Community.objects.filter(team__user=self)
        if communities:
            communities = f"User is member of the following communities:<br>" \
                f"{'<br>'.join([escape(community.name) for community in communities])}<br>"
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
