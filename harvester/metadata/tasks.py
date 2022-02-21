from datetime import timedelta

from django.utils.timezone import now
from django.urls import reverse
from celery import current_app as app

from harvester.tasks.base import DatabaseConnectionResetTask
from core.utils.notifications import send_admin_notification
from metadata.models import MetadataField, MetadataValue, MetadataTranslation
from metadata.utils.translate import fetch_eduterm_translations, fetch_edustandaard_translations, translate_with_deepl


def _translate_metadata_value(field, value):
    if field.english_as_dutch:
        return MetadataTranslation(nl=value, en=value, is_fuzzy=False)

    translations = fetch_eduterm_translations(value)
    if not translations:
        translations = fetch_edustandaard_translations(value)

    if translations:
        dutch, english = translations
        if dutch == english:
            english = translate_with_deepl(dutch)
        translation = MetadataTranslation(nl=dutch, en=english, is_fuzzy=True)
    else:
        translation = MetadataTranslation(nl=value, en=value, is_fuzzy=True)
    return translation


@app.task(name="sync_metadata", base=DatabaseConnectionResetTask)
def sync_metadata():
    frequencies = MetadataField.objects.fetch_value_frequencies(is_manual=False)

    metadata_updates = []
    for metadata_value in MetadataValue.objects.iterator():
        if metadata_value.field.name not in frequencies:
            continue
        frequency = frequencies[metadata_value.field.name].pop(metadata_value.value, 0)
        if not frequency and not metadata_value.is_manual:
            metadata_value.deleted_at = now()
            metadata_updates.append(metadata_value)
            continue
        metadata_value.frequency = frequency
        metadata_value.deleted_at = None
        metadata_value.updated_at = now()
        metadata_updates.append(metadata_value)
    MetadataValue.objects.bulk_update(metadata_updates, fields=["value", "frequency", "updated_at", "deleted_at"])

    metadata_inserts = []
    translation_inserts = []
    for field_name, field_frequencies in frequencies.items():
        field = MetadataField.objects.get(name=field_name)
        for value, frequency in field_frequencies.items():
            translation = _translate_metadata_value(field, value)
            translation_inserts.append(translation)
            metadata_value = MetadataValue(
                field=field,
                name=value,
                value=value,
                frequency=frequency,
                translation=translation,
                is_hidden=translation.is_fuzzy,
                lft=0,
                rght=0,
                level=0,
                tree_id=0
            )
            metadata_inserts.append(metadata_value)
    MetadataTranslation.objects.bulk_create(translation_inserts)
    MetadataValue.objects.bulk_create(metadata_inserts)
    MetadataValue.objects.rebuild()
    if metadata_inserts:
        send_admin_notification(
            "New metadata values and translations have been added",
            reverse("admin:metadata_metadatavalue_changelist") + "?is_fuzzy__exact=1"
        )

    in_30_days = now() + timedelta(days=30)
    MetadataValue.objects.filter(deleted_at__gte=in_30_days).delete()
