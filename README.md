# Một số thuật ngữ trong Toán rời rạc và Khoa học máy tính

*Selected Terms in Discrete Mathematics and Computer Science — An Annotated English–Vietnamese Glossary*

Một cuốn **sách mở** viết bằng [PreTeXt](https://pretextbook.org/): từ điển chú giải,
đối chiếu Anh–Việt, các thuật ngữ và khái niệm quen thuộc trong **toán rời rạc, lý
thuyết đồ thị và khoa học máy tính**.

## Đọc sách

- 📖 **Bản web**: <https://hoanganhduc.github.io/dm-concepts-vi/>
- 🔎 **Tra cứu nhanh** (lọc thời gian thực, không phân biệt dấu, hai chiều Anh ↔ Việt):
  <https://hoanganhduc.github.io/dm-concepts-vi/tra-cuu.html>
- 📄 **Bản PDF mới nhất**:
  [Releases](https://github.com/hoanganhduc/dm-concepts-vi/releases/latest)

## Ý tưởng

- Tổ chức theo **bảng chữ cái tiếng Anh**: mỗi chương là một chữ cái `A`, `B`, `C`, …
- Mỗi **mục từ** lấy một khái niệm hoặc ký hiệu tiếng Anh (chủ yếu từ *Rosen — Discrete
  Mathematics and Its Applications* và *Liben-Nowell — Connecting Discrete Mathematics
  and Computer Science*), nêu **định nghĩa bằng tiếng Việt**, kèm **nhãn từ loại** và
  liệt kê **mọi** thuật ngữ tiếng Việt tương ứng đã tìm thấy — mỗi biến thể kèm **trích
  dẫn** tới nguồn; một thuật ngữ được đánh dấu là cách dùng phổ biến.
- Nguồn thuật ngữ tiếng Việt: tổng hợp từ hơn 20 giáo trình, sách chuyên khảo trong
  nước và nguồn trực tuyến tin cậy.
- Với những khái niệm mà tiếng Việt **chưa thống nhất**, sách trình bày đầy đủ các quy
  ước (*nếu theo quy ước A thì…; nếu theo quy ước B thì…*) thay vì chọn sẵn một cách.

## Biên dịch và độ tin cậy

Sách được **tạo lập chủ yếu bằng trí tuệ nhân tạo (AI)** rồi rà soát dưới sự điều phối
của người biên soạn, **Duc A. Hoang (Hoàng Anh Đức)** (Trường Đại học Khoa học Tự
nhiên, ĐHQGHN). Tuy mỗi cách dùng đều kèm trích dẫn, người đọc **vẫn nên tự kiểm
chứng** trước khi dùng cho mục đích chính thức: vẫn còn sai sót do quá trình tự động
mặc dù đã có rà soát.

## Đóng góp

Mọi người đều có thể góp phần hoàn thiện cuốn sách:

- **fork** kho này, chỉnh sửa rồi tạo **pull request**; hoặc
- gửi email cho người biên tập: <hoanganhduc@hus.edu.vn>.

Người đóng góp được ghi nhận tự động trong chương **"Lời cảm ơn"** (từ danh sách góp ý
qua email và danh sách tác giả các pull request đã hợp nhất).

## Xây dựng cục bộ

Cần [PreTeXt CLI](https://pretextbook.org/doc/guide/html/tutorial-install.html)
(ví dụ trong một venv) và, cho bản PDF, XeLaTeX.

```bash
bash workflow/scripts/build-web.sh     # bản web  -> output/web
bash workflow/scripts/build-print.sh   # bản PDF  -> output/print/main.pdf
```

Mỗi lần đẩy lên `main`, GitHub Actions tự build bản web (đăng lên GitHub Pages) và tạo
một bản **release PDF** mới.

## Giấy phép

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — xem
[`LICENSE`](LICENSE). Cho phép phân phối, phối lại, chỉnh sửa và phát triển tài liệu,
**chỉ cho mục đích phi thương mại**, có ghi công, và phần phái sinh phải chia sẻ theo
cùng giấy phép.
