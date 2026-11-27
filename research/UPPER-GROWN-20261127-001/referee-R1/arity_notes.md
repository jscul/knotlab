# Four-place knots and repeated meetings

The strict eight-clause box survives with **two essential four-place not-all-equal knots** and with **every distinction held twice**. Twelve knots suffice. An entirely four-place not-all-equal construction also needs every one of its twelve knots. Its distinctions have two or three holders. A different law gives an upper step on ten knots.

## The not-all-equal constructions

Start with [the strict box grown in one round](open_witness.json). Its stage has two loose distinctions, 17 and 18. Add each as the fourth place of a different existing law in which it is absent. There are 111 ordered choices. **Exactly one** retains the eight specified lower bonds. The widened laws are `(9,11,12,17)` and `(13,14,15,18)`. All 19 distinctions now have two holders. The stage has 19,448 states, 34 six-reading words and seven upper words. Of the 12 source laws, deleting any one restores the missing upper word. The two four-place deletions restore 228 and 28 source states respectively. This closure is a chosen modification of the grown stage. [All widening choices and the complete positive record](arity_positive_widen.json)

For an entirely four-place construction, take [the earlier twelve-knot box](../../RING-BOND-20261127-001/referee-R1/layer_witness.json). Each old law holds two members of one carrier and one member of another carrier. Add another distinction from the latter carrier to that law, using the least unused label in that carrier. Each new law has four different places, two from each carrier. The resulting 55,172 states realize exactly the 37 six-reading words allowed by the eight lower clauses. Every source law is needed. Among the 18 distinctions, six have two holders and twelve have three. When the three readings in a lower clause all agree, the fourth place added to each of its three active laws has the same value as another place already there. Those laws still require three binary values to differ in pairs. Widening a law retains every previously allowed state. The direct state check also verifies unreadability at the wider source knots. [Four-place construction](arity_positive_uniform.json)

Two further closed controls append a pair of knots, one taking 17 and one taking 18, to the grown open stage. Both new knots also take the same two fresh distinctions in the first control and the same three in the second. Assigning the first two fresh distinctions different values extends every old state. Both controls have 14 knots, with every distinction held twice. The 21-distinction first control has 36,382 states. The 22-distinction second has 94,598. Both retain 34 six-reading words. The original twelve laws remain essential and either added law can be removed without restoring the missing word. [Both controls](arity_positive_cap.json)

For each construction the direct replay tests all eight lower images, every source-knot fix for single-knot readability, an allowed single change for every member of each agreement carrier, the upper image, and each source-law deletion. The upper readings here report disagreement within each pair of lower readings, so their missing word is 111. The canonical checker tests all contact roles of every lower bond and the upper relation, from both the exact lower image and the conjunction of the eight lower laws. [Role checks](arity_roles.json)

## A smaller upper step under even parity

On ten knots, six with four places and four with three, impose even parity at each knot. Each of the 18 raw distinctions has two holders. Divide them into nine disjoint pairs and let `x0,...,x8` report pair agreement. The 512 allowed source states realize exactly the 32 lower words given by odd parity on four triples. Their places are `(0,1,2)`, `(0,3,4)`, `(1,5,6)` and `(2,7,8)`. Each relation passes the knot test. None of the nine first readings is determined at a single source knot. Each of the nine raw pairs takes all four words.

There is also a closed example with **ten four-place even-parity knots** and 20 twice-held distinctions. Nine disjoint pairs give the same 32 lower words on its 2,048 allowed states. The two remaining distinctions do not enter a reading. In both constructions, replacing every source law by ordinary not-all-equal on exactly the same places gives all 512 lower words and all eight upper words. This control isolates the role of the law. [Entirely four-place parity witness and not-all-equal control](arity_uniform_parity_witness.json)

Because all four raw pair values occur, each pair reading needs both of its members as a function on that carrier. Source parity requires simultaneous changes in other distinctions whenever one raw distinction changes. A stronger requirement of an allowed single-distinction change would exclude these parity examples. The not-all-equal positives above meet that stronger test.

