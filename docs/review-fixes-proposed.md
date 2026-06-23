# Đề xuất sửa từ kết quả review

Review (Codex 20 batch + audit toàn cục) phát hiện thuật ngữ **recommended** không tuân thủ chính sách "recommended phải là thuật ngữ có trích dẫn từ nguồn không-phải-tham-khảo, ưu tiên nguồn mới". Các mục được chia 4 nhóm theo rủi ro.

## Nhóm 1 — RE-POINT (39): cùng thuật ngữ, chỉ gắn lại trích dẫn (AN TOÀN)

Thuật ngữ recommended **không đổi**; chỉ chuyển nhãn recommended sang một trích dẫn từ nguồn không-phải-Rosen-2003 đã có sẵn trong mục. Khuyến nghị: **áp dụng tự động**.

| id | thuật ngữ (giữ nguyên) | gắn trích dẫn |
|---|---|---|
| algorithm-analysis | Phân tích thuật toán | bib-nguyenducnghia-2006 |
| assignment | Phép gán | bib-nguyenducnghia-2006 |
| axiom | Tiên đề | bib-nguyenhuudien-2019 |
| bit | bit | bib-nguyenhuudien-2019 |
| cartesian-product | Tích Đềcác | bib-nguyenducnghia-2006 |
| ceiling-function | Hàm trần | bib-nguyenhuudien-2019 |
| coefficient | hệ số | bib-nguyenhuudien-2019 |
| compound-proposition | Mệnh đề phức hợp | bib-nguyenhuudien-2019 |
| conjecture | Giả thuyết | bib-leanhvinh-2020 |
| conjunction | Hội | bib-nguyenducnghia-2006 |
| digit | chữ số | bib-nguyenhoangthach-2020 |
| direct-proof | Chứng minh trực tiếp | bib-nguyenhuudien-2019 |
| disjoint | rời nhau | bib-nguyenhuudien-2019 |
| disjunction | Tuyển | bib-nguyenducnghia-2006 |
| decryption | giải mã | bib-nguyenducnghia-2006 |
| edge-chromatic-number | Sắc số cạnh | bib-leanhvinh-2020 |
| empty-set | Tập hợp rỗng | bib-nguyenhuudien-2019 |
| flowchart | Sơ đồ khối | bib-hoangchithanh-2007 |
| greatest-lower-bound | chặn dưới lớn nhất | bib-nguyenhuudien-2019 |
| inclusion-exclusion-principle | Nguyên lý bù trừ | bib-nguyenhuudien-2019 |
| indirect-proof | Chứng minh gián tiếp | bib-nguyenhuudien-2019 |
| inorder-traversal | trung thứ tự | bib-nguyenhuudien-2019 |
| irrational-number | số vô tỷ | bib-ngodactan-2004 |
| logarithm | lôgarit | bib-nguyenhuudien-2019 |
| multiple | bội | bib-leanhvinh-2020 |
| number-theory | Lý thuyết số | bib-ngodactan-2004 |
| power-set | tập lũy thừa | bib-ngodactan-2004 |
| parent | Đỉnh cha | bib-nguyenhoangthach-2020 |
| power | lũy thừa | bib-nguyenhuudien-2019 |
| proof | Chứng minh | bib-nguyenhuudien-2019 |
| pseudocode | Giả mã | bib-nguyenhuudien-2019 |
| spanning-subgraph | đồ thị con bao trùm | bib-ngodactan-2004 |
| symmetric-difference | Hiệu đối xứng | bib-nguyenducnghia-2006 |
| sorting | sắp xếp | bib-leanhvinh-2020 |
| term | số hạng | bib-nguyenhoangthach-2020 |
| the-pigeonhole-principle | Nguyên lý chuồng bồ câu | bib-ngodactan-2004 |
| the-product-rule | Quy tắc nhân | bib-nguyenhoangthach-2020 |
| union-of-sets | hợp của hai tập hợp | bib-nguyenhoangthach-2020 |
| variable | biến | bib-nguyenhuudien-2019 |

