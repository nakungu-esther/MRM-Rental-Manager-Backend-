from __future__ import annotations

from pathlib import Path


def write_placeholder_receipt_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Real implementation comes in the "PDF receipts" sprint day.
    path.write_bytes(b"%PDF-1.4\n% RentalMGR placeholder receipt\n")