Read `P=[x3=x5]`, `Q=[x4=x7]` and `R=[x6=x8]`. Adding the four lower parity requirements cancels `x0,x1,x2`, each of which occurs twice. The remaining six readings have even parity, giving the upper words **001, 010, 100, 111**. Each upper pair takes all four values, no single lower bond reads any upper reading, and removing any of the four lower constraints restores every other upper word. The four lower bonds are connected by shared readings. Every source-law deletion leaves the source relation unchanged because the sum of all its parity laws vanishes. This construction uses four multiword exclusions. The published simple three-place census concerns eight single-clause bonds under not-all-equal. [Source and deletion checks](arity_parity_witness.json) · [Canonical role checks](arity_roles.json)

## Exact searches under not-all-equal

Each source knot has distinct places, and the two holders of each raw distinction are distinct knots. The full search checks all carriers of two or three distinctions, all signs, and every disjoint choice that can fit six carriers. It removes a reading if some source knot determines its value on the allowed states. For each disjoint triple it tests all eight words. The triples missing exactly one supply the signed lower clauses. Starting from each such triple, the search replaces one reading at a time by a larger signed partner, requires the same signed clause on all eight choices, and checks that the six carriers are disjoint. Every box has a unique starting triple obtained by taking the smaller signed choice from each of its three pairs. Complementing all raw values preserves not-all-equal and every agreement. We therefore enumerate one state per complementary pair and identify complementary fixes of a source knot in the readability test. A shuffled state order can shorten the check when all eight words occur. Every claimed absence uses the entire state set.

| Three- or four-place class | Complete or selected | Systems | Strict boxes |
| --- | --- | ---: | ---: |
| Three-place, eight knots, at least one repeated meeting | Complete up to renaming | 15 | 0 |
| Three-place, ten knots, at least one repeated meeting | Complete up to renaming | 72 | 0 |
| Four-place, six knots | Complete up to renaming | 19 | 0 |
| Four-place, seven knots | Complete up to renaming | 50 | 0 |
| Four-place, eight knots | Complete up to renaming | 204 | 0 |
| Four-place, eight, nine and ten knots | Three specified cyclic patterns per size | 9 | 0 |
| Ten knots, two four-place, eight three-place | All 298 simple patterns plus 906 with repeated meetings | 1,204 | 0 |

Six disjoint carriers need at least 12 distinctions. Fewer than eight three-place knots or six four-place knots cannot supply them under the twice-held condition. The number of twice-held three-place knots is even.

The three-place generation uses the archived simple systems with four, six and eight knots as seeds. At any repeated meeting of multiplicity two, remove its two holders and reconnect the remaining two ends. In this temporary reduction both ends may have the same holder. A holder meeting itself is removed together with its sole neighbour, reconnecting that neighbour's two other ends. The two possible connected two-knot reductions are included directly. Reversing both operations, adding the simple seeds at their sizes, and testing isomorphisms with multiplicities enumerates every connected system with repeated meetings through ten. A triple meeting by itself already exhausts its two holders. [Eight knots](arity_cubic_8.jsonl) · [Ten knots](arity_cubic_10.jsonl)

At six and seven four-place knots, start from every connected simple meeting pattern in the small graph atlas in the literature, assign all positive meeting multiplicities giving four places everywhere, and identify renamings. The selected cyclic systems at each larger size join every knot `i` to `i+1` and `i+s` modulo the size, with `s=1,2,3`. All these systems use ordinary unsigned not-all-equal. [Six knots](arity_four_6.jsonl) · [Seven knots](arity_four_7.jsonl) · [Eight cyclic](arity_built_8.jsonl) · [Nine cyclic](arity_built_9.jsonl) · [Ten cyclic](arity_built_10.jsonl)

To recover all eight-knot four-place systems from seven, remove a holder and rejoin its four ends in pairs, leaving seven holders of four places. If no neighbour had three of these ends, they can be paired at distinct holders. Removing the holder leaves at most two connected parts, since each part has an even positive number of ends, and two ends in each part can be paired across the parts. Reversing this reduction means choosing two existing distinctions and giving their four ends to a new knot. If every holder has a triple meeting, those meetings pair the holders and their single remaining places connect the pairs in a cycle. Include this last pattern separately. The three cyclic eight-knot choices already occur in the 204. [All eight-knot four-place systems](arity_four_8.jsonl)

