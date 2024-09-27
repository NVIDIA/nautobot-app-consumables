"""Tests for template extensions defined in the Consumables app."""
from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings
from nautobot.core.testing import extract_page_body
from nautobot.core.testing.views import ModelViewTestCase
from nautobot.dcim.models import Device, DeviceType, Location
from nautobot.users.models import ObjectPermission
from nautobot.extras.models import Role, Status


class DeviceViewTemplateExtensionsTestCase(ModelViewTestCase):
    """Test the template extensions on a device detail view."""

    model = Device

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_get_instance_with_consumables(self):
        """Test that the Consumables tab appears in the detail view."""
        instance = self._get_queryset().filter(consumables__isnull=False).first()

        obj_perm = ObjectPermission(name="Test Permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        response_body = extract_page_body(response.content.decode(response.charset))

        self.assertIn(
            "consumables?tab=nautobot_consumables:1",
            response_body,
            msg=response_body
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_get_instance_without_consumables(self):
        """Test that the Consumables tab does not appear in the detail view."""
        location = Location.objects.filter(
            consumable_pools__isnull=True,
            location_type__nestable=True,
        ).first()
        site = location.site
        if site is None:
            site = location.ancestors().filter(site__isnull=False).first().site

        instance = self.model.objects.create(
            name="Test Device",
            device_type=DeviceType.objects.first(),
            device_role=Role.objects.first(),
            site=site,
            location=location,
            status=Status.objects.get_for_model(self.model).first(),
        )

        obj_perm = ObjectPermission(name="Test Permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        response_body = extract_page_body(response.content.decode(response.charset))

        self.assertNotIn(
            "consumables?tab=nautobot_consumables:1",
            response_body,
            msg=response_body
        )


class LocationViewTemplateExtensionsTestCase(ModelViewTestCase):
    """Test the template extensions on a device detail view."""

    model = Location

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_get_instance_with_consumable_pools(self):
        """Test that the Consumables tab appears in the detail view."""
        instance = self._get_queryset().filter(consumable_pools__isnull=False).first()

        obj_perm = ObjectPermission(name="Test Permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        response_body = extract_page_body(response.content.decode(response.charset))

        self.assertIn(
            "consumables?tab=nautobot_consumables:1",
            response_body,
            msg=response_body
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_get_instance_without_consumable_pools(self):
        """Test that the Consumables tab does not appear in the detail view."""
        instance = self._get_queryset().filter(consumable_pools__isnull=True).first()

        obj_perm = ObjectPermission(name="Test Permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        response_body = extract_page_body(response.content.decode(response.charset))

        self.assertNotIn(
            "consumables?tab=nautobot_consumables:1",
            response_body,
            msg=response_body
        )
