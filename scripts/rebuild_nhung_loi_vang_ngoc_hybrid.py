# -*- coding: utf-8 -*-
"""Rebuild a structured Markdown draft from the PDF-derived HTML layout.

This script is intentionally stdlib-only. The source HTML already contains one
absolute-positioned ``<p>`` per PDF text line, so the converter can recover
left/right chant columns from ``top`` and ``left`` coordinates without OCR.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROW_TOLERANCE_PT = 2.0
COLUMN_SPLIT_PT = 170.0
COLUMN_SPLIT_MARGIN_PT = 15.0
TABLE_CONTINUATION_GAP_PT = 28.0
PROSE_PARAGRAPH_GAP_PT = 19.0


def ensure_utf8_stdio() -> None:
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding="utf-8",
                errors="replace",
                line_buffering=True,
            )
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding="utf-8",
                errors="replace",
                line_buffering=True,
            )
    except Exception:
        pass


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"([A-Za-zÀ-Ỵà-ỹ])\s+([̣̀́̉̃])", r"\1\2", text)
    text = re.sub(r"(?<=[a-zà-ỹ])(?=[A-ZĐ])", " ", text)
    text = re.sub(r"(?<!\S)(?P<word>[A-Za-zÀ-Ỵà-ỹ]{2,})\s+(?P<tail>[A-Za-zÀ-Ỵà-ỹ])(?=\b)", r"\g<word>\g<tail>", text)
    text = re.sub(
        rf"\b([{UPPERCASE_VI}]" rf"{{2,}})\s+([{UPPERCASE_VI}]{{1,2}})\b",
        r"\1\2",
        text,
    )
    for old, new in COMMON_TEXT_REPAIRS:
        text = text.replace(old, new)
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    text = re.sub(r"(\.{3,})(?=\S)", r"\1 ", text)
    text = re.sub(r"([,;:?!])(?=\S)", r"\1 ", text)
    text = re.sub(r"\s+", " ", text)
    return unicodedata.normalize("NFC", text).strip()


COMMON_TEXT_REPAIRS: list[tuple[str, str]] = [
    ("Mỗi từđều", "Mỗi từ đều"),
    ("ngôn ngữnày", "ngôn ngữ này"),
    ("thếgiới", "thế giới"),
    ("vềviệc", "về việc"),
    ("giữgìn", "giữ gìn"),
    ("khổđau", "khổ đau"),
    ("cảchúng", "cả chúng"),
    ("cảkhổđau", "cả khổ đau"),
    ("đảnh lễĐức", "đảnh lễ Đức"),
    ("ngộhoàn", "ngộ hoàn"),
    ("chỉdạy", "chỉ dạy"),
    ("mởđầu", "mở đầu"),
    ("đa ̣o", "đạo"),
    ("Nguyệ n", "Nguyện"),
    ("Bậ c", "Bậc"),
    ("từbi", "từ bi"),
    ("vi diệ u", "vi diệu"),
    ("lợi la ̣c", "lợi lạc"),
    ("họđược", "họ được"),
    ("ởtrong", "ở trong"),
    ("trởnên", "trở nên"),
    ("giữgiới", "giữ giới"),
    ("tựmình", "tự mình"),
    ("Tựmình", "Tự mình"),
    ("tuệvô", "tuệ vô"),
    ("đãđược", "đã được"),
    ("bây giờđã", "bây giờ đã"),
    ("bây giờvà", "bây giờ và"),
    ("Bây giờvàở đây", "Bây giờ và ở đây"),
    ("Buddhaṃsaraṇaṃgacchāmi", "Buddhaṃsaraṇaṃ gacchāmi"),
    ("Dhammaṃsaraṇaṃgacchāmi", "Dhammaṃsaraṇaṃ gacchāmi"),
    ("Saṅghaṃsaraṇaṃgacchāmi", "Saṅghaṃsaraṇaṃ gacchāmi"),
    ("buddhaṃsaraṇaṃgacchāmi", "buddhaṃsaraṇaṃ gacchāmi"),
    ("dhammaṃsaraṇaṃgacchāmi", "dhammaṃsaraṇaṃ gacchāmi"),
    ("saṅghaṃsaraṇaṃgacchāmi", "saṅghaṃsaraṇaṃ gacchāmi"),
    ("buddhaṃpūjemi", "buddhaṃ pūjemi"),
    ("dhammaṃpūjemi", "dhammaṃ pūjemi"),
    ("saṅghaṃpūjemi", "saṅghaṃ pūjemi"),
    ("buddhaṃnamassāma", "buddhaṃ namassāma"),
    ("dhammaṃnamassāma", "dhammaṃ namassāma"),
    ("saṅghaṃnamassāma", "saṅghaṃ namassāma"),
    ("sikkhāpadaṃsamādiyāmi", "sikkhāpadaṃ samādiyāmi"),
    ("kammaṭṭhānaṃdehi", "kammaṭṭhānaṃ dehi"),
    ("củaS.N.", "của S.N."),
    ("đểcon", "để con"),
    ("đểtìm", "để tìm"),
    ("cóthể", "có thể"),
    ("có thểchứng", "có thể chứng"),
    ("Có thểchứng", "Có thể chứng"),
    ("có thểthấy", "có thể thấy"),
    ("mộtcách", "một cách"),
    ("hỗtrợ", "hỗ trợ"),
    ("quý vịđược", "quý vị được"),
    ("sựhướng dẫn", "sự hướng dẫn"),
    ("tinh tếvà", "tinh tế và"),
    ("vàở", "và ở"),
    ("họthẳng", "họ thẳng"),
    ("trởvề", "trở về"),
    ("từđó", "từ đó"),
    ("ởđây", "ở đây"),
    ("ởtrên", "ở trên"),
    ("ởbên", "ở bên"),
    ("thếgian", "thế gian"),
    ("thếkỷ", "thế kỷ"),
    ("quảtức", "quả tức"),
    ("đượctruyền", "được truyền"),
    ("mẹđẻ", "mẹ đẻ"),
]


UPPERCASE_VI = "A-ZĐÂĂÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘÚÙỦŨỤỨỪỬỮỰ"


def fold_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def style_pt(style: str, key: str, default: float = 0.0) -> float:
    match = re.search(rf"{re.escape(key)}\s*:\s*(-?\d+(?:\.\d+)?)pt", style)
    if not match:
        return default
    return float(match.group(1))


def markdown_table_cell(text: str) -> str:
    text = normalize_text(text)
    text = text.replace("\\", "\\\\")
    text = text.replace("|", r"\|")
    return text


def ends_hard(text: str) -> bool:
    return bool(re.search(r"[.,;:?!।॥\"”’)]$", text.strip()))


def starts_like_continuation(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    first = text[0]
    return first.islower() or first in "-–—,;:)]"


@dataclass
class Block:
    page: int
    top: float
    left: float
    line_height: float
    font_size: float
    text: str
    bold: bool = False
    italic: bool = False


@dataclass
class Row:
    page: int
    top: float
    blocks: list[Block] = field(default_factory=list)

    @property
    def font_size(self) -> float:
        return max((block.font_size for block in self.blocks), default=0.0)

    @property
    def bold(self) -> bool:
        return any(block.bold for block in self.blocks)

    @property
    def italic(self) -> bool:
        return any(block.italic for block in self.blocks)

    @property
    def left(self) -> float:
        return min((block.left for block in self.blocks), default=0.0)

    def text(self) -> str:
        return normalize_text(" ".join(block.text for block in sorted(self.blocks, key=lambda b: b.left)))


class PdfHtmlLayoutParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self.page_labels: list[str] = []
        self.current_page: int | None = None

        self._label_parts: list[str] | None = None
        self._para: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        tag = tag.lower()

        if tag == "p":
            cls = attrs_dict.get("class", "")
            if "page-label" in cls.split():
                self._label_parts = []
                return

            style = attrs_dict.get("style", "")
            if self.current_page is not None and "top:" in style and "left:" in style:
                line_height = style_pt(style, "line-height")
                self._para = {
                    "page": self.current_page,
                    "top": style_pt(style, "top"),
                    "left": style_pt(style, "left"),
                    "line_height": line_height,
                    "font_size": line_height,
                    "bold": False,
                    "italic": False,
                    "parts": [],
                }
                return

        if self._para is not None:
            if tag in {"b", "strong"}:
                self._para["bold"] = True
            elif tag in {"i", "em"}:
                self._para["italic"] = True

            span_style = attrs_dict.get("style", "")
            if "font-size:" in span_style:
                size = style_pt(span_style, "font-size")
                self._para["font_size"] = max(float(self._para["font_size"]), size)

    def handle_data(self, data: str) -> None:
        if self._label_parts is not None:
            self._label_parts.append(data)
        elif self._para is not None:
            parts = self._para["parts"]
            assert isinstance(parts, list)
            parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag != "p":
            return

        if self._label_parts is not None:
            label = normalize_text("".join(self._label_parts))
            self.page_labels.append(label)
            match = re.search(r"Trang\s+(\d+)\s*/\s*(\d+)", label)
            if match:
                self.current_page = int(match.group(1))
            self._label_parts = None
            return

        if self._para is not None:
            parts = self._para["parts"]
            assert isinstance(parts, list)
            text = normalize_text("".join(str(part) for part in parts))
            if text:
                self.blocks.append(
                    Block(
                        page=int(self._para["page"]),
                        top=float(self._para["top"]),
                        left=float(self._para["left"]),
                        line_height=float(self._para["line_height"]),
                        font_size=float(self._para["font_size"]),
                        text=text,
                        bold=bool(self._para["bold"]),
                        italic=bool(self._para["italic"]),
                    )
                )
            self._para = None


def find_default_html() -> Path:
    candidates = sorted(ROOT.glob("04.*/*.html"))
    if not candidates:
        raise SystemExit("No HTML source found under a folder starting with 04.")
    return candidates[0]


def is_running_header_or_footer(block: Block) -> bool:
    folded = fold_text(block.text)
    compact = re.sub(r"[^a-z0-9]+", "", folded)
    if block.top > 535 and re.fullmatch(r"[ivxlcdm]+|\d+", folded):
        return True
    if block.top < 80 and compact in {"sngoenka", "nhungloivangngoc"}:
        return True
    if block.font_size <= 10 and compact in {"sngoenka", "nhungloivangngoc"}:
        return True
    return False


def group_rows(blocks: list[Block]) -> dict[int, list[Row]]:
    rows_by_page: dict[int, list[Row]] = {}
    usable_blocks = [block for block in blocks if not is_running_header_or_footer(block)]
    for page in sorted({block.page for block in usable_blocks}):
        rows: list[Row] = []
        page_blocks = sorted(
            [block for block in usable_blocks if block.page == page],
            key=lambda block: (block.top, block.left),
        )
        for block in page_blocks:
            if rows and abs(rows[-1].top - block.top) <= ROW_TOLERANCE_PT:
                rows[-1].blocks.append(block)
                rows[-1].top = min(rows[-1].top, block.top)
            else:
                rows.append(Row(page=page, top=block.top, blocks=[block]))
        rows_by_page[page] = rows
    return rows_by_page


def split_columns(row: Row) -> tuple[str, str, list[Block]]:
    left_blocks: list[Block] = []
    right_blocks: list[Block] = []
    boundary_blocks: list[Block] = []

    for block in sorted(row.blocks, key=lambda item: item.left):
        if abs(block.left - COLUMN_SPLIT_PT) <= COLUMN_SPLIT_MARGIN_PT:
            boundary_blocks.append(block)
        if block.left < COLUMN_SPLIT_PT:
            left_blocks.append(block)
        else:
            right_blocks.append(block)

    left = normalize_text(" ".join(block.text for block in left_blocks))
    right = normalize_text(" ".join(block.text for block in right_blocks))
    return left, right, boundary_blocks


def is_heading_row(row: Row, left: str, right: str) -> bool:
    if right:
        return False
    text = row.text()
    if not text:
        return False
    if row.bold and row.font_size >= 12.5:
        return True
    if row.font_size >= 15.0 and len(text) < 90:
        return True
    return False


def is_table_like(row: Row, left: str, right: str, in_table: bool, prev_top: float | None) -> bool:
    if left and right and row.font_size <= 13.0:
        return True
    if not in_table or not (left or right):
        return False
    if prev_top is None:
        return False
    return row.font_size <= 12.5 and (row.top - prev_top) <= TABLE_CONTINUATION_GAP_PT


def is_table_section_heading_pair(row: Row, left: str, right: str) -> bool:
    if not row.bold or not left or not right:
        return False
    if row.font_size > 13.0:
        return False
    if len(left) > 40 or len(right) > 40:
        return False
    if ends_hard(left) or ends_hard(right):
        return False
    return True


def heading_level(row: Row) -> int:
    if row.font_size >= 15.0:
        return 2
    return 3


def append_table_row(
    table_rows: list[list[str]],
    left: str,
    right: str,
    review: list[str],
    page: int,
    top: float,
) -> None:
    if not table_rows:
        table_rows.append([left, right])
        return

    prev_left, prev_right = table_rows[-1]
    if left and right and prev_left and not ends_hard(prev_left) and starts_like_continuation(left):
        table_rows[-1][0] = f"{prev_left}<br>{left}"
        table_rows[-1][1] = f"{prev_right}<br>{right}" if prev_right else right
        review.append(
            f"- Page {page}, top {top:.1f}: merged probable split source line into previous table row."
        )
        return

    if (
        left
        and right
        and prev_right
        and prev_right.strip().endswith(",")
        and starts_like_continuation(left)
    ):
        review.append(
            f"- Page {page}, top {top:.1f}: possible shifted translation line; "
            "right cell may continue previous row."
        )

    if left and not right:
        table_rows[-1][0] = f"{prev_left}<br>{left}" if prev_left else left
        review.append(f"- Page {page}, top {top:.1f}: left-only table continuation.")
        return

    if right and not left:
        table_rows[-1][1] = f"{prev_right}<br>{right}" if prev_right else right
        review.append(f"- Page {page}, top {top:.1f}: right-only table continuation.")
        return

    table_rows.append([left, right])


def render_table(table_rows: list[list[str]]) -> list[str]:
    if not table_rows:
        return []
    lines = ["| Nguyên văn | Tiếng Việt |", "| --- | --- |"]
    for left, right in table_rows:
        lines.append(f"| {markdown_table_cell(left)} | {markdown_table_cell(right)} |")
    lines.append("")
    return lines


def render_hybrid(
    rows_by_page: dict[int, list[Row]],
    source_html: Path,
    review: list[str],
) -> list[str]:
    out: list[str] = [
        f"# {source_html.stem}",
        "",
        f"*Structured rebuild from `{source_html.name}` using PDF text-layer coordinates.*",
        "",
    ]

    table_rows: list[list[str]] = []
    prose_lines: list[str] = []
    heading_parts: list[str] = []
    heading_part_level = 3
    last_prose_top: float | None = None
    prev_table_top: float | None = None

    def flush_heading() -> None:
        nonlocal heading_parts, heading_part_level
        if heading_parts:
            out.append(f"{'#' * heading_part_level} {' '.join(heading_parts)}")
            out.append("")
            heading_parts = []

    def flush_prose() -> None:
        nonlocal prose_lines, last_prose_top
        if prose_lines:
            out.append(normalize_text(" ".join(prose_lines)))
            out.append("")
            prose_lines = []
        last_prose_top = None

    def flush_table() -> None:
        nonlocal table_rows, prev_table_top
        if table_rows:
            out.extend(render_table(table_rows))
            table_rows = []
        prev_table_top = None

    for page in sorted(rows_by_page):
        flush_prose()
        flush_table()
        flush_heading()
        rows = rows_by_page[page]

        for row in rows:
            left, right, boundary_blocks = split_columns(row)
            row_text = row.text()
            if not row_text:
                continue

            if boundary_blocks:
                joined = " / ".join(block.text for block in boundary_blocks)
                review.append(
                    f"- Page {page}, top {row.top:.1f}: near column boundary: {joined}"
                )

            in_table = bool(table_rows)
            if is_heading_row(row, left, right):
                flush_prose()
                flush_table()
                level = heading_level(row)
                if heading_parts and heading_part_level != level:
                    flush_heading()
                heading_part_level = level
                heading_parts.append(row_text)
                continue

            if is_table_section_heading_pair(row, left, right):
                flush_prose()
                flush_table()
                flush_heading()
                out.append(f"### {left} - {right}")
                out.append("")
                table_rows.append([left, right])
                prev_table_top = row.top
                continue

            if is_table_like(row, left, right, in_table, prev_table_top):
                flush_heading()
                flush_prose()
                append_table_row(table_rows, left, right, review, page, row.top)
                prev_table_top = row.top
                continue

            flush_table()
            flush_heading()
            if last_prose_top is not None and (row.top - last_prose_top) > PROSE_PARAGRAPH_GAP_PT:
                flush_prose()
            prose_lines.append(row_text)
            last_prose_top = row.top

        flush_prose()
        flush_table()
        flush_heading()

    return out


MISSING_SPACE_PATTERNS = [
    "từbi",
    "chỉdạy",
    "ngộhoàn",
    "cảchúng",
    "cảmọi",
    "tốNiết",
    "tốnày",
    "ởtrong",
    "họđược",
    "cảkhổđau",
]


def build_review(
    parser: PdfHtmlLayoutParser,
    rows_by_page: dict[int, list[Row]],
    output_lines: list[str],
    output_path: Path,
    old_md: Path | None,
    review_items: list[str],
) -> list[str]:
    skipped_headers = [block for block in parser.blocks if is_running_header_or_footer(block)]
    all_rows = [row for rows in rows_by_page.values() for row in rows]
    table_rows = [line for line in output_lines if line.startswith("| ") and " | " in line]
    output_text = "\n".join(output_lines)

    lines = [
        "# Hybrid rebuild review",
        "",
        "## Summary",
        "",
        f"- Page labels: {len(parser.page_labels)}",
        f"- Parsed text blocks: {len(parser.blocks)}",
        f"- Layout rows after header/footer filter: {len(all_rows)}",
        f"- Skipped running headers/footers: {len(skipped_headers)}",
        f"- Markdown table data rows: {max(0, len(table_rows) - 2 * output_text.count('| --- | --- |'))}",
        f"- Output: `{output_path.name}`",
        "",
    ]

    if old_md and old_md.is_file():
        old_text = old_md.read_text(encoding="utf-8", errors="replace")
        lines.extend(
            [
                "## Existing Markdown comparison",
                "",
                f"- Existing MD chars: {len(old_text)}",
                f"- Hybrid MD chars: {len(output_text)}",
                "",
            ]
        )

    suspect_rows: list[str] = []
    for row in all_rows:
        row_text = row.text()
        if any(pattern in row_text for pattern in MISSING_SPACE_PATTERNS):
            suspect_rows.append(f"- Page {row.page}, top {row.top:.1f}: {row_text}")
        if re.search(r"[a-zà-ỹ][A-ZĐ]", row_text):
            suspect_rows.append(f"- Page {row.page}, top {row.top:.1f}: {row_text}")

    if review_items:
        lines.extend(["## Parser review items", "", *review_items[:400], ""])
        if len(review_items) > 400:
            lines.append(f"- ... {len(review_items) - 400} more parser items omitted.")
            lines.append("")

    if suspect_rows:
        lines.extend(["## Suspect spacing/OCR rows", "", *suspect_rows[:300], ""])
        if len(suspect_rows) > 300:
            lines.append(f"- ... {len(suspect_rows) - 300} more suspect rows omitted.")
            lines.append("")

    return lines


def write_text(path: Path, lines: list[str]) -> None:
    text = "\n".join(lines).rstrip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Rebuild structured Markdown from PDF-derived HTML.")
    parser.add_argument("--html", type=Path, default=find_default_html(), help="PDF-derived HTML source.")
    parser.add_argument("--output", type=Path, default=None, help="Hybrid Markdown output path.")
    parser.add_argument("--review", type=Path, default=None, help="Review report output path.")
    args = parser.parse_args()

    source_html = args.html.resolve()
    if not source_html.is_file():
        print(f"HTML source not found: {source_html}", file=sys.stderr)
        return 1

    output_path = args.output.resolve() if args.output else source_html.with_name(f"{source_html.stem}.hybrid.md")
    review_path = args.review.resolve() if args.review else source_html.with_name(f"{source_html.stem}.hybrid.review.md")
    old_md = source_html.with_suffix(".md")

    layout_parser = PdfHtmlLayoutParser()
    layout_parser.feed(source_html.read_text(encoding="utf-8", errors="replace"))
    rows_by_page = group_rows(layout_parser.blocks)

    review_items: list[str] = []
    output_lines = render_hybrid(rows_by_page, source_html, review_items)
    review_lines = build_review(
        layout_parser,
        rows_by_page,
        output_lines,
        output_path,
        old_md,
        review_items,
    )

    write_text(output_path, output_lines)
    write_text(review_path, review_lines)

    print(f"Wrote: {output_path}")
    print(f"Wrote: {review_path}")
    print(f"Pages: {len(layout_parser.page_labels)}")
    print(f"Blocks: {len(layout_parser.blocks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
