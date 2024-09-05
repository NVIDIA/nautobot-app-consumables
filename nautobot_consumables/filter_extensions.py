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

"""Extensions to add filtering for available and used consumables to Devices and Locations."""
from nautobot.apps.filters import FilterExtension, RelatedMembershipBooleanFilter
from nautobot.dcim.models import Device, Location


class DeviceFilterExtension(FilterExtension):  # pylint: disable=too-few-public-methods
    """Extend the DeviceFilterSet to add a search for checked out consumables."""

    model = Device

    filterset_fields = {
        "nautobot_consumables_has_checked_out_consumables": RelatedMembershipBooleanFilter(
            field_name="consumables",
            label="Has Checked Out Consumables",
        ),
    }


class LocationFilterExtension(FilterExtension):  # pylint: disable=too-few-public-methods
    """Extend the LocationFilterSet to add a search for available consumables."""

    model = Location

    filterset_fields = {
        "nautobot_consumables_has_pools": RelatedMembershipBooleanFilter(
            field_name="consumable_pools",
            label="Has Consumable Pools",
        ),
    }


filter_extensions = [LocationFilterExtension]
