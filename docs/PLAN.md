# Kế hoạch xây dựng cuốn sách mở: *Từ điển chú giải Thuật ngữ Toán Rời rạc & Lý thuyết Đồ thị (Anh–Việt)*

> **Trạng thái:** Bản kế hoạch (chờ duyệt). Chưa khởi chạy quy trình nhiều-agent.
> **Working title (EN):** *Discrete Mathematics & Graph Theory: An English–Vietnamese Annotated Lexicon*
> **Working title (VI):** *Thuật ngữ Toán Rời rạc và Lý thuyết Đồ thị: Từ điển chú giải Anh–Việt*
> **Định dạng:** PreTeXt (theo khuôn của *Discrete Mathematics: An Open Introduction* — Oscar Levin).
> **Repo:** `DM-Concepts` (chính là repo này).

---

## 0. Nhật ký quyết định (Decision log)

Bốn quyết định nền tảng đã chốt với người dùng (2026-06-21):

| # | Quyết định | Lựa chọn | Hệ quả thiết kế |
|---|------------|----------|------------------|
| D1 | Ngôn ngữ diễn giải | **Chủ yếu tiếng Việt** | Thuật ngữ + ký hiệu tiếng Anh là *đầu mục* (headword); định nghĩa, đối chiếu, ghi chú viết bằng tiếng Việt. |
| D2 | Thể loại | **Từ điển thuật ngữ có chú giải** | Mỗi khái niệm = một *mục từ* gọn (định nghĩa, ký hiệu, thuật ngữ Việt + trích dẫn, ví dụ ngắn), không phải bài giảng đầy đủ. |
| D3 | Phạm vi pilot | **Một lát cắt dọc 1–2 chữ cái** | Làm trọn vẹn end-to-end một chữ (đề xuất **C**), khóa khuôn mẫu, rồi nhân rộng. |
| D4 | Biến thể thuật ngữ | **Liệt kê mọi biến thể kèm nguồn** | Mỗi cách dịch đã gặp được ghi kèm trích dẫn; cách dùng phổ biến/được khuyến nghị được đánh dấu. |
| D5 | Trải nghiệm bản HTML | **Tối ưu tìm kiếm & tra cứu thuật ngữ** | Bản web phải tra cứu nhanh, từ **cả hai chiều Anh ↔ Việt**, **không phân biệt dấu**; xem §5. |

**Nguồn nội dung:**
- Thuật ngữ & định nghĩa tiếng Anh: chủ yếu từ *Rosen — Discrete Mathematics and Its Applications*.
- Thuật ngữ tiếng Việt + trích dẫn: tổng hợp từ **toàn bộ** sách toán rời rạc & lý thuyết đồ thị tiếng Việt trong thư viện Zotero của người dùng.
- Thứ tự tra cứu tài liệu (bắt buộc): **Zotero → Calibre → trực tuyến**.

---

## 1. Tóm tắt điều hành

Cuốn sách là một **từ điển song ngữ có chú giải**, tổ chức theo bảng chữ cái tiếng Anh (mỗi chữ cái = một chương). Mỗi mục từ lấy một khái niệm/ký hiệu tiếng Anh (theo Rosen), nêu định nghĩa bằng tiếng Việt, liệt kê **mọi** thuật ngữ tiếng Việt tương ứng đã tìm thấy — mỗi biến thể kèm **trích dẫn chính xác** (sách, trang) tới nguồn tiếng Việt trong Zotero — kèm một ví dụ ngắn và các tham chiếu chéo. **Bản HTML được tối ưu để tìm kiếm và tra cứu thuật ngữ từ cả hai chiều Anh ↔ Việt, không phân biệt dấu** (xem §5).

Sản xuất nội dung được vận hành bằng một **"nhà máy" nhiều-agent** kết hợp đúng ba cơ chế người dùng yêu cầu:

