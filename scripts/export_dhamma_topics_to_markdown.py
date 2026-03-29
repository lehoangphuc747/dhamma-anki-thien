# -*- coding: utf-8 -*-
"""Tách từ vựng Dhamma Anki thành từng file Markdown theo chủ đề (dòng tiêu đề dạng "1. ...")."""
import re
from pathlib import Path

import eng_to_ipa as ipa_lib
import pandas as pd

# Thư mục gốc dự án = cha của thư mục chứa script này (…/Thiền).
BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "Dhamma_Anki_cleaned.xlsx"
OUT_DIR = BASE / "Dhamma_Anki_by_topic"

TOPIC_RE = re.compile(r"^(\d+)\.\s*(.+)$")
# "extremities (palms & soles)" — & nằm trong ngoặc, không tách được bằng quy tắc hai vế cùng số từ.
_PAREN_INNER_AND = re.compile(r"^(.+?)\s+\(([^)]+)\)\s*$")


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", title, flags=re.UNICODE)
    s = re.sub(r"\s+", "_", s.strip())
    if len(s) > 80:
        s = s[:80]
    return s or "topic"


def esc_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", "<br>")


# Sửa vài lỗi chính tả / biến thể trong bộ thẻ để từ điển IPA nhận ra.
_IPA_NORMALIZE = (
    ("experiencial", "experiential"),
    ("abdoment", "abdomen"),
)


def _normalize_for_ipa(phrase: str) -> str:
    s = phrase
    for bad, good in _IPA_NORMALIZE:
        s = re.sub(re.escape(bad), good, s, flags=re.IGNORECASE)
    return s


# eng-to-ipa thiếu một số từ → trả về dạng "word*". Thay bằng IPA thủ công (Anh–Mỹ).
_IPA_OOV_FIXES: tuple[tuple[str, str], ...] = (
    ("unwholesome*", "ʌnˈhoʊlsəm"),
    ("unwholesome", "ʌnˈhoʊlsəm"),
    ("equanimous*", "ˌiːkwəˈnɪməs"),
    ("defilement*", "dɪˈfaɪlmənt"),
    ("sinusitis*", "ˌsaɪnəˈsaɪtɪs"),
    ("earache*", "ˈɪreɪk"),
    ("hepatitis-a*", "ˌhɛpəˈtaɪtɪs ˈeɪ"),
    ("hepatitis-a", "ˌhɛpəˈtaɪtɪs ˈeɪ"),
)


def _fix_oov_in_ipa_string(out: str) -> str:
    s = out
    for bad, good in _IPA_OOV_FIXES:
        if bad in s:
            s = s.replace(bad, good)
    return s


def _ipa_inner(wrapped: str) -> str:
    """Bỏ một cặp /.../ bọc ngoài để ghép vào cụm lớn hơn."""
    w = wrapped.strip()
    if len(w) >= 2 and w.startswith("/") and w.endswith("/"):
        return w[1:-1]
    return w


def _ipa_parenthetical_and(raw: str) -> str | None:
    """Khớp 'trước (trái & phải)' và trả về IPA có giữ dấu & trong ngoặc."""
    m = _PAREN_INNER_AND.match(raw.strip())
    if not m:
        return None
    prefix, inner = m.group(1).strip(), m.group(2).strip()
    if inner.count(" & ") != 1:
        return None
    left, right = [x.strip() for x in inner.split(" & ", 1)]
    if not prefix or not left or not right:
        return None
    ip_p = _convert_one_segment(prefix)
    ip_l = _convert_one_segment(left)
    ip_r = _convert_one_segment(right)
    if not (ip_p and ip_l and ip_r):
        return None
    return (
        "/"
        + _ipa_inner(ip_p)
        + " ("
        + _ipa_inner(ip_l)
        + " & "
        + _ipa_inner(ip_r)
        + ")/"
    )


def _convert_one_segment(segment: str) -> str:
    """Một cụm (đã tách 'hoặc'); gạch nối trong cụm từ -> khoảng trắng để IPA dễ đọc."""
    seg = _normalize_for_ipa(segment.strip())
    if not seg:
        return ""
    seg = re.sub(r"-", " ", seg)
    seg = " ".join(seg.split())
    try:
        out = ipa_lib.convert(seg)
    except Exception:
        return ""
    out = " ".join(str(out).split())
    out = _fix_oov_in_ipa_string(out)
    if not out:
        return ""
    return "/" + out + "/"


