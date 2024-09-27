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

"""Forms for Nautobot Consumables models."""
from typing import Any

from django import forms
from nautobot.core.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from nautobot.dcim.models import Device, Location, Manufacturer
from nautobot.extras.forms import (
    CustomFieldModelCSVForm,
    CustomFieldModelFilterFormMixin,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    TagsBulkEditFormMixin,
)

from nautobot_consumables import models
from nautobot_consumables.fields import ConsumablesTypeJSONField


class ConsumableJSONFormMixin:  # pylint: disable=too-few-public-methods
    """Set the default exclude_list for Consumable JSON forms."""

    exclude_list = ["tags", "object_note", "schema", "data"]


class ConsumablesBaseModelForm(NautobotModelForm):
    """Default form init to handle disabling fields."""

    disabled: list[str] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize form and check for disabled fields."""
        super().__init__(*args, **kwargs)

        # If any of the `disabled` fields are set, either in the instance being updated, or in
        # the initial data, disable them in the UI
        for field in self.disabled:
            if (getattr(self.instance, field, None) is not None
                    or self.initial.get(field, None) is not None):
                self.fields[field].disabled = True


# Checked Out Consumables
class CheckedOutConsumableBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing CheckedOutConsumables."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.CheckedOutConsumable.objects.all(),
        widget=forms.MultipleHiddenInput,
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )

    quantity = forms.IntegerField(min_value=1, required=False)

    class Meta:
        """CheckedOutConsumableBulkEditForm model options."""


class CheckedOutConsumableCSVForm(CustomFieldModelCSVForm):
    """Form for importing a CheckedOutConsumable from a CSV file."""

    class Meta:
        """CheckedOutConsumableCSVForm model options."""

        model = models.CheckedOutConsumable
        fields = models.CheckedOutConsumable.csv_headers


class CheckedOutConsumableFilterForm(NautobotFilterForm, CustomFieldModelFilterFormMixin):
    """Form for filtering CheckedOutConsumable instances."""

    model = models.CheckedOutConsumable

    field_order = ["q", "consumable_pool", "device", "quantity"]
    q = forms.CharField(required=False, label="Search")

    consumable_pool = DynamicModelMultipleChoiceField(
        queryset=models.ConsumablePool.objects.all(),
        required=False,
    )

    device = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)


class CheckedOutConsumableForm(ConsumablesBaseModelForm):
    """Form for creating or editing a CheckedOutConsumable instance."""

    consumable_pool = DynamicModelChoiceField(
        queryset=models.ConsumablePool.objects.all(),
        label="Consumable Pool",
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label="Device",
    )

    quantity = forms.IntegerField(min_value=1)

    # Prevent users from changing the consumable pool or device once created
    disabled = ["consumable_pool", "device"]

    class Meta:
        """CheckedOutConsumableForm model options."""

        model = models.CheckedOutConsumable
        fields = [*models.CheckedOutConsumable.csv_headers, "tags"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize form and check for proper fields for the assigned consumable_pool."""
        super().__init__(*args, **kwargs)

        if pool := getattr(
            self.instance,
            "consumable_pool",
            models.ConsumablePool.objects.filter(
                pk=self.initial.get("consumable_pool", None)
            ).first()
        ):
            # If `device` is not set in the instance, or in the initial data, limit its
            # choices to those assigned to the same location as the ConsumablePool
            if getattr(self.instance, "device", self.initial.get("device", None)) is None:
                self.fields["device"].widget.add_query_param("location", pool.location.id)

            if getattr(self.instance, "quantity", None) is not None:
                max_quantity = self.instance.quantity + pool.available_quantity
                self.fields["quantity"].widget.attrs["max"] = max_quantity
                self.fields["quantity"].help_text = f"Max: {max_quantity}"
            else:
                self.fields["quantity"].widget.attrs["max"] = pool.available_quantity
                self.fields["quantity"].help_text = f"Max: {pool.available_quantity}"

        if self.initial.get("quantity", self.data.get("quantity", None)) is None:
            self.initial["quantity"] = 1


