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

"""Tests for models defined by the Consumables app."""
from time import sleep

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from nautobot.dcim.models import Device, Location, Manufacturer
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField, Status
from nautobot.tenancy.models import Tenant

from nautobot_consumables import models
from nautobot_consumables.tests.fixtures import create_env


class ConsumableTypeTestCase(TestCase):
    """Tests for the ConsumableType model."""

    @classmethod
    def setUpTestData(cls):
        """Set up the base test data."""
        test_schema = {
            "type": "object",
            "title": "Test Schema",
            "properties": {
                "length": {"title": "Length", "type": "integer", "propertyOrder": 10},
                "length_unit": {
                    "title": "Unit",
                    "type": "string",
                    "enum": ["m", "cm", "ft", "in"],
                    "options": {"enum_titles": ["Meters", "Centimeters", "Feet", "Inches"]},
                    "propertyOrder": 20,
                }
            }
        }
        cls.consumable_type = models.ConsumableType(name="Test Consumable Type", schema=test_schema)

    def test_validated_save(self):
        """Test creating a ConsumableType and saving it with validation."""
        self.consumable_type.validated_save()
        self.consumable_type.validated_save()

    def test_instance_name(self):
        """Test the string representation of the model."""
        self.assertEqual(f"{self.consumable_type}", "Test Consumable Type")

    def test_validate_schema(self):
        """Test schema validation."""
        self.consumable_type.schema["type"] = "imaginary"
        with self.assertRaises(ValidationError) as context:
            self.consumable_type.clean()
        error = context.exception
        self.assertEqual(
            error.message,
            "'imaginary' is not valid under any of the given schemas on ['type']"
        )

    def test_export_instance(self):
        """Test exporting the model to CSV."""
        csv = self.consumable_type.to_csv()
        self.assertIsInstance(csv, tuple)
        self.assertEqual(len(csv), 2)
        self.assertEqual(csv[0], self.consumable_type.name)


class ConsumableTestCase(TestCase):
    """Tests for the Consumable model."""

    @classmethod
    def setUpTestData(cls):
        """Set up the base test data."""
        cls.consumable = models.Consumable(
            name="Test Consumable",
            consumable_type=models.ConsumableType.objects.get(name="Cable"),
            manufacturer=Manufacturer.objects.first(),
            product_id="R2D2",
            data={
                "cable_type": "CAT6",
                "connector": "8P8C",
                "length": 5,
                "length_unit": "m",
                "color": "ff9800",
            },
        )

    def test_validated_save(self):
        """Test creating a Consumable and saving it with validation."""
        self.consumable.validated_save()
        self.consumable.validated_save()

    def test_instance_name(self):
        """Test the string representation of the model."""
        self.assertEqual(f"{self.consumable}", "Test Consumable")

    def test_change_consumable_type(self):
        """Test that changing the ConsumableType after creation raises an error"""
        self.consumable.validated_save()
        self.consumable.consumable_type = models.ConsumableType.objects.get(name="Generic")
        with self.assertRaises(ValidationError):
            self.consumable.validated_save()

    def test_export_instance(self):
        """Test exporting the model to CSV."""
        csv = self.consumable.to_csv()
        self.assertIsInstance(csv, tuple)
        self.assertEqual(len(csv), 5)
        self.assertEqual(csv[3], "R2D2")

    def test_template_details(self):
        """Test the generated template details property."""
        self.consumable.clean()
        self.assertIsInstance(self.consumable.template_details, list)
        self.assertIsInstance(self.consumable.template_details[0], tuple)
        self.assertEqual(len(self.consumable.template_details), 4)
        self.assertEqual(self.consumable.template_details[-1][-1]["value"], "Orange")

    def test_schema_validation(self):
        """Test that schema validation works."""
        self.consumable.clean()

        with self.subTest(check="bad_value"):
            self.consumable.data["color"] = "Black"
            with self.assertRaises(ValidationError) as context:
                self.consumable.clean()
            error = context.exception
            self.assertTrue(
                error.message.startswith("Data validation against schema schema failed: 'Black'")
            )

        with self.subTest(check="required"):
            self.consumable.data.pop("color")
            with self.assertRaises(ValidationError) as context:
                self.consumable.clean()
            error = context.exception
            self.assertEqual(
                error.message,
                "Data validation against schema schema failed: 'color' is a required property"
            )


