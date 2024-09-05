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

"""Views for the Nautobot Consumables app."""
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from nautobot.core.views import generic
from nautobot.core.views.viewsets import NautobotUIViewSet
from nautobot.dcim.models import Device, Location
from nautobot.extras.models import CustomField

from nautobot_consumables import filters, forms, models, tables
from nautobot_consumables.api import serializers


class CheckedOutConsumableUIViewSet(NautobotUIViewSet):
    """UI view set for CheckedOutConsumables."""

    action_buttons = ("export",)
    bulk_update_form_class = forms.CheckedOutConsumableBulkEditForm
    filterset_class = filters.CheckedOutConsumableFilterSet
    filterset_form_class = forms.CheckedOutConsumableFilterForm
    form_class = forms.CheckedOutConsumableForm
    lookup_field = "pk"
    queryset = models.CheckedOutConsumable.objects.all()
    serializer_class = serializers.CheckedOutConsumableSerializer
    table_class = tables.CheckedOutConsumableTable

    def get_extra_context(self, request, instance=None):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        if self.action in ["bulk_update", "bulk_destroy"]:
            instances = self.queryset.filter(pk__in=self.pk_list)
            context["table"] = tables.CheckedOutConsumableBulkEditTable(instances, orderable=False)

        if self.action in ["destroy", "bulk_destroy"]:
            context["panel_class"] = "warning"
            context["button_class"] = "warning"

        return context


class ConsumableUIViewSet(NautobotUIViewSet):
    """UI view set for Consumables."""

    bulk_update_form_class = forms.ConsumableBulkEditForm
    filterset_class = filters.ConsumableFilterSet
    filterset_form_class = forms.ConsumableFilterForm
    form_class = forms.ConsumableForm
    lookup_field = "pk"
    queryset = models.Consumable.objects.all()
    serializer_class = serializers.ConsumableSerializer
    table_class = tables.ConsumableTable

    def get_extra_context(self, request, instance=None):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        if self.action == "create":
            context["demo"] = True

        if self.action == "retrieve":
            context["table_consumablepools"] = tables.ConsumablePoolDetailConsumableTable(
                models.ConsumablePool.objects.filter(consumable=instance.pk)
            )
            if request.user.has_perm("nautobot_consumables.change_consumablepool"):
                context["table_consumablepools"].columns.show("pk")

            context["disable_pagination"] = len(context["table_consumablepools"].rows) <= 25

        if self.action in ["bulk_update", "bulk_destroy"]:
            instances = self.queryset.filter(pk__in=self.pk_list)
            context["table"] = tables.ConsumableBulkEditTable(instances, orderable=False)
        return context

    def get_template_name(self) -> str:
        """Get the appropriate template for create and update actions."""
        if self.action in ("create", "update"):
            return "nautobot_consumables/json_form.html"

        return str(super().get_template_name())


class ConsumablePoolUIViewSet(NautobotUIViewSet):
    """UI view set for ConsumablePools."""

    bulk_update_form_class = forms.ConsumablePoolBulkEditForm
    filterset_class = filters.ConsumablePoolFilterSet
    filterset_form_class = forms.ConsumablePoolFilterForm
    form_class = forms.ConsumablePoolForm
    lookup_field = "pk"
    queryset = models.ConsumablePool.objects.all()
    serializer_class = serializers.ConsumablePoolSerializer
    table_class = tables.ConsumablePoolTable

    obj: models.ConsumablePool

    def get_extra_context(self, request, instance=None):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        if self.action == "retrieve":
            checked_out_consumables = models.CheckedOutConsumable.objects.filter(
                consumable_pool=instance,
            )
            context["table_checkedoutconsumables"] = tables.CheckedOutConsumableTable(
                checked_out_consumables
            )
            if request.user.has_perm("nautobot_consumables.change_checkedoutconsumable"):
                context["table_checkedoutconsumables"].columns.show("pk")

            context["disable_pagination"] = len(context["table_checkedoutconsumables"].rows) <= 25

        if self.action == "update":
            if instance is None:
                instance = self.get_object()

            context["display_warning"] = instance.used_quantity > 0
            context["checked_out"] = instance.used_quantity

        if self.action in ["bulk_update", "bulk_destroy"]:
            pools = self.queryset.filter(pk__in=self.pk_list)
            context["table"] = tables.ConsumablePoolBulkEditTable(pools, orderable=False)

            checked_out = 0
            for pool in pools:
                checked_out += pool.used_quantity
            context["display_warning"] = checked_out > 0

        return context

    def _process_bulk_update_form(self, form) -> None:  # pylint: disable=too-many-branches
        """Perform the actual work on a bulk update if the form is valid."""
        request = self.request
        queryset = self.get_queryset()
        new_location: Location | None = form.cleaned_data.get("location", None)
        new_quantity: int | None = form.cleaned_data.get("quantity", None)
        nullified_fields = request.POST.getlist("_nullify")
        form_cf_to_key = {
            f"cf_{cf.key}": cf.name for cf in CustomField.objects.get_for_model(queryset.model)
        }

        with transaction.atomic():
            updated_objs = []
            checked_in = 0
            for instance in queryset.filter(pk__in=form.cleaned_data["pk"]):
                self.obj = instance
                if new_location is not None and instance.location != new_location:
                    instance.location = new_location
                    self.logger.debug("Pool %s is moving to %s", instance, new_location)
                    for checked_out in instance.checked_out.all():
                        checked_in += checked_out.quantity
                        checked_out.delete()

                if new_quantity is not None and instance.quantity != new_quantity:
                    instance.quantity = new_quantity

                # Handle any assigned custom fields
                for field_name in getattr(form, "custom_fields", []):
                    if field_name in form.nullable_fields and field_name in nullified_fields:
                        instance.cf[form_cf_to_key[field_name]] = None
                    elif form.cleaned_data.get(field_name) not in (None, "", []):
                        instance.cf[form_cf_to_key[field_name]] = form.cleaned_data[field_name]

                instance.validated_save()
                updated_objs.append(instance)
                self.logger.debug("Saved %s (PK %s)", instance, instance.pk)

                if form.cleaned_data.get("add_tags", []):
                    instance.tags.add(*form.cleaned_data["add_tags"])
                if form.cleaned_data.get("remove_tags", []):
                    instance.tags.remove(*form.cleaned_data["remove_tags"])

                if hasattr(form, "save_relationships") and callable(form.save_relationships):
                    form.save_relationships(instance=instance, nullified_fields=nullified_fields)

                if hasattr(form, "save_note") and callable(form.save_note):
                    form.save_note(instance=instance, user=self.request.user)

            if queryset.filter(pk__in=[i.pk for i in updated_objs]).count() != len(updated_objs):
                raise ObjectDoesNotExist

        if updated_objs:
            message = (
                f"{len(updated_objs)} Pools changed ({checked_in} consumables checked back in)"
            )
            self.logger.info(message)
            messages.success(self.request, message)

        self.success_url = self.get_return_url(request)


