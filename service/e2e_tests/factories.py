import factory
from surf.apps.users.models import User
from surf.apps.communities.models import Community, CommunityDetail, Team
from surf.statusenums import PublishStatus
from surf.apps.materials.models import Collection, Material


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
