#  SPDX-FileCopyrightText: Copyright (c) "2024" NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#  SPDX-License-Identifier: Apache-2.0
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""Tests for views defined in the Nautobot Consumables app."""
from copy import copy
import json

from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings
from nautobot.dcim.models import Device, Location, Manufacturer
from nautobot.users.models import ObjectPermission
from nautobot.utilities.testing import ViewTestCases, extract_page_body

from nautobot_consumables import models


class CheckedOutConsumableViewTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.GetObjectNotesViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Tests for the CheckedOutConsumable model views."""

    model = models.CheckedOutConsumable
    bulk_edit_data = {"quantity": 3}

    @classmethod
    def setUpTestData(cls):
        """Set up base data for the tests."""
        pools = [
            models.ConsumablePool.objects.last(),
            models.ConsumablePool.objects.get(name='Generic 4 Pool 1'),
            models.ConsumablePool.objects.get(name='Generic 5 Pool 1'),
        ]
        cls.form_data = {
            "consumable_pool": pools[0].pk,
            "device": Device.objects.filter(location=pools[0].location).first().pk,
            "quantity": 5,
        }
        cls.csv_data = (
            "consumable_pool,device,quantity",
            f"{pools[1].pk},{Device.objects.filter(location=pools[1].location).first().pk},5",
            f"{pools[1].pk},{Device.objects.filter(location=pools[1].location).last().pk},5",
            f"{pools[2].pk},{Device.objects.filter(location=pools[2].location).first().pk},5",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_edit_object_with_permission(self):
        """Handle the form idiosyncracies."""
        instance = self._get_queryset().all()[0]
        self.form_data = {
            "consumable_pool": instance.consumable_pool.pk,
            "device": instance.device.pk,
            "quantity": instance.quantity + 1,
        }

        super().test_edit_object_with_permission()

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_edit_object_with_constrained_permission(self):
        """Handle the form idiosyncracies."""
        instance = self._get_queryset().all()[0]
        self.form_data = {
            "consumable_pool": instance.consumable_pool.pk,
            "device": instance.device.pk,
            "quantity": instance.quantity + 1,
        }

        super().test_edit_object_with_constrained_permission()


class ConsumableViewTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Tests for the Consumable model views."""

    model = models.Consumable

    @classmethod
    def setUpTestData(cls):
        """Set up base data for the tests."""
        manufacturer = Manufacturer.objects.first()
        generic = models.ConsumableType.objects.get(name="Generic")

        cls.form_data = {
            "name": "Test Consumable 4",
            "manufacturer": manufacturer.pk,
            "product_id": "test04",
            "consumable_type": generic.pk,
        }

        cls.bulk_edit_data = {"manufacturer": Manufacturer.objects.last().pk}

        _ = models.Consumable.objects.create(
            name="Test Consumable 1",
            manufacturer=manufacturer,
            product_id="test01",
            consumable_type=generic,
        )
        _ = models.Consumable.objects.create(
            name="Test Consumable 2",
            manufacturer=manufacturer,
            product_id="test02",
            consumable_type=generic,
        )
        _ = models.Consumable.objects.create(
            name="Test Consumable 3",
            manufacturer=manufacturer,
            product_id="test03",
            consumable_type=generic,
        )

        cls.csv_data = (
            "name,consumable_type,manufacturer,product_id",
            f"Test Consumable 5,{generic.pk},{manufacturer.pk},test05",
            f"Test Consumable 6,{generic.pk},{manufacturer.pk},test06",
            f"Test Consumable 7,{generic.pk},{manufacturer.pk},test07",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_with_change_consumablepool_permission(self):
        """Test the detail view with change_consumablepool permissions."""
        instance = self._get_queryset().first()

        # Add model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["view", "change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # Without change_consumablepool permission, the Consumable Pools table won't show the pk
        # column, and the header will not have a toggle all checkbox.
        self.assertNotIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{instance.pools.first().pk}" /></td>',
            response_body,
            msg=response_body
        )

        obj_perm.object_types.add(ContentType.objects.get_for_model(models.ConsumablePool))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # With change_consumablepool permission, the Consumable Pools table will show the pk
        # column, and the header will have a toggle all checkbox.
        self.assertIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{instance.pools.first().pk}" /></td>',
            response_body,
            msg=response_body
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_edit_object_with_permission(self):
        """Handle the form idiosyncracies."""
        instance = models.Consumable.objects.first()
        self.form_data = copy(self.form_data)
        self.form_data["name"] = instance.name
        self.form_data["manufacturer"] = Manufacturer.objects.last().pk
        self.form_data["product_id"] = instance.product_id
        self.form_data["consumable_type"] = instance.consumable_type.pk

        super().test_edit_object_with_permission()

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_edit_object_with_constrained_permission(self):
        """Handle the form idiosyncracies."""
        instance = models.Consumable.objects.first()
        self.form_data = copy(self.form_data)
        self.form_data["name"] = instance.name
        self.form_data["manufacturer"] = Manufacturer.objects.last().pk
        self.form_data["product_id"] = instance.product_id
        self.form_data["consumable_type"] = instance.consumable_type.pk

        super().test_edit_object_with_constrained_permission()


class ConsumablePoolViewTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Tests for the ConsumablePool model views."""

    model = models.ConsumablePool

    @classmethod
    def setUpTestData(cls):
        consumable = models.Consumable.objects.first()
        location = Location.objects.last()
        cls.form_data = {
            "name": "Test Consumable Pool",
            "consumable": consumable.pk,
            "location": location.pk,
            "quantity": 42,
        }
        cls.bulk_edit_data = {
            "location": location.pk,
            "quantity": 99,
        }
        cls.csv_data = (
            "name,consumable,location,quantity",
            f"Test Pool 1,{consumable.pk},{location.pk},13",
            f"Test Pool 2,{consumable.pk},{location.pk},42",
            f"Test Pool 3,{consumable.pk},{location.pk},99",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_with_change_checkedoutconsumable_permission(self):
        """Test the detail view with change_checkedoutconsumable permissions."""
        instance = self._get_queryset().first()

        # Add model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["view", "change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # Without change_checkedoutconsumable permission, the Checked Out Consumables table won't
        # show the pk column, and the header will not have a toggle all checkbox.
        self.assertNotIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{instance.checked_out.first().pk}" /></td>',
            response_body,
            msg=response_body
        )

        obj_perm.object_types.add(ContentType.objects.get_for_model(models.CheckedOutConsumable))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # With change_checkedoutconsumable permission, the Checked Out Consumables table will
        # show the pk column, and the header will have a toggle all checkbox.
        self.assertIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{instance.checked_out.first().pk}" /></td>',
            response_body,
            msg=response_body
        )


class ConsumableTypeViewTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Tests for the ConsumableType model views."""

    model = models.ConsumableType
    form_data = {
        "name": "Test Consumable 4",
        "schema": json.dumps({
            "type": "object",
            "title": "Test Consumable Schema",
            "properties": {
                "unit": {
                    "type": "string",
                    "title": "Unit",
                },
            },
        }),
    }

    @classmethod
    def setUpTestData(cls):
        """Set up base data for the tests."""
        _ = models.ConsumableType.objects.create(name="Test Consumable 1")
        _ = models.ConsumableType.objects.create(name="Test Consumable 2")
        _ = models.ConsumableType.objects.create(name="Test Consumable 3")

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_with_change_consumable_permission(self):
        """Test the detail view with change_cconsumable permissions."""
        instance = self._get_queryset().get(name="Cable")
        test_consumable = models.Consumable.objects.filter(consumable_type=instance.pk).first()

        # Add model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["view", "change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # Without change_consumable permission, the Consumables table won't show the pk column, and
        # the header will not have a toggle all checkbox.
        self.assertNotIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{test_consumable.pk}" /></td>',
            response_body,
            msg=response_body
        )

        obj_perm.object_types.add(ContentType.objects.get_for_model(models.Consumable))

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

        response_body = extract_page_body(response.content.decode(response.charset))
        # With change_consumable permission, the Consumables table will show the pk column, and the
        # header will have a toggle all checkbox.
        self.assertIn(
            f'<td class="min-width"><input type="checkbox" name="pk" '
            f'value="{test_consumable.pk}" /></td>',
            response_body,
            msg=response_body
        )
