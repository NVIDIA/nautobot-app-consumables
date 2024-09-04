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

"""URL route mapping for the Nautobot Consumables app."""
from django.urls import path
from nautobot.core.views.routers import NautobotUIViewSetRouter

from nautobot_consumables import views

router = NautobotUIViewSetRouter()

router.register("checked-out-consumables", views.CheckedOutConsumableUIViewSet)
router.register("consumables", views.ConsumableUIViewSet)
router.register("consumable-pools", views.ConsumablePoolUIViewSet)
router.register("consumable-types", views.ConsumableTypeUIViewSet)

urlpatterns = [
    path(
        "devices/<uuid:pk>/consumables",
        views.DeviceConsumablesViewTab.as_view(),
        name="device_consumables_tab",
    ),
    path(
        "locations/<slug:slug>/consumables",
        views.LocationConsumablesViewTab.as_view(),
        name="location_consumables_tab",
    ),
]

urlpatterns += router.urls
