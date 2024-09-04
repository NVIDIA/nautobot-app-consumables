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

"""Tables for Nautobot Consumables models."""
import django_tables2 as tables
from django_tables2.utils import Accessor
from nautobot.utilities.tables import (
    BaseTable,
    ButtonsColumn,
    TagColumn,
    ToggleColumn,
)

from nautobot_consumables import models

# pylint: disable=too-few-public-methods


__all__ = [
    "CheckedOutConsumableBulkEditTable",
    "CheckedOutConsumableDetailDeviceTabTable",
    "CheckedOutConsumableDetailLocationTabTable",
    "CheckedOutConsumableTable",
    "ConsumableBulkEditTable",
    "ConsumablePoolBulkEditTable",
    "ConsumablePoolDetailConsumableTable",
    "ConsumablePoolDetailLocationTabTable",
    "ConsumablePoolTable",
    "ConsumableTable",
    "ConsumableTypeTable",
]


class CheckedOutConsumableBulkEditTable(BaseTable):
    """Table view for bulk-editing CheckedOutConsumable instances."""

    class Meta(BaseTable.Meta):
        """CheckedOutConsumableBulkEditTable model options."""

        model = models.CheckedOutConsumable
        fields = ["consumable_pool", "device", "quantity"]


class CheckedOutConsumableDetailDeviceTabTable(BaseTable):
    """Table view for CheckedOutConsumable instances associated with a Device."""

    pk = ToggleColumn()
    consumable_pool = tables.Column(linkify=True)
    location = tables.Column(linkify=True, accessor=Accessor("consumable_pool.location"))
    tags = TagColumn(url_name="plugins:nautobot_consumables:checkedoutconsumable_list")

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/checkedoutconsumable.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """CheckedOutConsumableDetailDeviceTabTable model options."""

        model = models.CheckedOutConsumable
        fields = ["pk", "consumable_pool", "location", "quantity", "tags", "actions"]


class CheckedOutConsumableDetailLocationTabTable(BaseTable):
    """Table view for CheckedOutConsumable instances associated with a Location."""

    pk = ToggleColumn()
    consumable_pool = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    tags = TagColumn(url_name="plugins:nautobot_consumables:checkedoutconsumable_list")

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/checkedoutconsumable.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """CheckedOutConsumableDetailLocationTabTable model options."""

        model = models.CheckedOutConsumable
        fields = ["pk", "consumable_pool", "device", "quantity", "tags", "actions"]


class CheckedOutConsumableTable(BaseTable):
    """Table view for CheckedOutConsumable instances."""

    pk = ToggleColumn()
    id = tables.Column(linkify=True)
    consumable_pool = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    location = tables.Column(linkify=True, accessor=Accessor("consumable_pool.location"))
    tags = TagColumn(url_name="plugins:nautobot_consumables:checkedoutconsumable_list")

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/checkedoutconsumable.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """CheckedOutConsumableTable model options."""

        model = models.CheckedOutConsumable
        fields = [
            "pk",
            "id",
            "consumable_pool",
            "device",
            "location",
            "quantity",
            "tags",
            "actions",
        ]
        default_columns = [
            "pk",
            "id",
            "consumable_pool",
            "device",
            "location",
            "quantity",
            "actions",
        ]


class ConsumableBulkEditTable(BaseTable):
    """Table view for bulk-editing Consumable instances."""

    class Meta(BaseTable.Meta):
        """ConsumableBulkEditTable model options."""

        model = models.Consumable
        fields = ["name", "consumable_type", "manufacturer", "product_id"]


class ConsumableTable(BaseTable):
    """Table view for Consumable instances."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    consumable_type = tables.Column(linkify=True)
    manufacturer = tables.Column(linkify=True)
    actions = ButtonsColumn(models.Consumable, buttons=("edit", "delete"), pk_field="pk")

    class Meta(BaseTable.Meta):
        """ConsumableTable model options."""

        model = models.Consumable
        fields = ["pk", "name", "consumable_type", "manufacturer", "product_id", "actions"]


class ConsumablePoolBulkEditTable(BaseTable):
    """Table view for bulk-editing ConsumablePool instances."""

    class Meta(BaseTable.Meta):
        """ConsumablePoolBulkEditTable model options."""

        model = models.ConsumablePool
        fields = ["pk", "name", "consumable", "location", "quantity"]


class ConsumablePoolDetailConsumableTable(BaseTable):
    """Table view for ConsumablePool instances associated with a Consumable instance."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    location = tables.Column(linkify=True)

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/consumable_consumablepool.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """ConsumablePoolDetailConsumableTable model options."""

        model = models.ConsumablePool
        fields = [
            "pk",
            "name",
            "location",
            "quantity",
            "available_quantity",
            "used_quantity",
            "actions",
        ]


class ConsumablePoolDetailLocationTabTable(BaseTable):
    """Table view for ConsumablePool instances associated with a Location."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    consumable = tables.Column(linkify=True)

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/consumablepool.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """ConsumablePoolDetailLocationTabTable model options."""

        model = models.ConsumablePool
        fields = [
            "pk",
            "name",
            "consumable",
            "quantity",
            "available_quantity",
            "used_quantity",
            "actions",
        ]


class ConsumablePoolTable(BaseTable):
    """Table view for ConsumablePool instances."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    consumable = tables.Column(linkify=True)
    location = tables.Column(linkify=True)

    actions = tables.TemplateColumn(
        template_name="nautobot_consumables/inc/actions/consumablepool.html",
        orderable=False,
        verbose_name="",
        attrs={"td": {"class": "text-right text-nowrap noprint"}},
    )

    class Meta(BaseTable.Meta):
        """ConsumablePoolTable model options."""

        model = models.ConsumablePool
        fields = [
            "pk",
            "name",
            "consumable",
            "location",
            "quantity",
            "available_quantity",
            "used_quantity",
            "actions",
        ]


class ConsumableTypeTable(BaseTable):
    """Table view for ConsumableType instances."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.ConsumableType, buttons=("edit", "delete"), pk_field="pk")

    class Meta(BaseTable.Meta):
        """ConsumableTypeTable model options."""

        model = models.ConsumableType
        fields = ["pk", "name", "actions"]
