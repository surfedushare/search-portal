from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.text import slugify
from elasticsearch.helpers import streaming_bulk
from rest_framework import serializers

from core.models import Dataset
from core.utils.elastic import get_es_client


class ElasticIndex(models.Model):

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.ELASTICSEARCH_ANALYSERS.items())
    dataset = models.ForeignKey(Dataset, related_name="indices", on_delete=models.CASCADE)
    configuration = JSONField(blank=True)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = get_es_client()

    @property
    def remote_name(self):
        if not self.id:
            raise ValueError("Can't get the remote name for an unsaved object")
        return slugify("{}-{}-{}".format(self.name, self.language, self.id))

    @property
    def remote_exists(self):
        if not self.id:
            raise ValueError("Can't check for existence with an unsaved object")
        return self.client.indices.exists(self.remote_name)

    def push(self, elastic_documents, recreate=True, request_timeout=300):  # why is the elastic cluster usually slow?
        if not self.id:
            raise ValueError("Can't push index with unsaved object")

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

        self.save()
        return errors

    def promote_to_latest(self):
        latest_alias = "latest-" + self.language
        if self.client.indices.exists_alias(name=latest_alias):
            self.client.indices.delete_alias(index="_all", name=latest_alias)
        self.client.indices.put_alias(index=self.remote_name, name=latest_alias)

    def clean(self):
        if not self.name:
            self.name = self.dataset.name
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
        search_analyzer = "dutch_dictionary_decompound" if lang == "nl" else \
            settings.ELASTICSEARCH_ANALYSERS[lang]
        return {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "analysis": {
                    "analyzer": {
                        "dutch_dictionary_decompound": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["dutch_stop", "dictionary_decompound"]
                        }
                    },
                    "filter": {
                        "dictionary_decompound": {
                            "type": "dictionary_decompounder",
                            "word_list_path": settings.ELASTICSEARCH_DECOMPOUND_WORD_LISTS.dutch,
                        },
                        "dutch_stop": {
                            "type": "stop",
                            "stopwords": "_dutch_"
                        }
                    }
                }
            },
            'mappings': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'analyzer': settings.ELASTICSEARCH_ANALYSERS[lang],
                        'search_analyzer': search_analyzer
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': settings.ELASTICSEARCH_ANALYSERS[lang],
                        'search_analyzer': search_analyzer
                    },
                    'transcription': {
                        'type': 'text',
                        'analyzer': settings.ELASTICSEARCH_ANALYSERS[lang],
                        'search_analyzer': search_analyzer
                    },
                    'description': {
                        'type': 'text',
                        'analyzer': settings.ELASTICSEARCH_ANALYSERS[lang],
                        'search_analyzer': search_analyzer
                    },
                    'url': {'type': 'text'},
                    'title_plain': {'type': 'text'},
                    'text_plain': {'type': 'text'},
                    'transcription_plain': {'type': 'text'},
                    'description_plain': {'type': 'text'},
                    'author': {
                        'type': 'keyword'
                    },
                    'authors': {
                        'type': 'text',
                        'fields': {
                            'keyword': {
                                'type': 'keyword',
                                'ignore_above': 256
                            }
                        }
                    },
                    'publishers': {
                        'type': 'keyword'
                    },
                    'publisher_date': {
                        'type': 'date',
                        'format': 'strict_date_optional_time||yyyy-MM||epoch_millis'
                    },
                    'aggregation_level': {
                        'type': 'keyword'
                    },
                    'keywords': {
                        'type': 'keyword'
                    },
                    'file_type': {
                        'type': 'keyword'
                    },
                    'id': {'type': 'text'},
                    'external_id': {
                        'type': 'keyword'
                    },
                    'arrangement_collection_name': {
                        'type': 'keyword'
                    },
                    'educational_levels': {
                        'type': 'keyword'
                    },
                    'lom_educational_levels': {
                        'type': 'keyword'
                    },
                    'disciplines': {
                        'type': 'keyword'
                    },
                    "suggest": {
                        "type": "completion"
                    },
                }
            }
        }


class ElasticIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElasticIndex
        fields = ("id", "name", "language", "remote_name",)
