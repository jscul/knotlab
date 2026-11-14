# READ-RULE independent recomputation and critique

**Verdict: Confirmed with fixes.** Theorems R and R1 are sound. The
unconditional **per-residue** dichotomy survives an explicit repair of its
interfaces and its member-counting argument. The literal syntactic converse
is refuted by a new family given in section 6; that family satisfies R's
exception and does not refute R or the dichotomy.

All scientific outputs are confined to this referee directory. No network,
Git mutation, publication, or lifecycle change was used. No Python under
either prohibited READ directory was opened or imported. READ-specific code
is fresh; the expressly permitted earlier referee's exact SAT search,
usual-limit semantics, and window reconstruction are reused and identified
in the manifests. This is same-task AI recomputation/review, without external
replication. Finite computations and symbolic arguments are distinguished.

## 1. The dichotomy: interfaces, attacks, constants, and effectivity

**Not a block — necessary proof repairs.** The written argument has two
defects, both repairable without rectangularity:

- The product from c_a to c_b covers source blocks c_a,...,c_{b-1}, whereas
  the stipulated unoccupied stretch is c_{a+1},...,c_b. Replace it by the
  product over **source blocks c_{a+1},...,c_b**, with top interface
  **ports(c_{a+1})** and bottom interface **ports(c_{b+1})**. Keep c_a's
  entire block and its selected own members in the upper context.
- Count a selected identity at its **unique allocating copy**, or in that
  copy's off-word side subtrees, rather than at every block where it appears
  as a carried port. Otherwise one root member occupies arbitrarily many
  levels, invalidating the counting inequality. An independently checked
  synthetic 3-bond at depth 20 with m=2 demonstrates that literal failure.

The corrected factorisation is exact. Every side subtree of a replaced
source block is represented by its exact usual-limit port relation. A
selected identity inherited into it stays an interface coordinate; only
unselected allocations are quantified. Preserve the carry map of **all**
top ports, including ancestor-owned non-main identities. Upper context,
interval relation, and full lower subtree then compose to exactly the same
selected-coordinate relation after pumping. Interface proxies equal to
selected coordinates must retain that equality, rather than quantifying
the selected coordinate away.

Move the retained lower subtree by an injective renaming, preserving its
overlap with upper identities through the carry map. Equality of the full
selected relation implies equal projections on **every subset**, so the
moved set remains a bond. Its target is still an own distinction of a
covered S copy. Inserting Pi/ell **additional** copies of a repeated
S-call word of length ell increases both S-call length and absolute target
depth by Pi; the wrapper offset stays fixed. All 5,964 study keys have
distinct arguments in every call, so the census needs only partial-injection
carry maps. Repeated-argument extensions should track a complete interface
identity partition, with their state count stated separately.

For counting, let n=d-delta, delta in {0,1}, and let t of the n pre-target
allocation collections be occupied. If no empty run exceeds m,
`n <= (m+1)t+m` and `t <= |W|-2`, since the main port and target-own
identity are distinct and outside those collections. This gives a lower
bound stronger than the advertised `d/(m+1)-1`, including wrappers. If any
long-gap bond exists at d_0, its size C instead bounds L at every later
depth in that residue modulo Pi=m!. Set L=+infinity where no bond exists;
no least bond is needed at those depths. Full argument:
[pumping_proof_audit.md](pumping_proof_audit.md).

**Adversarial recomputation.** No sublinear-unbounded counterexample was
found. Relation-free global minima for each of the two simple growers
`a43ab6412097` and `46540117e841` at absolute depths 7,8,10,12 are
**6,7,8,9**. The wrapper `4dc882a6a1d7` gives **6,6** at depths 7,8
(S-call lengths 6,7). Globality uses the permitted two-blank separation
argument to bound every smaller support's depth, not a moving window.
Six other deep wrapper cells timed out and remain unknown. Four slow-looking
unresolved families were searched at depths 2–6: nineteen minima of 4 are
exact only within the explicitly unfolded member universe; the remaining
cell has global minimum 3. None of those nineteen is reported as a global
minimum or an asymptotic result.

Hand attempts also fail to evade pumping. A repeatable stall admits a
bounded witness; a fixed long delay produces a small positive linear rate
(the arity-eight illustration is explicitly outside the ternary claim).
Putting members at square-number or exponentially sparse levels eventually
creates a long allocation-empty interval. Its first witness already pumps
to a constant bound throughout its later residue, contradicting unbounded
growth of the minimum. Side-subtree placement and non-main identity carriage
are covered by the corrected factorisation. Exact controls compare all
subset projections before/after pumping, including side members and a
non-main carried member.

