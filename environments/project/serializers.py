from rest_framework import serializers


class PersonSerializer(serializers.Serializer):

    name = serializers.CharField()
    email = serializers.CharField(required=False)


class OrganisationSerializer(serializers.Serializer):

    name = serializers.CharField()


class ProjectSerializer(serializers.Serializer):

    name = serializers.CharField()


class LabelSerializer(serializers.Serializer):

    label = serializers.CharField()
