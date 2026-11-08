# Why one row of creation reads the removed line's tie

Epic `CONTRA-PROOF-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** CONTRA-READ found that on the seven trisum glues of 8 to 12 lines one row of creation between glue lines
  singles out the contradictory class: removing line a leaves a's three points tied in that class and in no other, and the row reads
  the tie. Its selected next step was a proof.
- **The go-ahead.** The coordinator approved the attempt in this thread (2026-11-08), under the owner's standing mandate.
- **The approach.** Cheapest discriminator first: before proving the statement for every glue, test it on glues that are not trisum
  glues, random connected cubic glues with a class without solutions. Then look for the lemmas a proof would use.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Not for every glue.** On 19 random cubic glues of 8 to 10 lines, one row fails to read the tie exactly at the lines lying in a two-vertex cut of the incidence graph: 16 lines, two on each of the 8 glues of connectivity 2. There nothing creates anywhere in the tied row or in the row colliding with it. | computed | A |
| 2 | **It holds on every 3-connected glue tested:** the 11 random glues of connectivity 3 and the seven trisum glues. | computed | A |
| 3 | **The cuts.** Each is a pair of lines whose sides each have one more point than lines, and one side is always K4^(3) without a line: three lines on four points through one common point. | computed | A |
| 4 | **K4^(3)'s silence is not general.** In every tied class's row on 25 of the 26 glues, the K4^(3) far side creates at no line meeting the removed line in exactly one point; on the 12-line trisum glue of seed 1 it does, for 8 of 12 removed lines, while one row still reads the tie. | computed | A |
| 5 | **That is not the whole mechanism.** On a 3-connected glue where one row reads the tie, some classes are told apart from the tied one only by other entries. | computed | A |
| 6 | **A local lemma.** No single near point makes K4^(3) create, and a one-point local relation is degenerate exactly when its point is tied to the gluing line: the points tied to the removed line are never witnesses. | proved (exhaustive, 27 relations) | A |

## Answer

- **No proof for every glue, because the statement is false there.** Glues with a two-vertex cut are counterexamples: at the two cut
  lines, removing one leaves a rigid side, and the row reads nothing.
- **The conjecture to prove.** On glues whose incidence graph is 3-connected, one row of creation reads whether the removed line's
  points are tied. It held on all 18 such glues tested.
- **No local shortcut.** K4^(3)'s silence under the tie, which looked like the mechanism on the smaller glues, fails on a 12-line
  trisum glue where the reading still holds. The local lemma is proved but decides only the tied points.

## Reading

- **Where native creation cannot read the contradiction.** A two-vertex cut lets one line's removal isolate a rigid side, K4^(3)
  without a line. Its ties make nearly every gluing degenerate whether or not the contradiction is there, so creation sees the same
  thing in the contradictory class and in another.
- **Where it can.** Without such cuts, on every glue tested, creation between glue lines reads the contradiction from any one row.
- **A correction.** CONTRA-READ's entry in the knot intuition doc read the result without naming its family; it is narrowed to
  3-connected glues (`docs/CORRECTIONS.md`).
- **Doctrine.** Everything here is invariant under relabeling lines and points; the spanning trees only name the classes.

## Literature

- **Classical.** Connectivity of graphs and two-vertex cuts; switching classes of signed graphs (Zaslavsky).
- **Ours.** The rows and the tie (CONTRA-READ), the theorem behind the rows (SWITCH-PROOF), creation decided by local witnesses at the
  gluing line (PENDANT-LINE, CHAIN-TRANSFER).
- **New here.** The counterexamples at two-vertex cuts, the refined conjecture, the local lemma, and the failure of K4^(3)'s silence.

## Stress test

- **Already one family past.** The random glues are CONTRA-READ's reading tested outside the trisum family; that test found the
  counterexamples (`docs/LONG_RUNNING.md`, CONTRA-PROOF-R1, redrawn by ticket A's check).
- **One size past for the refined conjecture.** The five 14-line trisum glues, 3-connected, every row in full: pending at this commit; the first three glues (seeds 96, 282 and 288) pass, each single row
  singling out the contradictory class
  (`docs/LONG_RUNNING.md`, CONTRA-PROOF-S1).

## Pending

- **The stress test** above, if still running.
- **Still open from earlier epics.** As listed in SWITCH-READ's ledger.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — prove that one row reads the removed line's tie | **Status:** Partially successful | False in general; refined to 3-connected glues, with a proved local lemma |
| Local direction — what native creation sees of a signing | Continue | The refined conjecture and its first lemma are testable |
| Broader exploration — reading contradiction in other families | Unmapped | Only cubic glues of 8 to 14 lines are tested |
| Long-term goal — G4 Emergence lives in handles | Obstruction learned | Native creation cannot read the contradiction across a two-vertex cut |

**Corrections:** CONTRA-READ's reading in the knot intuition doc narrowed to 3-connected glues (Narrowing, too general).
**Goals:** G4 checkpoint (obstruction learned).
**Assumptions:** none added or changed.
**Stress test:** pending in the long-running index (CONTRA-PROOF-S1); three of the five 14-line trisum glues pass so far.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why two-vertex cuts hide the tie | 2/3 — Substantial | 2/3 — Testable | The side K4^(3) without a line, hanging from one point, against the eight signings of its cycles → a rigidity lemma, or a cut whose row reads | Selected |
| 2 | Prove the refined conjecture for 3-connected glues | 2/3 — Substantial | 1/3 — Stated | Find which entries tell the tied class apart where K4^(3) is loud → a lemma for them | Alternative · deferred |
| 3 | Random 3-connected glues one size past | 1/3 — Incremental | 3/3 — Ready | Draw 11- and 12-line glues with a class without solutions → a 3-connected failure, or more support | Alternative · deferred |

1. **The cuts.** Every failing cut had a side that is K4^(3) without a line, and once a cut line is removed that side hangs from the
   rest at one point. A finite analysis of such a side under its eight cycle signings may show why both the contradictory class and
   another leave nothing to create, which would turn the counterexamples into a theorem: where native creation cannot read the
   contradiction.
2. **The refined conjecture.** It is the theorem this line wants, but K4^(3)'s silence fails on a 12-line glue and no route covers
   the classes that silence and degeneracy leave.
3. **More glues.** Larger random 3-connected glues could break the refined conjecture; a class without solutions is rare among
   them (3 of 800 at 10 lines), so the draw is slow but ready.
