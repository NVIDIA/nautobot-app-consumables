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

"""Filters for Nautobot Consumables models."""
from nautobot.core.filters import SearchFilter, TagFilter
from nautobot.extras.filters import NautobotFilterSet

from nautobot_consumables.models import (
    CheckedOutConsumable,
    Consumable,
    ConsumablePool,
    ConsumableType,
)


class CheckedOutConsumableFilterSet(NautobotFilterSet):
    """Filter set for CheckedOutConsumable instances."""

    q = SearchFilter(
        filter_predicates={
            "consumable_pool__name": "icontains",
            "device__name": "icontains",
        },
    )

    tags = TagFilter()

    class Meta:
        """CheckedOutConsumableFilter model options."""

        model = CheckedOutConsumable
        fields = CheckedOutConsumable.csv_headers


class ConsumableFilterSet(NautobotFilterSet):
    """Filter set for Consumable instances."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "consumable_type__name": "icontains",
            "manufacturer__name": "icontains",
            "product_id": "icontains",
        },
    )

    tags = TagFilter()

    class Meta:
        """ConsumableFilterSet model options."""

        model = Consumable
        fields = Consumable.csv_headers


class ConsumablePoolFilterSet(NautobotFilterSet):
    """Filter set for ConsumablePool instances."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "consumable__name": "icontains",
            "location__name": "icontains",
        }
    )

    tags = TagFilter()

    class Meta:
        """ConsumablePoolFilterSet model options."""

        model = ConsumablePool
        fields = ConsumablePool.csv_headers


class ConsumableTypeFilterSet(NautobotFilterSet):
    """Filter set for ConsumableType instances."""

    q = SearchFilter(filter_predicates={"name": "icontains"})
    tags = TagFilter()

    class Meta:
        """ConsumableTypeFilterSet model options."""

        model = ConsumableType
        fields = ConsumableType.csv_headers
