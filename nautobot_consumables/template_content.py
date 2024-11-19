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

"""Extend the built-in templates with Consumables information."""
from typing import Any
from uuid import UUID

from django.urls import reverse
from nautobot.apps.ui import TemplateExtension

from nautobot_consumables.models import CheckedOutConsumable, ConsumablePool

# pylint: disable=abstract-method


class DeviceConsumablesCount(TemplateExtension):
    """Extend the dcim.device model templates."""

    model = "dcim.device"
    obj_pk: UUID
    consumables_count: int
    pools_count: int

    def __init__(self, context: Any) -> None:
        """Calculate the number of checked out consumables."""
        super().__init__(context)

        self.obj_pk = context["object"].pk
        self.consumables_count = CheckedOutConsumable.objects.filter(
            device__pk=self.obj_pk
        ).count()
        self.pools_count = ConsumablePool.objects.filter(
            location__pk=context["object"].location.pk
        ).count()

    def detail_tabs(self):
        """Add a tab for Consumables to the details page."""
        tabs = []

        if self.consumables_count > 0 or self.pools_count > 0:
            tabs.append(
                {
                    "title": self.render(
                        "nautobot_consumables/inc/tab_title.html",
                        extra_context={
                            "title": "Consumables",
                            "item_count": self.consumables_count,
                        },
                    ),
                    "url": reverse(
                        "plugins:nautobot_consumables:device_consumables_tab",
                        kwargs={"pk": self.obj_pk},
                    ),
                },
            )

        return tabs


class LocationConsumablesCount(TemplateExtension):
    """Extend the dcim.location model templates."""

    model = "dcim.location"
    obj_pk: UUID
    pools_count: int

    def __init__(self, context: Any) -> None:
        """Calculate the number of child consumables."""
        super().__init__(context)

        self.obj_pk = context["object"].pk
        self.pools_count = ConsumablePool.objects.filter(location__pk=self.obj_pk).count()

    def detail_tabs(self):
        """Add a tab for Consumables to the details page."""
        tabs = []

        if self.pools_count > 0:
            tabs.append(
                {
                    "title": self.render(
                        "nautobot_consumables/inc/tab_title.html",
                        extra_context={"title": "Consumables", "item_count": self.pools_count},
                    ),
                    "url": reverse(
                        "plugins:nautobot_consumables:location_consumables_tab",
                        kwargs={"pk": self.obj_pk},
                    ),
                },
            )

        return tabs


template_extensions = [DeviceConsumablesCount, LocationConsumablesCount]
