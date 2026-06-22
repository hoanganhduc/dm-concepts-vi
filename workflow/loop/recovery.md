# Autonomous loop — recovery

**Goal:** build verified EN–VI lexicon chapters for all alphabet letters (autonomous, no re-prompt).

**Current status:** running.

- **Done:** C (14 entries, enriched, 85 citations).
- **In progress:** G (build-chapter workflow `wpd4bi667`).
- **Pending:** A, B, D, E, F, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z.

**Next safe action:** when the G workflow completes → encode (`encode-chapter.py g`), add `ch-g.ptx` xinclude to `source/main.ptx`, validate, build, commit; then launch `build-chapter` for the next pending letter (A). Repeat per letter.

**Side job:** Rosen VI OCR (~180/978) → on completion, un-defer for a final reference-enrichment pass across all chapters (Rosen never recommended).

**Per-letter pipeline:** build-chapter workflow → `encode-chapter.py <l>` → xinclude in main.ptx → `validate-entry.py` → `build-search-index.py` → `pretext build web` → commit.

**Stop:** all letters processed; or user pause/stop; or a letter fails build 3× (skip + record).

**Evidence gates:** verified citations carry source_id+pdf_page+snippet; recommended from newest source; definitions checked vs Rosen by the panel; every chapter must build before commit.

- 2026-06-21T15:34:15 done G; next=A; done=2 skipped=0 pending=24
- 2026-06-21T16:10:02 done A; next=B; done=3 skipped=0 pending=23
- 2026-06-21T16:45:38 done B; next=D; done=4 skipped=0 pending=22
- 2026-06-21T17:22:05 done D; next=E; done=5 skipped=0 pending=21
- 2026-06-21T17:56:04 done E; next=F; done=6 skipped=0 pending=20
- 2026-06-21T18:31:35 done F; next=H; done=7 skipped=0 pending=19
- 2026-06-21T19:03:39 done H; next=I; done=8 skipped=0 pending=18
- 2026-06-21T19:37:56 done I; next=J; done=9 skipped=0 pending=17
- 2026-06-21T19:59:01 done J; next=K; done=10 skipped=0 pending=16
- 2026-06-21T20:36:25 done K; next=L; done=11 skipped=0 pending=15
- 2026-06-21T21:14:40 done L; next=M; done=12 skipped=0 pending=14
- 2026-06-21T21:49:01 done M; next=N; done=13 skipped=0 pending=13
- 2026-06-21T22:26:51 done N; next=O; done=14 skipped=0 pending=12
- 2026-06-21T22:58:39 done O; next=P; done=15 skipped=0 pending=11
- 2026-06-21T23:32:37 done P; next=Q; done=16 skipped=0 pending=10
- 2026-06-21T23:49:49 done Q; next=R; done=17 skipped=0 pending=9
- 2026-06-22T03:47:35 done R; next=S; done=18 skipped=0 pending=8
- 2026-06-22T04:20:57 done S; next=T; done=19 skipped=0 pending=7