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

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin
from rest_framework.serializers import HyperlinkedIdentityField

from nautobot_consumables import models


class CheckedOutConsumableSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the CheckedOutConsumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:checkedoutconsumable-detail",
    )

    class Meta:
        """CheckedOutConsumableSerializer model options."""

        model = models.CheckedOutConsumable
        fields = "__all__"


class ConsumableSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the Consumable model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumable-detail",
    )

    class Meta:
        """ConsumableSerializer model options."""

        model = models.Consumable
        fields = "__all__"


class ConsumablePoolSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the ConsumablePool model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumablepool-detail",
    )

    class Meta:
        """ConsumablePoolSerializer model options."""

        model = models.ConsumablePool
        fields = "__all__"


class ConsumableTypeSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """API serializer for the ConsumableType model."""

    url = HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_consumables-api:consumabletype-detail",
    )

    class Meta:
        """ConsumableTypeSerializer model options."""

        model = models.ConsumableType
        fields = "__all__"