For the ten-knot mixed class, contract two distinctions with four distinct holders in each of the 85 archived simple twelve-knot systems. Contraction here removes that distinction and gives its two holders' four remaining places one fresh, ordinary four-place not-all-equal law. There are 117 choices per source, 9,945 in all. An exact refinement and individualization of the weighted meeting pattern gives 1,204 distinct results. Conversely, split each four-place knot of a simple mixed pattern into two three-place knots sharing a fresh distinction, dividing its four old places into two pairs. This produces a simple connected twelve-knot pattern in the archived roster, so the 298 simple mixed cases are complete. The 906 others admit repeated meetings and the stated contraction. This search took 173 seconds. [Mixed ten-knot search](arity_mixed_ten.jsonl)

The earlier twelve-knot witness gives **90 boxes** in the independent search. A four-place control holds a lower pair together at each source law. Although the intended eight 111 exclusions hold, each first reading can be taken directly at a source knot. The full strict search gives **zero** on this control. [Controls](arity_controls.jsonl)

At six and seven four-place knots, **0/69** systems even have a single-clause triple on disjoint carriers with six raw distinctions left for the other three readings. At eight four-place knots **168/204** have one, with 7,510 such clauses in total. All **72/72** ten-knot three-place systems with repeated meetings and **1,204/1,204** ten-knot mixed systems have opportunities by this count, with respectively 3,954,785 and 41,920,489 eligible single clauses. [Opportunity counts](arity_totals.json)

The unrestricted nine- and ten-knot four-place classes, all other mixed degree counts, ten-knot mixed patterns with repeated meetings outside the stated contraction, and upper relations beyond the signed box on the not-all-equal rosters were not run. The counts of eligible triples and single-clause bonds in each exact search are in the [totals](arity_totals.json).

## Replay

From the repository root, run the commands in one shell and in the sequence shown. The compiled search runs as one process at a time while the Python driver waits. Initial timings with the same limits were 0.003 to 0.088 seconds per repeated-meeting three-place case, 0.004 to 0.114 per case in the exhaustive four-place rosters, up to 1.51 per case in the selected cyclic rosters, and 0.14 per mixed ten-knot case. The mixed roster took 173.4 seconds and the eight-knot four-place roster 22.6 seconds. Direct checks timed a prefix of 8,192 raw assignments. The two full parity replays took 0.89 and 3.73 seconds including their same-support controls.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd research/UPPER-GROWN-20261127-001/referee-R1
export TMPDIR="$PWD"
py=../../../.venv/bin/python
g++ -O3 -std=c++17 arity_exact.cpp -o arity_engine
for spec in 'cubic 8' 'cubic 10' 'four 6' 'four 7' 'four 8' 'built 8' 'built 9' 'built 10'; do
  set -- $spec
  "$py" -B arity_search.py --binary ./arity_engine --group "$1" --size "$2" --limit 1 >/dev/null
  "$py" -B arity_search.py --binary ./arity_engine --group "$1" --size "$2" >"arity_${1}_${2}.jsonl"
done
"$py" -B arity_search.py --binary ./arity_engine --group pilot --limit 1 >/dev/null
"$py" -B arity_search.py --binary ./arity_engine --group pilot >arity_controls.jsonl
"$py" -B arity_contract.py --binary ./arity_engine --sources earlier --limit 3 >/dev/null
"$py" -B arity_contract.py --binary ./arity_engine --sources all --inventory
"$py" -B arity_contract.py --binary ./arity_engine --sources all >arity_mixed_ten.jsonl
for part in widen uniform cap; do
  "$py" -B arity_positive.py --part "$part" --limit 2 --prefix 8192 >/dev/null
  "$py" -B arity_positive.py --part "$part" >"arity_positive_${part}.json"
done
"$py" -B arity_parity.py --pilot >/dev/null
"$py" -B arity_parity.py
"$py" -B arity_construct.py --sets 35 --prefix 8192 >/dev/null
"$py" -B arity_construct.py >arity_parity_witness.json
"$py" -B arity_uniform_parity.py --limit 2048 --prefix 8192 >/dev/null
"$py" -B arity_uniform_parity.py --limit 1137 >arity_uniform_parity_witness.json
"$py" -B arity_roles.py --pilot >/dev/null
"$py" -B arity_roles.py >arity_roles.json
"$py" -B arity_summary.py >arity_totals.json
"$py" -B -c "from pathlib import Path; p=Path('arity_engine'); assert not p.is_symlink() and p.read_bytes()[:4]==bytes([127,69,76,70]); p.unlink()"
```
