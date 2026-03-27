from __future__ import annotations

import re
from pathlib import Path

from .txt_preset_parser import parse_preset_file

_EXPLICIT_OUT_RANGE_RE = re.compile(r"--out-range=-[nd]\d+|:out_range=-[nd]\d+(?=(:|\s|$))")


def has_explicit_out_range(args_text: str) -> bool:
    return bool(_EXPLICIT_OUT_RANGE_RE.search(str(args_text or "")))


def _block_warning_label(block) -> str:
    category = str(getattr(block, "category", "") or "").strip()
    protocol = str(getattr(block, "protocol", "") or "").strip().lower() or "tcp"
    filter_file = str(getattr(block, "filter_file", "") or "").strip()

    if category and category != "unknown":
        return f"{category}/{protocol}"
    if filter_file:
        return f"{Path(filter_file).name}/{protocol}"
    return f"block/{protocol}"


def collect_missing_out_range_labels_from_file(preset_path: str | Path) -> list[str]:
    data = parse_preset_file(Path(preset_path))
    labels: list[str] = []
    seen: set[str] = set()

    for block in data.categories:
        block_text = str(getattr(block, "raw_args", "") or getattr(block, "args", "") or "")
        if has_explicit_out_range(block_text):
            continue

        label = _block_warning_label(block)
        dedupe_key = label.strip().lower()
        if not dedupe_key or dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        labels.append(label)

    return labels

