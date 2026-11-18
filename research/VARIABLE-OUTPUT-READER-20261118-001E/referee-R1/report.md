# Referee report VARIABLE-OUTPUT-READER-001E-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.** Every claim the coordinator listed reproduces with the referee's own code, and the proofs check
by hand where read. The referee's census also takes the minimum-width bound's exhaustive base independently to width 19.

## 1. The width-32 reader (question 1)

**Scope.** It is a rule for that one table, and the proof says so: "the universal question for other tables is open". It is claimed
across every reachable realization of that table, not across tables.

**Recomputed from scratch** (`referee_e_w32.json`), from the junction supports in the certificate (data only):

| Claim | Referee |
| --- | --- |
| "a triple may join exactly when all three distances are six" | the reader picks **8 of 4,960** triples, exactly the legal ones |
| the two realizations share the equations of 14 junctions | yes: a rank-14 space L (the true space has rank 15) |
| L alone reproduces the table | no |
| spaces L + ⟨S⟩ reproducing all 496 entries, over every word S of 3 to 6 distinctions whose pairs fit the table's bound (675 distinct spaces) | **exactly 2**: the true space and its (13 14) image |

**What is proved, and what is checked.**
- The study's argument has three steps:
  1. the table forces 14 independent equations (its short-support deductions);
  2. at most 15 fit (the rank bound 1 + ⌊(32 − 3)/2⌋);
  3. so a competitor is L or L + ⟨one generator⟩, and only two such spaces fit.
