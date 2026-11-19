# Referee report VARIABLE-OUTPUT-READER-001K-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **The width-26 swap and the width-28 pair reproduce exactly.**
- **The claim "whenever a triple can join, distances through five identify every junction" holds** on every family member to width
  30. That is one size past the study's examples, as a test of every renaming of each member's own table. The all-rival part rests
  on the study's finite closure.
- **One wording point, which the coordinator asked for.** The width-28 pair shows that the full table determines the arrangement
  only up to the table's own symmetries. A table symmetry need not be a symmetry of the arrangement, so the table alone does not fix
  which named distinctions carry the six-place equation, or the allowed states on named distinctions. Section 3 gives the wording.

The family: a ternary seed; two unary three-fresh additions; exactly one three-parent three-fresh addition; every other addition
two- or three-parent with two fresh. Its width is 2n + 4.

## 1. The cutoff five and the width-26 swap

**The width-26 swap** (`referee_k_sharp26.json`, replayed from `cases.json` under the referee's law and with the referee's own shore
tables):
- **It is in the family**, and the history is legal.
- **All 325 pairs agree after the swap (19 20) through K = 5** (D through 4), and **10 differ at K = 6**.
- **K(10, 19) = 6 and K(10, 20) = 7,** that is D = 5 and 6, as stated.
- **The legal menu is {12, 20, 21} and {12, 20, 22}.** The image {12, 19, 21} is forbidden.
- **Through K = 6, every symmetry of the table keeps both the menu and the junction supports.**

**The all-size proof checks at the argument level** (`proof.md`).
- **The width count.** The rival has the same unique ternary junction, read at K = 3, so its first two additions are unary and
  three-fresh. Its width 2r + 1 + a against the source's 2n + 4 makes a odd, with a ≥ 3 and r ≤ n.
- **The equations.** The n − 1 equations other than the six-place one are forced. The nine input–output pairs of the six-place
  junction at K = 6 force one more. So r = n and a = 3.
- **The shrink count.** It is read as n − 2 − n₄, which checks against the arity bookkeeping.
- **Three cases.**
  - Zero shrinks: 001I's reconstruction.
  - One shrink: the finite closure, 8,178 augmented records, all 5,771 with a legal triple admitting exactly the true six-place
    assignment.
  - Two shrinks: an empty menu, forced.
- **Not re-run:** the closures themselves.

## 2. "Whenever a triple can join, distances through five identify every junction"

**A self-symmetry test, one size past** (`family_self.py`). Every family member was grown by the family's own moves and deduplicated
up to isomorphism. For each member the referee computed its full table, its legal triples, and whether every symmetry of the table
clipped through K = 6, and of the full table, keeps its junction supports.

| Width | Family members | With a legal triple | Legal: a K ≤ 6 symmetry moves a support or a triple | Empty menu: a full-table symmetry moves a support |
| --- | --- | --- | --- | --- |
| 22 | 4 | 0 | none | 0 |
| 24 | 24 | 0 | none | 0 |
| 26 | 68 | 15 | **none** | 0 |
| 28 | 231 | 16 | **none** | **16** |
| 30 | 439 | 20 | **none** | 6 |

- **The self-symmetry part holds at every width.** In no member with a legal triple does a renaming that preserves the table through
  D = 5 move a junction or a triple.
- **Width 28 is the first width where a full-table symmetry moves a junction**, as the study says. It happens only where the menu is
  empty.
  - **Scope (added 2026-11-19, from the referee's 001L report).** This holds in the 001K family to width 30. It is not a general
    rule. Under the full law, 001L's width-46 continuation of the width-28 pair keeps all 1,035 distances equal on the same names
    and still hides the six-place junction, while eight triples are legal, with the same menu on both sides
    ([001L-R1, Section 7](../../VARIABLE-OUTPUT-READER-20261118-001L/referee-R1/report.md)).
- **The rival part of the claim was not tested exhaustively at these widths.** That part says a different arrangement cannot match
  the table either. The referee's all-rival census of every reachable type covers widths 12 to 22. There the family's only members
  are four width-22 types with empty menus: no rival matches them through K = 6, though K ≤ 5 already loses their junction
  identity. The census was stopped at width 24 for CPU. Beyond that, the all-rival claim rests on the study's closure.

## 3. The width-28 pair, and how to word it

`referee_k_w28.json`, replayed from `high_check.json`:
- **Both histories are legal and in the family.** Their full tables are **identical on all 378 pairs on the same names**.
- **Their parity-check spaces differ.**
  - The state whose ones are 11, 12, 14 and 21 is allowed in the first history and forbidden in the second.
  - The state with 22 in place of 21 is the reverse.
- **The swap (21 22) carries the first history's junctions onto the second's.** Before the join, 21 and 22 were both loose at the
  same junction. So the two are **the same arrangement up to renaming**: isomorphic as types.
- **The full table's symmetry group contains (21 22), and that symmetry moves the six-place junction's support.**
- **Both menus are empty.**

**How it should be worded against "the table determines the arrangement".** Suggested wording:

> The full bond-distance table determines the arrangement up to the symmetries of the table, not the named junctions. A symmetry of
> the table need not be a symmetry of the arrangement. At width 28, exchanging two distinctions that one junction held before the
> last join preserves all 378 distances but moves the six-place junction's equation, so the table does not fix which named
> distinctions carry that equation, nor the allowed states on named distinctions. The arrangement is the same up to renaming, and the
> three-parent menu is still determined: here it is empty, and through distance five it is fixed whenever a triple can join.

The last clause, and the identification of every junction whenever a triple can join, are statements about the 001K family. Under
the full law a junction can stay hidden while triples are legal (001L's width-46 example; scope note added 2026-11-19).

**Is it a first?**
- **On the three-parent side and for the allowed states, yes.**
- **It is not the first identical-table, different-junction pair in the program.** 001A's width-18 witness already had identical full
  tables on the same names with different eighth junctions, and different one- and two-parent menus. There the allowed states were
  equal; here they differ.

## Fixes for the owner (listed, not folded in)

None is a block.
1. **Wording.** Use the wording in section 3, or equivalent, wherever a result reads "the table determines the junctions or states".
2. **"First".** Say "first with different allowed states", and cite 001A's width-18 pair as the earlier identical-table pair whose
   states agree.

## How the work was split

- **The referee:**
  - read `decision.md`, `proof.md`, `high.md`, `cases.md` and the data files;
  - wrote `referee_k.py` (sharp26, w28, and the all-rival family census, partial) and `family_self.py` (the self-symmetry test to
    width 30), on the referee's 001F-R1 machinery.
- **Codex's code** was not imported or run.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Reproduction

Run from this folder.

| Command | Wall time |
| --- | --- |
| `referee_k.py sharp26` | 1 s |
| `referee_k.py w28` | 1 s |
| `family_self.py` | 1 min; with `WMAX=30`, about 3 min |
| `referee_k.py family 24 12` | stopped during width 24; the partial result in `referee_k_family.json` covers widths 12 to 22 |
