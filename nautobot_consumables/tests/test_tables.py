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

"""Tests for tables defined in the Nautobot Consumables app."""
from django.test import TestCase

from nautobot_consumables import tables


class TablesTestCase(TestCase):
    """Test cases for tables."""

    def test_model_table_orderable(self):
        """Assert that orderable is set to True by default."""
        for table_name in tables.__all__:
            with self.subTest(table_name=table_name):
                table = getattr(tables, table_name)
                queryset = table.Meta.model.objects.all()
                self.assertTrue(table(queryset).orderable)
