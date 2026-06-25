# DM-Concepts — Translation-Accuracy Review (5-loop multi-agent, Claude-verified)

Method: 5 loops, each a distinct angle, reviewed independently by Codex (OpenAI),
OpenCode (Gemini), CodeWhale (DeepSeek). Every agent finding was independently
verified by Claude against the real repo (data/terms/*.yaml + definitions +
cited snippets + Rosen conventions). Only verified items are listed. Review only
— no edits made.

Totals: ~90 raw agent findings → ~35 unique verified issues; ~45 rejected as
false positives (incl. cases where the agent's "fix" would INTRODUCE an error).

## HIGH severity (mistranslations / wrong content)
1. permutation — recommended "chỉnh hợp" + an r-permutation definition. Conflates permutation (hoán vị) with r-permutation/arrangement (chỉnh hợp). [4-loop consensus]
   Fix: headword "permutation" → recommended "hoán vị" with a "permute all n" definition; move the r-permutation content to a separate r-permutation entry.
2. existential-instantiation — "khởi tạo hiện sinh": "hiện sinh"=existentialism (mistranslation of "existential"); "khởi tạo"=initialization (wrong for "instantiation").
   Fix: "đặc biệt hóa tồn tại" / "cụ thể hóa tồn tại".
3. existential-generalization — "tổng quát hóa hiện sinh": same "hiện sinh" error.
   Fix: "tổng quát hóa tồn tại".
4. codomain — recommended "miền giá trị, tập đích": "miền giá trị" commonly means RANGE (image), not codomain. [3-agent consensus]
   Fix: "tập đích" / "đối miền".
5. inorder-traversal — example's "sorted ascending" BST output 5,2,6,1,3,9,7,10,4 is NOT sorted; a BST inorder must be sorted.
   Fix: correct the example to a genuinely sorted output for a consistent tree.
6. prime-implicant — definition reverses the implication: "không BỊ KÉO THEO BỞI" should be "không KÉO THEO" (a prime implicant implies no other implicant); contradicts the entry's own "nói cách khác" clause.
   Fix: change "không bị kéo theo bởi" → "không kéo theo".
7. dynamic-programming — example calls Dijkstra a DP algorithm; Dijkstra is GREEDY (Bellman–Ford is the DP one).
   Fix: drop Dijkstra or replace with a true DP example.
8. recursive-set — headword "recursive set" but term+def describe a "recursively DEFINED set"; in computability a recursive set = a DECIDABLE set (different concept).
   Fix: rename headword to "recursively defined set", or redefine as decidable.
9. Broken see_also (SYSTEMATIC, 17 entries / 21 targets) — see_also values are headword strings with spaces ("invalid argument", "rooted tree", "greatest common divisor", "conditional probability", …) instead of kebab-case ids, so the links silently do not render.
   Fix: convert see_also entries to entry ids; drop targets with no existing entry.

## MEDIUM severity
10. universal-instantiation — "khởi tạo phổ quát": "khởi tạo" wrong for "instantiation". Fix: "đặc biệt hóa phổ dụng".
11. closed-interval — "khoảng đóng": standard VN for [a,b] is "đoạn". Fix: "đoạn".
12. harmonic-series — headword "harmonic series" but term+def are the harmonic NUMBER H_n (finite sum). [3-loop consensus] Fix: separate series (chuỗi điều hòa) from number (số điều hòa).
13. master-theorem — "định lý thợ": poor literal of "master". Fix: "định lý Master" (usually untranslated).
14. linear-recurrence-relation — recommended bakes in "thuần nhất" (homogeneous); a separate homogeneous entry exists. Fix: drop "thuần nhất".
15. boolean-variable — "biến logic" looser than Boolean and inconsistent with its own def ("biến Boole"). Fix: "biến Boole".
16. reflexive-relation — "tính phản xạ" names the PROPERTY; headword is the relation. [3-loop] Fix: "quan hệ phản xạ".
17. inverse-of-a-conditional-statement — comma-joined double term "mệnh đề nghịch đảo, nghịch đảo"; also verify inverse/converse/contrapositive naming. Fix: single clean term.
18. domain-of-discourse — recommended "miền xác định" is IDENTICAL to the function-"domain" entry, conflating quantifier universe with a function domain. Fix: "vũ trụ/miền biện luận".
19. relation-property cluster (antisymmetric/symmetric/transitive-relation) — inconsistent + POS-mismatched terms ("phản xứng"/"đối xứng"/"bắc cầu" bare adjectives vs reflexive's "tính phản xạ"). Fix: make uniform ("quan hệ …" or "tính …").
20. first-order-logic — recommended "lôgic vị từ" cited to a snippet about quantifiers that does not contain the term. [2-agent] Fix: re-cite or mark uncited.

## LOW severity (term/POS/spelling)
base ("hệ cơ số"→"cơ số"); regular-graph (over-specifies "bậc k"→"đồ thị đều"); sequence ("dãy số"→"dãy"); greatest-lower-bound (spelling "chận"→"chặn"); inverse-modulo-m (term embeds variables a,m); homogeneous-recurrence-relation (over-specifies "tuyến tính"); simple-directed-graph (word order→"đơn đồ thị có hướng"); open-interval ("khoảng mở"→"khoảng"); sign-magnitude-format ("dấu-lượng"→"dấu và độ lớn"); well-formed-formulae (term/def inconsistency); contingency ("tiếp liên"→"mệnh đề bất định"); divisibility ("chia hết"→"tính chia hết"); functionally-complete ("hệ đầy đủ"→"đầy đủ về mặt chức năng"); summation vs sum (both "tổng").

## WEAK / debatable (flagged, terminology-dependent — decide per house style)
circuit (term "chu trình đơn" vs circuit semantics); join-lattice (result vs operation); open-walk (walk vs đường đi); xor ("hay loại trừ" vs "tuyển loại"); scale-free-network (unsettled VN); cantor-diagonalization (omits 0.999… caveat); type-0-grammar (production condition); axiom (well-ordering principle vs axiom); decreasing (strict vs non-strict).

## NOTES (completeness, not errors)
- Uncited recommended terms: extremal-graph-theory, fallacy-of-affirming-the-conclusion.
- New CS entries (Liben-Nowell: block-cipher, private-key-cryptography, …) still status=draft with uncited recommended terms.

## NOTABLE FALSE POSITIVES rejected by independent verification (≈45 total)
- mapping-rule (flagged 4×): "quy tắc song ánh" is correct — concept IS the bijection rule, deliberately unified + cross-linked.
- maximum-matching: agent wanted "cực đại" — that is *maximal*; "lớn nhất" is correct (suggestion would inject the maximal/maximum conflation).
- maximum-flow: "luồng cực đại" IS the standard VN term (max-flow/min-cut), not a conflation.
- path / simple-path / circuit DEFINITIONS: correctly follow ROSEN's conventions (Rosen's "path"=walk; "simple path"=no repeated edge; "circuit" allows repeated vertices). CodeWhale assumed the other convention.
- ~20 citation "mismatches" (gate, or-gate, self-complementary, recursive-function, …): the snippets DO contain the terms once OCR/diacritics are folded.
- private-key-encryption / np-complete / hamilton-circuit "empty duplicates": intentional see_ref redirect stubs.
- witness ("nhân chứng" = human witness, wrong); circular-reasoning (valid source-cited term); Trung Hoa→Trung Quốc (style only).

---

# Fixes applied (commits f730383, 50d916f, + follow-ups)

Verified errors were fixed (review→edit), EXCEPT the existential-instantiation /
existential-generalization ("hiện sinh") pair, left unchanged by request.

Convention-dependent entries (circuit, decreasing, type-0 grammar, axiom, Cantor
diagonalization) now present every convention in-book ("Nếu theo quy ước A …;
nếu theo quy ước B …"), dropping no variant. Term-only convention differences
already list every Vietnamese rendering under each entry.

Citation re-anchoring: of 14 terms made more correct, only "quan hệ phản xứng"
and "quan hệ truy hồi tuyến tính" are attested verbatim in the corpus (re-cited);
the rest are correct-but-unattested (the corpus uses the older terms).

see_also: headword-string targets converted to ids; recovered links to existing
entries. Genuinely missing concepts worth adding later: bijective proof,
brute-force algorithm, modular exponentiation.
