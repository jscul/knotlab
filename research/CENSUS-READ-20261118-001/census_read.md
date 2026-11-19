# Does the new distance reader read every growing census arrangement?

Epic `CENSUS-READ-20261118-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-READ-20261118-001#1`. Goals
G1 and G17; assumption A97. **Preliminary, stress test pending:** the full census pass is not finished; this section reads the
first 77 shards of the exact pass (1,925 arrangements, every stage, the sorted list's one- to four-knot part), so it is not a
sample of the whole census. [Pre-registration and its four amendments](preregistration.md) ·
[preliminary summary](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/summary_exact_prelim.json)

## Preliminary (2026-11-19, 1,925 arrangements, 9,695 stages)

- **The ring's success does not carry over.** On exact tables, the name-free reader R3n reads 252 of 9,695 stages exactly (2.6%)
  and 15 more as an outside swap; 884 come back as another presentation of the same allowed states, and 8,544 are misread. R3 under
  the census's own names: 249 exact. The frozen C1 fails (rigid stages misread), and the old reader misreads almost everything.
- **What the misreads share.**
  - 8,485 of the 9,695 stages come from starts in which two knots share two or more distinctions, which the reader refuses by
    construction; most have a pair at distance 1 (two knots of three places sharing two distinctions force the other two equal).
  - Most of the rest are not 3-connected (7,157 stages have a 2-separation, 2,120 a cut vertex), where junctions can be exchanged
    without changing the allowed states.
  - Symmetric ties: the three three-place knots in a triangle have a table that cannot tell their junctions from the triangles
    between them (the table's symmetries are the octahedron's, 48, against the arrangement's 24), so the name-free reader returns
    nothing there. This is the uniqueness question in its smallest form.
  - Two faults in my instruments, found here: when nothing is loose (a closed stage) the bond test wrongly requires the empty
    outside end to be connected, so every junction's own bond is missed (291 stages); and R3n's rule for jointly dependent
    candidates drops all of them when the loose set is as small as a junction.
- **Where it reads exactly, the needed distance is the largest junction less one, every time** (252 of 252 stages, largest
  junctions of 3 to 6 distinctions; R3 the same on its 249).
- **Side-limited tables are wrong on the census.** Tables over sides of at most six junctions differ from tables over eight on 199
  of 200 large stages, and from the exact table inside the reader's horizon; on the 5,659 stages of more than 14 junctions, R3's
  verdict changes on 450 between the side-limited and the exact table. Passes 1 and 2 are therefore not evidence above 14
  junctions.
- **Names.** R3's verdict changes under one of three renamings on 419 stages (4.3%); R3n's on one stage.

Next: fix the two instrument faults, classify each stage by whether a table symmetry moves its junctions, and read the whole census
again (Amendment 5).