1. **`autonomous-research-loop`** — vòng lặp tự trị **có biên** điều phối việc sản xuất **theo từng chữ cái**: tìm → trích xuất → khai thác thuật ngữ Việt → soạn mục → kiểm chứng → mã hóa PreTeXt → rà soát. Có sổ cái (ledger), ngân sách cứng, cổng bằng chứng, điều kiện dừng.
2. **`cross-agent-delegation`** — **hợp đồng gói nhiệm vụ** (task/result packet) ràng buộc mọi lần giao việc cho agent chuyên trách (Trích thuật ngữ, Khai thác tiếng Việt, Soạn định nghĩa, Mã hóa PreTeXt, Kiểm chứng). Orchestrator coi mọi gói kết quả là *bằng chứng chưa tin cậy* cho tới khi tự xác minh.
3. **`agent-group-discuss`** — **hội đồng biên tập nhiều-agent** triệu tập tại các cổng then chốt: chốt khuôn mẫu pilot, xử lý xung đột biến thể thuật ngữ, rà soát chất lượng cuối mỗi chương.

Lộ trình 5 pha: **Pha 0** nền móng & công cụ → **Pha 1** pilot (chữ C, khóa khuôn) → **Pha 2** nhân rộng A–Z bằng vòng lặp tự trị → **Pha 3** hợp nhất & rà soát toàn sách → **Pha 4** vòng bảo trì.

---

## 2. Hình dạng cuốn sách

### 2.1 Cấu trúc vĩ mô
- **Front matter:** trang tiêu đề, lời nói đầu (mục đích, cách dùng từ điển, quy ước trích dẫn & ký hiệu), bảng chữ viết tắt.
- **Thân sách:** 26 chương `A`, `B`, …, `Z` (bỏ qua chữ không có mục từ). Mỗi chương = các mục từ tiếng Anh bắt đầu bằng chữ cái đó, sắp theo a–z.
- **Back matter:**
  - **Chỉ mục song ngữ** (Index): cả đầu mục tiếng Anh lẫn mọi thuật ngữ tiếng Việt → cho phép tra cứu từ **cả hai** chiều.
  - **Trang tra cứu nhanh** (lọc-khi-gõ, không phân biệt dấu): xem §5.
  - **Danh sách ký hiệu** (Notation) tự sinh từ phần tử `<notation>` của PreTeXt.
  - **Thư mục** (References): danh mục đầy đủ nguồn tiếng Việt (xuất từ Zotero).
  - Colophon / giấy phép.

### 2.2 Giải phẫu một mục từ
Mỗi mục từ gồm các trường (xem mô hình dữ liệu ở §3):

1. **Đầu mục (headword):** thuật ngữ tiếng Anh + ký hiệu chuẩn (vd. *Chromatic number*, $$\chi(G)$$).
2. **Định nghĩa (tiếng Việt):** phát biểu hình thức, dựa trên định nghĩa của Rosen, kèm tham chiếu mục Rosen.
3. **Thuật ngữ tiếng Việt tương ứng:** danh sách **mọi** biến thể, mỗi biến thể kèm `[trích dẫn]` (tác giả, năm, trang); đánh dấu cách dùng phổ biến/khuyến nghị (theo D4).
4. **Ký hiệu & cách viết:** đưa vào `<notation>` để gom vào danh sách ký hiệu.
5. **Ví dụ ngắn** (tùy chọn, cho khái niệm trọng tâm).
6. **Xem thêm (cross-reference):** liên kết tới các mục liên quan (vd. *Coloring*, *Clique number*).
7. **Chỉ mục:** `<idx>` cho đầu mục tiếng Anh **và** từng thuật ngữ tiếng Việt.

---

## 3. Mô hình dữ liệu một mục từ

Mỗi mục từ trước hết tồn tại dưới dạng **dữ liệu có cấu trúc** (YAML, trong `data/terms/`) để máy kiểm tra được, rồi mới biên dịch sang PreTeXt. Lược đồ:

