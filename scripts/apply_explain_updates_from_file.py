# -*- coding: utf-8 -*-
"""
Cập nhật field `explain` cho `Dhamma_Anki_by_topic_json/all_topics.json`
dựa trên dữ liệu từ `for update only.json`.

Script này xử lý cả trường hợp `for update only.json` bị lỗi format kiểu:
    [ {...}, {...} ] [ {...}, {...} ]
(tức là nhiều mảng JSON nối tiếp nhau) bằng cách tách từng mảng hợp lệ,
gộp lại thành 1 mảng để parse.

Chạy từ thư mục Thiền:
    python scripts/apply_explain_updates_from_file.py
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
UPDATE_FILE = BASE / "for update only.json"
TARGET_FILE = BASE / "Dhamma_Anki_by_topic_json" / "all_topics.json"


def extract_top_level_arrays(raw: str) -> list[str]:
    """Trích các mảng JSON ở level ngoài cùng (bắt đầu '[' và khép ']' tại level 0)."""
    arrays: list[str] = []
    s = raw.strip()
    n = len(s)

    i = 0
    while i < n:
        # Tìm '[' ở level 0
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
            # Chưa tìm được mảng kết thúc
            break

    return arrays


def load_update_objects() -> list[dict]:
    if not UPDATE_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {UPDATE_FILE}")

    raw = UPDATE_FILE.read_text(encoding="utf-8")

    # Cố parse theo JSON chuẩn trước
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError("for update only.json không phải list ở level ngoài cùng.")
        return [x for x in parsed if isinstance(x, dict)]
    except json.JSONDecodeError:
        pass

    # Fallback: tách nhiều mảng nối tiếp thành nhiều substring hợp lệ
    arrays = extract_top_level_arrays(raw)
    if not arrays:
        raise ValueError("Không trích được mảng JSON từ for update only.json.")

    merged: list[dict] = []
    parse_errors: list[str] = []
    for idx, arr_str in enumerate(arrays):
        try:
            arr_parsed = json.loads(arr_str)
            if isinstance(arr_parsed, list):
                merged.extend([x for x in arr_parsed if isinstance(x, dict)])
            else:
                parse_errors.append(f"array#{idx}: not a list")
        except Exception as e:
            parse_errors.append(f"array#{idx}: {e}")

    if parse_errors:
        # Nếu vẫn còn lỗi, báo để bạn kiểm tra lại file
        raise ValueError("Lỗi parse các array con: " + "; ".join(parse_errors))

    return merged


def main() -> None:
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {TARGET_FILE}")

    updates = load_update_objects()
    if not updates:
        raise ValueError("Không có object để cập nhật trong for update only.json.")

    target_raw = TARGET_FILE.read_text(encoding="utf-8")
    target = json.loads(target_raw)
    if not isinstance(target, list):
        raise ValueError("all_topics.json không phải list.")

    by_id: dict[str, dict] = {}
    for item in target:
        if isinstance(item, dict) and "id" in item:
            by_id[str(item["id"])] = item

    updated = 0
    missing_ids: list[str] = []

    # Cập nhật MỖI `id` -> chỉ field `explain`
    # Nếu file updates trùng id nhiều lần thì lần cuối cùng thắng (đúng như iterate order).
    for u in updates:
        uid = str(u.get("id", "")).strip()
        if not uid:
            continue
        expl = u.get("explain", "")
        if uid in by_id:
            by_id[uid]["explain"] = "" if expl is None else str(expl)
            updated += 1
        else:
            missing_ids.append(uid)

    # Backup trước khi ghi đè
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = TARGET_FILE.with_name(f"all_topics.json.bak_explain_merge_{ts}")
    bak_path.write_text(target_raw, encoding="utf-8")

    # Ghi đè
    TARGET_FILE.write_text(json.dumps(target, ensure_ascii=False, indent=2), encoding="utf-8")

    # Dọn missing: loại trùng để dễ đọc
    missing_unique = sorted(set(missing_ids))

    print(f"Updated explain (attempt): {updated}/{len(updates)}")
    print(f"Missing ids: {len(missing_unique)}")
    if missing_unique:
        print("Missing:", ", ".join(missing_unique))


if __name__ == "__main__":
    main()

