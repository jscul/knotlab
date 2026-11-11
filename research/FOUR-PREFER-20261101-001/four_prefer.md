# Four-place laws that prefer a value: decision at closure

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `FOUR-PREFER-20261101-001`, closed 2026-11-01. Program: foundations.

## The request

The owner approved all three recommendations of `FOUR-PLACE-20261031-001` ("Can we do all 3?"). This epic is option (b): complete the
four-place picture with the laws that prefer a value.

## What was found

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Four-place knots are the relations whose excluded states form a non-empty independent set of the 4-cube: 742 relations, 20 classes (4 value-free, 16 preferring a value). Only parity is Schaefer-tractable. | proved | A |
| 2 | The clause (one excluded state) never fails on 4-regular systems: Hall matching, Tovey. | proved | A |
| 3 | Ten value-preferring classes build links and are NP-complete on 4-regular systems: class 1 directly, nine by realizing the twelve class on a three-point core and lifting its link piece. | proved; 240/240 end to end | B |
| 4 | The five weak classes (13–17, two or three excluded states) never failed: exact SAT search up to n = 6–8, hill-climbing up to n = 14 with growing solution counts. | computed; open | C |
| 5 | Of the 20 classes, 15 are settled and none is mutually selecting unless NP-complete problems are polynomial. A mutually selecting four-place knot would have to be one of the five weak classes. | proved | D |

## Answer

- **The four-place picture is complete except for five weak classes.**
- **Every class that fails builds equality.** Through it, its failures are as hard to recognise as unsatisfiability.
- **Every class that cannot fail is weak.** Proved for not-all-equal and the clause; observed for the five.
- **Nothing found is both rigid and failing.** The knot is the only such law at three places, so three stays special at the next arity
  for every law, not just for laws without a preferred value.

## Reading

- **The three-point core is the reason.** Three points on four lines, with one port per line, realizes the value-free twelve class from
  nine different classes. Almost every four-place law therefore builds equality, and hardness follows.
- **The three-place contrast.** At three places the corresponding core is the knot's piece, which builds nothing new (rigidity).
- **In the owner's terms.** At three places a relation can hide a distinction without being able to copy one. At four places, having
  more room, a law that can fail can also copy.

## Literature

- **Classical.** Schaefer (1978); Tovey (1984); Seymour (1974); Thomassen (1992).
- **What appears new.** The independent-set description of knots is elementary. The 20-class census, the lifted link pieces and the
  four-place selection table were found in no source checked.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — four-place laws that prefer a value | **Status:** Partially successful | 15 of 20 classes settled; the five weak classes never failed but are not proved to never fail. |
| Local direction — mutual selection at four places | Practically complete | Open: a never-fails theorem for classes 13–17. Tovey, Seymour–Thomassen and the local lemma do not reach them. |
| Broader exploration — the two/three boundary | Known alternatives | The owner has already approved (c), composition of the knot's contradictions toward native networks, and (a), the note on native selection. |
| Long-term goal — the two/three boundary as emergence | Capability gained | Three remains the only arity with a rigid failing law, now across all four-place knots up to five weak classes. |
| Next recommendation — option (c), then (a) | **Next step:** Continue, as approved. Open the composition epic, then write the note. | (c) asks whether selected spaces compose without hubs. (a) gathers the selection arc. The five weak classes are recorded as a side question (1/3). |
| Interest — that recommendation | **2/3 — Promising** | (c) bears directly on native networks; its main uncertainty is whether composition is more than the known splice calculus. |
| Execution — that action | Started (approved) | (c) opens now. |
