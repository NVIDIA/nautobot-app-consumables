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

"""Serializers for Nautobot Consumables API endpoints."""
from nautobot.core.api import WritableNestedSerializer
from nautobot.dcim.api.nested_serializers import (
    NestedLocationSerializer,
    NestedDeviceSerializer,
    NestedManufacturerSerializer,
)
from nautobot.extras.api.serializers import NautobotModelSerializer, TaggedModelSerializerMixin
from rest_framework.serializers import HyperlinkedIdentityField

from nautobot_consumables import models


class NestedCheckedOutConsumableSerializer(WritableNestedSerializer):
    """Nested API serializer for the CheckedOutConsumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:checkedoutconsumable-detail",
    )

    class Meta:
        """NestedCheckedOutConsumableSerializer model options."""

        model = models.CheckedOutConsumable
        fields = ["id", "url", "quantity"]


class NestedConsumableSerializer(WritableNestedSerializer):
    """Nested API serializer for the Consumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumable-detail",
    )

    class Meta:
        """NestedConsumableSerializer model options."""

        model = models.Consumable
        fields = ["id", "url", "name"]


class NestedConsumablePoolSerializer(WritableNestedSerializer):
    """Nested API serializer for the ConsumablePool model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumablepool-detail",
    )

    class Meta:
        """NestedConsumablePoolSerializer model options."""

        model = models.ConsumablePool
        fields = ["id", "url", "name", "quantity"]


class NestedConsumableTypeSerializer(WritableNestedSerializer):
    """Nested API serializer for the ConsumableType model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumabletype-detail",
    )

    class Meta:
        """NestedConsumableTypeSerializer model options."""

        model = models.ConsumableType
        fields = ["id", "url", "name"]


class CheckedOutConsumableSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the CheckedOutConsumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:checkedoutconsumable-detail",
    )

    consumable_pool = NestedConsumablePoolSerializer()
    device = NestedDeviceSerializer()

    class Meta:
        """CheckedOutConsumableSerializer model options."""

        model = models.CheckedOutConsumable
        fields = ["id", "url", "consumable_pool", "device", "quantity", "tags"]


class ConsumableSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the Consumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumable-detail",
    )

    consumable_type = NestedConsumableTypeSerializer()
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        """ConsumableSerializer model options."""

        model = models.Consumable
        fields = [
            "id",
            "url",
            "name",
            "consumable_type",
            "manufacturer",
            "product_id",
            "data",
            "schema",
            "tags",
        ]


class ConsumablePoolSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the ConsumablePool model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumablepool-detail",
    )

    consumable = NestedConsumableSerializer()
    location = NestedLocationSerializer()

    class Meta:
        """ConsumablePoolSerializer model options."""

        model = models.ConsumablePool
        fields = ["id", "url", "name", "consumable", "location", "quantity", "tags"]


class ConsumableTypeSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the ConsumableType model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumabletype-detail",
    )

    class Meta:
        """ConsumableTypeSerializer model options."""

        model = models.ConsumableType
        fields = ["id", "url", "name", "schema", "tags"]
