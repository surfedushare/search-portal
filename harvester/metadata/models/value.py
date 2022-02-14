from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from mptt.exceptions import InvalidMove

from metadata.models import MetadataTranslation, MetadataTranslationSerializer


class MetadataValueManager(TreeManager):

    def move_node(self, node, target, position='last-child'):
        if node.field_id != target.field_id:
            raise InvalidMove(f"Can not move '{node.value}' relative to '{target.value}', "
                              f"because they do not share a field")
        super().move_node(node, target, position=position)


class MetadataValue(MPTTModel):

    objects = MetadataValueManager()
    _tree_manager = MetadataValueManager()

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    field = models.ForeignKey("metadata.MetadataField", on_delete=models.CASCADE, null=False, blank=False)
    value = models.CharField(max_length=255, blank=False, null=False)
    translation = models.OneToOneField(MetadataTranslation, on_delete=models.PROTECT, null=False, blank=False)
    frequency = models.PositiveIntegerField(default=0)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_manual = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent and self.field_id != self.parent.field_id:
            raise ValidationError(f"Can not make '{self.value}' child of '{self.parent.value}', "
                                  f"because they do not share a field")
        super().clean()

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = ("field", "value",)


class MetadataValueSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()
    translation = MetadataTranslationSerializer()
    field = serializers.CharField(source="field.name")

    def get_children(self, obj):
        if obj.is_leaf_node():
            return []
        children = sorted(obj.get_children(), key=lambda child: child.frequency, reverse=True)
        max_children = self.context["request"].GET.get("max_children", "")
        max_children = int(max_children) if max_children else None
        return MetadataValueSerializer(children, many=True).data[:max_children]

    def get_children_count(self, obj):
        return len(obj.get_children())

    def get_frequency(self, obj):
        aggregation = obj.get_children().filter(deleted_at__isnull=True).aggregate(models.Sum("frequency"))
        return obj.frequency + (aggregation["frequency__sum"] or 0)

    class Meta:
        model = MetadataValue
        fields = ('id', 'parent', 'field', 'is_hidden', 'is_manual', 'children', 'children_count', 'value',
                  'translation', 'frequency',)
