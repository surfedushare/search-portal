from django.db import models
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from mptt.exceptions import InvalidMove

from metadata.models import MetadataTranslation, MetadataField


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

    field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, null=False, blank=False)
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

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = ("field", "value",)