# Consumables
class ConsumableBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing Consumables."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.Consumable.objects.all(),
        widget=forms.MultipleHiddenInput,
    )

    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
    )

    class Meta:
        """ConsumableBulkEditForm model options."""


class ConsumableCSVForm(CustomFieldModelCSVForm):
    """Form for importing a Consumable from a CSV file."""

    class Meta:
        """ConsumableCSVForm model options."""

        model = models.Consumable
        fields = models.Consumable.csv_headers


class ConsumableFilterForm(NautobotFilterForm, CustomFieldModelFilterFormMixin):
    """Form for filtering Consumable instances."""

    model = models.Consumable

    field_order = ["q", "consumable_type", "manufacturer", "name", "product_id"]
    q = forms.CharField(required=False, label="Search")

    consumable_type = DynamicModelMultipleChoiceField(
        queryset=models.ConsumableType.objects.all(),
        required=False,
    )

    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
    )


class ConsumableForm(ConsumablesBaseModelForm, ConsumableJSONFormMixin):
    """Form for creating or editing a Consumable instance."""

    consumable_type = DynamicModelChoiceField(queryset=models.ConsumableType.objects.all())

    manufacturer = DynamicModelChoiceField(queryset=Manufacturer.objects.all(), required=False)

    disabled = ["consumable_type"]

    class Meta:
        """ConsumableForm model options."""

        model = models.Consumable
        fields = [*models.Consumable.csv_headers, "tags"]


# Consumable Pools
class ConsumablePoolBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing ConsumablePools."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.ConsumablePool.objects.all(),
        widget=forms.MultipleHiddenInput,
    )

    location = DynamicModelChoiceField(queryset=Location.objects.all(), required=False)
    quantity = forms.IntegerField(min_value=1, required=False)

    class Meta:
        """ConsumablePoolBulkEditForm model options."""


class ConsumablePoolCSVForm(CustomFieldModelCSVForm):
    """Form for importing a ConsumablePool from a CSV file."""

    class Meta:
        """ConsumablePoolCSVForm model options."""

        model = models.ConsumablePool
        fields = models.ConsumablePool.csv_headers


class ConsumablePoolFilterForm(NautobotFilterForm, CustomFieldModelFilterFormMixin):
    """Form for filtering ConsumablePool instances."""

    model = models.ConsumablePool

    field_order = ["q", "consumable", "name", "location", "quantity"]
    q = forms.CharField(required=False, label="Search")

    consumable = DynamicModelMultipleChoiceField(queryset=models.Consumable.objects.all(), required=False)
    location = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), required=False)


class ConsumablePoolForm(ConsumablesBaseModelForm, ConsumableJSONFormMixin):
    """Form for creating or editing a ConsumablePool instance."""

    consumable = DynamicModelChoiceField(
        queryset=models.Consumable.objects.all(),
        label="Consumable",
    )

    location = DynamicModelChoiceField(queryset=Location.objects.all())

    # Prevent users from changing the consumable once created
    disabled = ["consumable"]

    class Meta:
        """ConsumablePoolForm model options."""

        model = models.ConsumablePool
        fields = [*models.ConsumablePool.csv_headers, "tags"]


# Consumable Types
class ConsumableTypeBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing ConsumableTypes."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.ConsumableType.objects.all(),
        widget=forms.MultipleHiddenInput,
    )

    class Meta:
        """ConsumableTypeBulkEditForm model options."""


class ConsumableTypeCSVForm(CustomFieldModelCSVForm):
    """Form for importing a ConsumableType from a CSV file."""

    class Meta:
        """ConsumableTypeCSVForm model options."""

        model = models.ConsumableType
        fields = models.ConsumableType.csv_headers


class ConsumableTypeFilterForm(NautobotFilterForm):
    """Form for filtering ConsumableType instances."""

    model = models.ConsumableType

    field_order = ["q", "name"]
    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)


class ConsumableTypeForm(NautobotModelForm, ConsumableJSONFormMixin):
    """Form for creating or editing a ConsumableType instance."""

    schema = ConsumablesTypeJSONField(label="", required=False)

    class Meta:
        """ConsumableTypeForm model options."""

        model = models.ConsumableType
        fields = [*models.ConsumableType.csv_headers, "tags"]
