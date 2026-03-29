# Scripts — Dhamma Anki / từ vựng Thiền

Thư mục này chứa các file Python xử lý dữ liệu từ vựng. **Luôn chạy lệnh từ thư mục cha `Thiền`** (hoặc dùng đường dẫn đầy đủ tới script), để script tìm đúng `Dhamma_Anki_cleaned.xlsx` và ghi ra `Dhamma_Anki_by_topic/`.

## Cài gói (một lần)

```bash
cd "…\Thiền"
python -m pip install -r scripts/requirements.txt
```

(Tuỳ chọn: cài thêm `matplotlib` nếu sau này có script vẽ biểu đồ từ Excel.)

---

## Bảng file — khi nào dùng file nào?

| File | Công năng (metadata) | Đầu vào | Đầu ra |
| --- | --- | --- | --- |
| `export_dhamma_topics_to_markdown.py` | **Tạo / cập nhật** toàn bộ Markdown theo chủ đề: đọc sheet `Vocabulary_Cleaned`, nhận dòng tiêu đề `1. …`, `2. …`, thêm cột **IPA** (eng-to-ipa + vài sửa tay), ghi `01_….md` … `20_….md` và `Dhamma_Anki_by_topic/README.md`. | `Dhamma_Anki_cleaned.xlsx` | Thư mục `../Dhamma_Anki_by_topic/` |

**Khi nào chạy:** sau khi sửa Excel sạch, hoặc sau khi chỉnh logic IPA trong script — chạy lại để đồng bộ file `.md`.

```bash
cd "…\Thiền"
python scripts/export_dhamma_topics_to_markdown.py
```

---

## Chuỗi dữ liệu (để không nhầm bước)

1. Bản gốc Excel → làm sạch (trùng, cột) → **`Dhamma_Anki_cleaned.xlsx`**
2. Chạy **`export_dhamma_topics_to_markdown.py`** → **`Dhamma_Anki_by_topic/*.md`**

File `split_md_by_topic.py` ở thư mục `Thiền` (nếu còn sót) đã **đổi tên và chuyển** thành `scripts/export_dhamma_topics_to_markdown.py` — chỉ dùng bản trong `scripts/`.
