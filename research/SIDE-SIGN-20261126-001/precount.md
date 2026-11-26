# The structural pre-count (run before the freeze)

`sides.py precount 0 7075` (structure only: no state was enumerated). Every census start grown 0, 1 and 2 rounds; a swap is
a renaming of order two that moves a knot; the kinds of sides under each lift (README.md, "The objects"). Rows:
[precount.jsonl.gz](precount.jsonl.gz).

| Law | Round | Stages | With a swap | Two-sided (min / max lift) | Several (min / max) | One-sided (min / max) | Distinctions | Parity dimension |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parity | 0 | 7,075 | 2,164 | 2,104 / 1,546 | 67 / 24 | 226 / 809 | 5–12 | 2–9 |
| parity | 1 | 5,111 | 2,442 | 2,389 / 2,090 | 574 / 431 | 182 / 636 | 5–24 | 2–14 |
| parity | 2 | 3,398 | 2,304 | 2,278 / 2,189 | 1,119 / 1,002 | 85 / 377 | 12–42 | 5–23 |
| nae | 0 | 7,075 | 2,164 | 2,104 / 1,546 | 67 / 24 | 226 / 809 | 5–12 | 2–9 |
| nae | 1 | 5,111 | 2,414 | 2,360 / 2,057 | 568 / 427 | 166 / 624 | 7–24 | 3–14 |
| nae | 2 | 5,111 | 3,341 | 3,301 / 3,137 | 1,402 / 1,190 | 166 / 624 | 9–42 | 4–23 |

A stage is counted under a kind when at least one of its swaps has that kind. No automorphism search was truncated.
