# Does creation between glue lines always single out the contradictory class?

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `CONTRA-READ-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** SWITCH-COMPLETE found that creation between glue lines does not tell switching classes apart and does not
  read the count. On both glues it computed, though, the one class without solutions, the class whose plain spaces are three-fold, had
  a glue block of its own. Its selected next step asked whether that always holds.
- **The go-ahead.** Taken at SWITCH-COMPLETE's close under the owner's standing mandate for autonomous research (2026-11-08).
- **The test.** Every trisum glue of 8 to 12 lines: the 8-line glue (seed 3), the 10-line glue (seed 6, isomorphic to seed 36), and
  the five 12-line glues (seeds 1, 192, 240, 246 and 300).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One contradictory class.** On each of the seven glues exactly one switching class has no solution: the class of the generator's Pfaffian signing. | computed | A, B |
| 2 | **Every single row singles it out** on the 8- and 10-line glues: for every line a, no other class of the glue without a has the contradictory class's row a. | computed | A |
| 3 | **Its block is its own** on the five 12-line glues; after the first row only the four classes over its restriction remain. | computed | B |
| 4 | **The removed line stays tied.** In the glue without a, a's three points are tied for the contradictory class and for no other class (follows from conclusion 1 and the class having no solution; computed). | computed, with the argument | A |
| 5 | **Degenerate gluings carry it.** In its row every line sharing two points with a is degenerate, and at lines sharing two points with no other line the degenerate entries alone single it out. | computed | A |
| 6 | **Stress test: every single row** on the five 12-line glues. Each single row singles the contradictory class out on all five glues too: for every line, no other class of the glue without it has the same row. | computed | stress test |

## Answer

- **Yes, on every glue tested.** On all seven trisum glues of 8 to 12 lines, creation between glue lines tells the contradictory class
  apart from every other class, and a single row is enough.
- **How.** Removing any line of the contradictory space leaves the line behind as a tie of its three points. Creation at the other
  lines reads that tie: through gluing lines that cannot show all six patterns, and through the knots that far sides add.

## Reading

- **Native creation reads where the contradiction lives.** With any one line removed, creation at the other lines tells whether
  restoring that line closes a contradiction. That is G4's question, whether native relations alone can read where a law creates a
  contradiction, answered for this family.
- **Contradiction, not counts.** With SWITCH-COMPLETE: creation is blind to many classes, among them every class where nothing
  creates, and it does not read the number of solutions, but it never confuses the contradictory class with another.
- **Why one row suffices.** The contradictory class's restriction is the only class of the glue without a that ties a's points; a
  second one would give a second contradictory class.
- **Doctrine.** Everything here is invariant under relabeling lines and points; the spanning tree only names the classes.

## Literature

- **Classical.** Switching classes of signed graphs (Zaslavsky); Pfaffian orientations (Kasteleyn).
- **Ours.** The theorem behind the rows (SWITCH-PROOF), the blindness of creation (SWITCH-COMPLETE), three-regular contradictions as the
  non-colourable plain spaces (THREEFOLD-SPACES, HANDLE-COUNT).
- **New here.** The recognition of the contradictory class by creation, and the tie mechanism.

## Stress test

One size past ticket A's every-row result, the five 12-line glues were computed in full in the background
(`docs/LONG_RUNNING.md`, CONTRA-READ-P2): for each line, the rows of all 2,048 classes of the glue without it. On every line of
every glue, only the contradictory class's restriction has its row (`stress_test_p2.json`, computed by `stress_test_p2.py` and
summarized by `stress_test_p2_summary.py`; the run's log is `stress_test_p2_log.txt`). Ticket B's pruned check agrees: after the first
line only the four classes over that restriction remain.

## Correction (2026-11-08)

- **The reading's family.** The first sentence of the reading above holds on 3-connected glues. `CONTRA-PROOF-20261108-001` found
  random cubic glues with a two-vertex cut where one row cannot read the removed line's tie (`docs/CORRECTIONS.md`). Every result
  of this epic concerns trisum glues, which are 3-connected, and stands.

## Pending

- **Still open from earlier epics.** As listed in SWITCH-READ's ledger.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does creation always single out the contradictory class? | **Status:** Successful | Yes on all seven glues of 8 to 12 lines, by a single row |
| Local direction — what native creation sees of a signing | Continue | A proof that a row reads the removed line's tie looks within reach |
| Broader exploration — contradiction against counting | Capability gained | Creation reads the contradiction but not the count |
| Long-term goal — G4 Emergence lives in handles | Capability gained | Native relations read where the contradiction lives, in this family |

**Corrections:** none.
**Goals:** G4 checkpoint (capability gained).
**Assumptions:** none added or changed.
**Stress test:** passed: every single row singles out the contradictory class on the five 12-line glues too (CONTRA-READ-P2).

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove that one row reads the removed line's tie | 2/3 — Substantial | 2/3 — Testable | Degenerate partners plus PENDANT-LINE's two-round rule → a proof, or a glue where a row fails | Selected |
| 2 | Why there is one contradictory class | 2/3 — Substantial | 1/3 — Stated | Relate the unsatisfiable class to Pfaffian orientations → a proof or a second class | Alternative · deferred |
| 3 | One size past: the 14-line glues | 1/3 — Incremental | 3/3 — Ready | Prune by rows as in ticket B → a sharing class, or none | Alternative · deferred |

1. **A proof.** It would turn the recognition into a theorem: creation with one line removed reads whether that line's points are tied,
   so native relations read the contradiction. The degenerate partners are already proved; the junction lines and the other lines need
   the two-round rule.
2. **One contradictory class.** The argument for conclusion 4 rests on it, and on these glues it is computed, not proved. It may follow
   from Kasteleyn's theory of Pfaffian orientations, which the generator's signing comes from.
3. **Larger glues.** The 14-line glues have 32,768 classes each, and pruning makes them cheap; they would extend the range, not the
   understanding.