## Nhóm 2 — SỬA NGỮ NGHĨA / cải thiện rõ ràng (2): đã xác minh thủ công

| id | recommended hiện tại | đổi thành | trích dẫn | lý do |
|---|---|---|---|---|
| geodesic | khoảng cách | **đường đi ngắn nhất** | bib-nguyenhuudien-2019 | Headword là *shortest path*; "khoảng cách" = độ dài (distance). Biến thể có trích dẫn khớp khái niệm. |
| conditional-statement | Cấu trúc điều kiện | **Phép kéo theo** | bib-nguyenhuudien-2019 | "Cấu trúc điều kiện" là dịch máy (giống lập trình); dùng biến thể có trích dẫn nguồn-thật gần nghĩa nhất. |

## Nhóm 3 — ĐỔI THUẬT NGỮ (73): cần bạn duyệt từng mục

Recommended hiện tại khác mọi biến thể có trích dẫn. Một số là dịch máy nên thay; một số ứng viên lại **sai/hẹp nghĩa** (vd `propositional-function` "hàm mệnh đề" vs ứng viên "vị từ"=predicate). KHÔNG áp dụng hàng loạt.

| id | recommended hiện tại | nguồn gốc | ứng viên có trích dẫn |
|---|---|---|---|
| asymptotic-notation | ký hiệu ô lớn | uncited | big-O (bib-nguyenhuudien-2019); quan hệ big-O (bib-nguyenhuudien-2019); đánh giá big-O (bib-nguyenhuudien-2019) |
| associated-homogeneous-recurrence-relation | hệ thức truy hồi thuần nhất tương ứng | uncited | quan hệ truy hồi thuần nhất liên kết (bib-nguyenhoangthach-2020) |
| asymptotic-estimate | đánh giá tiệm cận | uncited | đánh giá big-O (bib-nguyenhuudien-2019) |
| atomic-proposition | mệnh đề nguyên tử | Rosen-2003 | mệnh đề sơ cấp (bib-nguyenhuudien-2019) |
| average-case-complexity | Độ phức tạp trường hợp trung bình | uncited | thời gian tính trung bình (bib-nguyenducnghia-2006) |
| backtracking | kỹ thuật quay lui | Rosen-2003 | thuật toán quay lui (bib-nguyenducnghia-2006) |
| best-case-complexity | Độ phức tạp trường hợp tốt nhất | uncited | thời gian tính tốt nhất (bib-nguyenducnghia-2006) |
| bi-implication | tương đương | Rosen-2003 | phép tương đương (bib-nguyenhuudien-2019) |
| binary-operator | toán tử hai ngôi | Rosen-2003 | toán tử logic (bib-nguyenhuudien-2019); toán tử (bib-ngodactan-2004) |
| binary | Hệ cơ số 2 (nhị phân) | uncited | khai triển nhị phân (bib-nguyenhuudien-2019); biểu diễn nhị phân (bib-nguyenducnghia-2006); biểu diễn nhị phân (bib-hoangchithanh-2007) |
| boolean-variable | biến Boole | Rosen-2003 | biến logic (bib-nguyenhuudien-2019) |
| bound-variable | biến ràng buộc | uncited | biến bị ràng buộc (bib-nguyenhuudien-2019) |
| carry | nhớ | Rosen-2003 | số nhớ (bib-nguyenhuudien-2019); có nhớ (bib-nguyenducnghia-2006) |
| centre | tâm | Rosen-2003 | tâm của đồ thị (bib-hoangchithanh-2007); trung tâm (bib-leanhvinh-2020); đỉnh tâm (bib-ngodactan-2004) |
| chinese-postman-problem | Bài toán người đưa thư Trung Hoa | uncited | bài toán người phát thư Trung Hoa (bib-nguyenhuudien-2019) |
| conditional-statement | Cấu trúc điều kiện | uncited | Phép kéo theo (bib-nguyenhuudien-2019) |
| congruence | phương trình đồng dư | Rosen-2003 | quan hệ đồng dư (bib-nguyenhuudien-2019); phép đồng dư (bib-nguyenhuudien-2019) |
| conjunctive-normal-form | dạng hội chuẩn tắc | Rosen-2003 | dạng chuẩn tắc hội (bib-nguyenhuudien-2019); dạng chính tắc hội (bib-nguyenhuudien-2019); dạng hội chuẩn tắc hoàn toàn (bib-nguyenducnghia-2006) |
| contradiction | mâu thuẫn | Rosen-2003 | hằng sai (bib-nguyenhuudien-2019) |
| converse | mệnh đề đảo | Rosen-2003 | mệnh đề ngược lại (bib-hoangchithanh-2007); điều ngược lại (bib-nguyenducnghia-2006) |
| cover | bao phủ | uncited | tập phủ đỉnh (bib-leanhvinh-2020); tập phủ cạnh (bib-leanhvinh-2020); phủ đỉnh (bib-nguyenducnghia-2006) |
| character-cipher | mật mã ký tự | uncited | mật mã học (bib-hoangchithanh-2007) |
| de-morgans-laws-for-quantifiers | Luật De Morgan cho lượng từ | uncited | quy tắc phủ định mệnh đề có lượng từ (bib-nguyenhuudien-2019) |
| decimal | Hệ cơ số 10 (hệ thập phân) | uncited | hệ cơ đếm thập phân (bib-nguyenducnghia-2006); ký số thập phân (bib-nguyenhuudien-2019) |
| difference | Hiệu | Rosen-2003 | hiệu của tập (bib-nguyenducnghia-2006) |
| directed-acyclic-graph | đồ thị có hướng không có chu trình | uncited | đồ thị định hướng phi chu trình (bib-hoangchithanh-2007); đồ thị định hướng phi chu trình (bib-nguyenhuudien-2019) |
| disjunctive-syllogism | Tam đoạn luận tuyển | Rosen-2003 | Tam đoạn luận rời (bib-nguyenhuudien-2019) |
| dual | Đối ngẫu | Rosen-2003 | đồ thị đối ngẫu (bib-nguyenhuudien-2019); đồ thị đối ngẫu (bib-nguyenhoangthach-2020); đồ thị đối ngẫu (bib-ngodactan-2004) |
| duality-principle | Nguyên lý đối ngẫu | Rosen-2003 | luật đối ngẫu (bib-nguyenducnghia-2006) |
| even | chẵn | Rosen-2003 | số chẵn (bib-nguyenhuudien-2019); số nguyên chẵn (bib-nguyenhuudien-2019); số chẵn (bib-nguyenhoangthach-2020) |
| factorial-sequence | Dãy giai thừa | uncited | n giai thừa (bib-nguyenhoangthach-2020); hàm giai thừa (bib-ngodactan-2004) |
| functionally-complete | đầy đủ | Rosen-2003 | hệ đầy đủ (bib-nguyenducnghia-2006) |
| generalized-binomial-coefficient | hệ số nhị thức tổng quát | uncited | hệ số nhị thức mở rộng (bib-nguyenhoangthach-2020) |
| graph-invariant | bất biến đồ thị | uncited | bất biến đối với phép đẳng cấu (bib-nguyenhuudien-2019); tính chất bất biến (bib-nguyenhoangthach-2020) |
| geometric-distribution | phân phối hình học | uncited | biến ngẫu nhiên (bib-leanhvinh-2020) |
| implication | kéo theo | Rosen-2003 | phép kéo theo (bib-nguyenhuudien-2019); hàm kéo theo (bib-nguyenducnghia-2006) |
| increasing | tăng | Rosen-2003 | hàm tăng (bib-nguyenhuudien-2019); hàm tăng (bib-nguyenducnghia-2006); dãy tăng (bib-nguyenducnghia-2006) |
| inductive-step | Bước quy nạp | Rosen-2003 | Bước qui nạp (bib-nguyenhuudien-2019) |
| inference-rule | quy tắc suy luận | Rosen-2003 | quy tắc suy diễn (bib-nguyenhuudien-2019); luật suy diễn (bib-nguyenhuudien-2019) |
| jordan-curve-theorem | định lý đường cong Jordan | uncited | đường cong Jordan khép kín (bib-ngodactan-2004); đường cong Jordan (bib-ngodactan-2004) |
| logical-operators | toán tử lôgic | uncited | phép toán logic (bib-nguyenhuudien-2019); liên kết logic (bib-nguyenhuudien-2019) |
| logical-rules-of-inference | Các quy tắc suy luận lôgic | uncited | quy tắc suy diễn (bib-nguyenhuudien-2019); luật suy diễn (bib-nguyenhuudien-2019) |
| minimization | rút gọn | Rosen-2003 | tối thiểu hoá (bib-nguyenducnghia-2006); dạng tuyển chuẩn tắc tối thiểu (bib-nguyenducnghia-2006) |
| minterm | tiểu hạng | Rosen-2003 | hội sơ cấp (bib-nguyenducnghia-2006); hội sơ cấp (bib-nguyenhuudien-2019); hội cơ bản (bib-nguyenhuudien-2019) |
| multiple-directed-edges | cạnh có hướng bội | uncited | cạnh bội (bib-nguyenhoangthach-2020); cạnh bội (bib-nguyenhuudien-2019) |
| n-ary-relation | quan hệ n ngôi | uncited | quan hệ 2 ngôi (bib-nguyenhuudien-2019); quan hệ hai ngôi (bib-nguyenhoangthach-2020); quan hệ hai ngôi (bib-nguyenducnghia-2006) |
| pairwise-relatively-prime | đôi một nguyên tố cùng nhau | Rosen-2003 | nguyên tố cùng nhau đôi một (bib-nguyenhoangthach-2020) |
| partial-fraction-decomposition | Phân tích thành phân số riêng | uncited | phân thức đơn giản (bib-ngodactan-2004); phép tách phân thức (bib-nguyenducnghia-2006) |
| postorder-traversal | hậu thứ tự | Rosen-2003 | duyệt theo thứ tự sau (bib-hoangchithanh-2007); duyệt theo thứ tự sau (bib-nguyenhuudien-2019) |
| product | Tích | Rosen-2003 | Tích Descartes (bib-nguyenhuudien-2019); Tích Descartes (bib-nguyenhoangthach-2020); Tích Đề các (bib-ngodactan-2004) |
| proof-by-contraposition | Chứng minh phản đảo | uncited | mệnh đề phản đảo (bib-nguyenhuudien-2019) |
| propositional-function | hàm mệnh đề | Rosen-2003 | vị từ (bib-nguyenhuudien-2019) |
| real-numbers | Tập số thực | uncited | tập hợp các số thực (bib-nguyenhuudien-2019); số thực (bib-nguyenhoangthach-2020) |
| recursive-function | Hàm định nghĩa bằng đệ quy | uncited | định nghĩa đệ quy (bib-nguyenhuudien-2019); định nghĩa bằng đệ quy (bib-nguyenhuudien-2019) |
| self-complementary | tự bù | Rosen-2003 | đồ thị tự bù (bib-ngodactan-2004) |
| separating-set-of-edges | tập cạnh phân tách | uncited | lát cắt cạnh (bib-nguyenhoangthach-2020) |
| simplification | Rút gọn | Rosen-2003 | Qui tắc rút gọn (bib-nguyenhuudien-2019) |
| space-complexity | Độ phức tạp theo không gian | uncited | độ phức tạp không gian (bib-nguyenhuudien-2019) |
| strictly-decreasing | thực sự giảm | Rosen-2003 | giảm thực sự (bib-leanhvinh-2020) |
| string | chuỗi ký tự | uncited | xâu ký tự (bib-nguyenducnghia-2006); xâu ký tự (bib-nguyenhuudien-2019) |
| strong-mathematical-induction | Quy nạp toán học mạnh | uncited | nguyên lý qui nạp dạng mạnh (bib-nguyenhuudien-2019) |
| subdivision | phép phân chia | Rosen-2003 | phép chia cạnh (bib-nguyenhoangthach-2020); phép chia cạnh (bib-nguyenducnghia-2006); chia cạnh (bib-hoangchithanh-2007) |
| sum-of-products-expansion | khai triển tổng các tích | Rosen-2003 | dạng tuyển chuẩn tắc hoàn toàn (bib-nguyenducnghia-2006) |
| the-bijection-rule | Quy tắc song ánh | uncited | phương pháp song ánh (bib-leanhvinh-2020) |
| the-first-principle-of-mathematical-induction | Nguyên lý Thứ nhất của Quy nạp toán học | uncited | nguyên lý quy nạp (bib-leanhvinh-2020); phương pháp quy nạp toán học (bib-nguyenhuudien-2019) |
| the-generalized-pigeonhole-principle | Nguyên lý chuồng bồ câu tổng quát | uncited | Nguyên lý Dirichlet tổng quát (bib-nguyenducnghia-2006); Nguyên lý Dirichlet tổng quát (bib-nguyenhuudien-2019); Nguyên lý Dirichlet mở rộng (bib-ngodactan-2004) |
| time-complexity | Độ phức tạp theo thời gian | uncited | độ phức tạp thời gian (bib-nguyenhuudien-2019) |
| traveling-salesman-problem | Bài toán người giao hàng | uncited | Bài toán người du lịch (bib-nguyenducnghia-2006) |
| union | Hợp | Rosen-2003 | đồ thị hợp (bib-nguyenhoangthach-2020); hợp của hai đồ thị (bib-ngodactan-2004) |
| universal-generalization | Tổng quát hóa phổ quát | uncited | tổng quát hóa phổ dụng (bib-nguyenhuudien-2019); tổng quát hóa phổ dụng (bib-nguyenhuudien-2019) |
| universal-instantiation | Khởi tạo phổ quát | uncited | đặc biệt hóa phổ dụng (bib-nguyenhuudien-2019) |
| valid-inference-rule | quy tắc suy luận lôgic hợp lý | uncited | quy tắc suy diễn (bib-nguyenhuudien-2019); qui tắc suy diễn hợp lý (bib-nguyenhuudien-2019); luật suy diễn (bib-nguyenhuudien-2019) |
| weak-mathematical-induction | Quy nạp toán học yếu | uncited | phương pháp quy nạp toán học (bib-nguyenhuudien-2019) |

