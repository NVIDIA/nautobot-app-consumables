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

"""Tests for forms defined in the Nautobot Consumables app."""

import json

from nautobot.core.testing import TestCase
from nautobot.dcim.models import Device, Location, Manufacturer

from nautobot_consumables import forms, models


class CheckedOutConsumableFormsTestCase(TestCase):
    """Test the forms for the CheckedOutConsumable model."""

    def test_create_checkedoutconsumable_form(self):
        """Test creating a new CheckedOutConsumable instance."""
        pool = models.ConsumablePool.objects.last()
        form = forms.CheckedOutConsumableForm(
            initial={
                "consumable_pool": pool.pk,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("data-query-param-location", form.fields["device"].widget.attrs)

        form = forms.CheckedOutConsumableForm(
            data={
                **form.initial,
                "device": Device.objects.filter(location=pool.location).first().pk,
            },
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_update_checkedoutconsumable_form(self):
        """Test updating a CheckedOutConsumable instance."""
        instance = models.CheckedOutConsumable.objects.first()
        form = forms.CheckedOutConsumableForm(instance=instance)

        self.assertTrue(form.fields["consumable_pool"].disabled)
        self.assertTrue(form.fields["device"].disabled)

    def test_checkedoutconsumable_bulk_edit_form(self):
        """Test creating a bulk edit form instance."""
        form = forms.CheckedOutConsumableBulkEditForm(
            model=models.CheckedOutConsumable,
            data={"pk": [i.pk for i in models.CheckedOutConsumable.objects.all()]},
        )

        self.assertTrue(form.is_valid())

    def test_checkedoutconsumable_filter_form(self):
        """Test creating a Filter form instance."""
        form = forms.CheckedOutConsumableFilterForm(data={"device": [Device.objects.first().pk]})

        self.assertTrue(form.is_valid())


class ConsumableFormsTestCase(TestCase):
    """Test the forms for the Consumable model."""

    def test_create_consumable_form(self):
        """Test creating a new Consumable instance."""
        form = forms.ConsumableForm(
            data={
                "name": "Test Consumable",
                "consumable_type": models.ConsumableType.objects.get(name="Transceiver").pk,
                "manufacturer": Manufacturer.objects.first().pk,
                "product_id": "test0001",
                "data": {"reach": "LR", "form_factor": "QSFP-DD (400GE)"},
            },
        )

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_update_consumable_form(self):
        """Test updating a Consumable instance."""
        instance = models.Consumable.objects.first()
        form = forms.ConsumableForm(instance=instance)

        self.assertTrue(form.fields["consumable_type"].disabled)

    def test_consumable_bulk_edit_form(self):
        """Test creating a bulk edit form instance."""
        form = forms.ConsumableBulkEditForm(
            model=models.Consumable,
            data={"pk": [i.pk for i in models.Consumable.objects.all()]},
        )

        self.assertTrue(form.is_valid())

    def test_consumable_filter_form(self):
        """Test creating a Filter form instance."""
        form = forms.ConsumableFilterForm(data={"name": "Cable 1"})

        self.assertTrue(form.is_valid())


class ConsumablePoolFormsTestCase(TestCase):
    """Test the forms for the ConsumablePool model."""

    def test_create_consumablepool_form(self):
        """Test creating a new ConsumablePool instance."""
        form = forms.ConsumablePoolForm(
            data={
                "name": "Test Pool",
                "consumable": models.Consumable.objects.first().pk,
                "location": Location.objects.first().pk,
                "quantity": 50,
            },
        )

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_update_consumablepool_form(self):
        """Test updating a ConsumablePool instance."""
        instance = models.ConsumablePool.objects.first()
        form = forms.ConsumablePoolForm(instance=instance)

        self.assertTrue(form.fields["consumable"].disabled)

    def test_consumablepool_bulk_edit_form(self):
        """Test creating a bulk edit form instance."""
        form = forms.ConsumablePoolBulkEditForm(
            model=models.ConsumablePool,
            data={"pk": [i.pk for i in models.ConsumablePool.objects.all()]},
        )

        self.assertTrue(form.is_valid())

    def test_consumablepool_filter_form(self):
        """Test creating a Filter form instance."""
        form = forms.ConsumablePoolFilterForm(data={"location": [Location.objects.first().pk]})

        self.assertTrue(form.is_valid())


class ConsumableTypeFormsTestCase(TestCase):
    """Test the forms for the ConsumableType model."""

    def test_create_consumabletype_form(self):
        """Test creating a new ConsumableType instance."""
        with self.subTest(initial="no_schema"):
            form = forms.ConsumableTypeForm(data={"name": "Test Consumable"})
            self.assertTrue(form.is_valid())
            self.assertEqual(
                form.fields["schema"].get_bound_field(form, "schema").value(),
                "{}",
            )

        with self.subTest(initial="bad_schema"):
            form = forms.ConsumableTypeForm(
                data={"name": "Test Consumable", "schema": "{'bad': 'data',}"}
            )
            self.assertEqual(
                form.fields["schema"].get_bound_field(form, "schema").value(),
                "{'bad': 'data',}",
            )
            self.assertFalse(form.is_valid())

        with self.subTest(initial="schema"):
            test_schema = {
                "type": "object",
                "title": "Test Schema",
                "properties": {"unit": {"title": "Unit", "type": "string"}},
            }
            form = forms.ConsumableTypeForm(
                data={
                    "name": "Test Consumable",
                    "schema": json.dumps(test_schema),
                }
            )
            self.assertTrue(form.is_valid())
            self.assertEqual(
                form.fields["schema"].get_bound_field(form, "schema").value(),
                json.dumps(test_schema, sort_keys=True, indent=4, ensure_ascii=False),
            )

    def test_consumabletype_bulk_edit_form(self):
        """Test creating a bulk edit form instance."""
        form = forms.ConsumableTypeBulkEditForm(
            model=models.ConsumableType,
            data={"pk": [i.pk for i in models.ConsumableType.objects.all()]},
        )

        self.assertTrue(form.is_valid())

    def test_consumabletype_filter_form(self):
        """Test creating a Filter form instance."""
        form = forms.ConsumableTypeFilterForm(data={"q": "Test"})

        self.assertTrue(form.is_valid())
