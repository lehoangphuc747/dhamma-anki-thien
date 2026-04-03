# -*- coding: utf-8 -*-
"""
Vá file `for update only.json` nếu bị lỗi format kiểu:
  [ {...}, {...} ] [ {...}, {...} ]

Script sẽ:
1) Thử parse JSON chuẩn trước.
2) Nếu lỗi, trích từng mảng JSON ở level ngoài cùng, rồi gộp lại thành 1 mảng hợp lệ.
3) Tạo backup: for update only.json.bak_fix_<timestamp>
4) Ghi đè lại file gốc.

Chạy từ thư mục Thiền:
  python scripts/fix_for_update_only_json.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
UPDATE_FILE = BASE / "for update only.json"


def extract_top_level_arrays(raw: str) -> list[str]:
    arrays: list[str] = []
    s = raw.strip()
    n = len(s)
    i = 0

    while i < n:
        if s[i] != "[":
            i += 1
            continue

        start = i
        level = 0
        in_string = False
        escape = False

        while i < n:
            ch = s[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == "\"":
                    in_string = False
            else:
                if ch == "\"":
                    in_string = True
                elif ch == "[":
                    level += 1
                elif ch == "]":
                    level -= 1
                    if level == 0:
                        arrays.append(s[start : i + 1])
                        i += 1
                        break
            i += 1
        else:
            break

    return arrays


def load_and_fix() -> list[dict]:
    raw = UPDATE_FILE.read_text(encoding="utf-8")

    # Parse chuẩn
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError("Không phải list ở level ngoài cùng.")
        return [x for x in parsed if isinstance(x, dict)]
    except json.JSONDecodeError:
        pass

    arrays = extract_top_level_arrays(raw)
    if not arrays:
        raise ValueError("Không trích được mảng JSON từ file.")

    merged: list[dict] = []
    for idx, arr_str in enumerate(arrays):
        arr_parsed = json.loads(arr_str)
        if not isinstance(arr_parsed, list):
            raise ValueError(f"array#{idx} không phải list.")
        merged.extend([x for x in arr_parsed if isinstance(x, dict)])

    return merged


def main() -> None:
    if not UPDATE_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {UPDATE_FILE}")

    merged = load_and_fix()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = UPDATE_FILE.with_name(f"{UPDATE_FILE.name}.bak_fix_{ts}")
    bak_path.write_text(UPDATE_FILE.read_text(encoding="utf-8"), encoding="utf-8")

    UPDATE_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Fixed for update only.json, objects:", len(merged))


if __name__ == "__main__":
    main()