class ConsumableTypeUIViewSet(NautobotUIViewSet):
    """UI view set for ConsumableTypes."""

    bulk_update_form_class = forms.ConsumableTypeBulkEditForm
    filterset_class = filters.ConsumableTypeFilterSet
    filterset_form_class = forms.ConsumableTypeFilterForm
    form_class = forms.ConsumableTypeForm
    lookup_field = "pk"
    queryset = models.ConsumableType.objects.all()
    serializer_class = serializers.ConsumableTypeSerializer
    table_class = tables.ConsumableTypeTable

    def get_extra_context(self, request, instance=None):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        if self.action == "retrieve":
            context["table_consumables"] = tables.ConsumableTable(
                models.Consumable.objects.filter(consumable_type=instance.pk)
            )
            if request.user.has_perm("nautobot_consumables.change_consumable"):
                context["table_consumables"].columns.show("pk")

            context["disable_pagination"] = len(context["table_consumables"].rows) <= 25

        return context

    def get_template_name(self) -> str:
        """Get the appropriate template for create and update actions."""
        if self.action in ("create", "update"):
            return "nautobot_consumables/json_form.html"

        return str(super().get_template_name())


class DeviceConsumablesViewTab(generic.ObjectView):
    """View for adding a Consumables tab to Device details."""

    queryset = Device.objects.all()
    template_name = "nautobot_consumables/device_consumables.html"

    def get_extra_context(self, request, instance):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        context["table_checkedoutconsumables"] = tables.CheckedOutConsumableDetailDeviceTabTable(
            models.CheckedOutConsumable.objects.filter(device__pk=instance.pk)
        )
        context["disable_pagination_checkedout"] = len(
            context["table_checkedoutconsumables"].rows
        ) <= 25

        context["table_consumablepools"] = tables.ConsumablePoolDetailLocationTabTable(
            models.ConsumablePool.objects.filter(location__pk=instance.location.pk)
            .exclude(checked_out__device__pk=instance.pk)
        )
        context["disable_pagination_pools"] = len(context["table_consumablepools"].rows) <= 25

        context["add_querystring"] = f"location={instance.location.pk}"

        return_url = [reverse(
            "plugins:nautobot_consumables:device_consumables_tab",
            kwargs={"pk": instance.pk},
        ), "tab=nautobot_consumables:1"]
        context["return_url"] = "?".join(return_url)

        return context


class LocationConsumablesViewTab(generic.ObjectView):
    """View for adding a Consumables tab to Location details."""

    queryset = Location.objects.all()
    template_name = "nautobot_consumables/location_consumables.html"

    def get_extra_context(self, request, instance):
        """Gather extra context for the views."""
        context = super().get_extra_context(request, instance)

        location_pools = models.ConsumablePool.objects.filter(location=instance.pk)
        context["table_consumablepools"] = tables.ConsumablePoolDetailLocationTabTable(
            location_pools
        )
        context["table_checkedoutconsumables"] = tables.CheckedOutConsumableDetailLocationTabTable(
            models.CheckedOutConsumable.objects.filter(consumable_pool__in=location_pools)
        )

        context["add_querystring"] = f"location={instance.pk}"

        context["disable_pagination_pools"] = len(context["table_consumablepools"].rows) <= 25
        context["disable_pagination_checkedout"] = len(
            context["table_checkedoutconsumables"].rows
        ) <= 25

        return_url = [reverse(
            "plugins:nautobot_consumables:location_consumables_tab",
            kwargs={"pk": instance.pk},
        ), "tab=nautobot_consumables:1"]
        context["return_url"] = "?".join(return_url)

        return context
