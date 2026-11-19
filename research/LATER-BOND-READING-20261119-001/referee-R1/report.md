# Referee report LATER-BOND-READING-001-R1 (Codex; exact least bonds by the referee's own MILP, its own compression and families)

**Verdict: confirmed. No Block to this study. Part of the literal sample is a stress test pending (stopped at the owner's
request).**
- **For THREE-RIGID's direction this is a Block at all sizes.** Pair and triple readings with the growing end fixed do not carry
  even the next round, and no fixed reading order suffices.
- **THREE-WAY and TRIPLE-GROWN: a Narrowing.** Their bounded statements, about collisions found so far, stand.

## The points asked

1. **The 104-junction stage: confirmed.**
   - **The stage.** Regrown from the literal start by the referee's engine: (56, 276) → (104, 372) → (146, 450), with age 1 equal
     to the literal start plus its round.
   - **The exchange (a ↔ c)** is an involution. It fixes all 180 live distinctions, and the two hub equations leave the span at
     ages 1 and 2, each with a four-distinction certificate.
   - **The named entries.** These are exact least bonds by the referee's MILP (`bondmilp.py`, which agrees with enumeration on
     200 random graphs):
     - K(4, 10) = K(10, 16) = 24 at age 1 (distance 23);
     - at age 2 they are 22 and 24 (distances 21 and 23). Both names are old, so no fresh naming repairs it.
   - **The full pair and triple readings.** The referee compressed the stage itself: the 20 starting junctions with no loose
     distinction form the core, and 12 branches of capacity 4 become virtual links. That gives 60 classes, as the study has, and
     the referee enumerated all 620,485 bonds. Every set of 1, 2 or 3 classes holding a moved class reads the same as its image.
   - **The compression, checked against the literal graph:**
     - 100 core-only queries: literal MILP equals compressed;
     - 468 pairs of a moved bundle with every other bundle (4 of 12 chunks) and 666 random moved triples, all on the literal
       graph: each equals its image.
     - **Stress test pending:** the other 8 chunks were stopped.
2. **The four-distinction repair: confirmed.**
   - **The quartet.** {0, 3, 24, 26} has no bond, and its image has least bond 46. The companion {3, 4, 6, 10} has none, and its
     image 48.
   - **The 24 listed maps.** On the compressed table all keep every 1-, 2- and 3-class reading. Exactly 4 carry the equations (so
     they carry every later reading). Each of the other 20 changes a 4-class set (none against 46 or 48).
   - **The exchange** changes 8,864 of the 487,635 four-class sets. That is the study's 4,432 orbits counted both ways.
   - **Not checked:** that these 24 are all the pair-and-triple-keeping renamings (the completeness of the group).
3. **The all-size construction (constructive-proof.md): proved as written, and checked at r = 2, 3, 4.**
   - **The proof.**
     - **The bound** 4L + 2s + (I − 1)N + 4(2L + I − 1) + (r + 1)(2M + I) = 30sr + 14s + r² + 8r − 17 and its margin
       7r² + 208r + 417 below sM were rechecked.
     - **The bipartite-component argument** for at most r marks, and the image of the (r + 1)-mark query isolating a, are sound.
     - **At age 2,** the red pair costs 3L, while its image meets two edge-disjoint weighted circuits and costs at least 4L.
     - **The meet-once replacement** by cost-one units is the same substitution checked in GROWN-END-READING-R1.
   - **The compressed instances, by MILP:**

     | r | (r+1)-mark query, image | age-2 pair, image (3L, 4L) | sets of ≤ r classes with a moved class | largest, sM |
     | ---: | --- | --- | --- | --- |
     | 2 | 2,129, none | 96, 160 (96, 128) | 98 of 98 equal | 415, 2,048 |
     | 3 | 3,363, none | 180, 282 (180, 240) | 5,057 of 5,057 equal | 803, 3,200 |
     | 4 | 4,877, none | 288, 436 (288, 384) | 3,000 sampled, all equal | 1,399, 4,608 |

     The hubs' separating flows are at least sM in each.
4. **The 239-junction stage keeps every later pair and triple: confirmed.**
   - **Why.** With two attachments, a later internal reading is min(t, L_H(X) + λ′). The referee's maximum flow gives λ = 1 at
     every age from 0 to 12, with sizes matching the study's to (415, 995). Every reading therefore stays as it was.
   - **The equation change** persists at every age.
   - **The four-name query.** {y(2,8), uw(8,(2,8)), uw(0,(0,8)), uw(8,(0,8))} has no bond, and its image has exact least bond
     117.
5. **The search bounds: not rebuilt (lighter).**
   - **The superset argument for ≤ 17 distinctions** was read and is sound as a superset: n ≤ (2W + 1)/3 junctions with the
     exterior, and the wired graph is two-connected.
   - **The sweep** (nauty, a rank filter, 18,330,249 allocations) and the 3,162,112 panel assignments were not rerun.
   - **An independent bounded check exists.** GROWN-END-READING-R1's census (widths 3 to 16, stages of at most 11 junctions)
     found no triple-keeping map that fails.

## What this does to the three-way line

- **THREE-RIGID's direction: Block at all sizes.**
  - R3 (triples force the equations) was already refuted by the 239-junction stage.
  - This stage refutes three-way transport itself: pairs, triples and the fixed end do not carry the next round.
  - The all-size family shows that no fixed order r suffices; the needed order grows at least like √(size).
  - The frozen hunt's predictions Q1 and Q2 (at most 14 junctions) are untouched.
  - The route that survives is equation-span transport (Claim B*), or a reading order that grows with size.
- **THREE-WAY and TRIPLE-GROWN: Narrowing.** Their claims that triples separate every collision found so far stand. The general
  reading, that pair and triple readings separate reached collisions, is false at 104 and 239 junctions. A97's wording on triples
  should say "within the censuses" (for the owner).

## Points for the owner (listed, not folded in)

1. **replay.md says** the 239 stage's four-name image "has a witnessed bond of size 126". The exact least bond is 117, so 126 is a
   witness, not the minimum. **Not a block.**
2. **The completeness of the 24-map group** and the global search bounds were not independently rebuilt. **Not a block.**

## How the work was split

- **The referee:**
  - read `decision.md`, `proof.md`, `constructive-proof.md`, `boundary-proof.md`, `replay.md`, `small-width.md` and `census.md`;
  - wrote `bondmilp.py` (exact least bonds, checked against enumeration) and `job_lbr.py`, with its own compression, bond
    enumeration, family builder and 239-junction growth (from GROWN-END-READING-R1).
- **Read as data:** the literal start and maps.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py`: `runs/referee-lbr`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
