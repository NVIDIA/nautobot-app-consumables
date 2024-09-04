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

"""Add Nautobot Consumables views to the navigation menus."""
from nautobot.core.apps import (
    NavMenuAddButton,
    NavMenuGroup,
    NavMenuItem,
    NavMenuImportButton,
    NavMenuTab,
)

menu_items = (
    NavMenuTab(
        name="Consumables",
        permissions=["nautobot_consumables.view_consumable"],
        groups=[
            NavMenuGroup(
                name="Consumables",
                items=[
                    NavMenuItem(
                        link="plugins:nautobot_consumables:consumabletype_list",
                        name="Consumable Types",
                        permissions=["nautobot_consumables.view_consumabletype"],
                        buttons=[
                            NavMenuAddButton(
                                link="plugins:nautobot_consumables:consumabletype_add",
                                permissions=["nautobot_consumables.add_consumabletype"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_consumables:consumabletype_import",
                                permissions=["nautobot_consumables.add_consumabletype"],
                            ),
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_consumables:consumable_list",
                        name="Consumables",
                        permissions=["nautobot_consumables.view_consumable"],
                        buttons=[
                            NavMenuAddButton(
                                link="plugins:nautobot_consumables:consumable_add",
                                permissions=["nautobot_consumables.add_consumable"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_consumables:consumabletype_import",
                                permissions=["nautobot_consumables.add_consumabletype"],
                            ),
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_consumables:consumablepool_list",
                        name="Consumable Pools",
                        permissions=["nautobot_consumables.view_consumablepool"],
                        buttons=[
                            NavMenuAddButton(
                                link="plugins:nautobot_consumables:consumablepool_add",
                                permissions=["nautobot_consumables.add_consumablepool"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_consumables:consumablepool_import",
                                permissions=["nautobot_consumables.add_consumablepool"],
                            ),
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_consumables:checkedoutconsumable_list",
                        name="Checked Out Consumables",
                        permissions=["nautobot_consumables.view_checkedoutconsumable"],
                    ),
                ],
            ),
        ],
    ),
)