```yaml
id: chromatic-number              # khóa kebab-case, duy nhất toàn sách
letter: C
headword_en: "Chromatic number"
notation: "\\chi(G)"              # LaTeX, rỗng nếu không có ký hiệu
rosen_ref: "Rosen §10.8"          # mục định nghĩa trong Rosen
definition_vi: >                  # định nghĩa tiếng Việt (văn xuôi)
  Sắc số của đồ thị G, ký hiệu \chi(G), là số màu nhỏ nhất cần dùng
  để tô các đỉnh sao cho hai đỉnh kề nhau luôn khác màu.
vi_terms:                         # MỌI biến thể, mỗi cái kèm nguồn (D4)
  - term: "sắc số"
    source_id: bib-doquockhanh-2010
    page: "tr. 142"
    recommended: true             # đánh dấu cách dùng phổ biến
  - term: "số màu"
    source_id: bib-nguyenduchung-2003
    page: "tr. 88"
    recommended: false
example_vi: >                     # tùy chọn
  Với đồ thị đầy đủ K_n ta có \chi(K_n)=n.
see_also: [coloring, clique-number, k-colorable]
status: draft                     # draft | verified | panel-approved
provenance:                       # dấu vết để kiểm chứng & phục hồi
  extracted_by: "packet:term-extract-C#003"
  verified_by: "packet:verify-C#011"
```

Lược đồ này là **hợp đồng** giữa các agent: Khai thác sinh `vi_terms`, Kiểm chứng xác nhận `source_id`/`page`, Mã hóa biến nó thành PreTeXt. Trường `status` lái cổng chất lượng.

---

## 4. Ánh xạ sang PreTeXt

Khuôn công cụ theo đúng *discrete-book* của Levin: **PreTeXt CLI**, xuất **web (HTML) + PDF**, triển khai **GitHub Pages**, giấy phép mở.

Ánh xạ trường → phần tử PreTeXt:

| Trường dữ liệu | Phần tử PreTeXt |
|----------------|------------------|
| Chữ cái | `<chapter xml:id="ch-C"><title>C</title>` |
| Mục từ | `<definition xml:id="def-chromatic-number">` (khối *definition-like*, có số & tham chiếu chéo) |
| Đầu mục EN + thuật ngữ VI | `<title>` + nhiều `<idx>` (song ngữ) |
| Ký hiệu | `<notation><usage>…</usage><description>…</description></notation>` → tự gom vào danh sách ký hiệu |
| Định nghĩa & biến thể | `<statement>` với `<p>`, `<ul>`; trích dẫn bằng `<xref ref="bib-…"/>` |
| Ví dụ | `<example>` |
| Xem thêm | `<xref ref="def-…"/>` |
| Nguồn tiếng Việt | `<biblio xml:id="bib-…">` trong `references.ptx` (xuất từ Zotero BibTeX) |

**Ví dụ một mục từ đã mã hóa** (mẫu để khóa khuôn ở pilot):

```xml
<definition xml:id="def-chromatic-number">
  <title>Chromatic number — Sắc số</title>
  <idx><h>chromatic number</h></idx>
  <idx><h>sắc số</h></idx>
  <idx><h>số màu</h></idx>
  <notation>
    <usage><m>\chi(G)</m></usage>
    <description>sắc số của đồ thị <m>G</m></description>
  </notation>
  <statement>
    <p>
      <term>Sắc số</term> của đồ thị <m>G</m>, ký hiệu <m>\chi(G)</m>, là số màu
      nhỏ nhất cần dùng để tô các đỉnh sao cho hai đỉnh kề nhau luôn khác màu
      (theo <xref ref="bib-rosen-2019"/>, §10.8).
    </p>
    <p>Thuật ngữ tiếng Việt tương ứng:</p>
    <ul>
      <li><term>sắc số</term> <xref ref="bib-doquockhanh-2010"/> (tr. 142) — cách dùng phổ biến</li>
      <li><term>số màu</term> <xref ref="bib-nguyenduchung-2003"/> (tr. 88)</li>
    </ul>
  </statement>
</definition>
```

> Lưu ý kỹ thuật: ký hiệu tiếng Việt cần font/locale phù hợp khi xuất PDF (PreTeXt dùng `xelatex` hỗ trợ Unicode tốt). Sẽ kiểm thử ở Pha 0.

---

## 5. Khả năng tìm kiếm & tra cứu (bản HTML)

Vì đây là một **từ điển**, trải nghiệm tra cứu trên bản web là ưu tiên hàng đầu (yêu cầu D5). Bản HTML được thiết kế để tìm kiếm và tra cứu thuật ngữ thật nhanh, **từ cả hai chiều Anh ↔ Việt**, và **không phụ thuộc server** (chạy hoàn toàn phía client, hợp với hosting tĩnh như GitHub Pages).

