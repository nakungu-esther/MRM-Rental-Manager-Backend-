from __future__ import annotations

import re

UG_PHONE_RE = re.compile(r"^(?:\\+256|0)(?:7\\d{8})$")


def is_valid_ug_phone(phone: str) -> bool:
    return bool(UG_PHONE_RE.match(phone.strip()))

