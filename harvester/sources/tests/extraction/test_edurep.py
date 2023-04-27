from datetime import datetime
import os
import json

from django.test import TestCase
from django.utils.timezone import make_aware
from django.conf import settings
from bs4 import BeautifulSoup

import edurep.extraction
from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.edurep.extraction import EdurepJsonSearchResourceFactory, SET_SPECIFICATION
from edurep.extraction import EdurepDataExtraction
from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from sources.extraction.edurep import EdurepMetadataExtraction, EDUREP_EXTRACTION_OBJECTIVE


class TestEdurepJsonMigration(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(os.path.join(settings.BASE_DIR, "sources", "factories", "fixtures",
                               "fixture.edurep.migration.xml")) as edurep_file_old:
            data_old = edurep_file_old.read()

            edurep_parsed_old = BeautifulSoup(data_old, "xml")
            oaipmh_objective = {
                "@": EdurepDataExtraction.get_oaipmh_records,
                "external_id": EdurepDataExtraction.get_oaipmh_external_id,
                "state": EdurepDataExtraction.get_oaipmh_record_state
            }
            oaipmh_objective.update(edurep.extraction.EDUREP_EXTRACTION_OBJECTIVE)
            extract_config = create_config("extract_processor", {
                "objective": oaipmh_objective
            })
            prc = ExtractProcessor(config=extract_config)
            cls.xml_data = [*prc.extract("application/xml", edurep_parsed_old)]
        with open(os.path.join(settings.BASE_DIR, "sources", "factories", "fixtures",
                            "fixture.edurep.migration.json")) as edurep_file_new:
            data_new = edurep_file_new.read()

            edurep_parsed_new = json.loads(data_new)

            metadata_objective = {
                "@": "$.response.items",
                "external_id": "$.@id",
                "state": EdurepMetadataExtraction.get_record_state
            }
            metadata_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
            extract_config = create_config("extract_processor", {
                "objective": metadata_objective
            })
            prc = ExtractProcessor(config=extract_config)
            cls.json_data = [*prc.extract("application/json", edurep_parsed_new)]

    def test_if_id_equal(self):
        for i in range(4):
            json_docu = self.json_data[i]
            xml_docu = self.xml_data[i]
            self.assertEqual(json_docu["external_id"], xml_docu["external_id"])\

    # Year and date do not show up in the xml file
    # def test_if_date_equal(self):
    #     for i in range(4):
    #         json_docu = self.json_data[i]
    #         xml_docu = self.xml_data[i]
    #         self.assertEqual(json_docu["publisher_date"], xml_docu["publisher_date"])
    #
    # def test_if_year_equal(self):
    #     import ipdb; ipdb.set_trace()
    #     for i in range(4):
    #         json_docu = self.json_data[i]
    #         xml_docu = self.xml_data[i]
    #         self.assertEqual(json_docu["publisher_year"], xml_docu["publisher_year"])

    def test_if_lowest_educational_level_equal(self):
        for i in range(4):
            json_docu = self.json_data[i]
            xml_docu = self.xml_data[i]
            self.assertEqual(json_docu["lowest_educational_level"], xml_docu["lowest_educational_level"])

    def test_if_educational_level_equal(self):
        for i in range(4):
            json_docu = self.json_data[i]
            xml_docu = self.xml_data[i]
            self.assertEqual(set(json_docu["lom_educational_levels"]), set(xml_docu["lom_educational_levels"]))

    def test_if_documents_equal(self):
        for i in range(4):
            json_docu = self.json_data[i]
            xml_docu = self.xml_data[i]
            self.assertEqual(json_docu["files"], xml_docu["files"])


class TestGetHarvestSeedsEdurep(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        EdurepJsonSearchResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.EDUREP_JSONSEARCH, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        import json; print(json.dumps(seeds[0], indent=4))
        self.assertEqual(seeds[0]["external_id"], "jsonld-from-lom:wikiwijsmaken:41156")

    def test_state_education_level(self):
        seeds = self.seeds

        for i in range(5):
            state = seeds[i]["state"]
            lowest_educational_level = seeds[i]["lowest_educational_level"]
            if lowest_educational_level < 2:
                self.assertEqual(state, "inactive")
            else:
                self.assertEqual(state, "active")
