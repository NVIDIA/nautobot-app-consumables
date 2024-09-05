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

"""Additional fields for the Naautobot Consumables app."""
import json
from typing import Any

from django.forms.fields import InvalidJSONInput, JSONString
from nautobot.apps.forms import JSONField as NBJSONField


class ConsumablesTypeJSONField(NBJSONField):
    """
    Custom wrapper around Nautobot's JSONField wrapper.

    Their wrapper is intended to avoid presenting "null" as the default text in a JSON field,
    but it doesn't actually work because the ancestor JSON field considers the empty string to
    be a null value, and returns None for it anyway.
    """
    empty_values = (None, '', ())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set the default widget placeholder to '{}'."""
        super().__init__(*args, **kwargs)
        self.widget.attrs["placeholder"] = "{}"

    def prepare_value(self, value: Any) -> Any:
        """Make sure the value is never None."""
        if isinstance(value, InvalidJSONInput):
            return value
        if value is None:
            return JSONString("{}")
        return json.dumps(value, sort_keys=True, indent=4, ensure_ascii=False)

    def to_python(self, value: Any | None) -> Any:
        """Make sure value is never returned as None."""
        if value is None:
            value = "{}"
        return super().to_python(value)