- The referee confirmed step 3 by enumerating every possible extra generator, which is broader than the study's 13 grouped candidates.
- The referee did not re-derive step 1 (that L is forced by the table alone).
- Given the two spaces, the allowed-state theorem (001D's Theorem 2) gives the same eight triples in every realization.
- **Not a block.** Step 1 is the study's own deduction from 001D, and the referee's check covers the final count.

## 2. The four-distinction theorem and the five-distinction example (question 2)

**The theorem** (`live_four.md`) checks by hand.
- Equations of size ≤ 4 are bonds.
- Three-bit bonds are the trivalent stars the table reveals.
- A four-bit bond through a live mark l is:
  - u's own four-star; or
  - a sum of two trivalent stars, one of them at u; or
  - a bond with a shore of three or more junctions, which holds no eligible distinction.
- Each of the three row types is right:
  - arity 5 or 6 gives N₃(l) = ∅;
  - arity 4 forces its support;
  - in the trivalent case, a rival four-bit equation W meets S, or a neighbouring ternary star T, in exactly two bits, so W △ S or
    W △ T is a ternary equation, present in both codes.
- **It rests on three results from earlier in the line.** The referee checked the last one empirically:
  - ternary-star recognition (001D);
  - the two-site four-bond form;
  - the ineligibility theorem for large shores (`frontier_exchange.md`, which uses 001D's two-sink restriction).
- **The empirical test of the ineligibility theorem** (`referee_e_frontier14.json`): 4,000 random continuations of one to eight
  joins from the theorem's own example. That example is the 14-junction presentation whose four loose distinctions {27, 29, 30, 31}
  form a bond with a 14-junction shore.
  - **No legal triple ever uses one of the four**, across 190 legal triples in 25 continuations.
  - **No continuation of four or fewer joins has any legal triple**, as the note states.
  - A broader random search found no other such frontier: none of 34,541 four-bit bonds in 3,519 targeted presentations had a shore
    of three or more junctions. They are rare.

**The five-distinction example**, replayed from its history (`referee_e_five.json`):
- the history is legal, at width 30 with 13 junctions;
- the five loose distinctions {17, 25, 27, 28, 29} **form a bond**;
- **all ten distances are 4**;
- **2 of the 10 triples are legal**, {17, 25, 28} and {17, 25, 29}, and 8 are forbidden;
- the table's two automorphisms keep the legal triples;
- after the join (6, 10, 12), four loose distinctions remain and there is no legal triple.

## 3. The minimum-width bound of 21 (question 3)

**It is argued for widths below 15 and exhaustive for 15 to 20.**
- **The argument checks by hand.**
  - A legal triple's parents and witnesses induce a six-cycle, which needs a seventh junction meeting the opposite side's three.
  - So the first legal triples come at seven junctions, at width ≥ 15.
- **The exhaustive part.** This study covers widths 15 to 17, and the earlier studies 001A to 001C cover 18 to 20.
- **The referee's independent exhaustive census, to width 19** (`referee_e_small19.json`):
  - every reachable presentation, by breadth-first growth with isomorphism of the incidence graphs and the seed unmarked;
  - each one's table, legal triples and table automorphisms.

| Width | Presentations (referee) | Study | Distinct table classes | Two presentations with possibly isometric tables | Automorphisms moving a legal triple |
| --- | --- | --- | --- | --- | --- |
| 15 | 302 (21 / 201 / 80 at 5 / 6 / 7 junctions) | 302 (21 / 201 / 80) | 302 | 0 | 0 |
| 16 | 661 (258 / 403) | 661 (258 / 403) | 661 | 0 | 0 |
| 17 | 1,517 (212 / 1,007 / 298) | 1,517 (212 / 1,007 / 298) | 1,517 | 0 | 0 |
| 18 | 3,495 | (001A) | 3,495 | 0 | 0 |
| 19 | 8,191 | 8,191 (001D) | 8,191 | 0 | 0 |

- **The legal-triple counts per row match the study's:** 22, 95, 244 and 52.
- Every presentation at widths 15 to 19 has its own table class, so no isometry between different presentations exists there.
- All 882,404 table automorphisms keep the legal triples.
- **Width 20 was not rerun.** There, by 001D, distinct presentations can share a table (24 sources), all with empty menus.
- **So the bound is exhaustive computation plus a short argument, and the referee confirms its base independently through width 19.**

## 4. The higher-arity claim (question 4)

- **The recognition criterion checks by hand.** It says: in a cographic matroid, for r ≥ 4, C is a bond iff d_{r−1}(C ∖ {i}) = r
  for every i.
  - If C is neither a bond nor contains a proper subbond, it is independent.
  - The forced columns f_i = Σ_{j≠i} e_j then contract to the Fano plane.
  - The Fano plane is not cographic: it is one of Tutte's excluded minors, and the study gives a direct graph proof.
- **The consequence checks**, given 001D's allowed-state theorem:
  - triple minima (3, 4 or other) give the bonds of sizes 3 and 4;
  - quintuple minima (5, 6 or other) give those of sizes 5 and 6;
  - every junction star has size 3 to 6, so these generate the full cut space, and hence the allowed states and the verdicts.
  - That theorem was read and not re-refereed in full; the 001D referee report says so.
- **The width-32 numbers, recomputed:** d₃({4, 11, 13}) = **10**, d₃({4, 11, 14}) = **8**, and **200 of the 4,960** ternary entries
  change under (13 14).
- **The six-sharpness remark** for Boolean parity readings was not checked.

## Fixes for the thread (listed for the owner, not folded in)

1. **"Exactly two reachable parity relations fit the full table".** Name its premise: the 14 equations forced by the short-support
   deductions. The referee confirms the count given that premise, over all 675 candidate extra generators. **Not a block.**
2. **The minimum-width bound.** Cite the referee's independent census to width 19: identical counts, every table class distinct, no
   automorphism moving a legal triple. **Not a block.**

## How the work was split

- **The referee:**
  - read `proof.md`, `live_four.md`, `small_widths.md`, `extra_reading.md` and `frontier_exchange.md`;
  - wrote `referee_e.py`, on its 001D-R1 code:
    - the width-32 reader, candidate spaces and ternary minima;
    - the five-distinction replay;
    - the exhaustive census of widths 15 to 19;
    - continuations of the four-distinction frontier.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_e.py`.**
- **`referee_e_w32.json`, `_five.json`, `_small.json` (to width 17), `_small19.json`, `_frontier14.json` and `_frontier.json`** (the
  broader random search, which found no large-shore frontier).

Reproduce, from `research/VARIABLE-OUTPUT-READER-20261118-001E/referee-R1/`. The width-19 census takes about 5 minutes; the rest take
under a minute each.

```sh
../../../.venv/bin/python -B referee_e.py w32 > referee_e_w32.json
../../../.venv/bin/python -B referee_e.py five > referee_e_five.json
../../../.venv/bin/python -B referee_e.py small 19 > referee_e_small19.json
../../../.venv/bin/python -B referee_e.py frontier14 > referee_e_frontier14.json
```
