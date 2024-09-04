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

"""App config declaration for Nautobot Consumables."""
# Metadata is inherited from Nautobot. If not including Nautobot
# in the environment, this should be added
from importlib import metadata

from django.db.models.signals import post_migrate
from nautobot.extras.plugins import NautobotAppConfig

dist = metadata.distribution(__name__)
__version__ = dist.metadata.get("Version")  # type: ignore[attr-defined]


class NautobotConsumablesConfig(NautobotAppConfig):
    """Plugin configuration for Consumables."""

    name: str = "nautobot_consumables"
    verbose_name: str = "Consumables Tracking for Nautobot"
    version: str = f"{__version__}"
    author: str = f"{dist.metadata.get('Author')}"  # type: ignore[attr-defined]
    author_email: str = f"{dist.metadata.get('Author-email')}"  # type: ignore[attr-defined]
    description: str = f"{dist.metadata.get('Summary')}"  # type: ignore[attr-defined]
    base_url = "consumables"
    required_settings: list[str] = []
    min_version: str = "1.6.1"
    max_version: str = "1.9999"
    caching_config: dict[str, str | dict[str, str]] = {}

    def ready(self) -> None:
        """Register custom signals at startup."""
        # pylint:disable=import-outside-toplevel
        from nautobot_consumables import signals
        post_migrate.connect(signals.post_migrate_create_defaults, sender=self)

        super().ready()


config = NautobotConsumablesConfig  # pylint:disable=invalid-name