class ConsumablePoolTestCase(TestCase):
    """Tests for the ConsumablePool model."""

    @classmethod
    def setUpTestData(cls):
        """Set up the base test data."""
        consumable = models.Consumable.objects.create(
            name="Test Consumable",
            consumable_type=models.ConsumableType.objects.get(name="Cable"),
            manufacturer=Manufacturer.objects.first(),
            product_id="R2D2",
            data={
                "cable_type": "CAT6",
                "connector": "8P8C",
                "length": 5,
                "length_unit": "m",
                "color": "ff9800",
            },
        )

        cls.consumable_pool = models.ConsumablePool(
            consumable=consumable,
            name="Test Consumable Pool",
            location=Location.objects.first(),
            quantity=13,
        )

    def test_validated_save(self):
        """Test creating a ConsumablePool and saving it with validation."""
        self.consumable_pool.validated_save()
        self.consumable_pool.validated_save()

    def test_instance_name(self):
        """Test the string representation of the model."""
        self.assertEqual(
            f"{self.consumable_pool}",
            f"Test Consumable Pool ({self.consumable_pool.location.name})"
        )

    def test_change_consumable(self):
        """Test that changing the Consumable after creation raises an error."""
        self.consumable_pool.validated_save()
        self.consumable_pool.consumable = models.Consumable.objects.first()
        with self.assertRaises(ValidationError):
            self.consumable_pool.validated_save()

    def test_export_instance(self):
        """Test exporting the model to CSV."""
        csv = self.consumable_pool.to_csv()
        self.assertIsInstance(csv, tuple)
        self.assertEqual(len(csv), 4)
        self.assertEqual(csv[0], self.consumable_pool.name)

    def test_used_and_available(self):
        """Test the used_quantity and available_quantity properties."""
        self.consumable_pool.validated_save()
        models.CheckedOutConsumable.objects.create(
            consumable_pool=self.consumable_pool,
            device=Device.objects.first(),
            quantity=6,
        )

        self.assertEqual(self.consumable_pool.used_quantity, 6)
        self.assertEqual(self.consumable_pool.available_quantity, 7)


class CheckedOutConsumableTestCase(TestCase):
    """Tests for the CheckedOutConsumable model."""

    @classmethod
    def setUpTestData(cls):
        """Set up the base test data."""
        pool = models.ConsumablePool.objects.get(name="Cable 1 Pool 1")
        cls.checked_out_consumable = models.CheckedOutConsumable(
            consumable_pool=pool,
            device=Device.objects.filter(location=pool.location).last(),
            quantity=5,
        )

    def test_validated_save(self):
        """Test creating a CheckedOutConsumable and saving it with validation."""
        self.checked_out_consumable.validated_save()
        self.checked_out_consumable.validated_save()

    def test_instance_name(self):
        """Test the string representation of the model."""
        new_checked_out_consumable = models.CheckedOutConsumable()

        with self.subTest(check="empty"):
            self.assertEqual(f"{new_checked_out_consumable}", "No Device | No Pool")

        with self.subTest(check="device_only"):
            new_checked_out_consumable.device = Device.objects.first()
            self.assertEqual(f"{new_checked_out_consumable}", "Device 1-1 | No Pool")

        with self.subTest(check="pool_only"):
            new_checked_out_consumable.device = None
            new_checked_out_consumable.consumable_pool = models.ConsumablePool.objects.get(
                name="Generic 1 Pool 1",
            )
            self.assertEqual(f"{new_checked_out_consumable}", "No Device | Generic 1 Pool 1")

        with self.subTest(check="complete"):
            self.assertEqual(f"{self.checked_out_consumable}", "Device 1-2 | Cable 1 Pool 1")

    def test_invalid_device(self):
        """Test checking out to a Device in a different location."""
        device = Device.objects.filter(location=Location.objects.last()).first()
        self.checked_out_consumable.device = device
        with self.assertRaises(ValidationError) as context:
            self.checked_out_consumable.validated_save()
        error = context.exception.error_dict["__all__"][0]
        pool = self.checked_out_consumable.consumable_pool
        self.assertEqual(
            error.message,
            f"Cannot check out consumables from Pool {pool.name} in location "
            f"{pool.location.name} to Device {device.name} in location {device.location.name}"
        )

    def test_invalid_quantity(self):
        """Test trying to check out more items than are available."""
        pool = self.checked_out_consumable.consumable_pool
        requested = pool.available_quantity + 5
        self.checked_out_consumable.quantity = requested
        with self.assertRaises(ValidationError) as context:
            self.checked_out_consumable.validated_save()
        error = context.exception.error_dict["__all__"][0]
        self.assertEqual(
            error.message,
            f"Consumable pool does not have enough available capacity, "
            f"requesting {requested}, only {pool.available_quantity} available.",
        )

    def test_export_instance(self):
        """Test exporting the model to CSV."""
        csv = self.checked_out_consumable.to_csv()
        self.assertIsInstance(csv, tuple)
        self.assertEqual(len(csv), 3)
        self.assertEqual(csv[2], 5)
