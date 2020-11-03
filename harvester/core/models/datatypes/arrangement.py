import logging
from collections import Iterator, defaultdict
from zipfile import BadZipFile
from bs4 import BeautifulSoup
from urlobject import URLObject

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.utils.timezone import now
from django.utils.functional import cached_property

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch
from core.models import CommonCartridge, FileResource


log = logging.getLogger("harvester")


class Arrangement(DocumentCollectionMixin, CollectionBase):
    """
    When people search in the portal this is what they find.
    The Arrangement is in other words responsible for generating the Elastic Search Document.
    It does this through possibly multiple Datagrowth Documents.
    A Datagrowth Document is akin to a file.
    """

    dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    collection = models.ForeignKey("Collection", blank=True, null=True, on_delete=models.CASCADE)
    meta = postgres_fields.JSONField(default=dict)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection or self.collection)
        doc.dataset = self.dataset
        doc.arrangement = self
        return doc

    def update(self, data, by_reference, validate=True, batch_size=32, collection=None):
        collection = collection or self
        Document = collection.get_document_model()
        assert isinstance(data, (Iterator, list, tuple, dict, Document)), \
            f"Collection.update expects data to be formatted as iteratable, dict or {type(Document)} not {type(data)}"

        count = 0
        for updates in ibatch(data, batch_size=batch_size):
            # First we bulk update by getting all objects whose identifier value match any update's "by" value
            # and then updating these source objects.
            # One update object can potentially target multiple sources
            # if multiple objects with an identifier of "by" exist.
            updated = set()
            hashed = {update[by_reference]: update for update in updates}
            sources = {source[by_reference]: source for source in collection.documents.filter(
                reference__in=hashed.keys())}
            for source in sources.values():
                source.update(hashed[source.reference], validate=validate)
                count += 1
                updated.add(source.reference)
            Document.objects.bulk_update(
                sources.values(),
                ["properties"],
                batch_size=datagrowth_settings.DATAGROWTH_MAX_BATCH_SIZE
            )
            # After all updates we add all data that hasn't been used in any update operation
            additions = [update for identify, update in hashed.items() if identify not in updated]
            if len(additions):
                count += self.add(additions, validate=validate, batch_size=batch_size, collection=collection)

        return count

    @cached_property
    def base_document(self):
        text_documents = self.documents.exclude(properties__file_type="video")
        video_documents = self.documents.filter(properties__file_type="video")
        base_document = video_documents.first()
        if base_document is None:
            base_document = text_documents.first()
        return base_document

    def store_language(self):
        self.meta["language"] = self.base_document.get_language() if self.base_document else "unk"
        self.save()

    @staticmethod
    def get_search_document_details(reference_id, url, title, text, transcription, mime_type, file_type,
                                    is_part_of=None, has_part=None):
        has_part = has_part or []
        return {
            '_id': reference_id,
            'title': title,
            'text': text,
            'transcription': transcription,
            'url': url,
            'title_plain': title,
            'text_plain': text,
            'transcription_plain': transcription,
            'file_type': file_type,
            'mime_type': mime_type,
            'has_part': has_part,
            'is_part_of': is_part_of,
            'suggest': title.split(" ") if title else [],
        }

    def get_search_document_base(self):
        """
        This method returns either a delete action or a partial upsert action.
        If it returns a partial update action it will only fill out all data
        that's the same for all documents coming from this Arrangement.
        Only the reference_id gets added for both partial update and delete actions

        :return: Elastic Search partial update or delete action
        """
        # First we fill out all data we know from the Arrangement or we have an early return for deletes
        # and unknown data
        base = {
            "language": self.meta.get("language", "unk"),
        }
        if self.deleted_at:
            base["_op_type"] = "delete"
            return base
        elif not self.base_document:
            return base
        # Then we enhance the data with any data coming from the base document belonging to the arrangement
        base.update({
            'external_id': self.base_document.properties['external_id'],
            'disciplines': self.base_document.properties['disciplines'],
            'educational_levels': self.base_document.properties['educational_levels'],
            'lom_educational_levels': self.base_document.properties['lom_educational_levels'],
            'author': self.base_document.properties['author'],
            'authors': self.base_document.properties['authors'],
            'publishers': self.base_document.properties['publishers'],
            'description': self.base_document.properties['description'],
            'publisher_date': self.base_document.properties['publisher_date'],
            'copyright': self.base_document.properties['copyright'],
            'aggregation_level': self.base_document.properties['aggregation_level'],
            'keywords': self.meta['keywords'],
            'oaipmh_set': self.collection.name,
            'arrangement_collection_name': self.collection.name  # TODO: remove this once everything uses oaipmh_set
        })
        return base

    def unpack_package_documents(self, reference_id, base_url):
        """
        This methods returns content data if this arrangement is a package.
        The content should be merged with other ES data to form a proper search document.
        Currently this method relies heavily on the structure in wikiwijsmaken packages
        and is not expected to work with IMSCC in general.
        """
        # First we try to find all navigation links and their href's by looking at the HTML in the downloaded file
        _, html_file_id = self.base_document.properties["pipeline"]["file"]["resource"]
        file_resource = FileResource.objects.get(id=html_file_id)
        content_type, file = file_resource.content
        soup = BeautifulSoup(file, "html5lib")
        navigation_links = defaultdict(list)
        for navigation_link in soup.find_all("a", class_="js-menu-item"):
            navigation_links[navigation_link.text.strip()].append(navigation_link["href"])

        # Then we parse the IMSCC package file and extract items from its manifest file
        _, package_file_id = self.base_document.properties["pipeline"]["package_file"]["resource"]
        package_file = FileResource.objects.get(id=package_file_id)
        cc = CommonCartridge(file=package_file.body)
        try:
            cc.clean()
            package_content = cc.list_content_by_title()
        except (ValidationError, BadZipFile):
            log.warning(f"Invalid or missing common cartridge for file resource: {package_file.id}")
            return []

        # Combine the links and content into documents we may search for
        results = []
        for title, links in navigation_links.items():
            results += [
                {
                    "_id": reference_id + link,
                    "is_part_of": reference_id,
                    "link": link,
                    "url": base_url + link,
                    "title": title,
                    "text": package_content[title].pop(0) if len(package_content[title]) else "",
                }
                for link in links
            ]
        return results

    def to_search(self):

        elastic_base = self.get_search_document_base()
        if not self.base_document:
            # TODO: figure out why some arrangements get 0 documents
            # Is this only in old dataset dumps or still happening??
            elastic_base["_id"] = self.meta["reference_id"]
            return elastic_base

        # Gather text from text media
        text_documents = self.documents.exclude(properties__file_type="video")
        texts = []
        for doc in text_documents:
            texts.append(doc.properties["text"])
        text = "\n\n".join(texts)

        # Gather text from video media
        video_documents = self.documents.filter(properties__file_type="video")
        transcriptions = []
        for doc in video_documents:
            if doc.properties["text"] is None:
                continue
            transcriptions.append(doc.properties["text"])
        transcription = "\n\n".join(transcriptions)

        # Get the base url without any anchor fragment
        base_url = str(URLObject(self.base_document["url"]).with_fragment(""))

        # First we yield documents for each file in a package when dealing with a package
        child_ids = []
        if self.meta.get("is_package", False):
            for package_document in self.unpack_package_documents(self.meta["reference_id"], base_url):
                child_ids.append(package_document["_id"])
                elastic_details = self.get_search_document_details(
                    package_document["_id"],
                    package_document["url"],
                    package_document["title"],
                    package_document["text"],
                    transcription="",
                    mime_type="text/html",
                    file_type=settings.MIME_TYPE_TO_FILE_TYPE["text/html"],
                    is_part_of=package_document["is_part_of"]
                )
                elastic_details.update(elastic_base)
                yield elastic_details

        # Then we yield a Elastic Search document for the Arrangement as a whole
        elastic_details = self.get_search_document_details(
            self.meta["reference_id"],
            self.base_document["url"],
            self.base_document["title"],
            text,
            transcription,
            self.base_document["mime_type"],
            self.base_document["file_type"],
            has_part=child_ids
        )
        elastic_details.update(elastic_base)
        yield elastic_details

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)
