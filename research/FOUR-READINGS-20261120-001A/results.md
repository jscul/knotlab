# When contradictory parity rules admit a common operator reading

**Supplied operator values let two readers win every trial on six parity knots even though no state of the nine distinctions satisfies all six rules.** Five mutually meeting knots are the smallest pattern ordinary parity growth reaches that accepts such a reading after one rule is changed to odd. The growth itself closes with an even rule.

> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** All 115 operator certificates and 58
> refutations in any dimension replayed; 9/9 against 8/9 classically, with no complete-record change across far settings;
> growth closes 121 of 173 types, 79 admitting operators after one sign is supplied; smallest five knots and ten
> distinctions. **Narrowing:** the twelve constructed subset controls used limits of two to six steps; at the common
> three-step limit 3/12 closed under parity (9/12 over the recorded limits), 0/12 under not-all-equal. **Not a block:**
> the trace Tr(PQ) is 1/2 exactly when both answer triples are legal and agree, and the archive's integer is Tr((8P)(8Q));
> in the eight-knot table the equal weights fall on ordered pairs of answer triples and are supplied (uniform local
> marginals leave the joint weights open). Logged in `docs/CORRECTIONS.md`.

John's question was “How could something like quantum entanglement exist? It's because space is not the right base-reality to be exploring. Logic is.” His criterion was “It doesn't need to be testable, it needs to click into place.” The six-rule example and the operator classification are known mathematics. What this study adds is an exact test of which closed holdings ordinary growth can produce, its size minima, a comparison with the program's own markers and two full-record tables with different quantum verdicts. [Frozen design](preregistration.md) · [Prior objects](prior_work.md)

## Six knots, nine distinctions, two complete records

Name the distinctions by two indices from 1 to 3. The first three knots hold each row of the following table and the other three each column. The odd rule is at column 3. A displayed pair of letters means the tensor product of the usual Pauli matrices. I denotes the identity.

| | First distinction in row | Second | Third |
|---|---|---|---|
| First knot | X I | I X | X X |
| Second knot | I Z | Z I | Z Z |
| Third knot | X Z | Z X | Y Y |

