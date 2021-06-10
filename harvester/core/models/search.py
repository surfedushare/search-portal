from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import make_aware
from elasticsearch.helpers import streaming_bulk
from rest_framework import serializers

from surfpol.configuration import create_elastic_search_index_configuration
from core.models import DatasetVersion
from core.utils.elastic import get_es_client


class ElasticIndex(models.Model):

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.ELASTICSEARCH_ANALYSERS.items())
    dataset_version = models.ForeignKey(DatasetVersion, related_name="indices", on_delete=models.SET_NULL, null=True)
    configuration = models.JSONField(blank=True)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    pushed_at = models.DateTimeField(null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = get_es_client()

    def delete(self, using=None, keep_parents=False):
        if self.remote_exists:
            self.client.indices.delete(index=self.remote_name)
        super().delete(using=using, keep_parents=keep_parents)

    @property
    def remote_name(self):
        if not self.id:
            raise ValueError("Can't get the remote name for an unsaved object")
        return slugify(f"{self.name}-{self.language}")

    @property
    def remote_exists(self):
        if not self.id:
            raise ValueError("Can't check for existence with an unsaved object")
        return self.client.indices.exists(self.remote_name)

    def push(self, elastic_documents, recreate=True, request_timeout=300):  # why is the elastic cluster usually slow?
        if not self.id:
            raise ValueError("Can't push index with unsaved object")

        current_time = make_aware(datetime.now())
        remote_name = self.remote_name
        remote_exists = self.remote_exists

        # Some preparation based on remote state as well as command line options
        if remote_exists and recreate:
            self.client.indices.delete(index=remote_name)
        if remote_exists and recreate or not remote_exists:
            if self.configuration is None:
                self.configuration = self.get_index_config(self.language)
            self.client.indices.create(
                index=remote_name,
                body=self.configuration
            )
        if recreate:
            self.error_count = 0

        # Actual push of docs to ES
        errors = []
        for is_ok, result in streaming_bulk(self.client, elastic_documents, index=remote_name,
                                            chunk_size=100, yield_ok=False, raise_on_error=False,
                                            request_timeout=request_timeout):
            if not is_ok:
                self.error_count += 1
                errors.append(result)

        self.pushed_at = current_time
        self.save()
        return errors

    def promote_to_latest(self):
        latest_alias = "latest-" + self.language
        if self.client.indices.exists_alias(name=latest_alias):
            self.client.indices.delete_alias(index="_all", name=latest_alias)
        self.client.indices.put_alias(index=self.remote_name, name=latest_alias)

    def clean(self):
        if not self.name:
            self.name = f"{self.dataset_version.dataset.name}-{self.dataset_version.version}"
        if self.language and not self.configuration:
            self.configuration = self.get_index_config(self.language)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "elastic index"
        verbose_name_plural = "elastic indices"

    @staticmethod
    def get_index_config(lang):
        """
        Returns the elasticsearch index configuration.
        Configures the analysers based on the language passed in.
        """
        decompound_word_list = None
        if settings.ELASTICSEARCH_ENABLE_DECOMPOUND_ANALYZERS:
            decompound_word_list = settings.ELASTICSEARCH_DECOMPOUND_WORD_LISTS.dutch
        return create_elastic_search_index_configuration(
            lang,
            settings.ELASTICSEARCH_ANALYSERS[lang],
            decompound_word_list=decompound_word_list
        )


class ElasticIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElasticIndex
        fields = ("id", "name", "language", "remote_name",)
