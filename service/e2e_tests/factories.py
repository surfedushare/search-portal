import factory
from surf.apps.users.models import User
from surf.apps.communities.models import Community, CommunityDetail, Team
from surf.statusenums import PublishStatus
from surf.apps.materials.models import Collection, Material
from surf.vendor.surfconext.models import DataGoalPermission, DataGoal, PrivacyStatement

from django.utils.timezone import now


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'john{}'.format(n))
    first_name = 'John'
    last_name = 'Doe'
    email = factory.Sequence(lambda n: 'test{}@surf.com'.format(n))
    is_superuser = True
    is_staff = True
    is_active = True


class PrivacyStatementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrivacyStatement

    name = "Communities"
    is_active = True
    en = "English text"
    nl = "Nederlandse text"
    created_at = "2019-12-06T13:23:59.167Z",
    modified_at = "2020-04-02T11:42:57.279Z"


class DataGoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DataGoal

    type = 'Communities'
    statement = factory.SubFactory(PrivacyStatementFactory)
    is_active = True
    priority = 1
    is_notification_only = False
    is_after_login = True
    more_info_route = 'privacy'
    en_title = 'Communities'
    nl_title = 'Communities'
    en_description = 'If you create an account by logging in with SURFconext a unique identifier, your email address ' \
                     'and your SURFconext group memberships will also be used. The search portal uses this ' \
                     'information to determine which communities you can manage.'
    nl_description = 'Als je een account aanmaakt door in te loggen met SURFconext  dan verwerken we een unieke ' \
                     'identifier, je e-mailadres en je groepslidmaatschappen van SURFconext. Het zoekportaal bepaalt ' \
                     'met die informatie welke communities je beheert.'


class DataGoalPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DataGoalPermission

    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(DataGoalFactory)
    recorded_at = now()
    is_allowed = True
    is_retained = True


class CommunityDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommunityDetail

    class Params:
        english = factory.Trait(
            language_code="EN",
            title="Ethics",
            description="English version of ethics community"
        )
        dutch = factory.Trait(
            language_code="NL",
            title="Ethiek",
            description="Nederlandse versie van ethiek community"
        )


class CommunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Community

    name = 'Ethiek'
    external_id = factory.Sequence(lambda n: 'testgroup{}'.format(n))
    publish_status = PublishStatus.PUBLISHED

    dutch_details = factory.RelatedFactory(
        CommunityDetailFactory,
        factory_related_name="community",
        dutch=True
    )

    english_details = factory.RelatedFactory(
        CommunityDetailFactory,
        factory_related_name="community",
        english=True
    )


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    user = factory.SubFactory(UserFactory)
    community = factory.SubFactory(CommunityFactory)
    team_id = factory.SelfAttribute('community.external_id')


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    title_nl = "Handige leermaterialen"
    title_en = "Useful materials"
    publish_status = PublishStatus.PUBLISHED

    @factory.post_generation
    def communities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for community in extracted:
                self.communities.add(community)


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    external_id = "external:id"
    title = "De kunst van materiaal"
    description = "Alles over het maken van kwalitatieve materialen"
    material_url = "https://www.surf.nl/"
    applaud_count = 2
    star_4 = 1
    view_count = 104

    @factory.post_generation
    def collections(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for collection in extracted:
                self.collections.add(collection)
