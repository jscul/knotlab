# How hard is recognizing a safe split?

Status: Proved

## Standard statement

Take two consecutive parts of a guarded two-route formula whose internal middle and padding names occur at most twice in their respective roles. At the cut there is exactly one shared middle and no shared pad. Compare using the same bit for its two occurrences with giving them independent bits. Deciding whether both readings allow *exactly the same triples* of the two outer boundaries and the cut bit is NP-hard under polynomial-time many-one reductions. This holds on one computable wiring per number of source variables, varying only its switches. The same reduction works for equality after forgetting the cut bit, and for preservation of SAT at the prescribed outer pair \(1,0\).

For general explicit instances a constant number of nonadaptive SAT queries suffices. This gives an upper bound with an NP oracle. We do not assert NP membership or completeness of the general comparison problem.

## Nearest known result

The accepted fixed-wiring construction represents arbitrary strict 3-CNF using the switches of a serial two-route formula under two-use middle and pad constraints. Its internal stage implications are all positive, with switched padding values. The earlier block solver separates sections sharing only an interface bit. The new reduction adds two stages and turns the problem of *recognizing* a sound separation across one shared choice into the original SAT decision. [Fixed compiler](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md) · [Earlier block computation](../../SWAPPED-ROUTE-GROUPING-20261115-001C/SWAPPED-ROUTE-GROUPING-20261115-001C-P001_decision_and_controls/proof.md)

## Construction and argument

Let \(F\) be a strict 3-CNF on \(n\) variables and take the fixed catalogue of every signed clause on three distinct names. Enable just the clauses of \(F\). Use the compiled stages as a block with free endpoint bits \(a,u\), removing the external endpoint requirements by switching them off. For \((a,u)=(1,0)\), supplying these two values by observation has exactly the same effect as the original endpoint requirements, since the respective padding and witnesses are private. Thus the block permits this pair precisely when \(F\) is satisfiable. It always permits \(00,01,11\): for constant endpoints assign every signal constantly, and for \(01\) use all zeros except the last boundary. Every positive implication is then satisfied for every pad value. The block therefore realizes
\[
             P_F(a,u)=[a\le u]\ \lor\ \operatorname{SAT}(F).
\]

Append two stages with fresh names, using a single new upper middle \(h\) in both. In the first stage enable just \(u\to h\). In the second enable \(b\to h\) and \(h\to z\), where \(b\) is the cut boundary and \(z\) the last boundary. Enable both padded halves of each required implication. All other half-slots in the new stages are off. The padding names of these two stages are private. The two suffix stages use identical guards for every \(F\), and \(h\) is the only name with one occurrence on each side of the cut. Both its occurrences constrain possible local states. The inputs to the recognition problem are the *joined* formula and the cut. The split formula is determined by this input.

With separate copies, choose \(u=a\) in the first block, \(h_L=1\) and \(h_R=b\). Consequently
\[
             R_{\rm split}(a,b,z)=[b\le z].
\]
With a common \(h\), a witness needs \(u\le h\), \(b\le h\le z\) and \(P_F(a,u)\). Eliminating \(h\) and \(u\) gives
\[
             R_{\rm joined}(a,b,z)
              =[b\le z]\ \land\big([a\le z]\lor\operatorname{SAT}(F)\big).
\]
For instance when \(F\) is satisfiable choose \(u=0,h=b\). When it is unsatisfiable, the three inequalities require \(a\le z\), and \(u=a,h=\max(a,b)\) suffice if \(b\le z\) as well. Thus the two triple relations agree exactly when \(F\) is satisfiable. Otherwise they differ at just \(100\), in the order \(a,b,z\). The split relation always admits the external pair \(1,0\) by taking \(b=0\), so the same equivalence applies after existentially forgetting \(b\). ∎

The original compiler has \(4m+12n+8\) stages for \(m\) catalogue slots, so this wiring has \(4m+12n+10\) with \(m=8\binom n3\). The whole transformation has polynomial size after indexing source variables. Repeated source clauses can use one selector. For any fixed \(n\), a satisfiable and an unsatisfiable menu can have exactly the same wiring and the same guard values in both stages next to the cut. Thus looking only at those stages cannot classify the split. A uniform polynomial-time exact recognizer on all such inputs would give a polynomial-time algorithm for strict 3-SAT. This conditional implication is compatible with efficient exact tests on restricted blocks or with summaries already in hand.

For the oracle upper bound, fix each of the eight boundary triples in the joined and split formulas by three units and ask SAT independently. Compare the resulting tables. The one-name structure further limits any disagreement to the two triples \(100,110\), as shown in the direct analysis of active switches. Four SAT queries, two per triple, therefore suffice for triple preservation in this positive model. For the outer pair \(10\), two direct SAT queries suffice. The constructive local-support reader supplies another bound when the internal blocks are tractable. [Support test](../../GUARD-CHOICE-SEPARATION-20261115-001A/GUARD-CHOICE-SEPARATION-20261115-001A-P001_boundary_supports/proof.md) · [Two potentially lost triples](../../GUARD-CHOICE-SEPARATION-20261115-001B/GUARD-CHOICE-SEPARATION-20261115-001B-P001_live_switches/proof.md)

The checker evaluates \(F\) independently by enumeration, pins every raw switch on the joined and separated CNFs, and tests all eight boundary triples in both. It exhausts all 256 source menus on three variables and tests fixed rosters on four and five. One joined raw clause list per width and every suffix guard bit are checked to stay fixed. [Raw replay](check.py) · [Counts](checks.json)
