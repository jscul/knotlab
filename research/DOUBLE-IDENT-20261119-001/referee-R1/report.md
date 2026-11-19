# Referee report DOUBLE-IDENT-001-R1 (proof read; own data, classification, relayed model, growth and class prediction)

**Verdict: confirmed. Lemma M and Theorem 6 hold, and Corollary 7's census figures reproduce. No Block; one hypothesis to state
and one wording point.**
- **Lemma M is correct, in both of the steps the hand-off asks about.**
  - **Round 1.** Candidates, valid sets, groups and offshoots depend only on the neighbour sets, with every knot a possible common
    neighbour, and on the open counts. Which loose distinction a knot gives is immaterial, by the swap symmetries.
  - **The implied step.** In a connected presentation where every distinction lies in at most two junctions, summing the
    equations of a set S leaves exactly S's loose distinctions and those S shares with junctions outside it, whatever the
    multiplicities. So a set of loose distinctions lies in the span only if it is all of them. "Implied" is therefore "takes every
    loose distinction", and it reads only counts.
- **The classification reads (S3) and (S4) with dead knots as common neighbours, as stated.** In `machine_check.py`, round-1 groups
  among the live knots are formed in the whole presentation, dead knots included. The (S4) test takes common neighbours in the
  underlying simple graph over all knots.
- **The referee's own classification of all 26,441 arrangements gives the study's numbers exactly:**

| Class | Count |
| --- | ---: |
| In the class | 11,512 (437 simple, 11,075 with double touches) |
| One loose distinction | 727 |
| No loose distinction | 234 |
| Out by (S3) / by (S4) | 905 / 2,053 |
| Stall | 11,010 |

- **The identification checks out with an independent model.** The referee compared its own growth, with the program's rule, to
  its own relayed X⁺ model, using keys that include the parents' keys, at every round to 6:
  - all 437 simple arrangements in the class agree;
  - so does a deterministic sample of 1,415 with double touches (one in eight);
  - all 727 one-loose arrangements close at round 1.
- **dims.py's rule for bare cycles is right, and the class prediction reproduces.**
  - **The rule.** A piece whose core has one cycle, all of whose blocks are pairs, and no pendant point is a loop with W = y^L. Its
    counts are eventually constant, so it has dimension 1. Any extra block, pendant point, ray or second cycle makes the growth
    exponential.
  - **The census.** On all 12,473 arrangements in the class, one-loose and loose-free ones included, the referee's own prediction
    equals the census's measured class: 2,882 close, 1,470 have dimension 1, 8,108 dimension 2, and 13 are exponential.
  - **So 8,108 of the census's 9,564 two-dimensional growths lie in the proved class.**
- **The two-holder hypothesis** (every distinction in one or two knots) is the program's convention, and the census meets it by
  construction. The implied step needs it.

## Points for the owner (listed, not folded in)

1. **The class should state "no stall".** It is listed as (S3), (S4) and (S6′). With given places, unlike bare sizes, a live knot
   can have demand above its open count. Round 1 is then unavailable and the extended complex would need a negative number of
   pendant points (s = open − d). The machine check excludes these 11,010 stalls, and Theorem 6 should name the condition: open_k ≥
   d_k for every live knot. **Not a block.**
2. **The machine check's growth runs with GF(2) elimination off** (JOIN-GROWTH's structural test). Lemma M(4) is exactly what
   justifies that here: connected presentations with at most two holders. The referee's growth, with elimination on, agrees on
   every arrangement compared. A sentence tying the two together would help. **Not a block.**

## How the work was split

- **The referee:**
  - read `double_ident.md`, `proof.md`, `machine_check.py` with its output, and `dims.py` with its output;
  - wrote `job_double.py`: data, classification, X⁺ builder, class prediction and the key comparison. It builds on its
    RELAY-IDENT-R1 relayed model and growth, CHAIN-IDENT-R1 and RING-IDENT-R1 code, and the FIRST-KNOT-R1 engine.
- **Read as data:** the touch census's runs.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 127 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