Năm lớp tra cứu, xếp chồng:

1. **Tìm kiếm toàn văn sẵn có của PreTeXt** — bật tính năng search của PreTeXt-CLI cho bản web; lập chỉ mục toàn bộ nội dung. Đây là lớp nền.
2. **Trang "Tra cứu nhanh" (instant filter)** — một trang companion (`tra-cuu.html`) liệt kê **mọi** mục từ kèm ô **lọc-khi-gõ** bằng JavaScript thuần. Khớp đồng thời với: đầu mục tiếng Anh, **mọi** biến thể tiếng Việt, ký hiệu, và phần định nghĩa. Kết quả lọc tức thời, mỗi dòng liên kết thẳng tới mục đầy đủ. Đây là tính năng "sát thủ" cho một từ điển.
3. **Tìm kiếm không phân biệt dấu (diacritics-insensitive)** — chuẩn hóa Unicode (NFD + bỏ dấu tổ hợp) khi so khớp, để gõ `so mau` vẫn ra `số màu`, gõ `do thi` ra `đồ thị`, gõ `cay khung` ra `cây khung`. Thiết yếu cho tiếng Việt và là điểm yếu của tìm kiếm mặc định.
4. **Chỉ mục song ngữ (Index)** — `<idx>` cho cả đầu mục EN lẫn từng thuật ngữ VI, nên trang Index tự sinh tra được từ **cả hai** ngôn ngữ, mọi mục đều có liên kết.
5. **Điều hướng A–Z + permalink** — thanh nhảy nhanh theo chữ cái; mỗi mục có `xml:id` → URL/anchor **ổn định** để đánh dấu, trích dẫn, hoặc chia sẻ trực tiếp tới một thuật ngữ.

Điểm mấu chốt về kiến trúc: dữ liệu cho lớp (2)/(3) là `entries.json`, **sinh tự động** từ chính `data/terms/*.yaml` (lược đồ §3). Nhờ vậy **một nguồn dữ liệu duy nhất** nuôi cả nội dung PreTeXt lẫn trang tra cứu nhanh — không nhập liệu trùng. Khả năng tìm kiếm được kiểm thử ngay ở pilot (Pha 1) và là một tiêu chí ra của chương C.

---

## 6. Kiến trúc "nhà máy" nhiều-agent

Đây là phần trung tâm: ghép **ba** cơ chế thành một dây chuyền sản xuất mạch lạc. Orchestrator (agent chính) sở hữu điều phối, xác nhận, và tổng hợp cuối.

### 6.1 `autonomous-research-loop` — bộ điều khiển theo từng chữ cái

Mỗi chữ cái được sản xuất bởi **một** vòng lặp tự trị có biên. Bốn file trạng thái bắt buộc đặt trong `workflow/loop/<letter>/`:

- **`loop_state.json`** — `goal`: "Sản xuất chương <X> đã kiểm chứng & build được"; `success_criteria`; `mode`; `stop_conditions`; `status`.
- **`budget.json`** — `max_iterations` (đề xuất 8/chữ cái), `max_child_workers` (đề xuất 5), `max_source_hops`, ngân sách token.
- **`iterations.jsonl`** — bản ghi nối-thêm mỗi vòng (objective, evidence checked, actions, output, gaps, budget, decision).
- **`recovery.md`** — điểm phục hồi, blocker, hành động an toàn kế tiếp, khoảng trống bằng chứng.

**Mode dùng:** `bounded-research` (khai thác + soạn), `panel-loop` (cổng rà soát).

**Cổng bằng chứng (evidence gates):**
- Mỗi thuật ngữ Việt phải có `source_id` + trang thật → đối chiếu lại với Zotero trước khi nhận.
- Mỗi định nghĩa phải có `rosen_ref`.
- Mỗi mục phải **build được** trong PreTeXt trước khi gộp.
- Khẳng định phân biệt rõ *bằng chứng đã xác nhận* với *suy luận*.

