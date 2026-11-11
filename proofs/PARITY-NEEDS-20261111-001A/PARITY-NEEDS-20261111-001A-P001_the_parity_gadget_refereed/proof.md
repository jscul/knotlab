# The gadget refereed, and the least genus for parity

Status: Proved (independent check of the gadget; exact capped search). `check.py --part referee|tori|steered|summary`, ticket A of
`research/PARITY-NEEDS-20261111-001/preregistration.md`, frozen in commit `b6ededb25` before the search ran. Every part reproduces.

## 1. The 8-point gadget, refereed

`referee.py`, fresh code reading only `gadget.json`: a valid knot space (every line on three distinct points, every point on three
lines, two faces, genus 4 traced from the rotation system, every face odd so the law is Kasteleyn); 8 floor states, on which point 5 is
the parity of points 0, 3 and 4; under the canonical K1–K3 test every line is a knot and the four-point parity relation, with the other
points as witnesses, is a knot. Passed. (Independent code by the same author, not an independent reviewer.)

## 2. One handle is enough (exact)

Every simple lattice torus up to 20 points (281), every class and interface; and 1,200 random knot spaces steered to genus 1, 2 and 3
(353 never reached their genus and were skipped; none was dropped by its cap; the parts took 11 and 15 seconds).

| Genus | Spaces read | Total parity | Total majority |
| --- | --- | --- | --- |
| 1 (lattice tori and steered) | 394 | 772 | 2,706 |
| 2 (steered) | 336 | 20 | 22,260 |
| 3 (steered) | 398 | 12 | 43,130 |

No other non-unate map occurs. **The least genus with parity is 1**: the lattice torus (2, 0, 4), 8 points and 8 faces, in its class 3,
computes the parity of points 0, 1 and 4 at point 5 at every input pattern. 16 of the 281 lattice tori (8 to 18 points) compute parity;
none of the 113 steered random tori did.

## 3. Where parity sits (computed, after the run)

In each of the 16 tori, parity occurs exactly in the class with the fewest floor states, and in no other class: (2, 0, 4) has classes with
18, 24, 16 and 8 floor states, and parity only in the class with 8, where the held points fix everything. A small most-constrained class
is not enough: tori without parity also have most-constrained classes of 2 to 64 states. This was read after the run and is not part of
the frozen marks.

## Against the pre-registration

The prediction of no parity on tori was wrong: one handle suffices. The answer by rule: least genus 1 in the range, the smallest instance
the 8-point torus (2, 0, 4) with 8 faces. Genus 0 is excluded for disk gadgets unless P = NP (pre-registration). After the run, the
summary step read the part files under the wrong key and was corrected to read `checks.result`; the search parts were not touched.