Freshly enumerated monoids give the following explicit constants. Counts
include the empty word; products are Boolean port relations and carry maps
track all three source ports. Full keys and all eleven samples are in
[pumping_results.json](pumping_results.json).

| Family prefix | Distinct products | Carry maps | Reachable pairs m | Pi=m! | Linear constant |
| --- | ---: | ---: | ---: | --- | --- |
| `a43ab6412097` | 5 | 3 | 5 | 120 | 1/6 |
| `a430c16bc410` (wrapper) | 5 | 3 | 5 | 120 | 1/6 |
| `bc22e10bb149` | 3 | 2 | 3 | 6 | 1/4 |
| `9d46d50f19d1` | 4 | 2 | 4 | 24 | 1/5 |
| `e35d907e41c9` | 588 | 8 | 596 | 596! | 1/597 |
| `277e4af88ffd` (wrapper) | 2,799 | 23 | 3,173 | 3173! | 1/3174 |
| `ce444059ece1` | 5,709 | 14 | 5,709 | 5709! | 1/5710 |
| `432127c418b0` (wrapper) | 29,359 | 14 | 29,359 | 29359! | 1/29360 |

**Narrowing — effectivity and threshold.** A long-gap witness W at d_0
supplies the explicit threshold d_0 and bound C=|W|. The sufficient numerical
trigger `|W| < d_0/(m+1)-1`, equivalently `d_0>(m+1)(C+1)`, forces such a
gap. For the synthetic m=2, Pi=2, C=3 family, depths 13 and 14 are sufficient
seeds for the two residues, giving bound 3 thereafter. The monoid, period,
and constant are effective. Enumerating finite supports and checking exact
projections semi-decides boundedness on a residue and finds a threshold
under a promise of eventual boundedness. The proof supplies **no decision
procedure or finite growth test**, no advance onset bound from an arbitrary
C alone, and no ultimate periodicity of L's values. This is not a theorem
that the underlying decision problem is undecidable.

**Not a block — known mathematics in kind, novelty unverified.** From memory,
without network verification: repetition of prefix states is standard finite
monoid pumping. Classical tropical/min-plus cyclicity theorems can give
stronger eventual affine periodic behavior under their hypotheses, but this
work has not represented minimal non-shattering as a fixed additive-cost
matrix problem. The specific work here is the identity-sensitive
finite-support factorisation and allocation count, rather than a new
pumping principle. For contrast, a distance automaton can realise
`f(a^{n1} b ... b a^{nk})=min(k,min_i n_i)`. Its maximum over length-N words
is the greatest t with `t^2+t-1<=N`, hence grows like sqrt(N); its minimum is
1. This illustrates why max-over-words sublinear growth does not contradict
READ's minimum over target words/supports. It is a derived example here,
not a verified literature attribution.

## 2. Theorem R: exact exception and correct quantifier

The local equivalence passes exhaustively. A positive NAE triple has three
antipodal pairs of allowed assignments; their **seven nonempty unions**
exhaust all living complement-closed context projections on {p,x,z}. A
generic enumerator of all minimal non-shattered subsets finds a bond inside
W through p,x exactly when the stated exception fails. Precisely two of
the seven projections are exceptions: {p,x} is free and z is opposite to
one of them. Opposite to both instead ties p to x. All three nonempty
complement-closed pair contexts for the pendant case also pass; z=p gives
the separate 2-bond case. Dead relations are rejected.

The relation-free CNF audit checks **all nine exception families and twenty
nonexceptions**, totalling **919 concrete Q states and 1,996 eligible
readings**. The nine alone account for 899 states and 1,956 readings.
Every tested triple agrees with the local equivalence. Other bonds of size
3 are independently found and deletion-checked in **all twenty repeating
Q phases of the nine exceptions**. These establish L<=3 on every large
depth; they do not assert that the exceptional triple itself is a bond.

**Not a block — complete the coverage count.** The theorem needs
`for every repeating exact-depth Q phase, there exists an eligible carried
state and a surviving reading`. It does not require one candidate to
survive every eligible carried state. Pooling several Q phases and finding
one survivor somewhere would also be insufficient in general.