**Điều kiện dừng (mặc định, theo hợp đồng skill):** dừng khi (a) chương hoàn tất + build + hội đồng duyệt, (b) cạn ngân sách cứng, hoặc (c) người dùng yêu cầu dừng. Plateau / thiếu bằng chứng / blocker lặp lại **không** phải điều kiện dừng — ghi nhận rồi hạ quyết định xuống `revise`/`delegate` và tiếp tục.

### 6.2 `cross-agent-delegation` — hợp đồng gói cho agent chuyên trách

Mọi lần giao việc dùng **task packet** tối thiểu, đóng kín. Năm vai chuyên trách:

| Vai (worker) | Đầu vào | Đầu ra | Công cụ chính |
|--------------|---------|--------|----------------|
| **Term Extractor** | chữ cái + Rosen (Zotero/Calibre) | danh sách thuật ngữ EN + `rosen_ref` + định nghĩa EN | `literature-scout`, `docling` |
| **Vietnamese Term Miner** | 1 thuật ngữ EN + corpus Việt (Zotero) | mọi `vi_terms` + `source_id` + trang | `zotero`, `docling` |
| **Definition Drafter** | mục dữ liệu | `definition_vi`, `example_vi` theo văn phong | `draft-writing`, `prose` |
| **PreTeXt Encoder** | mục đã verify | XML hợp lệ + cập nhật `references.ptx` + build pass | `functions.exec_command` (pretext) |
| **Verifier / Fact-checker** | mục draft | xác nhận ánh xạ thuật ngữ, trích dẫn, đúng toán học; cờ xung đột | `proof-checker`, `paper-reviewer` |

**Lược đồ task packet** (đóng kín, không mang quyền thực thi):
```yaml
objective: "Khai thác thuật ngữ tiếng Việt cho 'Chromatic number'"
input_refs: [ "term:chromatic-number", "zotero-collection:DM-VI" ]
constraints:
  - "Chỉ dùng nguồn tiếng Việt trong Zotero (thứ tự Zotero→Calibre→online)."
  - "Không bịa thuật ngữ hay số trang."
  - "Ghi MỌI biến thể đã gặp."
evidence_requirements: "source_refs kèm số trang cho mỗi biến thể"
output_contract: "danh sách vi_terms theo lược đồ §3"
exclusions: [ "không sửa file", "không spawn agent con", "không tổng hợp kết luận cuối" ]
```
**Quy tắc cứng:** gói **không** chứa trường mang quyền (`execute`, `command`, `confirmed_by_parent`, …); orchestrator **tự xác minh** schema + provenance + nguồn trước khi chấp nhận result packet (coi là chưa tin cậy).

### 6.3 `agent-group-discuss` — hội đồng biên tập

Triệu tập tại **ba** cổng, mỗi lần có **cổng xác nhận** trước khi spawn:

1. **Chốt khuôn pilot** (cuối Pha 1): phê duyệt mẫu mục từ, văn phong, quy ước trích dẫn, chính sách biến thể.
2. **Xử lý xung đột biến thể** (theo nhu cầu, kiểu `debate`): khi các nguồn mâu thuẫn về cách dịch/định nghĩa.
3. **Rà soát chất lượng cuối mỗi chương** (kiểu `panel_judge`).

**Khuôn mẫu:** phỏng theo *Knuth Structured Manuscript Review*, vai:
- **Correctness Reviewer** (định nghĩa đúng toán học so với Rosen) — tier R4.
- **Lexicography & Terminology Reviewer** (ánh xạ thuật ngữ trung thực, đủ biến thể, trích dẫn chính xác) — R3.
- **Exposition/Clarity Reviewer** (văn phong tiếng Việt, theo `math-manuscript-style`) — R2/R3.
- **Editor / Synthesizer** (hợp nhất, ra quyết định) — R3/R4.

Mọi vai sinh văn bản phải nạp khối văn phong (`writing-style-settings.md` + `math-manuscript-style.md`).

