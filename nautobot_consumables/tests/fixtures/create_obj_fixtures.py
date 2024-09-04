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

"""Create test environment object fixtures."""
from nautobot.dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Location,
    LocationType,
    Manufacturer,
    Site,
)
from nautobot.utilities.choices import ColorChoices

from nautobot_consumables import models


def create_site() -> Site:
    """Add a test Site instance."""
    site, _ = Site.objects.get_or_create(name="Site 1")
    return site


def create_location_type() -> LocationType:
    """Add a Building LocationType."""
    location_type, _ = LocationType.objects.get_or_create(name="Building")
    return location_type


def create_locations(site: Site, location_type: LocationType) -> list[Location]:
    """Add test Location instances."""
    locations: list[Location] = []
    for num in range(1, 6):
        added, _ = Location.objects.get_or_create(
            name=f"Location {num}",
            location_type=location_type,
            site=site,
        )
        locations.append(added)

    return locations


def create_manufacturers() -> list[Manufacturer]:
    """Add test Manufacturer instances."""
    manufacturers: list[Manufacturer] = []
    for num in range(1, 6):
        mfgr, _ = Manufacturer.objects.get_or_create(name=f"Manufacturer {num}")
        manufacturers.append(mfgr)

    return manufacturers


def create_devices(locations: list[Location]):
    """Add test Device instances."""
    site = Site.objects.first()
    manufacturer = Manufacturer.objects.first()

    device_type, _ = DeviceType.objects.get_or_create(
        manufacturer=manufacturer,
        model="Device Type 1",
        slug="device_type_1",
    )

    device_role, _ = DeviceRole.objects.get_or_create(
        name="Device Role 1",
        slug="device_role_1",
        color="ff0000",
    )

    for num in range(1, 6):
        _ = Device.objects.get_or_create(
            device_type=device_type,
            device_role=device_role,
            name=f"Device {num}-1",
            site=site,
            location=locations[num - 1],
        )

        _ = Device.objects.get_or_create(
            device_type=device_type,
            device_role=device_role,
            name=f"Device {num}-2",
            site=site,
            location=locations[num - 1],
        )


def create_consumables(
    manufacturers: list[Manufacturer] | None = None
) -> list[list[models.Consumable]]:
    """Add test Consumables instances."""
    colors = ColorChoices.as_dict()

    # Default consumable types are added during the post-migration step,
    # so they already exist.
    generic_consumable = models.ConsumableType.objects.get(name="Generic")
    cable_consumable = models.ConsumableType.objects.get(name="Cable")
    transceiver_consumable = models.ConsumableType.objects.get(name="Transceiver")

    if manufacturers is None:
        manufacturers = create_manufacturers()

    consumables: list[list[models.Consumable]] = []
    for num in range(1, 6):
        mfgr = manufacturers[num - 1]

        generic, _ = models.Consumable.objects.get_or_create(
            name=f"Generic {num}",
            manufacturer=mfgr,
            product_id=f"generic_00{num}",
            consumable_type=generic_consumable,
        )

        cable, _ = models.Consumable.objects.get_or_create(
            name=f"Cable {num}",
            manufacturer=mfgr,
            product_id=f"cable_00{num}",
            consumable_type=cable_consumable,
            data={
                "color": list(colors)[num],
                "length": num,
                "cable_type": "CAT6a",
                "connector": "8P8C",
                "length_unit": "ft",
            },
        )

        transceiver, _ = models.Consumable.objects.get_or_create(
            name=f"Transceiver {num}",
            manufacturer=mfgr,
            product_id=f"transceiver_00{num}",
            consumable_type=transceiver_consumable,
            data={
                "reach": "LR",
                "form_factor": "QSFP-DD (400GE)",
            },
        )

        consumables.append([generic, cable, transceiver])

    return consumables


def create_consumable_pools(consumables: list[list[models.Consumable]], locations: list[Location]):
    """Add test ConsumablePools instances."""
    for num in range(1, 6):
        index = num - 1
        for consumable_num, consumable in enumerate(consumables[index], 1):
            pool, _ = models.ConsumablePool.objects.get_or_create(
                name=f"{consumable.name} Pool 1",
                consumable=consumable,
                location=locations[index],
                quantity=num * consumable_num * 13,
            )

            if num > 3:
                continue

            models.CheckedOutConsumable.objects.get_or_create(
                consumable_pool=pool,
                device=Device.objects.filter(location=locations[num - 1]).first(),
                quantity=pool.quantity / 2,
            )


def create_env():
    """Populate environment with basic test data."""
    print("Creating Base Data")

    print(" - Site")
    site = create_site()

    print(" - LocationType")
    location_type = create_location_type()

    print(" - Manufacturers")
    manufacturers = create_manufacturers()

    print(" - Locations")
    locations = create_locations(site, location_type)

    print(" - Devices")
    create_devices(locations)

    print(" - Consumables")
    consumables = create_consumables(manufacturers)

    print(" - Consumable Pools")
    create_consumable_pools(consumables, locations)
