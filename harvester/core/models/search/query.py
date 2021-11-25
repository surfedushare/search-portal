from collections import defaultdict

from django.conf import settings
from django.db import models, transaction
from django.utils.text import slugify
from rest_framework import serializers


class QueryRanking(models.Model):

    query = models.ForeignKey("core.Query", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    subquery = models.CharField(max_length=255, db_index=True)
    version = models.CharField(max_length=50, default=settings.VERSION, editable=False)
    ranking = models.JSONField(default=dict)
    is_approved = models.BooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_elastic_ratings(self, as_dict=False):
        ratings = [
            {
                "_index": key.split(":")[0],
                "_id": key.split(":")[1],
                "rating": value
            }
            for key, value in self.ranking.items()
        ]
        return ratings if not as_dict else {rating["_id"]: rating["rating"] for rating in ratings}


class ListFromUserSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        request = self.context["request"]
        data = data.filter(user=request.user)
        return super().to_representation(data)


class UserQueryRankingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryRanking
        list_serializer_class = ListFromUserSerializer
        fields = ("subquery", "ranking",)


class QueryManager(models.Manager):

    def get_query_rankings(self, user):
        rankings = defaultdict(dict)
        for ranking in QueryRanking.objects.filter(user=user):
            rankings[ranking.query].update(ranking.get_elastic_ratings(as_dict=True))
        return rankings


class Query(models.Model):

    objects = QueryManager()

    query = models.CharField(max_length=255, db_index=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=QueryRanking)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_elastic_query_body(self, fields, enrichments=None):
        enrichments = enrichments or []
        query = f"{self.query} {' '.join(enrichments).strip()}"
        return {
            'bool': {
                'query': {
                    "bool": {
                        "must": [{
                            "simple_query_string": {
                                "fields": fields,
                                "query": query,
                                "default_operator": "and"
                            }
                        }],
                        "should": {
                            "distance_feature": {
                                "field": "publisher_date",
                                "pivot": "90d",
                                "origin": "now",
                                "boost": 1.15
                            }
                        }
                    }
                },
            }
        }

    def get_elastic_ranking_request(self, user, fields):
        ratings = []
        for ranking in self.queryranking_set.filter(user=user):
            ratings += ranking.get_elastic_ratings()
        return {
            "id": slugify(self.query),
            "request": {
                "query": self.get_elastic_query_body(fields)
            },
            "ratings": ratings
        }

    def __str__(self):
        return self.query

    class Meta:
        verbose_name_plural = "queries"


class QuerySerializer(serializers.ModelSerializer):

    rankings = UserQueryRankingSerializer(source="queryranking_set", many=True, read_only=False, allow_null=False,
                                          required=True)

    def validate(self, data):
        data = super().validate(data)
        query = data["query"]
        for ranking in data["queryranking_set"]:
            if query == ranking["subquery"]:
                break
        else:
            raise serializers.ValidationError("At least one ranking must be specified with the main query as subquery")
        return data

    def build_query_rankings(self, instance, user, validated_data):
        rankings = []
        instance.queryranking_set.filter(user=user).delete()
        for ranking in validated_data:
            rankings.append(QueryRanking(user=user, query=instance, **ranking))
        QueryRanking.objects.bulk_create(rankings)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        query, created = Query.objects.get_or_create(query=validated_data["query"])
        self.build_query_rankings(query, request.user, validated_data["queryranking_set"])
        return query

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context["request"]
        self.build_query_rankings(instance, request.user, validated_data["queryranking_set"])
        return instance

    class Meta:
        model = Query
        fields = ("query", "rankings", "created_at", "modified_at",)