### 6.4 Luồng end-to-end một mục từ
```
[autonomous-research-loop: chữ X]
  1. Term Extractor (packet) ──▶ danh sách thuật ngữ EN cho X
  2. for each term:
       Vietnamese Miner (packet) ──▶ vi_terms + trích dẫn
       Definition Drafter (packet) ──▶ definition_vi
       Verifier (packet) ──▶ xác nhận / cờ xung đột
       └─ nếu xung đột ──▶ [agent-group-discuss: debate] ──▶ quyết định
  3. PreTeXt Encoder (packet) ──▶ XML + build check
  4. cuối chữ X ──▶ [agent-group-discuss: panel_judge] ──▶ duyệt / sửa
  5. loop ghi iteration, cập nhật recovery; chữ X xong ──▶ chữ kế tiếp
  (orchestrator xác minh MỌI result packet trước khi nhận)
```

---

## 7. Lộ trình theo pha

### Pha 0 — Nền móng & công cụ *(thủ công, orchestrator)*
- **0.1** Liệt kê corpus tiếng Việt trong Zotero (toán rời rạc + lý thuyết đồ thị) → `data/sources/registry.yaml`; xuất BibTeX → `source/references.ptx`. Xác nhận Rosen có trong Zotero/Calibre.
- **0.2** Cài đặt PreTeXt CLI; dựng khung repo (xem §8); cấu hình xuất web + PDF (kiểm thử Unicode tiếng Việt với `xelatex`); **bật tìm kiếm web** + script sinh `entries.json` cho trang tra cứu nhanh (§5).
- **0.3** CI/CD: GitHub Actions build + deploy GitHub Pages; chọn giấy phép mở (đề xuất **CC BY-SA 4.0**, như sách mở).
- **0.4** Chốt lược đồ dữ liệu mục từ (§3) + script `validate-entry`.
- **Tiêu chí ra:** repo build ra trang web rỗng + 1 mục mẫu; CI xanh; registry nguồn khởi tạo.

### Pha 1 — Pilot: chữ **C** (khóa khuôn) *(D3)*
- Chạy trọn dây chuyền §6.4 cho chữ C (Connected, Chromatic number, Cycle, Coloring, Clique, Complement, Complete graph, …).
- Triệu tập **hội đồng biên tập** (cổng 1) để phê duyệt: mẫu mục từ, văn phong, trích dẫn, chính sách biến thể, lược đồ chỉ mục song ngữ.
- **Tiêu chí ra:** một chương C hoàn chỉnh, đã kiểm chứng, build & deploy; "khuôn mẫu" + script tái dùng đã khóa; **tra cứu nhanh + tìm kiếm không phân biệt dấu hoạt động trên bản web**; báo cáo bài học.

### Pha 2 — Nhân rộng A–Z *(autonomous-research-loop)*
- Mỗi chữ cái còn lại: một vòng lặp tự trị có biên (tái dùng khuôn đã khóa), giao việc qua packet, hội đồng làm cổng rà soát mỗi chương.
- Ưu tiên thứ tự theo mật độ thuật ngữ (vd. nhóm giàu khái niệm: G *graph/…*, T *tree/…*, P *path/…*).
- **Tiêu chí ra:** 26 chương verify + build; mọi cross-ref phân giải được.

### Pha 3 — Hợp nhất & rà soát toàn sách
- Dựng **chỉ mục song ngữ**, **danh sách ký hiệu**; giải trùng thuật ngữ giữa các chương; thống nhất cách đặt biến thể.
- Hội đồng rà soát toàn sách; cổng `research-verification-gate` trước khi gọi "hoàn tất"; phát hành phiên bản 1.0.

### Pha 4 — Vòng bảo trì
- Vòng lặp tự trị chế độ `monitor`: nạp nguồn Zotero mới / chỉnh sửa theo thời gian, không cần nhắc lặp.

---

## 8. Cấu trúc repo & toolchain

