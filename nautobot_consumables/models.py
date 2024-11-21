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

"""Models for Nautobot Consumables Tracking."""

from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey
from jsonschema import draft4_format_checker  # pylint: disable=no-name-in-module
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
from jsonschema.validators import Draft4Validator
from nautobot.core.models.fields import NaturalOrderingField
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.utils import extras_features


def get_key_detail(key: str, value: Any, schema: Any) -> dict[str, Any]:
    """Get details for model keys."""
    properties: dict[str, Any] = {"value": value}

    if title := schema.get("title"):
        properties["title"] = title
        if title.lower() == "color":
            properties["background_color"] = value
    else:
        properties["title"] = key

    if schema.get("type") == "array":
        properties["array"] = True

    if schema.get("enum") and schema.get("options", {}).get("enum_titles"):
        properties["value"] = schema["options"]["enum_titles"][schema["enum"].index(value)]

    if property_order := schema.get("propertyOrder"):
        properties["propertyOrder"] = property_order

    return properties


class JSONModel(PrimaryModel):
    """JSON data model for objects that can be validated against a schema."""

    data = models.JSONField(blank=True, null=True)
    schema = models.JSONField(blank=True, null=True)

    class Meta:
        """Metaclass attributes."""

        abstract = True

    @property
    def template_details(self) -> list[tuple[str, Any]]:
        """Merge the details and schema for nice output in templates."""
        details: dict[str, Any] = {}
        detail_list: list[tuple[str, Any]] = []

        if isinstance(self.schema, dict) and isinstance(self.data, dict):
            for key, value in self.schema.get("properties", {}).items():
                details[key] = get_key_detail(key, self.data.get(key), value)

        # Find any properties named "*_unit" and combine their values with the corresponding
        # property value, e.g. `length = 1` and `length_unit = "ft"` combine to `1 ft`
        assert isinstance(self.schema, dict)  # noqa: S101
        for unit_key in [key for key in self.schema.get("properties", {}) if key.endswith("unit")]:
            prop = unit_key.strip("_unit")
            if self.schema.get("properties", {}).get(prop):
                details[prop]["value"] = f"{self.data.get(prop)}{self.data.get(unit_key)}"
                details.pop(unit_key, None)

        if details:
            detail_list = sorted(details.items(), key=lambda x: x[1].get("propertyOrder", 1000))

        return detail_list

    def clean(self):
        """Validate the data."""
        super().clean()

        if self.schema:
            try:
                Draft4Validator.check_schema(self.schema)
            except SchemaError as error:
                path = "']['".join(error.path)
                raise ValidationError(f"{error.message} on ['{path}']") from error

            if self.data:
                try:
                    Draft4Validator(self.schema, format_checker=draft4_format_checker).validate(
                        self.data
                    )
                except JSONSchemaValidationError as error:
                    message = [f"Data validation against schema schema failed: {error.message}"]
                    if error.path:
                        sep = "']['"
                        message.extend(["on", f"['{sep.join(error.path)}']"])

                    raise ValidationError(" ".join(message)) from error


class ConsumableType(JSONModel):
    """
    A ConsumableType defines a type of consumable that can be used, e.g. a cable.

    The ConsumableType model allows users to define custom product types using a JSON schema to
    define the characteristics and options for the consumable items.
    """

    name = models.CharField(max_length=100, db_index=True, unique=True)
    _name = NaturalOrderingField(target_field="name", max_length=255, blank=True, db_index=True)

    class Meta:
        """ConsumableType model options."""

        verbose_name = "Consumable Type"
        verbose_name_plural = "Consumable Types"

    def __str__(self) -> str:
        """Default string representation of the ConsumableType."""
        return str(self.name)


