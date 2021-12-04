from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now

from core.models import Document


class TestExtensionAPI(TestCase):

    fixtures = ["datasets-history"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="supersurf")
        cls.addition_properties = {
            "title": "title",
            "description": "description",
            "language": "nl",
            "copyright": "cc-by-40"
        }
        cls.extension_properties = {
            "authors": [
                {"name": "Monty Python"}
            ],
            "parties": [
                {"name": "I love the 90's"}
            ],
            "themes": [
                {"label": "90's"}
            ],
            "keywords": [
                {"label": "90's"}
            ]
        }

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def assert_properties(self, properties, external_id="external-id", is_addition=False):
        # First we assert the basic props
        self.assertEqual(properties.pop("external_id"), external_id)
        # Then we assert all properties related to additions
        for key in self.addition_properties.keys():
            if not is_addition:
                self.assertNotIn(key, properties)
            else:
                self.assertEqual(properties.pop(key), self.addition_properties[key])
        # All remaining properties should be regular extension properties
        for key in self.extension_properties.keys():
            self.assertEqual(properties[key], self.extension_properties[key])

    def test_list(self):
        response = self.client.get("/api/v1/extension/")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)
        extension = response_data[0]
        self.assertIn("properties", extension)

    def test_create_addition(self):
        """
        When creating an addition Extension we should be able to set properties like: title and description,
        because when an Extension is an addition there exists no Document that provides that data.
        """
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "is_addition": True,
            "external_id": "external-id",
            "children": children,
            **self.extension_properties,
            **self.addition_properties,
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_addition"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_addition=True)

    def test_create_addition_no_children(self):
        """
        It should be possible to create an "addition" extension that does not have children
        """
        body = {
            "is_addition": True,
            "external_id": "external-id",
            **self.extension_properties,
            **self.addition_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_addition"])
        self.assert_properties(response_data["properties"], is_addition=True)

    def test_add_children(self):
        """
        It should be possible to add children to a Document through extending it, or giving a Document a parent.
        """
        datetime_begin_test = now()
        external_id = "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        ]
        parents = [
            "63903863-6c93-4bda-b850-277f3c9ec00e"
        ]
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertFalse(response_data["is_addition"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assertEqual(response_data["properties"].pop("parents"), parents)
        self.assert_properties(response_data.pop("properties"), is_addition=False, external_id=external_id)
        document = Document.objects.get(reference=external_id)
        self. assertGreater(document.modified_at, datetime_begin_test,
                            "Expected modified_at of document to get updated")

    def test_update_addition(self):
        """
        Updating an existing Extension means that all properties will get overridden.
        There is no merging done for properties.
        """
        external_id = "custom-extension"
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "external_id": external_id,
            "is_addition": True,
            "children": children,
            **self.extension_properties,
            **self.addition_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_addition"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_addition=True, external_id=external_id)

    def test_update(self):
        """
        Updating an existing Extension means that all properties will get overridden.
        There is no merging done for properties.
        """
        datetime_begin_test = now()
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        children = [
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "external_id": external_id,
            "is_addition": False,
            "children": children,
            **self.extension_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertFalse(response_data["is_addition"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_addition=False, external_id=external_id)
        document = Document.objects.get(reference=external_id)
        self. assertGreater(document.modified_at, datetime_begin_test,
                            "Expected modified_at of document to get updated")

    def test_state_addition(self):
        external_id = "custom-extension"
        body = {
            "external_id": external_id,
            "is_addition": True,
            "state": Document.States.INACTIVE,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_addition"])
        self.assertEqual(response_data["properties"]["state"], Document.States.INACTIVE.value)
        body["state"] = Document.States.ACTIVE
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data["properties"]["state"], Document.States.ACTIVE.value)

    def test_deactivate(self):
        datetime_begin_test = now()
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            "is_addition": False,
            "state": Document.States.INACTIVE,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertFalse(response_data["is_addition"])
        self.assertEqual(response_data["properties"]["state"], Document.States.INACTIVE.value)
        body["state"] = Document.States.ACTIVE
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data["properties"]["state"], Document.States.ACTIVE.value)
        document = Document.objects.get(reference=external_id)
        self. assertGreater(document.modified_at, datetime_begin_test,
                            "Expected modified_at of document to get updated")

    def test_invalid_update_addition(self):
        """
        Once an Extension is created as addition we can't go back.
        It is however possible to edit other properties like the children.
        """
        external_id = "custom-extension"
        body = {
            "external_id": external_id,
            "is_addition": False,
            **self.extension_properties
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(
            response.status_code, 400,
            "Did not expect that updating a parent extension to a non-parent extension is allowed"
        )
        external_id = "custom-extension"
        body = {
            "external_id": external_id,
            "is_addition": True,
            "children": []
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["properties"]["children"], [])

    def test_delete(self):
        datetime_begin_test = now()
        external_id = "custom-extension"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 204)
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 204)
        document = Document.objects.get(reference=external_id)
        self. assertGreater(document.modified_at, datetime_begin_test,
                            "Expected modified_at of document to get updated")
        external_id = "does-not-exist"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_invalid_external_id(self):
        # It should be impossible to create non-parent Extensions if a Document with given external_id does not exist
        external_id = "not-a-document"
        body = {
            "external_id": external_id,
            "is_addition": False,
            **self.extension_properties,
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        # It should be impossible to update an Extension when external_id in path and body mismatch
        external_id = "custom-extension"
        body = {
            "external_id": "body-id",
            "is_addition": True,
            **self.extension_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_parents(self):
        datetime_begin_test = now()
        external_id = "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        ]
        parents = [
            "does-not-exist"
        ]
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        document = Document.objects.get(reference=external_id)
        self.assertLess(document.modified_at, datetime_begin_test,
                        "Expected modified_at of document to remain the same")

        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        document = Document.objects.get(reference=external_id)
        self.assertLess(document.modified_at, datetime_begin_test,
                        "Expected modified_at of document to remain the same")

    def test_invalid_children(self):
        datetime_begin_test = now()
        external_id = "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        children = [
            "does-not-exist"
        ]
        parents = [
            "63903863-6c93-4bda-b850-277f3c9ec00e"
        ]
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        document = Document.objects.get(reference=external_id)
        self.assertLess(document.modified_at, datetime_begin_test,
                        "Expected modified_at of document to remain the same")

        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        document = Document.objects.get(reference=external_id)
        self.assertLess(document.modified_at, datetime_begin_test,
                        "Expected modified_at of document to remain the same")

    def test_invalid_properties_non_addition(self):  # TODO: this test should work differently
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "is_addition": False,
            "external_id": "external-id",
            "children": children,
            **self.extension_properties,
            **self.addition_properties,
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        external_id = "custom-extension"
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "external_id": external_id,
            "is_addition": False,
            "children": children,
            **self.extension_properties,
            **self.addition_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate(self):
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            **self.extension_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
