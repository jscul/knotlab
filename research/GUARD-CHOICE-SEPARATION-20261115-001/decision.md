# When two blocks can forget a shared choice

For a fixed choice of initial, cut and final boundary values, each side can report whether it allows the shared bit to be 0, to be 1, or both. If both sides are possible, they can solve that case separately exactly when their sets share a value. One side forcing 0 and the other forcing 1 is the only obstruction on one shared bit. To forget the bit for all inputs of this layout and guard setting, perform this test on all boundary triples. When the cut bit is hidden, test whether *some* cut value works for the same outer pair. A different cut value really can rescue such a pair. The table algorithm gives actual joined assignments and takes linear indexed work per internal mixed-pad choice on each side. [Support algorithm and proof](../../proofs/GUARD-CHOICE-SEPARATION-20261115-001A/GUARD-CHOICE-SEPARATION-20261115-001A-P001_boundary_supports/proof.md)

On the same two-stage wiring, keep the upper implications \(x\to h\to b\) and \(b\to h\to z\). The common choice \(h=b\) works for every surviving triple. Turn off just one raw guard on the left outgoing implication. For \((x,b,z)=(1,0,0)\), the left now allows \(h=1\) and the right requires \(h=0\). Splitting the choice creates this one boundary assignment. Turn off one more guard on the right outgoing implication and \(h=1\) works everywhere. From that last setting turning the right guard on again changes the joined, endpoint-pinned answer from SAT to UNSAT and keeps the split answer SAT. The two occurrences are genuinely active. Across a complete-stage cut on positive routes, sharing only padding names always permits separate solving for each boundary triple. [Fixed switch comparisons and pad-only theorem](../../proofs/GUARD-CHOICE-SEPARATION-20261115-001B/GUARD-CHOICE-SEPARATION-20261115-001B-P001_live_switches/proof.md)

Determining the two allowed-value sets from long blocks can take most of the work. We built one wiring for each source width, with the same two guarded stages next to the cut and just one crossing middle. Switches earlier in the formula encode any strict 3-CNF. Dropping agreement preserves all boundary assignments exactly when that 3-CNF has a solution. The equivalence also holds after hiding the cut bit. One polynomial-time test that correctly recognizes every such split would decide general 3-SAT in polynomial time. On the unrestricted one-middle family, at most two triples can be lost. Querying joined and split feasibility on those two triples gives a four-query upper bound. [Reduction and raw checks](../../proofs/GUARD-CHOICE-SEPARATION-20261115-001C/GUARD-CHOICE-SEPARATION-20261115-001C-P001_recognition_cost/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one shared choice | **Status:** Successful | Exact agreement test and guard-only recognition reduction |
| Local direction — summarize a block | Continue | One bit suffices when the side supports are available |
| Broader exploration — efficient SAT shortcuts | Known alternatives | Pad-only cuts and implication reachability |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | The cost of finding a grouping can encode 3-SAT |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Find what two shared choices must report together | 2/3 — stronger block summaries | 3/3 — three-stage test | Compare separate bit supports with joint supports → find a guarded disagreement or prove none | Selected · started |
| 2 | Compare overlap measures on flat and factored formulas | 2/3 — representation sensitivity | 3/3 — paired encodings | Evaluate one proposed work measure on an equivalent pair → reassess at the first separation | Alternative · deferred |

The bounded first discriminator for #1 found a disagreement on three stages. At boundary values \(1,0,0\), enable only \(x\to h\) and \(k\to b\) on the left, and only \(h\to c\to k\) through the right block's internal boundary \(c\). All pads are private. Then the left allows just the pair \(10\). The right allows \(00,01,11\). Each coordinate agrees separately, yet no joint assignment exists. We checked both allowed sets and all four ways to retain or split the two names on the raw ternary clauses. This is a bounded follow-up example. The remaining question is how cheaply a block can report the needed implications on larger interfaces. Candidate #2 has concrete paired inputs from the basket. It would test an overlap measure if a specific proposed measure guides a new decision.

**Basis:** Three locally proved results with separate raw-CNF checks and witness recovery. Enumerated 9,520 local support entries, 4,760 joined/split triple comparisons, and the reduction's complete three-variable guard menu, followed by larger four- and five-variable menus. The reduction supplies the asymptotic conclusion. The formula and all guard switches are supplied input data. No claim about a new native knot enters the argument.

**Corrections:** None to earlier formal results. **Goals:** G3 and G16 gain an exact separation criterion, an efficient pad-only case and an obstruction to unrestricted recognition. **Assumptions:** The proved criteria state separately which boundary bits are observed and when endpoint guards are pinned. The declarations specialize the existing supplied finite route model. No standing assumption changed.

**Basket:** B182 was taken for the one-shared-choice question. B181 asks for a broader simulation; SIGNED-KNOT-OVERLAP-20261114-001#1 is candidate #2 here. The separately selected B183 takes the stronger proof-model direction.

**Review:** Independent internal checks give V1 support for the finite replays. The outside design advisor was unavailable at its weekly quota. The intersection rule is classical, and the local claims concern its realizations and recognition on this exact family.

## Final report as sent

2026-11-15 17:42:31 UTC

One switch on unchanged wiring can make agreement on one shared choice decisive. The exact test is to compare the values the two sides can actually use. Those summaries may themselves encode strict 3-SAT, even on one shared bit. With two shared choices, the three-stage follow-up already requires their joint values.