def _split_english_for_ipa(raw: str) -> tuple[list[str], str]:
    """Tách mục từ theo ký hiệu nối; trả về (các phần, chuỗi nối giữa các khối IPA).

    Giữ đúng ký tự gốc (><, /, &) trong cột IPA để khớp mắt với cột English.
    """
    if "><" in raw:
        parts = [p.strip() for p in raw.split("><")]
        return parts, " >< "
    # English dùng / làm “hoặc”. Không dùng ký tự / làm nối giữa các /.../ IPA (sẽ thành / / /).
    # Dùng ⁄ (U+2044 FRACTION SLASH) — nhìn giống / nhưng không dính viền IPA.
    if "/" in raw:
        parts = [p.strip() for p in raw.split("/") if p.strip()]
        return parts, " ⁄ "
    # Hai vế song song: "A & B" — chỉ tách khi hai vế cùng số từ (tránh "calm & quiet mind").
    if " & " in raw:
        segs = [p.strip() for p in raw.split(" & ")]
        if len(segs) == 2:
            w0, w1 = len(segs[0].split()), len(segs[1].split())
            if w0 == w1 and w0 >= 1:
                return segs, " & "
    return [raw], ""


def english_to_ipa(text: str) -> str:
    """Chuyển cụm tiếng Anh sang IPA (eng-to-ipa, kiểu Mỹ). Ô trống -> rỗng.

    Các nhánh tách bởi /, ><, hoặc & (khi hai vế cùng số từ) được nối lại bằng đúng ký tự đó.
    """
    raw = text.replace("<br>", " ").replace("\\|", "|").strip()
    if not raw:
        return ""

    paren_and = _ipa_parenthetical_and(raw)
    if paren_and is not None:
        return paren_and

    parts, joiner = _split_english_for_ipa(raw)

    if len(parts) > 1 and joiner:
        chunks: list[str] = []
        for p in parts:
            c = _convert_one_segment(p)
            if c:
                chunks.append(c)
        if chunks:
            return joiner.join(chunks)

    return _convert_one_segment(parts[0])


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Vocabulary_Cleaned")
    df["English"] = df["English"].astype(str).str.strip()
    df["Vietnamese"] = df["Vietnamese"].apply(
        lambda x: "" if pd.isna(x) else str(x).strip()
    )

    OUT_DIR.mkdir(exist_ok=True)

    topics: list[tuple[dict, list[tuple[str, str]]]] = []
    current: dict | None = None
    rows_buffer: list[tuple[str, str]] = []

    for _, row in df.iterrows():
        en, vi = row["English"], row["Vietnamese"]
        m = TOPIC_RE.match(en)
        is_topic = m is not None and vi == ""

        if is_topic:
            if current is not None:
                topics.append((current, rows_buffer))
            num, title = m.group(1), m.group(2).strip()
            current = {"num": num, "title": title, "full": en}
            rows_buffer = []
        else:
            if current is None:
                current = {"num": "00", "title": "Uncategorized", "full": "Uncategorized"}
                rows_buffer = []
            rows_buffer.append((en, vi))

    if current is not None:
        topics.append((current, rows_buffer))

    index_lines = [
        "# Dhamma Anki — Từ vựng theo chủ đề",
        "",
        "Các file được tách từ `Dhamma_Anki_cleaned.xlsx`. Cột **IPA** do `eng-to-ipa` (Anh–Mỹ). Nhiều nhánh: **><** và **&** (hai vế cùng số từ) giữ nguyên ký tự giữa các khối; khi English dùng **/**, giữa các khối IPA dùng **⁄** (xẹt mảnh) để không trùng viền `/.../`.",
        "",
        "Tạo lại các file này: chạy `python scripts/export_dhamma_topics_to_markdown.py` từ thư mục `Thiền`.",
        "",
        "| # | Chủ đề | File |",
        "| --- | --- | --- |",
    ]

    for t, rows in topics:
        num = t["num"]
        title = t["title"]
        fname = f"{int(num):02d}_{slugify(title)}.md"
        path = OUT_DIR / fname

        lines = [
            f"# {t['full']}",
            "",
            "| English | IPA | Vietnamese |",
            "| --- | --- | --- |",
        ]
        for en, vi in rows:
            ipa_val = english_to_ipa(en)
            line = (
                "| "
                + esc_cell(en)
                + " | "
                + esc_cell(ipa_val)
                + " | "
                + esc_cell(vi)
                + " |"
            )
            lines.append(line)

        path.write_text("\n".join(lines), encoding="utf-8")
        index_lines.append("| " + num + " | " + title + " | [" + fname + "](" + fname + ") |")

    (OUT_DIR / "README.md").write_text("\n".join(index_lines), encoding="utf-8")

    print("Folder:", OUT_DIR)
    print("Topics:", len(topics))
    for t, rows in topics:
        print(" ", t["full"], "->", len(rows), "terms")


if __name__ == "__main__":
    main()
