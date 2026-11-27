# What the newly closed stages could carry

The two rival laws produced the same 171 newly closed systems, including the identities of their distinctions. Giving each closing census start one count per law, the independent search matched all 342 archived rows for both lower bonds and boxes. The 205,986 lower bonds under each law all exclude exactly one three-bit word. On the raw agreement readings, 178,398 exclude 111, 24,885 exclude a word with two ones and 2,703 exclude a word with one one. [Closed stages and archive comparison](closed_counts.json)

| Necessary condition | Newly closed starts per law |
| --- | ---: |
| At least twelve distinctions for six disjoint carriers of size two or three | 120 |
| At least twelve distinctions and at least eight lower clauses | 111 |
| Six disjoint agreement carriers, each unread at every single source knot | 97 |
| Six such carriers exist somewhere, and the system has at least eight lower clauses | 91 |
| At least one lower clause leaves room for three more mutually disjoint unread carriers | 21 |
| At least eight lower clauses separately leave room in that way | 21 |
| Two lower clauses together use six disjoint carriers, as every frozen box requires | 0 |

For the four-clause form, take the two A agreements together, either B agreement and either C agreement. The reported lower clauses forbid 111 on A0 B0 C0, A0 B1 C1, A1 B0 C1 and A1 B1 C0, after a consistent value is chosen for each reading. Of the 171 closed stages, twelve have two clauses sharing exactly one signed reading on five disjoint carriers, with room for two more distinctions. Only three have an unread sixth carrier available after such a choice. Those three are all nine-knot stages with fifteen distinctions. They supply 32 partial choices and zero complete four-clause forms. [Closed stages](closed_counts.json)

The obstruction already holds on the carriers. Each of the 68,408 lower clauses that could be extended supplied a first triple. Across those clauses there were 714,445 choices of three more mutually disjoint unread carriers. Each such choice was tested for a second clause on the three new carriers, and for the other three clauses of the alternating form, with every forbidden value disregarded. Neither occurred. The count of choices gives each first clause a separate count. It does not count distinct six-carrier sets. [Carrier-only enumeration](closed_support_counts.json)

### Search and scope

Each source knot imposed not-all-equal. The lower search enumerated all assignments on the distinct source names and all agreements on two or three of them. A reading passed the single-knot test if, for every source knot, two allowed states with identical values on that knot had different values of the reading. On each triple of disjoint carriers whose readings passed, the program kept exactly the constrained images that projected onto all four words on each pair. It evaluated both agreement values at every place. For each single-clause image, its one excluded word supplied the three signed values of that clause. [Allowed-state search](closed_bonds.cpp)

The frozen eight-clause test required all eight choices of one member per pair, using the same signed value at all appearances of a reading. The four-clause test allowed all 14 nonconstant ways to assign one A member to each B and C choice. Two assignments alternate, four depend on B alone or C alone, and eight use one A member on one choice and the other on three. All three possible conjunction pairs were tested. Only the two alternating assignments describe the four-clause form stated in the earlier report, up to renaming. A nonalternating nonconstant assignment always has two clauses on six disjoint carriers. Indeed, if the choices of A agree for 00 and 11, and also for 01 and 10, the assignment is constant or alternating. In the alternating case each of the four clauses meets every other clause in exactly one reading. No closed stage completed any of the 14 lower forms. There were zero source-law deletion tests on closed-census upper witnesses. [Signed search](closed_forms.py)

The second enumeration started afresh from the unsigned lower clauses. For every first clause `abc`, it enumerated all unordered triples `def` of additional disjoint unread carriers. A complementary clause would be `def`. Each alternating completion assigns `a,b,c` in some order to the three pairs `de,df,ef`, making three more clauses. All six assignments were tested whenever the pairs occurred in any lower clauses. Forgetting the forbidden signs can only add possibilities. [Carrier-only search](closed_supports.py)

The counts cover every newly closed stage in the six-round census under both rival laws. Other carrier sizes, signed changes to individual distinctions *inside* a carrier, overlapping carriers, other upper readings and later rounds were outside this search.

### Controls

Literal tuple enumeration agreed on every eligible reading and signed lower clause on five closed examples with six through ten distinctions. These included a five-knot stage with 128 bonds and a six-knot stage with 1,104 bonds. A separate computation on all 64 words of six readings agreed on every four-clause pattern for all 256 subsets of the eight planted clauses, under each of two sign assignments. Changing a sign at just one occurrence broke the frozen box. With the signs disregarded, this changed control kept its four complementary pairs and two alternating patterns. [Truth-table controls](closed_controls.json) · [Carrier-only control](closed_support_counts.json)

On the six published carriers of the known ten-knot closed source the search recovered the alternating step. Direct enumeration found 1,638 allowed source states, 29 six-reading words and seven upper words. Dropping source law 0 restored 111 on 18 assignments. On the six published carriers of the twelve-knot closed source it recovered one frozen box, with 7,570 allowed source states, 37 six-reading words and seven upper words under disagreement. Dropping source law 0 restored 111 on 40 assignments. The affected alternating and frozen forms disappeared respectively in the corresponding searches on the six specified carriers. Applying the canonical test in all three contact roles gave 54 expected outcomes across lower images, source and conjunction upper images, and the full upper images after deletion. [Physical controls](closed_controls.json) · [Ten-knot source](../../UPPER-GROWN-20261127-001/referee-R1/upper_four_closed.json) · [Twelve-knot source](../../RING-BOND-20261127-001/referee-R1/layer_witness.json)

### Reproduction

Run from the repository root after the independent growth replay has written `growth_stages.json`. Each command uses one process for the search. The 3 GiB address-space limit applies to each command. The three census pilot cases have six, twelve and fifteen distinctions. The signed pilot took 1.17 seconds. Extrapolating its slowest case over 171 distinct stages gave less than three minutes. The full signed census took 4.46 seconds. The carrier-only pilot took 0.27 seconds and its full census took 2.03 seconds. The control pilot took 0.12 seconds and the full controls took 0.83 seconds. Peak resident memory in these runs was under 33 MiB. [Signed pilot](closed_pilot.json) · [Carrier-only pilot](closed_supports_pilot.json) · [Control pilot](closed_control_pilot.json)

```sh
ulimit -v 3145728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
closed_review=research/CLOSED-BY-CUTS-20261127-001/referee-R1
c++ -O3 -std=c++17 -fPIC -shared "$closed_review/closed_bonds.cpp" -o "$closed_review/closed_bonds.so"
.venv/bin/python -B "$closed_review/closed_forms.py" --cases 17 61 1348 --output closed_pilot.json
.venv/bin/python -B "$closed_review/closed_forms.py" --output closed_counts.json
.venv/bin/python -B "$closed_review/closed_supports.py" --cases 17 61 1348 --output closed_supports_pilot.json
.venv/bin/python -B "$closed_review/closed_supports.py" --output closed_support_counts.json
.venv/bin/python -B "$closed_review/closed_controls.py" --pilot
.venv/bin/python -B "$closed_review/closed_controls.py"
```
