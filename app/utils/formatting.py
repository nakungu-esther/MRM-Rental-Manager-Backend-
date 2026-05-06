from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def format_ugx(amount: Decimal | int | float | str) -> str:
    dec = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    dec = dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    whole = int(dec)
    return f"UGX {whole:,}"

