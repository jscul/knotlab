# Does an ordinary birth choose the sign law?

**Neither operation is forced by the fewest-funded parity growth rule. The sign-law selection stays open.** A particular three-knot start really does produce the exterior even-parity constraint predicted by positive counting. Growth also admits the two complete fillings that cancel in the signed calculation. Other births and two-parent joins supply direct counterexamples to both universal criteria. [Design committed before the runs](https://github.com/jscul/knotlab/blob/37526d190dcf6408bd7c9656c40fade68a5b7154/research/GROWTH-SIGN-LAW-20261125-001/preregistration.md) · [Two rival tests](../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/results.md#which-operations-come-from-the-ternary-alone)

A “join” in this study is a birth that takes an existing distinction from each of two or more parents. The rule performs a test if the event itself fixes its inputs and uses its result to determine a child, a permitted transition or a subsequent outcome. An equivalent implicit calculation qualifies. We tested births and joins separately. A chosen contraction of an otherwise unchanged record is evidence about that reading of the record.

## Where three copies really do close

Start with the three ternary holdings (0,2,3), (0,1,4) and (1,2,5). The rule takes the three private distinctions 3, 4 and 5, creates one new holding on exactly them and gives it zero fresh distinctions. Adding the three old parity equations modulo two cancels the shared distinctions 0, 1 and 2 in pairs. Thus the new even constraint on 3, 4 and 5 already followed from the start.

For every even exterior there are exactly two complete old fillings and both remain possible as distinct full records after the birth. At exterior **000**, the three shared distinctions can be **000** or **111**. Under the all-positive tensor their contributions total $1+1=2$. Under the signed tensor they total $1-1=0$. The actual birth still occurs. Its exterior support agrees exactly with the positive contraction. The growth event neither suppresses this child nor identifies its two full records. No other field or subsequent constraint consults that signed total. The different three-copy results can be reproduced by applying the October summation rule to the fixed records. On a four-ternary cyclic comparison the same signed sum at exterior 0000 is 2. [Independent exterior enumeration](verify_selectors.py) · [Earlier signed summation](../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md)

The starting knots from GROWN-OPPOSITE-READS each have **four** distinctions. With three such knots the round gives one three-parent child with three fresh distinctions, together with three one-parent children with two fresh distinctions each. The six private distinctions of the old knots form 32 allowed exterior words. Summing the two private bits modulo two at each parent yields a useful three-bit reading with four even possibilities. The three individual distinctions the central child actually takes have **all eight** possibilities. This holds for all eight ways to choose which member of each private pair pays. The two readings refer to different physical distinctions. [Original four-place fixtures](../GROWN-OPPOSITE-READS-20261125-001/verify_larger.py) · [Private-pair comparison](../../artifacts/GROWTH-SIGN-LAW-20261125-001/GROWTH-SIGN-LAW-20261125-001-E001_growth_operations/selector_controls.json)

## Actual births and the open-bit test

The five-knot start gives five two-parent children. For example, original parents 0 and 2 share no distinction with one another. They fund a child on old distinctions 5 and 9 and new distinctions 15 and 16. With these two original parents there is no third shared internal distinction that would close the three copies. The child requires the XOR of its two fresh bits to equal the XOR of its two inherited bits. It accepts each of the four inherited assignments. It chooses no open real coefficients or two-bit readout. Seven starting knots give seven joins of the same kind. The unary children of a single starting ternary give independent birth counterexamples.

There is genuine reversible information in an ordinary birth. For a unary ternary child the inherited bit $x$ and the fresh pair $y,z$ satisfy $x=y\mathbin{\oplus}z$. The pair recovers $x$ exactly. Read either fresh bit alone and each of its two values occurs once for either input. If an analyst instead sums the unused bit against coefficients $(u,v)$, the unsigned matrix has determinant $u^2-v^2$ and loses invertibility at $(1,1)$. Applying the same summation to the signed three-bit tensor gives determinant $-(u^2+v^2)$, nonzero for every nonzero real pair. The actual growth rule uses the same possible extensions under both sign assignments. It enforces neither open-coefficient test. [Determinants and ordinary one-bit and two-bit readings](../../artifacts/GROWTH-SIGN-LAW-20261125-001/GROWTH-SIGN-LAW-20261125-001-E001_growth_operations/selector_controls.json)

The reason extends beyond the list of starts. The transition first computes parent groups, available private distinctions, demand, and whether a zero-fresh constraint was already implied. It keeps the older holdings and appends the funded ones. A new holding with fresh parity bits gives each admissible inherited assignment equally many extensions. A zero-fresh holding admitted by the parity rule already follows from the older constraints. For a full successor word $y$, its old restriction $\pi(y)$ is unique. Either sign decoration $s$ on the old words can be carried as $s(\pi(y))$ on the successors with precisely the same ordinary transition. This also explains why recovering an old word from its extensions can mimic reversibility for both sign choices. The diagnostic about a supplied odd sign in a closed round is evaluated only after the birth. It cannot affect funding. [Physical update](../../experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py) · [Complete-round cross-check](../../experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py) · [After-birth diagnostic](../../experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/growth.py)

## Scaffolds and order

| Starting holdings | Births in one complete round | Extensions of each old word |
| --- | --- | ---: |
| One ternary | Three one-parent children | 8 |
| Two ternaries sharing two distinctions | Two one-parent children | 4 |
| Three ternaries, one distinction shared by each pair | One three-parent closing | 1 |
| Three four-place knots in cyclic order | One three-parent and three one-parent children | 32 |
| Five four-place knots in cyclic order | Five two-parent children | 32 |
| Seven four-place knots in cyclic order | Seven two-parent children | 128 |

We reversed the order in which already funded children were added in every multiple-birth fixture. We also reversed the presentation of the starting holders and exchanged equivalent private payments wherever possible. The resulting holdings agree after matching names. We then changed the *chronology*: under the separate present-state serial rule, independently eligible births at either end of a connected four-knot start can fire in either order. Both orders preserve the same old words and each inherited bit has two fresh fillings. In the seven-knot control, the same two parents can join immediately or each make a one-parent child first. Even holding the two physical payments fixed at 63 and 65, the join gets **one** fresh distinction when first and **two** when delayed. The order control thus changes an actual birth while leaving both sign laws possible. The already closed and underfunded inputs supplied no birth and were excluded from the universal test. [Production and serial receipts](../../artifacts/GROWTH-SIGN-LAW-20261125-001/GROWTH-SIGN-LAW-20261125-001-E001_growth_operations/results.json) · [Archived serial rule](../../experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/serial_orders.py)

The two sign laws remain distinct extensions of the ordinary allowed-state model. If one *requires* a signed exterior contraction to agree with the ordinary closing, the three-ternary fixture excludes the negative signing. If one *requires* reversible open-bit maps for every nonzero real input, the determinant test selects it. These are additional, testable requirements. The owner’s stop condition is met for the specified growth law.

## Replay

The production run checked 24 births, including 14 with multiple parents and 12 with exactly two. It took 0.69 seconds and peaked at 172,944 KiB. The production checker reproduces the original five-knot starting and grown holdings from the earlier archive. A separate exact enumeration checks which physical fillings survive, the two determinants and the comparison with four copies. The canonical K1–K3 checker passed for the even relations of arity three, four and six. This is a finite experimental audit accompanied by an argument about the inspected parity update. No empirical frequencies enter the verdict. [Original grown study](../GROWN-OPPOSITE-READS-20261125-001/results.md) · [Growth source](../../experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A-E001_freedom/ordinary.py)

```sh
id=GROWTH-SIGN-LAW-20261125-001
family="artifacts/$id/${id}-E001_growth_operations"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -B "$family/check.py" --check
python3 -B "research/$id/verify_selectors.py" --check "$family/selector_controls.json"
```

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| Growth as a selector of the sign law | Successful test | Neither operation is forced |
| Three-copy closing | Exact on ordinary support at one start | Both old fillings survive each even exterior |
| Selecting a sign law in the wider program | Open | The two additional criteria still disagree |
| G5 Dynamics and G9 Witnesses | Obstruction learned | Both signings can accompany every full ordinary extension |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Select a sign at an actual change of state | 2/3 — Substantial | 1/3 — Stated | Identify an independent rule → the two signings give different native successors | Alternative · deferred |

**STOP.** The requested universal test is settled for the ordinary birth rule. An independently motivated rule that observes the difference could reopen selection. Another starting size under the same update would still retain the full old word.

**Corrections:** The growth test leaves the earlier signed calculation intact.

**Goals:** G5 and G9 now have an explicit boundary between ordinary growth and signed summation.

**Assumptions:** The source sign choice and open summation in A271 and A272 remain supplied. The test varied the ordering convention in A104. A273 records the two readings of the four-place start.

**Scaffolds:** The starts, the use of complete rounds or a current-state order, equivalent loose payments, and alternative exterior readings were all varied.
