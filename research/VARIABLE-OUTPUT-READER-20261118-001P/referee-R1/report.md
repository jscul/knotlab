# Referee report VARIABLE-OUTPUT-READER-001P-R1 (fresh code, no Codex), with the two other points of John's pasted summary

**Verdict on 001P: confirmed. No Block.** The width-31 example reproduces exactly. The theorem's conclusion holds exhaustively at
widths 31 and 33 against every overlapping replacement of the six-place junction's attachments, not only single exchanges. The
all-size step rests on the finite formation closure, which was read, not re-implemented.

**The other two points of the summary.**
- **Its account of our six UNIQUE-TABLE pairs is right, with one wording point,** Not a block.
- **Its stated priority is already answered for the complete-round law** (GROW-SMALL's created pair), and stays open only for its
  own serial law from a single seed. Narrowing of "remains open".

## 1. 001P, one attachment exchange

**The width-31 example (`job_p.py` part E; the referee's 001F serial-law engine and exact bond tables).**

| Check | Result |
| --- | --- |
| The 13 chronological supports, replayed | lawful, and the one-spent family's moves. Two unary three-fresh births; a binary third three-fresh birth; six binary two-fresh joins; a ternary two-fresh join; the ternary fourth three-fresh birth H = {13, 20, 23, 24, 27, 28}; its ternary spending child {15, 22, 24, 29, 30} |
| The rival with 23 → 25 at H | lawful in the same order (H's parents become 4, 8, 6); menu empty, against the source's {25, 26, 29} and {25, 26, 30} |
| Readings in the source | K(27, 25) = K(28, 25) = 6; K(13, 25) = K(20, 25) = K(24, 25) = 7 |
| Entries that differ, of 465 | 0 through D = 4, 11 through D = 5, 47 in full |
| The same-holder exchange 23 → 26 | lawful; the menu becomes {23, 25, 29} and {23, 25, 30}; 0 / 12 / 20 entries differ |

**The theorem, exhaustively at widths 31 and 33 (part S).** The members are physical types from the referee's own 001O
one-spent generator, regenerated with the width bound.

| | Width 31 | Width 33 (one past) |
| --- | ---: | ---: |
| Physical members / with a legal triple | 8,621 / 2,394 (as the study) | 23,094 / 3,984 |
| Live members with one six-place junction | all | all |
| Single exchanges: different holder (four distinct holders) / same holder | 54,419 (39,656) / 4,921, as the study's sweep | 90,520 (68,536) / 7,328 |
| … the added name at K = 6 to both loose outputs (no colour filter) | 64 / 16 | 32 / 8 |
| … and at K ≤ 6 to all three retained names | **0 / 0** | **0 / 0** |
| Every overlapping replacement A′ (1 to 4 names changed, four distinct holders) | 317,719 | 537,859 |
| … every pair of the new six-place star at K ≤ 6 in the source (necessary for a match through D = 5) | **0** | **0** |

- **The filter used.** A lawful rival's six-place star is a bond, so every pair in it reads K ≤ 6 there. A rival matching through
  D = 5 must therefore have every pair of F ∪ A′ at K ≤ 6 in the source too.
- **No replacement of any size survives,** at either width. The referee did not apply the colour condition, so its 64 includes
  candidates the study's colour step removes before its 16. The final count is the same zero.
- **The four closure records' shortest widths are 31, 31, 33 and 33.** The width-33 run is the first width that holds all four.

**The argument, read.**
- **Lemma O, the inherited inverse,** fixes the small supports and the pair F. The referee confirmed this at the argument level
  in its 001O report.
- **The strict reading K(s, i) ≤ 6 < K(f, i)** (siblings.md) and the case analysis that forces A′ = A are sound as written:
  - if f is attached it displaces s, and the retained input i would read ≤ 6 to f;
  - if an input is removed it is loose beside f in the six-loose exterior bond;
  - if s is removed it becomes a sibling of f with identical readings.
- **The boundary-change formula** h − p + 2(p − j) equals h + p − 2j, the change from adding a site. The parent-closure argument
  (shore.md) follows from it.
- **Not re-derived:**
  - the 244,740-record closure and its 416,024-record audit (the study's separately written C++);
  - the chained earlier results (001F, 001J, 001K, 001N).

  The referee's exhaustive widths 31 and 33 agree with what the closure implies.

## 2. The summary's account of the six UNIQUE-TABLE pairs

These are the study's own results (UNIQUE-TABLE, by Claude), summarised, not a new Codex computation. The referee checked them in
UNIQUE-TABLE-R1, and the three-way readings in THREE-WAY-R1 and TRIPLE-GROWN-R1.
- **"Every pair distance agrees, and a three-distinction reading separates all six pairs."** Right. The full tables are equal
  entry by entry, and the three-way readings differ on 116 to 208 triples. Five of the six have a second rival, eleven in all.
- **"In the sixth, both add three junctions, but different distinctions join."** Right (pop-0007).
- **"In five cases the census arrangement adds three junctions and its rival stalls"** holds only with each arrangement grown as
  a new start, every junction holding a loose distinction live. Under the census's own continuation, where only the round-1
  junctions are live, those five rivals grow 4 against 3. This was the correction folded into UNIQUE-TABLE (09cd67d50). Either way
  the law separates each pair at its next step. **Not a block.**

## 3. The summary's stated priority, against what is already known

"Whether the cheapest-count rule can grow both members of such a pair remains open. One pair with two lawful histories, identical
distances, and different next joins would show that the growth process itself can produce a distinction its pair distances lose."
- **For the six static pairs: no.** None of the eleven rivals is reachable:
  - by complete rounds from any start, as PARENT-RULE's backed-pairs property shows (every reached stage has it, the rivals lack
    it);
  - or under the serial mixed law (UNIQUE-TABLE-R1's reachability search).
- **For the complete-round law in general: yes, already shown.** GROW-SMALL's created pair:
  - two lawful histories, one round of the cheapest counts from the legal 7-junction starts atlas 448 and atlas 581;
  - identical full tables at 12 junctions, checked entry by entry, and different allowed states;
  - next tables at 19 junctions that are not isometric, so the next joins differ.

  The referee rebuilt it from scratch in GROW-SMALL-R1 and CREATED-PAIR-R1. The other 86 pairs reached the same way have identical
  tables and different states, so the growth does produce distinctions its pair distances lose. They join alike next round.
- **What separates the two kinds is the growing end, not more distance.**
  - **The theory.** EXTEND-ROUND proved that one round reads only the live junctions, their loose counts and the sets met by one
    junction.
  - **The evidence.** Every table renaming that keeps that reading extended through the next round: 36,060 on the carried pairs,
    and 1,746,752 census self-pairs in HUNT-SHORTEN-R1.
  - **The created pair** has no renaming that keeps the reading (0 of 96).
  - **PROVE-B (in progress)** reports an arrangement where such a renaming does not extend, but it is not a reached stage.
- **So the priority is open only in its own setting:** the serial law from a single seed, with identical tables and different next
  menus. Codex's own N pair (width 31) has identical exact tables and different states, but the same three legal triples. **The
  question "can the growth make such a pair" is a Narrowing:** it is answered for the complete-round law, and open for the serial
  law from one seed.

## How the work was split

- **The referee:**
  - read 001P's `proof.md`, `exchange.md`, `shore.md`, `siblings.md`, `controls.md` and `audit_shores.md`;
  - wrote `job_p.py`. It uses its own VARIABLE-OUTPUT-READER-001F-R1 serial-law engine and bond tables, and its 001O-R1 family
    generator.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 287 MB; 2 and 8 minutes for widths 31 and 33).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
