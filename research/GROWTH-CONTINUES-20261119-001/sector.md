# What the 13-and-4 sector gives one round later

On start-03 there is a funded age-ten birth with **at least 183,833,974,142,794 age-nine parents requiring at least three holding blocks**. Every maximal extension of the displayed family has these properties. At least **20,527,630,615,620** specified parents in each extension admit no individual replacement. The total fraction of replaceable parents, including the members added by maximal extension, remains open. Age eight had only 28,065 junctions in total. [Exact replay and counts](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/sector_witness.json)

## From a held family to a birth

Write $C$ for the 13,041 age-eight junctions common to blocks 13 and 4, and $H$ for the 21,070 in their union. The previous count gives exactly $s=183,833,974,142,787$ legal age-nine children whose rosters contain $C$. Denote their family by $S$. Their old rosters lie entirely in $H$. Taken alone, the whole family is held by every site of $C$. The replay sharpens its shared trace. Every site of $H$ occurs in some member of $S$. Indeed, every site in the sole held maximal set, block 4, has a compatible site in $H$ outside that block, so the pair can extend to an unheld maximal set in $H$. Consequently a site belongs to every member of $S$ exactly when it is compatible with all of $H$, counting itself. There are 13,161 such sites. [Original sector proof and count](../HUB-GUIDED-SAMPLE-20261119-001/structure.md)

An age-nine block indexed by an old site $v$ contains precisely those children whose old roster contains $v$. Thus a family is pairwise compatible when its rosters meet pairwise. Two blocks cover it exactly when two old sites hit every roster. Checking all raw blocks also checks all choices after contained blocks are removed. [Reached-stage rule](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md)

The following seven further rosters are explicit. Start with the listed old sites, then repeatedly add the first compatible site in the indicated order among the 28,065 original site IDs. Each finished roster is maximal on the whole old stage, lies in no old holding block, and has a member outside $H$.

| Initial old sites | Completion order | Roster size | Members in $C$ |
|---|---|---:|---:|
| 10294, 10427, 17868 | increasing | 355 | 9 |
| 8497, 12040 | increasing | 1,496 | 133 |
| 4674, 27760 | decreasing | 2,189 | 1,322 |
| 9944, 27909 | decreasing | 3,984 | 972 |
| 0, 8850 | increasing | 11,516 | 8,832 |
| 10217, 12040 | decreasing | 3,717 | 560 |
| 0, 8583, 23544 | increasing | 13,830 | 9,778 |

Every one meets every member of $S$ through $C$. All 21 pairwise intersections of the seven are nonempty, the smallest having three sites. Among the 28,065 old sites there are 48 nonempty membership patterns on the seven rosters. Taking two patterns at a time gives 126 distinct unions, all missing at least one roster. Three old sites, 0, 7194 and 17843, hit the seven and all of $S$. Thus the displayed family has covering number exactly three. Every maximal extension has covering number at least three and at least $s+7$ members. Its size and failure of a one-block cover make it a legal large group. The funded rule provides the requisite open counts at this reached stage. A child with at most two old parents could never belong to such an extension, since its own parents hit every roster it meets. [Literal checks](../../experiments/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/sector_checks.py)

## Protected sector members

The following argument includes every possible outsider. Suppose three distinct actual age-nine rosters $P_-,P,P_+$ belong to the extension. A replacement for $P$ must miss $P$ and meet $P_-$ and $P_+$. It must therefore contain one old site from each of $P_-\setminus P$ and $P_+\setminus P$. If every cross pair between these differences is old-incompatible, no lawful outsider can do this.

In the published two-block calculation a maximal roster $P(U)$ is specified by the union $U$ of the right-hand exclusions of some left sites. Distinct feasible unions give distinct physical rosters. Enlarging $U$ can add only left sites and remove only right sites. Use the two actual left sites 16799 and 16800, with exclusion masks $a,b$, and the two right-hand flags $u=193,v=192$ in physical site IDs. The mask $a$ contains $u$ alone among these two flags, and $b$ contains both. Take any feasible $U$ with both flags absent and the other 35 flags of $a\cup b$ present. Then $U$, $U\cup a=U\cup\{u\}$, and $U\cup a\cup b=U\cup\{u,v\}$ are feasible by union closure. All three are nonempty, so each yields a genuine birth. The sole held maximal set corresponds to the empty right-hand exclusion.

Only a right-hand site testing $u$ can be lost in the first step. Only a left site requiring $v$ can be gained in the second. The literal block table gives 196 possible right sites and 25 possible left sites, with **zero compatible cross pairs**. The preceding test protects the middle roster under every maximal extension. Distinct base unions $U$ yield distinct middle rosters because deleting $u$ recovers $U$.

Conditioning the archived exact counting circuit gives 20,527,630,615,620 base unions. The independently encoded 507-variable closure formula with 37 physical unit clauses gives the same integer in Ganak 2.9.0 exact mode. This protects at least 11.16% of the identified sector. It supplies an absolute bound on the whole extension's irreplaceable members. The number of additional members in an extension and their available replacements are unknown, so this certificate does not establish the registered upper bound of three replaceable members per 2,000. All searches here chose witnesses. No population frequency is inferred from their selection. [Conditioned formula](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/sector_fiber.cnf) · [Source of both integer encodings](../HUB-GUIDED-SAMPLE-20261119-001/structure.md)

## Why the sector count alone does not iterate

A finite pair of funded starts isolates the role of outsiders. Take $k\ge3$ pairs of alternatives and a common set $C_0$ of $h\ge2$ sites. Each alternative meets every other alternative except its partner. Every member of $C_0$ meets all the alternatives and the rest of $C_0$. Hold the all-first and all-second choices, each together with $C_0$. Supply each remaining compatible cross pair of alternatives with its own two-site block. The unheld maximal rosters are precisely $P_T=C_0\cup T$ for the $s_0=2^k-2$ mixed choices $T$ of one member per pair. Every compatible pair occurs in one of these rosters. Set each initial open count to its exact demand. The ordinary dead-hub realization supplies connected literal starts with these blocks and open counts. All children share $C_0$, so their next large group is held and the next births all have two parents. [Hub realization](../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md)

In the second start, add a site $x$ outside the same sector, incompatible with every member of $C_0$. Give it two holding blocks, one with all first alternatives and one with all second alternatives, and fund each site at its revised demand. The original sector, its closure, and its $P_T$ rosters persist. The additional births are exactly $Q_T=\{x\}\cup T$. Of the resulting children, only $P_T$ and $Q_{\bar T}$ are incompatible. Hence the following stage has $2^{s_0}$ maximal choices of $s_0$ children, at most $2k+2$ of them held by an older site. The original $P_T$ have just $k$ individually replaceable members in either start, the fraction $k/(h+k)$ being arbitrarily small. The matched starts exhibit two different one-round outcomes with the same closed sector and the same original replacement fraction. An induction for start-03 would need a new covering and replacement certificate at each round, or a law transporting both properties.

## Replay

From the repository root, run the following with the project Python. Without a stage argument the checker rebuilds start-03 through its eighth round from the preserved literal start and checks the canonical stage digest. It reads the portable sector circuit from the previous study's archived bundle. An optional `--stage` accepts a byte-identical stage export. The emitted JSON includes the seven roster digests, all pairwise intersections and the 37 unit clauses. Ganak's independent replay uses `--prob 0 --mode 0 --verb 0` with the linked conditioned formula.

```sh
.venv/bin/python -B experiments/GROWTH-CONTINUES-20261119-001/*/sector_checks.py
```
