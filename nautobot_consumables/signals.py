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

"""Signal handlers for Nautobot Consumables app."""
import logging
from typing import TypedDict

from nautobot.apps.choices import (
    ColorChoices,
    CableTypeChoices,
    InterfaceTypeChoices,
    PortTypeChoices,
)

from nautobot_consumables.models import ConsumableType

logger = logging.getLogger("rq.worker")


class JSONSchemaData(TypedDict, total=False):
    """Represents the JSON schema dict with types."""
    title: str
    type: str
    propertyOrder: int  # pylint: disable=invalid-name
    enum: list[str]
    options: dict[str, list[str]]


def create_json_schema_type(title: str, values_dict: dict, property_order: int | None = None):
    """Create a properly formatted schema type from dict."""
    data: JSONSchemaData = {
        "title": title,
        "type": "string",
        "enum": [],
    }

    if property_order:
        data["propertyOrder"] = property_order

    if title.lower() == "color":
        data["options"] = {"enum_titles": []}

    for item, value in values_dict.items():
        if title.lower() == "color":
            data["enum"].append(item)
            data["options"]["enum_titles"].append(value)
        else:
            data["enum"].append(value)

    return data


def post_migrate_create_defaults(*args, **kwargs):  # pylint: disable=W0613
    """Callback function for post_migrate signal -- create default ConsumableTypes."""
    form_factors = {}
    for key, value in InterfaceTypeChoices.CHOICES:
        if key in ["Ethernet (modular)", "FibreChannel", "InfiniBand", "Other"]:
            form_factors.update(dict(value))

    transceiver_schema = {
        "type": "object",
        "title": "Transceiver Details",
        "required": ["form_factor", "reach"],
        "properties": {
            "form_factor": create_json_schema_type("Form Factor", form_factors, 10),
            "reach": create_json_schema_type("Reach", {"lr": "LR", "sr": "SR", "er": "ER"}, 20),
        },
    }

    cable_schema = {
        "type": "object",
        "title": "Cable Details",
        "required": ["cable_type", "connector", "length", "length_unit", "color"],
        "properties": {
            "cable_type": create_json_schema_type("Cable Type", CableTypeChoices.as_dict(), 10),
            "connector": create_json_schema_type("Connector", PortTypeChoices.as_dict(), 20),
            "length": {"title": "Length", "type": "integer", "propertyOrder": 30},
            "length_unit": {
                "title": "Unit",
                "type": "string",
                "enum": ["m", "cm", "ft", "in"],
                "options": {"enum_titles": ["Meters", "Centimeters", "Feet", "Inches"]},
                "propertyOrder": 40,
            },
            "color": create_json_schema_type("Color", ColorChoices.as_dict(), 50),
        },
    }

    ConsumableType.objects.update_or_create(name="Generic", defaults={"schema": {}})
    ConsumableType.objects.update_or_create(
        name="Transceiver",
        defaults={"schema": transceiver_schema},
    )
    ConsumableType.objects.update_or_create(name="Cable", defaults={"schema": cable_schema})
