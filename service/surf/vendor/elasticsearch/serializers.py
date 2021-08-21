import boto3
from botocore.exceptions import ClientError
import os

from django.conf import settings
from rest_framework import serializers

from project.serializers import PersonSerializer, OrganisationSerializer, LabelSerializer, ProjectSerializer


PREVIEW_SMALL = "preview-200x150.png"
PREVIEW_ORIGINAL = "preview.png"
s3_client = boto3.client("s3")


def get_preview_absolute_uri(preview_path, preview_type, duration=7200):
    """
    Generate a presigned URL to share the S3 object where this resource is stored.
    If the application is not connected to S3 it simply returns a local path.
    """
    if preview_path is None:
        return None

    if settings.AWS_HARVESTER_BUCKET_NAME is None:
        return os.path.join(settings.MEDIA_URL, "harvester", preview_path, preview_type)

    # Generate a presigned URL for the S3 object
    lookup_params = {
        "Bucket": settings.AWS_HARVESTER_BUCKET_NAME,
        "Key": f"{preview_path}/{preview_type}"
    }
    try:
        return s3_client.generate_presigned_url("get_object", Params=lookup_params, ExpiresIn=duration)
    except ClientError:
        return None


class BaseSearchResultSerializer(serializers.Serializer):

    external_id = serializers.CharField()
    doi = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    url = serializers.URLField()
    title = serializers.CharField()
    description = serializers.CharField()
    language = serializers.CharField()
    copyright = serializers.CharField()


class EdusourcesSearchResultSerializer(BaseSearchResultSerializer):

    files = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        )
    )
    publish_datetime = serializers.CharField(source="publisher_date", allow_blank=True, allow_null=True)
    educationallevels = serializers.ListField(child=serializers.CharField(), source="lom_educational_levels")
    disciplines = serializers.ListField(child=serializers.CharField())
    themes = serializers.ListField(child=serializers.CharField(), default=[])
    source = serializers.CharField(source="harvest_source")
    ideas = serializers.ListField(child=serializers.CharField())
    technical_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    keywords = serializers.ListField(child=serializers.CharField())
    publishers = serializers.ListField(child=serializers.CharField())
    authors = serializers.ListField(child=serializers.CharField())
    has_parts = serializers.ListField(child=serializers.CharField())
    is_part_of = serializers.ListField(child=serializers.CharField())

    preview_path = serializers.CharField(default=None, allow_blank=True, allow_null=True)
    preview_thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()

    def get_preview_thumbnail_url(self, obj):
        return get_preview_absolute_uri(obj["preview_path"], PREVIEW_SMALL)

    def get_preview_url(self, obj):
        return get_preview_absolute_uri(obj["preview_path"], PREVIEW_ORIGINAL)


class RelationSerializer(serializers.Serializer):

    authors = PersonSerializer(many=True)
    keywords = LabelSerializer(many=True)
    parties = OrganisationSerializer(many=True)
    themes = LabelSerializer(many=True)
    projects = ProjectSerializer(many=True)
    children = serializers.ListField(child=serializers.CharField())
    parents = serializers.ListField(child=serializers.CharField())


class NPPOSearchResultSerializer(BaseSearchResultSerializer):

    type = serializers.CharField(source="technical_type")
    published_at = serializers.CharField(source="publisher_date", allow_blank=True, allow_null=True)
    research_object_type = serializers.CharField()
    relations = RelationSerializer()


SearchResultSerializer = None
if settings.PROJECT == "edusources":
    SearchResultSerializer = EdusourcesSearchResultSerializer
elif settings.PROJECT == "nppo":
    SearchResultSerializer = NPPOSearchResultSerializer
