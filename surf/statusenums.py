from django_enumfield import enum


class PublishStatus(enum.Enum):  # NB: this enum has a hard copy in the webapp
    DRAFT = 0
    REVIEW = 1
    PUBLISHED = 2

    __labels__ = {
        DRAFT: "Draft",
        REVIEW: "Review",
        PUBLISHED: "Published",
    }