| Every-large-depth R coverage, window-bounded in-scope population | Families / 5,067 | Draw weight / 5,129 | Weight share |
| --- | ---: | ---: | ---: |
| Stricter every eligible carried-state reading | 4,479 | 4,486 | 87.463443% |
| Correct some-state reading in every exact Q phase | **4,484** | **4,491** | **87.560928%** |

The published 87.5% is a valid rounded lower bound. Correct coverage rounds
to **87.6%**. The five additional weight-one families are `5dd5ab5a117eb660`,
`52997167e985b8f4`, `7ecf57750d7d2775`, `63577d9cf381049f`, and
`39f7b334062ac725`; each has a direct surviving witness in every phase.
They resolve the five quantifier ambiguities. Exactly nine exception-only
families remain, with **68 capped cases unknown**, rather than 73 cases
including five unresolved quantifiers. No R gate violation was found.
See [coverage_report.md](coverage_report.md) and
[coverage_reconciliation.json](coverage_reconciliation.json).

**Narrowing — exactness is local to W.** The exception characterises failure
to find the p,x bond **inside that triple**. It is not an iff criterion for
L>3, as the nine alternative-bond certificates demonstrate.

## 3. Theorem R1 and the 469/471 reconciliation

R1's proof is sound: if z is own, in no other constraint and in no call
argument, its value can be chosen independently subject only to the
displayed NAE. The triple projection is exactly P(p,x) conjoined with NAE.
The three nonempty complement-closed P cases give either the tied p,x pair
or the full six-state NAE triple as a bond.

The fresh syntax check retains finite helper-call arguments before
flattening, as well as recursive-call arguments. A pendant-looking
constraint after flattening cannot erase the frozen no-call guard. Candidate
rosters, carried sequences, and R1 flags agree on **all 5,964 families**.

**Not a block — denominators differ.** There are **471** R1-covered
in-scope families on every residue, of which **469** belong to the original
5,067 window-bounded population. Thus coverage is **9.255970% of bounded
families**, or **469/5,129 = 9.1440827% of bounded draw weight**. The other
two, `d5ac8dc038ae968e` and `ce083ff8262fab67`, were stratum-I/undecided
with capped Q windows and inherited caps. Their syntax still proves the
bound; they were not members of the frozen window-bounded denominator.

## 4. Q3's proposed counterexample

Confirmed: both variants have **L(s)=2 at every depth 1–6**, by independent
direct exact search. Explicit witnesses are the main a and the target's
own u; their projection is exactly {01,10}, while both singletons are full.
This is a global minimum, since complement closure rules out singleton
bonds anywhere. The repeated-argument constraint and the four-positive-NAE
gadget both enforce u!=a, as separately enumerated. The same two-member
argument works at every depth, beyond the finite checks.

**Not a block — the failed prediction is already correctly rejected.** The
gadget itself creates the forbidden short bond. No proposed growth survives.
The free a/x pair and a nonminimal supersupport containing the tie reject
as controls. Evidence: [q3_results.json](q3_results.json).

## 5. The study Codex's five ambiguities

| Ambiguity | Referee judgment and required reading |
| --- | --- |
| 1. Which states for R? | **Not a block.** Use some state where the position is carried by identity, in every repeating exact Q phase. Uncarried states cannot instantiate the hypothesis. Universal carried-state survival is sufficient but unnecessarily strong. |
| 2. Which exception quantifier for Q1? | **Not a block.** Exception-only requires eligible readings to exist and **every eligible reading in every available carried state** to be killed on that phase. A bad state for each candidate is insufficient if any good state remains. This resolves five cases positively; nine exact exceptions and 68 capped unknowns remain. |
| 3. 83 versus 90 undecided? | **Not a block.** Ninety is the original window-stage count; 83 is the later headline after seven path-DP rescues. CARRY's note also preserves stricter/full cap-admission counts of 85/81. Label the evidence stage and admission rule; no theorem needs an invented unspecified roster of 83. |
| 4. What does the product cap count? | **Not a block.** The mathematics needs relation/carry pairs because conditional slices depend on identity carriage. An operational cap must state whether it counts those stored pairs or distinct Boolean relations. The frozen wording did not decide this; keep the one disputed family capped instead of retroactively selecting a convention. Either outcome leaves Q2 far below 90%. |
| 5. Which families have the counterexample's shape? | **Narrowing.** No formal matching predicate was supplied, so no descriptive census count follows. Report only explicit keys and tested predicates. Q3's given shape in fact supplies a size-two bond. |

