from core.tests.factories import (DatasetVersionFactory, CollectionFactory, DocumentFactory,
                                  ElasticIndexFactory, HttpTikaResourceFactory)


def _serialize_resource(resource=None):
    if resource is None:
        return {
            "success": False,
            "resource": None,
            "id": None
        }

    return {
        "success": resource.success,
        "resource": "{}.{}".format(resource._meta.app_label, resource._meta.model_name),
        "id": resource.id
    }


def create_dataset_version(dataset, version, created_at, include_current, copies=3, docs=5):
    for ix in range(0, copies):
        dataset_version = DatasetVersionFactory.create(
            dataset=dataset,
            version=version,
            is_current=include_current and ix == 0,
        )
        dataset_version.created_at = created_at  # only possible to overwrite after creation
        dataset_version.save()
        collection = CollectionFactory.create(
            name=dataset.name,
            dataset_version=dataset_version,
            created_at=created_at,
            modified_at=created_at
        )
        for language in ["nl", "en"]:
            ElasticIndexFactory.create(
                dataset_version=dataset_version,
                name=f"{dataset.name}-{dataset_version.version}",
                language=language,
                configuration={}
            )
        for ixx in range(0, docs):
            tika_resource = HttpTikaResourceFactory.create(
                created_at=created_at,
                modified_at=created_at,
                purge_at=created_at
            )
            pipeline = {
                "tika": _serialize_resource(tika_resource)
            }
            DocumentFactory.create(
                dataset_version=dataset_version,
                collection=collection,
                created_at=created_at,
                modified_at=created_at,
                pipeline=pipeline
            )
