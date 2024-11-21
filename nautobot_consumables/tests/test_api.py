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

"""Test the Nautobot Consumables API endpoints."""

from django.contrib.auth import get_user_model
from nautobot.core.testing.api import APIViewTestCases
from nautobot.dcim.models import Device, Location, Manufacturer

from nautobot_consumables import models

User = get_user_model()


class CheckedOutConsumableAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the CheckedOutConsumable API."""

    model = models.CheckedOutConsumable
    brief_fields = ["display", "id", "quantity", "url"]
    bulk_update_data = {"quantity": 5}

    @classmethod
    def setUpTestData(cls):
        """Set up data for the tests."""
        cable_pool = models.ConsumablePool.objects.get(name="Cable 5 Pool 1")
        transceiver_pool = models.ConsumablePool.objects.get(name="Transceiver 5 Pool 1")
        generic_pool = models.ConsumablePool.objects.get(name="Generic 5 Pool 1")

        cls.create_data = [
            {
                "consumable_pool": cable_pool.pk,
                "device": Device.objects.filter(location=cable_pool.location).first().pk,
                "quantity": 10,
            },
            {
                "consumable_pool": transceiver_pool.pk,
                "device": Device.objects.filter(location=transceiver_pool.location).first().pk,
                "quantity": 10,
            },
            {
                "consumable_pool": generic_pool.pk,
                "device": Device.objects.filter(location=generic_pool.location).first().pk,
                "quantity": 10,
            },
        ]


class ConsumableAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Consumable API."""

    model = models.Consumable
    brief_fields = ["display", "id", "name", "url"]

    @classmethod
    def setUpTestData(cls):
        """Set up data for the tests."""
        cls.update_data = {"manufacturer": Manufacturer.objects.last().pk}
        cls.bulk_update_data = {"manufacturer": Manufacturer.objects.last().pk}

        models.Consumable.objects.create(
            name="Test Cable",
            manufacturer=Manufacturer.objects.first(),
            product_id="test_cable_001",
            consumable_type=models.ConsumableType.objects.get(name="Cable"),
            data={
                "color": "ffc107",
                "length": 25,
                "cable_type": "CAT6a",
                "connector": "8P8C",
                "length_unit": "m",
            },
        )
        models.Consumable.objects.create(
            name="Test Transceiver",
            manufacturer=Manufacturer.objects.first(),
            product_id="test_transceiver_001",
            consumable_type=models.ConsumableType.objects.get(name="Transceiver"),
            data={"reach": "LR", "form_factor": "QSFP-DD (400GE)"},
        )
        models.Consumable.objects.create(
            name="Test Generic",
            manufacturer=Manufacturer.objects.first(),
            product_id="test_generic_001",
            consumable_type=models.ConsumableType.objects.get(name="Generic"),
        )

        cls.create_data = [
            {
                "name": "Test Consumable 1",
                "consumable_type": models.ConsumableType.objects.get(name="Cable").pk,
                "manufacturer": Manufacturer.objects.first().pk,
                "product_id": "test_cable_0001",
                "data": {
                    "color": "ff9800",
                    "length": 50,
                    "cable_type": "CAT6a",
                    "connector": "8P8C",
                    "length_unit": "m",
                },
            },
            {
                "name": "Test Consumable 2",
                "consumable_type": models.ConsumableType.objects.get(name="Transceiver").pk,
                "manufacturer": Manufacturer.objects.first().pk,
                "product_id": "test_transceiver_0002",
                "data": {
                    "reach": "LR",
                    "form_factor": "QSFP-DD (400GE)",
                },
            },
            {
                "name": "Test Consumable 3",
                "consumable_type": models.ConsumableType.objects.get(name="Generic").pk,
                "manufacturer": Manufacturer.objects.first().pk,
                "product_id": "test_generic_0003",
                "data": {},
            },
        ]


class ConsumablePoolAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the ConsumablePool API."""

    model = models.ConsumablePool
    brief_fields = ["display", "id", "name", "quantity", "url"]

    @classmethod
    def setUpTestData(cls):
        """Set up data for the tests."""
        cls.update_data = {"location": Location.objects.last().pk}
        cls.bulk_update_data = {"location": Location.objects.last().pk}

        models.ConsumablePool.objects.create(
            name="Test Pool 1",
            consumable=models.Consumable.objects.get(name="Cable 4"),
            location=Location.objects.first(),
            quantity=39,
        )
        models.ConsumablePool.objects.create(
            name="Test Pool 2",
            consumable=models.Consumable.objects.get(name="Transceiver 4"),
            location=Location.objects.first(),
            quantity=39,
        )
        models.ConsumablePool.objects.create(
            name="Test Pool 3",
            consumable=models.Consumable.objects.get(name="Generic 4"),
            location=Location.objects.first(),
            quantity=39,
        )

        cls.create_data = [
            {
                "name": "Test Pool 4",
                "consumable": models.Consumable.objects.get(name="Cable 5").pk,
                "location": Location.objects.first().pk,
                "quantity": 42,
            },
            {
                "name": "Test Pool 5",
                "consumable": models.Consumable.objects.get(name="Transceiver 5").pk,
                "location": Location.objects.first().pk,
                "quantity": 42,
            },
            {
                "name": "Test Pool 6",
                "consumable": models.Consumable.objects.get(name="Generic 5").pk,
                "location": Location.objects.first().pk,
                "quantity": 42,
            },
        ]


class ConsumableTypeAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the ConsumableType API."""

    model = models.ConsumableType
    brief_fields = ["display", "id", "name", "url"]
    bulk_update_data = {"schema": {"type": "object", "properties": {}}}
    create_data = [
        {"name": "Test Consumable Type 4", "schema": {}},
        {"name": "Test Consumable Type 5", "schema": {}},
        {"name": "Test Consumable Type 6", "schema": {}},
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up data for the tests."""
        models.ConsumableType.objects.create(name="Test Consumable Type 1", schema={})
        models.ConsumableType.objects.create(name="Test Consumable Type 2", schema={})
        models.ConsumableType.objects.create(name="Test Consumable Type 3", schema={})
