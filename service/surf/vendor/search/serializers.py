import os
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse

from django.conf import settings
from rest_framework import serializers

from project.serializers import PersonSerializer, OrganisationSerializer, LabelSerializer, ProjectSerializer


PREVIEW_SMALL = "preview-200x150.png"
PREVIEW_ORIGINAL = "preview.png"
s3_client = boto3.client("s3")


def get_preview_absolute_uri(url, duration=7200):
    """
    Generate a presigned URL to share the S3 object where this resource is stored.
    If the application is not connected to S3 it simply returns a local path.
    """
    if url is None:
        return None

    if settings.AWS_HARVESTER_BUCKET_NAME is None:
        if "s3.amazonaws.com" not in url:
            return url
        return "http://localhost:8000/" + os.path.join("media", "harvester", urlparse(url).path.strip("/"))

    # Generate a presigned URL for the S3 object
    lookup_params = {
        "Bucket": settings.AWS_HARVESTER_BUCKET_NAME,
        "Key": urlparse(url).path.strip("/")
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
    video = serializers.DictField()
    harvest_source = serializers.CharField()


class EdusourcesSearchResultSerializer(BaseSearchResultSerializer):

    files = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        )
    )
    published_at = serializers.CharField(source="publisher_date", allow_blank=True, allow_null=True)
    lom_educational_levels = serializers.ListField(child=serializers.DictField())
    studies = serializers.ListField(child=serializers.DictField())
    disciplines = serializers.ListField(child=serializers.CharField(), default=[],
                                        source="learning_material_disciplines_normalized")
    ideas = serializers.ListField(child=serializers.CharField())
    technical_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    keywords = serializers.ListField(child=serializers.CharField())
    publishers = serializers.ListField(child=serializers.CharField())
    authors = serializers.ListField(child=serializers.CharField())
    has_parts = serializers.ListField(child=serializers.CharField())
    is_part_of = serializers.ListField(child=serializers.CharField())
    consortium = serializers.CharField(allow_blank=True, allow_null=True)

    previews = serializers.SerializerMethodField()

    view_count = serializers.IntegerField()
    applaud_count = serializers.IntegerField()
    avg_star_rating = serializers.IntegerField()
    count_star_rating = serializers.IntegerField()

    def get_previews(self, obj):
        previews = obj.get("previews", {})
        return {
            image_key: get_preview_absolute_uri(url)
            for image_key, url in previews.items()
        }


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
    extension = serializers.DictField()
    relations = RelationSerializer()


SearchResultSerializer = None
if settings.PROJECT == "edusources":
    SearchResultSerializer = EdusourcesSearchResultSerializer
elif settings.PROJECT == "nppo":
    SearchResultSerializer = NPPOSearchResultSerializer
