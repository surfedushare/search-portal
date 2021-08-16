from django.test import TestCase
from django.contrib.auth.models import User


class TestExtensionAPI(TestCase):

    fixtures = ["datasets-history"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="supersurf")
        cls.parent_properties = {
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

    def assert_properties(self, properties, external_id="external-id", is_parent=False):
        # First we assert the basic props
        self.assertEqual(properties.pop("external_id"), external_id)
        # Then we assert all properties related to parentship
        for key in self.parent_properties.keys():
            if not is_parent:
                self.assertNotIn(key, properties)
            else:
                self.assertEqual(properties.pop(key), self.parent_properties[key])
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

    def test_create_parent(self):
        """
        When creating a parent Extension we should be able to set properties like: title and description,
        because when an Extension is a parent there exists no Document that provides that data.
        """
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "is_parent": True,
            "external_id": "external-id",
            "children": children,
            **self.extension_properties,
            **self.parent_properties,
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_parent"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_parent=True)

    def test_create_parent_no_children(self):
        """
        It should be possible to create a "parent" extension that does not have children (yet)
        """
        body = {
            "is_parent": True,
            "external_id": "external-id",
            **self.extension_properties,
            **self.parent_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_parent"])
        self.assert_properties(response_data["properties"], is_parent=True)

    def test_create_no_parent(self):
        """
        It should be possible to create a "non-parent", that has children.
        This only means that the Extension itself is not a parent, but the underlying Document might be.
        We also test making a child of a Document
        """
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
        self.assertFalse(response_data["is_parent"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assertEqual(response_data["properties"].pop("parents"), parents)
        self.assert_properties(response_data.pop("properties"), is_parent=False, external_id=external_id)

    def test_update_parent(self):
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
            "is_parent": True,
            "children": children,
            **self.extension_properties,
            **self.parent_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertTrue(response_data["is_parent"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_parent=True, external_id=external_id)

    def test_update_no_parent(self):
        """
        Updating an existing Extension means that all properties will get overridden.
        There is no merging done for properties.
        """
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        children = [
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "external_id": external_id,
            "is_parent": False,
            "children": children,
            **self.extension_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertFalse(response_data["is_parent"])
        self.assertEqual(response_data["properties"].pop("children"), children)
        self.assert_properties(response_data["properties"], is_parent=False, external_id=external_id)

    def test_invalid_update_parent(self):
        """
        Once an Extension is created as parent we can't go back. It is however possible to remove the children.
        This effectively tells Elastic to keep using the Extension as a source for data.
        It's expected that at a later time new children get added.
        """
        external_id = "custom-extension"
        body = {
            "external_id": external_id,
            "is_parent": False,
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
            "is_parent": True,
            "children": []
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["properties"]["children"], [])

    def test_delete(self):
        external_id = "custom-extension"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 204)
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 204)
        external_id = "does-not-exist"
        response = self.client.delete(f"/api/v1/extension/{external_id}/", content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_invalid_external_id(self):
        # It should be impossible to create non-parent Extensions if a Document with given external_id does not exist
        external_id = "not-a-document"
        body = {
            "external_id": external_id,
            "is_parent": False,
            **self.extension_properties,
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        # It should be impossible to update an Extension when external_id in path and body mismatch
        external_id = "custom-extension"
        body = {
            "external_id": "body-id",
            "is_parent": True,
            **self.extension_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_parents(self):
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

        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_children(self):
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

        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            "children": children,
            "parents": parents,
            **self.extension_properties
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_properties_non_parent(self):
        children = [
            "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751",
            "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257"
        ]
        body = {
            "is_parent": False,
            "external_id": "external-id",
            "children": children,
            **self.extension_properties,
            **self.parent_properties,
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
            "is_parent": False,
            "children": children,
            **self.extension_properties,
            **self.parent_properties,
        }
        response = self.client.put(f"/api/v1/extension/{external_id}/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate_parent(self):
        external_id = "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751"
        body = {
            "external_id": external_id,
            **self.extension_properties
        }
        response = self.client.post("/api/v1/extension/", body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