Every row product is +I. The three column products are +I, +I and −I. Matrices within each of the six holdings commute. Each can therefore be measured jointly. The operators across different holdings can fail to commute. This is the literature’s Mermin–Peres magic square. [Mermin (1990)](https://doi.org/10.1103/PhysRevLett.65.3373) · [Peres (1990)](https://doi.org/10.1016/0375-9601%2890%2990172-K)

The scalar contradiction follows by multiplying all six equations. Each of the nine values occurs twice, giving +1, while the six right-hand signs give −1. At any connected size, deleting any one rule permits a solution. Choose the shared distinctions on a spanning tree of holders to meet the remaining demands, working toward the deleted holder, and choose every other distinction freely. Thus a single deletion gives exactly 2^(m−n+1) states on m distinctions and n holders. Every proper subset of rules extends to one such deletion. A loose distinction in a connected component can absorb any residual sign. In a disconnected pattern, one loose distinction only gives this guarantee in its own component.

| Rules retained out of six | Number of such parts | States on the nine distinctions per part | K1, K2, K3 on distinctions used by the part |
|---|---:|---:|---|
| 0 | 1 | 512 | No, yes, yes on the empty support |
| 1 | 6 | 256 | Yes, yes, yes |
| 2 | 15 | 128 | Yes, no, yes |
| 3 | 20 | 64 | Yes, no, yes |
| 4 | 15 | 32 | Yes, no, yes |
| 5 | 6 | 16 | Yes, no, yes |
| 6 | 1 | 0 | Yes, no, no |

Every retained rule in every nonempty proper part projects to all four of its own permitted triples. When five remain, the omitted triple projects to exactly the four words of the opposite parity. The six-rule contradiction fails coexistence. Deleting a rule differs from forgetting one distinction of a relation. These counts and the canonical checker compare all 64 subsets. [All parts and all local projections](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/six_parts.json)

Give the two readers a maximally entangled state of two four-valued systems. Alice independently receives one of the three rows, Bob one of the three columns, both uniformly. Alice measures its three operators, and Bob the transposes of his three. Each returns all three signs. Each of the nine input pairs has the same rule for its complete 8-by-8 output table: the eight pairs of answers satisfying both local signs and agreeing on their shared distinction each have probability **1/8**. The other 56 have probability zero. Each local legal triple has probability 1/4 for every far setting, so the full-record change in either direction is zero. The integer trace of the two joint outcome projectors verifies every entry, including zeros. *(R1: the trace is 1/2 exactly when both triples are legal and agree, zero otherwise; the stored integer is Tr((8P)(8Q)), 32 or 0.)* This is a six-context agreement game scored by wins, with all nine setting pairs counted. [Complete tables and integer Born traces](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json)

| Supply and score | Best result |
|---|---:|
| One common assignment, six parity rules checked | 5/6 |
| The identical common assignment on both sides, nine cross-reader trials checked | 6/9 |
| Each reader may return a different legal local string for each setting, nine trials checked | 8/9 |
| Supplied operators and entangled preparation | 9/9 |

The first two optima follow because one violated rule is attainable and costs its three input pairs. For the third, perfect agreement would define a value for every shared distinction and thereby satisfy all six rules. One disagreement is attainable by giving all-zero legal answers except for one sign on the odd column. Exhaustive checks covered 512 assignments and all 4,096 pure local strategies with legal answers. Shared randomness cannot raise their maximum. Changing the weighting to double the mass of a compatible pair when its shared bit is 1 keeps every allowed event and gives full-record total variation 1/6 on either side. The agreement condition supplies support. A probability rule is a separate choice.

## An exact reading of the holdings

Two patterns suffice. In the first, five disjoint internally connected groups of knots each share a distinction with each of the other four groups. In the second, six such groups form two threes and each group meets all three on the other side. Additional holdings and meetings may be ignored. **A connected twice-held odd contradiction admits an operator reading exactly when at least one pattern is present.** This criterion uses only shared distinctions. Its mathematical justification is Arkhipov's classification (the literature's nonplanarity criterion), in the connected-group form of the forbidden-minor theorem. The criterion is known. A positive reading still supplies the operators. [Arkhipov (2012)](https://arxiv.org/abs/1209.3819) · [Paddock, Russo, Silverthorne and Slofstra](https://arxiv.org/abs/2205.04645)

The census includes every simple connected sharing with at least three places per holder and at most seven holders. Each type has one vote. A second count lets every labelled pattern have one vote. Multiple shared distinctions per pair are treated algebraically below the table.

| Knots | Unlabelled types | Operator yes | Operator no | Reached with one odd rule supplied, yes / all reached types | Labelled types, yes / total |
|---:|---:|---:|---:|---:|---:|
| 4 | 1 | 0 | 1 | 0/1 | 0/1 |
| 5 | 3 | 1 | 2 | 1/2 | 1/26 |
| 6 | 19 | 10 | 9 | 6/10 | 541/1,858 |
| 7 | 150 | 104 | 46 | 72/108 | 140,844/236,926 |
| **Total** | **173** | **115** | **58** | **79/121** | **141,386/238,811** |

Every positive case has an independently constructed array of signed Pauli products. Checking every local commutator and multiplying the operators produces the prescribed signs. Each observable actually takes both eigenvalues in every stored positive witness. Every negative case has a replayable word reduction from all of its local product equations to I = −I. This rules out arbitrary operator dimensions. An independent search for the connected groups and the theorem's planarity test give the same 173 verdicts. Direct enumeration of every labelled subset of possible meetings agrees, by size and number of distinctions, with multiplying each type by its number of labellings. Moving the odd sign from last to first leaves every verdict unchanged. With all signs even every case is satisfiable. [Census, witnesses and holdings](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json) · [Negative word reductions](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/arbitrary_operator_refutations.json) · [Derivations](derivations.md)

Distinctions shared by the same two holders commute with each other and with every operator used by either holder. Their product can replace the entire bundle. Conversely one operator and identities refill it. If a bundle has at least two members, multiplying two of them by the same independent sign creates variation without changing either rule. This is the convention of Hermitian involutions used in the theorem. Two holders with three distinctions all in common already contradict each other when their signs differ, and demand opposite values from the same operator product. Thus “smallest” for the six-knot example refers to **nine distinctions for an operator-positive pattern**. Five holders with every pair sharing one distinction already qualify at ten distinctions. [Repeated-holding and sign controls](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/additional_controls.json)

**G4's Fano pieces.** The literal Fano pattern consists of seven distinctions and seven triples, each distinction held three times. Deleting a holder leaves four distinctions held three times. Deleting one distinction leaves all six others held three times. Neither piece can occur with the original incidences inside twice-held rules. Erase instead every rule using the deleted distinction and four triples remain, with each pair of triples meeting once. This weaker marker occurs on the four-knot all-pairs type, whose signed contradiction has no operator reading. The six-knot positive example has neither marker. Under not-all-equal the intact Fano pattern has 0/128 states, while the six-knot three-against-three pattern has 102/512. A single odd parity sign has no counterpart in that unsigned not-all-equal control. G4's conclusion about its own three-held contradictions keeps its original scope. [Fano study](../ATOM-ONE-20261107-001/atom_one.md) · [Marker controls](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/marker_controls.json)

**October's charge, twists and holes.** The charge is odd in every case. It determines the failure of a scalar state, and its position can be moved by changing signs along a chain. A three-place parity rule has four forbidden words and the same local hole reading of rank three under either sign. Take six three-place knots, either in two threes with every cross-meeting, or in two mutually meeting triples joined by three matched distinctions. Both have nine distinctions, four independent loops, and the same local holes, degrees and charge. Only the first accepts operators. This is the smallest mismatch by number of distinctions with these counts fixed. Adding the presence of an odd-length holder loop as a marker still fails, at six knots and ten distinctions. One such pair differs by replacing meeting 01 with 03, with every other meeting fixed; the second arrangement then accepts operators. The literal holdings are types 188 and 189 of the stored census. These results test the registered markers. The connected-group criterion above *does* decide the answer. [Charge depth study](../DEEP-HOLES-20261020-001/deep_holes.md) · [Exact opposite-verdict pairs](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/additional_controls.json)

The October permutation test requires a specified transfer on every link. An odd number of specified swaps has no fixed bit, and an even number fixes both. Assigning one odd *holder* supplies no such link data. The October odd-loop identity also needs orientations, a twist on named loop classes and an orientation weighting. These are absent in the sharing census. We tested the defined transfer parity and the ordinary length-parity control, and leave the orientation-dependent statistic undefined here. [October hole comparison](../HOLES-COHOMOLOGY-20261019-001/holes_cohomology.md) · [Odd-loop identity](../ODD-LOOP-20261023-001/odd_loop_identity.md)

## Which closed structures does ordinary growth produce?

For a proposed final knot $v$ with three or more places, delete $v$, keeping its distinctions loose at their old holders. This gives an exact decision for reachability from *some* connected lawful open start in at least one ordinary step. The other holders must each have at least three places. Deleting any one holder from the original closed sharing must leave it connected. The distinctions of (v) must have different other holders. Every pair of those holders must have a common witness in the remaining structure, and no earlier witness may meet them all. Test every choice of (v). The criterion handles old repeated meetings. Among the 173 census types the direct ordinary forward rule restored 397 of 1,183 specified last holders. Their 121 different reached types include 79 that admit operators after re-signing. [Every puncture and ordinary result](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/all_punctures.json)

The reason is that every funded closing step has a sole birth and consumes every loose distinction. Each parent gives that birth exactly one distinction. Conversely the registered common-holder conditions give precisely one group. Summing the existing parity equations forces even parity at the last knot, and the birth takes no fresh distinction. The physical source is lawful exactly when its written knots project to their complete local rules; the connected-deletion criterion certifies that. Under not-all-equal the same funded proposals require fresh distinctions. A new odd demand is a subsequent supplied change of sign. It destroys scalar coexistence.

| Meaning of smallest reached operator-positive pattern | Minimum | How it is attained |
|---|---|---|
| Any final knot of at least three places | **5 knots, 10 distinctions** | Four mutually meeting knots with one loose distinction each grow one four-place knot. |
| All knots have three places | **12 knots, 18 distinctions** | Replace one knot of the six-knot positive pattern by the seven-knot configuration in the derivation. Delete and regrow its central knot. |
| Last birth may specifically be an implied two-place tie | **6 holders, 11 distinctions** | Split one meeting of the five-knot all-pairs pattern through the new tie. |
| Fewest initial distinctions | **1 initial knot with 4 distinctions** | It grows the 16-knot four-label subset structure. |

A nine-distinction positive pattern must be the six-knot three-against-three case. After deleting any of its knots, each of the two remaining knots on that side meets all three proposed parents. The three residual pairs are each owed a distinction at their two parents, so the one loose distinction per parent is insufficient and the round stalls. This eliminates the only nine-distinction candidate. Doubling a meeting away from a valid final knot preserves the five-holder witness. Doubling a meeting at the proposed last knot prevents the single birth. The [size proofs and explicit cases](derivations.md) give the sharp three-place and two-place bounds separately.

With $k$ leaves around a spent knot and $k-1$ loose distinctions per leaf, ordinary parity growth produces exactly the subsets of $k$ labels, with two holders sharing when they differ by one label (the literature's hypercube). For $k=3$, all eight knots close and no one-odd operator reading exists. For $k=4$, all 16 close and the four-label structure admits a reading. Every larger $k$ contains the same sixteen as a subpattern. Literal replays at $k=3,4,5$ give 8/12, 16/32 and 32/80 knots/distinctions. A spare at the spent holder gives another growing family, so the same final inputs no longer close the whole stage. Giving a *single initial holder* a spare before it has had children instead makes one additional leaf. We checked both choices, including the resulting six-label control. [Original subset argument](../BOND-CLOSURE-20261120-001/bond_radius.md) · [Literal replays](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/growth_histories.json)

The sampled comparison used four independent uniform labelled trees at each of sizes 4, 5 and 6, with 16, 125 and 1,296 possible labelled tree words respectively. Each holder received one extra loose distinction independently with probability 1/4 above its arity-three minimum. Every start was lawful under both laws. Of all 12 samples, 5 funded and 7 stalled under each law. Within three formation steps parity closed 2/12, both at operator-negative patterns, and 3/12 were still growing. Not-all-equal closed 0/12, with 5/12 still growing. All three archived explosive starts, weighted at one third each as a separate stress panel, continued under both laws throughout those three steps. Their birth counts were (8,12,15), (10,16,26) and (15,27,56), with the last source previously proved to have at least exponentially many births under parity. [Seven-knot exponential certificate](../HEAVY-GROWTH-20261119-001/pure.md) No source met a size cap. The 12 constructed subset controls have a separate denominator. Nine closed under parity and none under not-all-equal *(R1: over limits of two to six steps; at the common three-step limit 3/12 closed under parity and 0/12 under not-all-equal)*. These comparisons do not estimate a universal frequency or an infinite-horizon frequency.

A separate singleton stress replay used the six-knot source chosen for its recorded jump from 386 parity births at step seven to 28,065 at step eight. All six initial local rules passed under each law. The first three funded parent steps produced **10, 16 and 27 births under both laws**, leaving 59 holders and 227 distinctions with openings after the third step. This reproduces its early parity counts and applies the same test under not-all-equal. Its large later jump is prior evidence; the growth rate at unlimited step count is a separate question. [Supplemental freeze](supplemental_stress_freeze.md) · [Literal replay](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/supplemental_stress.json)


## A non-signalling table that no quantum state produces

Use the eight closed knots arising from three labels. Give Alice the four subsets of even size and Bob the four of odd size. The uniform sharing promise gives **12** ordered setting pairs, each sharing exactly one distinction. For each meeting, assign 1/8 to each of the eight compatible ordered triples and zero to the other 56 *(R1: ordered pairs of answer triples, and the equal weighting is supplied; weights (3, 1, 1, 3)/16 within each shared-bit value keep the same local marginals)*. Each full local triple is uniform on its four legal words whatever the other reader receives. Thus the change in the full record is **zero in both directions**. Alternatively sample the two settings independently: four of the 16 pairs share nothing. Give these 16 compatible output pairs probability 1/16 each. All 16 input pairs are counted and the same marginal conclusion holds. Weighting the compatible pairs differently can change the marginals. [Both tables](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json)

**Neither version can come from any fixed quantum state with local measurements.** Each distinction occurs in exactly one Alice and one Bob input. Perfect agreement transfers each bit operator between readers on their common preparation. All the signed products would then hold for the same family of operators. Label two four-knot cycles plus their four matched meetings; on either cycle the ordered product of the four matched operators equals the product of that cycle's four signs, by successive cancellation. The same ordered product would be both +I and −I. This argument uses only the twelve actual meeting pairs. It therefore rules out the full independent-setting completion as well. It concerns an exact perfect table and supplies no value for the best imperfect quantum score. [Local measurement argument and explicit cancellation](derivations.md#why-the-eight-knot-table-has-no-quantum-realization)

The input roles matter. For four mutually meeting knots, let *either* reader receive *any* knot and test ordered distinct pairs only. The same uniform allowed-and-agree prescription admits a classical realization: 32 equally weighted local instruction lists reproduce the exact twelve tables. Requiring the two readers to return the same full word when they receive the same knot removes this realization, and the synchronized requirements are quantum-impossible. Hence a conclusion about the operators of the underlying structure needs a matching argument about the actual questions asked. [Full four-knot control](../../artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json)

| Scope | Verdict | Why |
|---|---|---|
| This attempt — rules with no joint state | **Status: Successful** | Census complete, both reader tables settled |
| Local direction — ordinary parity closure | Exact criterion | Reachability from an open lawful start |
| Broader exploration — G17 meeting patterns | Known alternatives | Equal local marginals can accompany either operator verdict |
| G18 Comparing growth laws | Capability gained | Ordinary parity produces qualifying holdings |
| G4 Emergence lives in Fano pieces and knots | Scope distinguished | Literal Fano pieces require a third holding |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Independent check of the reaching rule and the negative game | 2/3 — Substantial | 3/3 — Ready | Reconstruct the 12-knot example and ordered products → reproduce or refute | Selected · awaiting go-ahead |
| 2 | Derive a rule for operator values from ordinary holdings | 2/3 — Substantial | 1/3 — Exploratory | Specify a native outcome rule on five knots → compare its complete setting table | Alternative · deferred |

The independent check addresses the size claim and the operator bridge with finite witnesses and explicit reductions. The second direction targets the crucial G18 gap but has no proposed ordinary operation assigning operators, preparations or weights.

**Corrections:** None to an earlier result. The pencil claim about the four-leaf family holds. Nine distinctions minimize the static positive example and do not minimize its knot count.

**Goals:** G18 gains an exact possibility with supplied quantum values and a reachability condition. G17 gains named control denominators. G4's marker has a different holding count.

**Assumptions:** Connected finite sources, arity and reachability conventions, tensor measurements and specified weightings are declared in the frozen design.

**Scaffolds:** The odd rule, supplied operators and preparation, fixed reader roles, synchrony, setting and answer weightings, built starts and the three-step observation were tested against the listed alternatives.

**Basket:** Independent referee pending. The production of an odd requirement and its operator reading by the ordinary law remains open.

The model supplies the holdings and the even closing rule. The signed contradiction requires giving up one joint state for the whole. Each separate parity rule, every proper part's scalar coexistence and each shared distinction's identity remain. The supplied quantum reading can retain perfect agreement and complete local marginals. The ordinary model still lacks a mechanism giving these measurements or their probabilities.
