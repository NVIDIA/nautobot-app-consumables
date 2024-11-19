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

"""API endpoint views for Nautobot Consumables."""
from nautobot.apps.api import NautobotModelViewSet

from nautobot_consumables import filters, models
from nautobot_consumables.api import serializers


class CheckedOutConsumableAPIViewSet(NautobotModelViewSet):
    """API view set for CheckedOutConsumable instances."""

    queryset = models.CheckedOutConsumable.objects.all()
    serializer_class = serializers.CheckedOutConsumableSerializer
    filterset_class = filters.CheckedOutConsumableFilterSet


class ConsumableAPIViewSet(NautobotModelViewSet):
    """API view set for Consumable instances."""

    queryset = models.Consumable.objects.all()
    serializer_class = serializers.ConsumableSerializer
    filterset_class = filters.ConsumableFilterSet


class ConsumablePoolAPIViewSet(NautobotModelViewSet):
    """API view set for ConsumablePool instances."""

    queryset = models.ConsumablePool.objects.all()
    serializer_class = serializers.ConsumablePoolSerializer
    filterset_class = filters.ConsumablePoolFilterSet


class ConsumableTypeAPIViewSet(NautobotModelViewSet):
    """API view set for ConsumableType instances."""

    queryset = models.ConsumableType.objects.all()
    serializer_class = serializers.ConsumableTypeSerializer
    filterset_class = filters.ConsumableTypeFilterSet