```
DM-Concepts/
├── README.md
├── LICENSE                     # CC BY-SA 4.0 (đề xuất)
├── docs/
│   └── PLAN.md                 # tài liệu này
├── project.ptx                 # manifest PreTeXt CLI
├── publish/
│   └── publication.ptx         # cấu hình xuất web/PDF
├── source/
│   ├── main.ptx                # gốc sách: frontmatter + chương A..Z + backmatter
│   ├── frontmatter.ptx
│   ├── ch-A.ptx … ch-Z.ptx     # mỗi chữ cái một file (xinclude)
│   ├── references.ptx          # thư mục nguồn Việt (từ Zotero)
│   └── backmatter.ptx          # index, notation, colophon
├── data/
│   ├── sources/registry.yaml   # đăng ký nguồn tiếng Việt
│   ├── terms/entries-C.yaml …  # dữ liệu mục từ theo lược đồ §3
│   └── rosen-index.yaml        # chỉ mục thuật ngữ Rosen
├── workflow/
│   ├── loop/<letter>/          # loop_state.json, budget.json, iterations.jsonl, recovery.md
│   ├── packets/                # task/result packet (cross-agent-delegation)
│   ├── panels/                 # artifact agent-group-discuss
│   └── scripts/                # mine-zotero, bibtex2ptx, validate-entry, build-search-index, build
├── assets/search/              # tra-cuu.html (lọc-khi-gõ), lookup.js, entries.json (sinh tự động)
└── .github/workflows/build.yml # CI: build + deploy Pages
```

**Toolchain:** PreTeXt CLI (`pretext build web`, `pretext build pdf`), `xelatex` cho PDF Unicode, GitHub Actions → Pages. Bản web **bật tìm kiếm toàn văn của PreTeXt** và kèm **trang tra cứu nhanh** (§5). Mọi truy xuất nguồn theo thứ tự Zotero→Calibre→online; **không** dùng `curl`/`wget` tải từ trang xuất bản.

---

## 9. Cổng chất lượng & bằng chứng

- **Không trích dẫn → không vào sách:** mọi thuật ngữ Việt phải có `source_id` + trang thật, orchestrator đối chiếu Zotero.
- **Định nghĩa đối chiếu Rosen:** sai lệch → Verifier chặn.
- **Build-gate:** mỗi mục phải compile PreTeXt trước khi gộp (kiểm trong CI).
- **Xung đột → hội đồng:** mâu thuẫn biến thể/định nghĩa đưa ra `agent-group-discuss` (debate).
- **Tách bằng chứng/suy luận:** mọi khuyến nghị phân biệt rõ.
- **Cổng giao hàng:** `research-verification-gate` trước mọi tuyên bố "xong/hoàn tất".

---

## 10. Ngân sách, rủi ro, chỉ số

**Ngân sách (đề xuất, mỗi chữ cái):** ≤ 8 vòng lặp; ≤ 5 worker đồng thời; cổng hội đồng 2 vòng. Có thể chỉnh ở `budget.json`.

**Rủi ro & giảm thiểu:**
| Rủi ro | Giảm thiểu |
|--------|------------|
| Thuật ngữ Việt không nhất quán giữa nguồn | D4: liệt kê mọi biến thể + đánh dấu phổ biến; hội đồng xử lý xung đột |
| Trích dẫn/trang bịa | Cổng bằng chứng + orchestrator đối chiếu Zotero |
| Rosen không có trong Zotero/Calibre | Pha 0.1 xác nhận trước; nếu thiếu → `getscipapers` |
| Font/PDF tiếng Việt lỗi | Kiểm thử `xelatex` ở Pha 0.2 |
| Phải sửa khuôn hàng loạt về sau | Pilot khóa khuôn trước khi nhân rộng (D3) |
| Vòng lặp chạy lan | Ngân sách cứng + điều kiện dừng + recovery ledger |

**Chỉ số tiến độ:** số mục `verified` / `panel-approved` mỗi chương; tỉ lệ mục có ≥1 trích dẫn; số cross-ref phân giải được; CI xanh.

---

## 11. Việc cần bạn duyệt để bắt đầu

1. **Tiêu đề & giấy phép:** xác nhận working title và CC BY-SA 4.0.
2. **Chữ pilot:** xác nhận **C** (hay chọn chữ khác).
3. **Cho phép Pha 0:** dựng khung repo PreTeXt + liệt kê corpus Zotero + cài toolchain.
4. **Cách chạy nhà máy:** vì quy trình nhiều-agent (Pha 1–2) tốn nhiều token, xác nhận bạn muốn khởi chạy bằng orchestration nhiều-agent (mở lại `ultracode`/Workflow) khi tới Pha 1.

> Sau khi bạn duyệt, tôi bắt đầu **Pha 0** (chỉ thao tác cục bộ, an toàn) rồi mới tới pilot.