class Consumable(JSONModel):
    """
    A Consumable is a discrete version of a ConsumableType.

    For example, for a ConsumableType of `cable`, a Consumable might be `3ft Cat6 Ethernet, Red`.
    """

    consumable_type: ForeignKey = models.ForeignKey(to=ConsumableType, on_delete=models.PROTECT)

    name = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        help_text="The name of the Consumable product, e.g. 'Red 3ft Cat6 Ethernet'.",
    )
    _name = NaturalOrderingField(target_field="name", max_length=255, blank=True, db_index=True)

    manufacturer: ForeignKey = models.ForeignKey(
        to="dcim.Manufacturer",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    product_id = models.CharField(
        max_length=100,
        help_text="Product ID/Part number/SKU",
        verbose_name="Product ID",
    )

    class Meta:
        """Consumable model options."""

        unique_together = [["manufacturer", "consumable_type", "product_id"]]
        ordering = ["consumable_type", "_name"]
        verbose_name = "Consumable"
        verbose_name_plural = "Consumables"

    def __str__(self) -> str:
        """Default string representation of the Consumable."""
        return str(self.name)

    def clean(self):
        """Validate a Consumable instance."""
        if self.present_in_database:
            obj = self.__class__.objects.get(pk=self.pk)
            if self.consumable_type != obj.consumable_type:
                raise ValidationError("ConsumableType cannot be changed after creation.")
        else:
            # If this is a new Consumable, copy the schema from its ConsumableType
            self.schema = self.consumable_type.schema

        super().clean()

    def save(self, *args, **kwargs):
        """Save the Consumable instance to the database."""
        # If this is a new Consumable, copy the schema from its ConsumableType
        if not self.present_in_database:
            if self.schema is None:
                self.schema = self.consumable_type.schema
        else:
            # Make sure ConsumableType does not change
            self.consumable_type = self.__class__.objects.get(pk=self.pk).consumable_type

        super().save(*args, **kwargs)


@extras_features("custom_fields", "custom_links", "graphql", "relationships")
class ConsumablePool(PrimaryModel):
    """A pool of Consumable items available for use at a Location."""

    consumable: ForeignKey = models.ForeignKey(
        to="Consumable",
        on_delete=models.PROTECT,
        related_name="pools",
    )

    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="A descriptive name for the Consumable pool",
    )
    _name = NaturalOrderingField(target_field="name", max_length=255, blank=True, db_index=True)

    location: ForeignKey = models.ForeignKey(
        to="dcim.Location",
        on_delete=models.PROTECT,
        related_name="consumable_pools",
    )

    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        """ConsumablePool model options."""

        unique_together = [["consumable", "location", "name"]]
        ordering = ["consumable", "location", "name"]
        verbose_name = "Consumable Pool"
        verbose_name_plural = "Consumable Pools"

    def __str__(self) -> str:
        """Default string representation of the ConsumablePool."""
        return f"{self.name} ({self.location})"

    @property
    def used_quantity(self) -> int:
        """Calculate how many Consumable in the pool have been checked out."""
        used = 0
        for checked_out in self.checked_out.all():
            used += checked_out.quantity

        return used

    @property
    def available_quantity(self) -> int:
        """Calculate how many Consumable in the pool are available to be checked out."""
        return self.quantity - self.used_quantity

    def clean(self):
        """Validate a ConsumablePool instance."""
        super().clean()

        if self.present_in_database:
            obj = self.__class__.objects.get(pk=self.pk)
            if self.consumable != obj.consumable:
                raise ValidationError("Consumable cannot be changed after creation.")


@extras_features("custom_fields", "custom_links", "graphql", "relationships")
class CheckedOutConsumable(PrimaryModel):
    """ConsumablePool items that have been checked out for use on a device."""

    consumable_pool: ForeignKey = models.ForeignKey(
        to="ConsumablePool",
        on_delete=models.PROTECT,
        related_name="checked_out",
    )

    device: ForeignKey = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.PROTECT,
        related_name="consumables",
    )

    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        """CheckedOutConsumable model options."""

        verbose_name = "Checked Out Consumable"
        verbose_name_plural = "Checked Out Consumables"
        unique_together = [["device", "consumable_pool"]]
        ordering = ["consumable_pool", "device"]

    def __str__(self) -> str:
        """Default string representation of the CheckedOutConsumable."""
        parts = [
            self.device.name if hasattr(self, "device") else "No Device",
            self.consumable_pool.name if hasattr(self, "consumable_pool") else "No Pool",
        ]
        return " | ".join(parts)

    def clean(self):
        """Validate a CheckedOutConsumable instance."""
        super().clean()

        if hasattr(self, "device") and hasattr(self, "consumable_pool"):
            if self.device.location != self.consumable_pool.location:  # pylint: disable=no-member
                # pylint: disable=no-member
                raise ValidationError(
                    f"Cannot check out consumables from Pool {self.consumable_pool.name} in "
                    f"location {self.consumable_pool.location.name} to Device {self.device.name} "
                    f"in location {self.device.location.name}"
                )

            previous_quantity = 0
            if self.present_in_database:
                obj = self.__class__.objects.get(pk=self.pk)
                previous_quantity = obj.quantity

            # pylint: disable=no-member
            maximum_quantity = previous_quantity + self.consumable_pool.available_quantity
            if self.quantity > maximum_quantity:
                raise ValidationError(
                    f"Consumable pool does not have enough available capacity, requesting "
                    f"{self.quantity}, only {maximum_quantity} available."
                )