## Nhóm 4 — WEAK-CITATION (63): thuật ngữ ổn nhưng chỉ Rosen-2003 trích

Thuật ngữ recommended đúng và phổ biến, nhưng trong corpus chỉ có Rosen-2003-vi (tham khảo) trích. Lựa chọn: (a) re-mine corpus tìm nguồn mới hơn, hoặc (b) chấp nhận giữ "cách dùng" không trích dẫn. Ưu tiên thấp.

> alphabetical-order, and-gate, binary-search-tree, boolean-expression, boolean-product, boolean-sum, combinatorial-circuit, common-ratio, composite-number, contingency, carmichael-number, circular-reasoning, computable-function, concatenation, consistent-compound-propositions, cryptosystem, decimal-representation, decision-tree, decreasing, derivation-tree, exclusive-or, empty-string, encryption, fallacy, gate, identity-function, index-of-summation, inverter, invertible-function, literal, loop-invariant, lower-limit, language, membership-table, mersenne-prime, naive-set-theory, or-gate, paradox, pivot, product-of-sums-expansion, partial-function, phrase-structure-grammar, projection, pseudoprime, relational-data-model, square-root, strictly-increasing, sum, summation-notation, summation, sample-space, shift-cipher, the-second-principle-of-mathematical-induction, the-sieve-of-eratosthenes, type-0-grammar, type-1-grammar, type-2-grammar, type-3-grammar, uncountable-set, unary-operator, uncomputable-function, well-formed-formulae, witness

## Nhóm 5 — NOISE (34): gợi ý mất chữ/đầu ngữ — GIỮ NGUYÊN

Ứng viên Codex là dạng cụt của thuật ngữ hiện tại (vd `independent-events`: "biến cố độc lập" vs gợi ý "biến cố"). Không sửa.
