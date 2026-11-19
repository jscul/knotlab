# Referee report GROWN-END-SWAP-001-R1 (Codex's result, checked with the referee's own code under our complete-round law)

**Verdict: confirmed. It is a true counterexample to Claim B on a reached stage of our law.** The bond-distance table plus the
round's reading does not always carry the next table.
- **The proved results stand:** EXTEND-ROUND's Lemma A and Claim B\*, and both studies' computed results within their bounds.
- **Narrowing** of the readings drawn from Claim B in EXTEND-ROUND and HUNT-SHORTEN.

## 1. Both rounds are our law's, and the ten-junction stage is reached

The referee's FIRST-KNOT-R1 engine runs the program's complete-round cheapest counts: an implied junction gets exactly d, any other
max(d, 3 − p, 1). From the six-junction start it reproduces both literal stages (`job_swap.py` part X).
- **Round 1.** The groups are S–D (through A) and S–E (through D), and B has two offshoots. This adds {9, 11, 15}, {10, 12, 16},
  {13, 17, 18} and {14, 19, 20}, with lookahead demands (1, 1, 1, 1).
- **Round 2.** This adds {15, 16, 21}, {17, 19, 22, 23}, {18, 24, 25} and {20, 26, 27}, with demands (0, 2, 1, 1).
- **The start is a legal start for our law.** Six knots of 3 to 5 places, connected, every distinction in one or two knots. Two
  knots, M and A, are dead, and three pairs of knots meet twice. So the ten-junction stage is a reached stage of round 1.
- **The seven- and eleven-junction constructions** also reproduce both rounds.

## 2. The 210 distances, the swap and the two entries

The referee computed full tables by its own shore enumeration on the reached stage (21 distinctions) and the successor (28).

| Check | 6-junction start | 7 | 11 |
| --- | --- | --- | --- |
| The swap (0 2) keeps every pair of the reached table | **all 210** | all 231 | all 378 |
| K = D + 1 of (0, 1) and (2, 1): reached / successor | 4, 4 / **3, 4** | the same | the same |
| Successor pairs the extension fails on | (0,1), (0,3), (1,2), (2,3) | the same four | the same four |
| Any isometry of the successor table agreeing with the swap on every old distinction | **none** (exact search) | none | none |
| Permutations of 0–3 kept by the reached table / also by the successor's | 24 / **8** | 24 / 8 | 24 / 8 |

So "no choice of fresh names can repair the mismatch" holds. The failing pairs are old ones, and a search constrained to the swap
on every old distinction finds no isometry at all.

## 3. Does the swap keep the round's reading? Yes, in exactly EXTEND-ROUND's sense

- **The reading R is kept.** EXTEND-ROUND-R1's test (loose distinctions onto loose ones, each live star onto a live star, the
  family F of live sets met by one junction onto F) passes with F whole and with its maximal members, with ψ the identity.
- **The equations are not carried.** The swap maps A's support {0, 1, 4, 5} to {2, 1, 4, 5}, which is no junction. It is a table
  isometry that breaks holder classes ({0, 1} at M and A, {2, 3} at M and B).
- **So it lies exactly in Claim B's hypothesis and outside Claim B\*'s.** Claim B\* needs the span carried, and is untouched.
- **Lemma A still holds here.** The round's groups and fresh counts are the same on both sides. What the table loses is which old
  pair becomes closer: the bond {0, 1, 21} forms, and its image would need {2, 1, …}.

## 4. Reconciliation with HUNT-SHORTEN and EXTEND-ROUND

- **No missed case, a different population.** The law is the same complete-round law, so the difference is the population.
  - **HUNT-SHORTEN's 23,003 stages** are grown from the touch census's starts of at most five knots.
  - **This stage needs the six-knot start.** By PARENT-RULE's unique predecessor its peel is that start, which no stage of positive
    age can be, since S and D are live and meet. The referee also checked directly: none of the census's 2,994 ten-junction stages
    is isomorphic to it.
  - **The referee's earlier run did look at this kind of symmetry.** It covered holder-breaking ones (1,630,590 of them, every one
    extending). This mechanism simply needs a larger start: M with two pairs of parallel distinctions to A and B, and a round that
    cuts the A–B connectivity outside M from two to one.
- **EXTEND-ROUND's 36,060 are also a different population.** They are GROW-SMALL's carried pairs, whose starts meet once. The
  counterexample's start meets twice, and Codex leaves the meet-once case open.

## Grades

1. **The counterexample is genuine.** Claim B, "if a table isometry keeps the round's reading, its extension is an isometry of the
   next table", is false on reached stages of our law. It is a self-pair on one history.
2. **EXTEND-ROUND: Narrowing.** Lemma A and Claim B\* are proved and unaffected. Claim B was stated as computed and unproved, and
   "all 2,198 (referee: 36,060) extensions held" stays true of its population. What must narrow is the reading, "distance plus the
   growing end carries what grows one round further". It holds on GROW-SMALL's meet-once pairs and on the census's stages, and fails
   in general on reached stages. Direction #1, "prove Claim B for reached meet-once stages", stays open only with the meet-once
   restriction.
3. **HUNT-SHORTEN: Narrowing.** "No counterexample to Claim B within the stated bounds" stands: every symmetry of every census stage,
   per the referee's run. Its interpretation does not stand beyond those bounds: "when the matching keeps the growing end … it has
   not appeared; whatever protects lies in the full reading". The reading does not protect in general.
4. **PROVE-B** (in progress): its target must carry a restriction, such as meet-once starts or the census's starts. The
   unrestricted statement for reached stages is now refuted.
5. **The referee's own HUNT-SHORTEN-R1 and EXTEND-ROUND-R1 statements** were made within their populations and stand. Their
   remarks that Claim B was "complete on GROW-SMALL's pairs" or "on the bound" are correct as scoped. **Not a block.**

## How the work was split

- **The referee:**
  - read Codex's `proof.md`, `decision.md`, `construction.md` and `verify.md`;
  - wrote `job_swap.py`. It uses its own FIRST-KNOT-R1 engine with the program's rule, CENSUS-READ-R1's shore enumeration,
    EXTEND-ROUND-R1's reading test and extension, CREATED-PAIR-R1's isometry search, and HUNT-SHORTEN-R1's census regrowth.
- **Read as data:** the starts and permutations in `construct_6.json`, `construct_7.json` and `construct_11.json`, and the touch
  census.
- **No Codex code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (seconds).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
