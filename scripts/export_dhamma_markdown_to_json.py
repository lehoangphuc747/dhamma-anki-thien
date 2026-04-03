# -*- coding: utf-8 -*-
"""Chuyển các file Markdown trong Dhamma_Anki_by_topic/*.md sang JSON.

Chạy từ thư mục Thiền:
    python scripts/export_dhamma_markdown_to_json.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MD_DIR = BASE / "Dhamma_Anki_by_topic"
OUT_DIR = BASE / "Dhamma_Anki_by_topic_json"

# Bỏ qua README; chỉ xử lý *.md có bảng từ vựng.
SKIP_NAMES = {"readme.md"}


def _split_table_row(line: str) -> list[str]:
    """Tách một dòng bảng Markdown theo |, tôn trọng \\| trong ô."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    parts = re.split(r"(?<!\\)\|", s)
    return [p.replace("\\|", "|").strip() for p in parts]


def _is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.match(r"^:?-+:?$", c.strip()) for c in cells if c.strip())


def parse_markdown_table(lines: list[str], start_idx: int) -> tuple[list[dict[str, str]], int]:
    """Parse bảng bắt đầu từ dòng start_idx. Trả về (rows, index_sau_bảng)."""
    if start_idx >= len(lines):
        return [], start_idx

    header = _split_table_row(lines[start_idx])
    if len(header) < 3:
        return [], start_idx

    sep_idx = start_idx + 1
    if sep_idx >= len(lines):
        return [], start_idx

    sep_cells = _split_table_row(lines[sep_idx])
    if not _is_separator_row(sep_cells):
        return [], start_idx

    # Chuẩn hóa tên cột (tiếng Anh / tiếng Việt ở header).
    norm = []
    for h in header:
        low = h.lower().strip()
        if low == "english":
            norm.append("english")
        elif low == "ipa":
            norm.append("ipa")
        elif low == "vietnamese":
            norm.append("vietnamese")
        elif "giải thích" in low or "detail" in low or "explain" in low:
            norm.append("explain")
        else:
            norm.append(h)

    rows_out: list[dict[str, str]] = []
    i = sep_idx + 1
    while i < len(lines):
        raw = lines[i].strip()
        if not raw.startswith("|"):
            break
        cells = _split_table_row(raw)
        if len(cells) < 3:
            break
        row: dict[str, str] = {}
        for j, key in enumerate(norm):
            val = cells[j] if j < len(cells) else ""
            row[key] = val
        rows_out.append(row)
        i += 1

    return rows_out, i


def parse_md_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = ""
    if lines and lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()

    all_rows: list[dict[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines):
            table_rows, next_i = parse_markdown_table(lines, i)
            if table_rows:
                all_rows.extend(table_rows)
                i = next_i
                continue
        i += 1

    # Đảm bảo mọi dòng có đủ khóa (explain có thể rỗng) và gắn thêm title cho từng row.
    for r in all_rows:
        if "Giải thích chi tiết" in r:
            legacy = r.pop("Giải thích chi tiết", "")
            r["explain"] = (r.get("explain") or legacy or "").strip()
        r.setdefault("english", "")
        r.setdefault("ipa", "")
        r.setdefault("vietnamese", "")
        r.setdefault("explain", "")
        # Thêm cột title để mỗi dòng biết mình thuộc chủ đề nào.
        r.setdefault("title", title)

    return {
        "title": title,
        "source_file": path.name,
        "row_count": len(all_rows),
        "rows": all_rows,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(
        p
        for p in MD_DIR.glob("*.md")
        if p.name.lower() not in SKIP_NAMES
    )

    combined: list[dict] = []
    combined_rows: list[dict] = []

    for md_path in md_files:
        data = parse_md_file(md_path)
        combined.append(data)
        # Gom tất cả dòng vào một list phẳng để dùng trực tiếp theo cấp English.
        for row in data["rows"]:
            combined_rows.append(row)

        out_name = md_path.stem + ".json"
        out_path = OUT_DIR / out_name
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("Wrote", out_path.relative_to(BASE), "rows:", data["row_count"])

    # all_topics.json: danh sách PHẲNG các dòng từ vựng, mỗi dòng có english/ipa/vietnamese/detail/title.
    all_path = OUT_DIR / "all_topics.json"
    all_path.write_text(
        json.dumps(combined_rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Wrote", all_path.relative_to(BASE), "rows:", len(combined_rows))


if __name__ == "__main__":
    main()
