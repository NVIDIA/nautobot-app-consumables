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
from django.utils.crypto import get_random_string
import factory.random
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Location, Manufacturer
from nautobot.utilities.choices import ColorChoices

from nautobot_consumables import models


def create_devices():
    """Add test Device instances."""
    for num in range(1, 6):
        device_type = factory.random.randgen.choice(DeviceType.objects.all())
        device_role = factory.random.randgen.choice(DeviceRole.objects.all())
        location = factory.random.randgen.choice(Location.objects.filter(site__isnull=False))

        _ = Device.objects.get_or_create(
            device_type=device_type,
            device_role=device_role,
            name=f"Device {num}-1",
            site=location.site,
            location=location,
        )
        _ = Device.objects.get_or_create(
            device_type=device_type,
            device_role=device_role,
            name=f"Device {num}-2",
            site=location.site,
            location=location,
        )


def create_consumables() -> list[list[models.Consumable]]:
    """Add test Consumables instances."""
    colors = ColorChoices.as_dict()

    # Default consumable types are added during the post-migration step,
    # so they already exist.
    generic_consumable = models.ConsumableType.objects.get(name="Generic")
    cable_consumable = models.ConsumableType.objects.get(name="Cable")
    transceiver_consumable = models.ConsumableType.objects.get(name="Transceiver")

    consumables: list[list[models.Consumable]] = []
    for num in range(1, 6):
        mfgr = factory.random.randgen.choice(Manufacturer.objects.all())

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


def create_consumable_pools(consumables: list[list[models.Consumable]]):
    """Add test ConsumablePools instances."""
    for num in range(1, 6):
        index = num - 1
        device = factory.random.randgen.choice(Device.objects.all())

        for consumable_num, consumable in enumerate(consumables[index], 1):
            pool, _ = models.ConsumablePool.objects.get_or_create(
                name=f"{consumable.name} Pool 1",
                consumable=consumable,
                location=device.location,
                quantity=num * consumable_num * 13,
            )

            if num > 3:
                continue

            models.CheckedOutConsumable.objects.get_or_create(
                consumable_pool=pool,
                device=device,
                quantity=pool.quantity / 2,
            )


def create_env(seed: str | None = None):
    """Populate environment with basic test data."""
    if seed is None:
        seed = get_random_string(16)
    factory.random.reseed_random(seed)

    print("Creating Devices")
    create_devices()

    print("Creating Consumables")
    consumables = create_consumables()

    print("Creating Consumable Pools")
    create_consumable_pools(consumables)