## 6. Wording, scope, and a new converse counterexample

**Narrowing — per residue and weak rate.** Replace “two speeds only” and
“nothing grows slowly” by: **On each residue modulo a computable period,
L is eventually bounded or has a positive linear lower bound.** Different
residues may take different branches. This is a lower bound, not an exact
growth rate or a claim of uniform linear speed; m can be very large.

**Not a block — distinguish the frozen and proved statements.** The frozen
dichotomy assumed conditional rectangularity. The repaired pumping theorem
is a post-registration generalisation that removes that hypothesis. Its
proof is separate from the census. The frozen finite-local-state decision
claim and ultimate-periodicity wording are not proved by this argument.
Remove the Reading's proposed “finite growth test” unless a decision
procedure is supplied; absence of a long-gap certificate has not been made
decidable here.

**Narrowing — “No family is known” needs a definition of effective reading.**
The literal syntactic converse is false in the same covered-target setup.
Take

    S(a,b,c), own x,w:
      NAE(a,x,b), NAE(c,x,w), SELF(a,b,x).

Let main have ports p,q,r, force p!=q **entirely in the wrapper**, and call
S(p,q,r). A positive distinct-argument implementation uses wrapper-own e,f,g
and

    NAE(p,q,e), NAE(p,q,f), NAE(p,q,g), NAE(e,f,g).

The last four constraints enforce p!=q. Persistent p and q occur with
own x in a reading constraint at every S copy, but NAE(p,x_i,q) is always
true. The remaining component is

    NAE(r,x_0,w_0), NAE(x_0,x_1,w_1), ... .

For **absolute depth d>=1**, including the wrapper, **L(d)=d+2**. A witness
is `{r,w_0,...,w_{d-1},x_{d-1}}`. It excludes the two complementary forced
alternating assignments and shatters every proper subset. Conversely,
omitting any earlier pendant w_j existentially erases its constraint and
separates root from target; every bond must include all those pendants.
For target w_{d-1}, the mandatory d+1-member set is itself shattered, so
one additional member is necessary. The wrapper component is independent
and cannot supply a smaller mixed bond. This argument permits arbitrary
members below the target and both own target choices.

Direct exact searches give **3,4,5,6,7,8** at depths 1–6 for both wrapper
variants, with all smaller supports excluded and explicit witnesses checked
separately. The positive variant has key prefix `8b467690607dc017` and
distinct arguments throughout. Full key, proof, and data are in
[growth_hand_read_exception_argument.md](growth_hand_read_exception_argument.md)
and [growth_hand_read_exception_results.json](growth_hand_read_exception_results.json).
This is a new hand family, not a change to the census counts. All its
persistent readings satisfy R's exact exception. If “effectively read”
means exception-free reading, R already excludes growth on that residue;
if it means the defined syntactic reading, this construction refutes the
claimed necessity. Leaving “effectively” undefined obscures that distinction.

**Narrowing — scope throughout.** Every R/R1 bound and the pumping conclusion
concerns an own target of **S reached through S calls**. Other recursive
definitions' own targets remain outside these conclusions. A global minimum
over covered targets does not classify every individual bond or every
target. These are usual-limit finite-coordinate bond results; they do not
establish an additional finite-change source theorem for infinite native
knots.

## Files written and validation

The main deliverable is this file. Detailed proof and constants:
`pumping_proof_audit.md`, `pumping_audit.py`, `pumping_results.json`.
The `coverage_*` scripts/data/report/manifests contain the full independent
census and direct controls. The `growth_*` scripts/data/report/manifests
contain global and finite-prefix searches, retained timeouts, hand attempts,
and the new counterexample. `q3_audit.py` and `q3_results.json` contain the
two Q3 recomputations. `referee_validate.py`, `referee_validation.json`, and
`referee_manifest.json` provide final reconciliation, a separate finite
chain-relation check, and the complete file/hash inventory.

The longest completed census command took about six minutes; all commands
stayed below fifteen minutes. Computational lanes used the requested
workspace Python with `-B`, bounded memory, and no more than three concurrent
computations. JSON/JSONL parsing, Python AST parsing, input/script hashes,
cross-output count reconciliation, and targeted mathematical controls pass.
No whole-repository test suite was run. Timeouts and finite-member-universe
limits remain explicit; no finite computation is substituted for the uniform
pumping or pendant arguments.
