# The ruler on balanced weaves

Epic `RULER-FLAT-20261111-001` (RULER-20261111-001 direction 1; G1, question 9; program topology, group spacing), 2026-11-11, at the
coordinator's go-ahead under the owner's standing mandate. Statement frozen in commit be062a849 before the proof was written. The
canonical K1–K3 test is unchanged.

## Words

The owner's rule of 2026-11-11 and the guide's glossary (`publication/knotlab/INTUITIONS.md`, "Words for space"): the program is
building space, so spatial words are not literal yet. This note names its objects by distinctions, knots and counts, and gives each
classical name once, as the drawn picture or the literature's term; the proof keeps the literature's terms.
- A **two-fold weave** has every co-knotted pair in exactly two knots and the knots at each distinction in one cycle (literature: a
  closed triangulated surface); it is **balanced** when every distinction lies in six knots (literature: flat). The **open balanced
  weave** is the infinite one with no loops (drawn: the triangular lattice, the plane).
- A **loop** is a cycle of co-knotted pairs that no patch of knots fills; the **loop length** is the least length of a loop
  (literature: edge-width).
- A closed balanced weave is **two-sided** when every knot can be given a turning order such that each pair is turned one way by one
  of its knots and the other way by the other (then it is a one-pair weave; drawn: a torus), **one-sided** otherwise (drawn: a Klein
  bottle). It is **directed** when every co-knotted pair can be given a direction that makes each knot a directed cycle: every
  two-sided weave is, and half of the one-sided ones (drawn: a Klein bottle whose glide mirror is parallel to a lattice edge; the
  literature's term here is "edge glide").
- The **height** of a not-all-equal state rises by one along a directed pair whose two values differ and falls by two along one whose
  values are equal; around a loop of a closed weave it gains a fixed amount, its **winding**.

## The question

- **Where it comes from.** In the open balanced weave the not-all-equal knot (NAE) sets bond distance equal to graph distance + 1
  at every distance (`RULER-20261111-001`, proved). On closed balanced weaves it was computed: faithful at loop length at least 5,
  equal to distance 3 on two-sided weaves of loop length at least 6, with shortcuts on thinner ones (`LONG-LOOP-20261111-001`).
- **The question.** Prove a range for the ruler on closed balanced weaves, or find the first counterexample.

## The question in standard terms

For the ground states of the triangular Ising antiferromagnet on a 6-regular triangulation of the torus or Klein bottle, describe the
minimal non-shattered vertex sets, and the smallest one containing two vertices at graph distance d.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The invariant: the margin of the best winding.** On a two-sided weave a state's height winds by a fixed amount around each loop; the allowed windings are exactly the slopes satisfying three inequalities (Lemma T0). The margin M is the largest, over allowed windings, of the least extra cost D(0, ℓ) − τ(ℓ) of going once around a loop. It is a multiple of 3 and at most 3/2 the loop length; on 62% of the two-sided weaves to 80 distinctions it is 3/2 the loop length rounded down to a multiple of 3. | proved; computed exactly on every two-sided weave to 96 | A |
| 2 | **States exist exactly when M ≥ 0** (T1 with Lemma T1). Every two-sided weave of loop length at least 2 to 96 distinctions has M ≥ 0, so all of them have states. | proved; the second sentence computed | A |
| 3 | **The lower bound (T2):** β ≥ min(δ, M/3) + 1. A bond either winds around a loop, costing at least M/3 + 2 distinctions, or unwinds to a bond of the open weave, costing δ + 2. | proved; checked on every two-sided weave to 96 (every distance-3 shortcut has M ≤ 6) | A |
| 4 | **The ruler (T3):** β = δ + 1 whenever δ < M/3; the open weave's least bond (one side of a knot-shaped patch of side δ with its opposite corner; drawn: a triangle of side δ) carries over. | proved; checked at distances 2 and 3 on every faithful two-sided weave to 96 | A |
| 5 | **Faithful (T4):** a two-sided weave with M > 3 is read faithfully; nothing is frozen and no two distinctions are tied already when M ≥ 3. | proved; checked on all 1,698 such worlds with M > 3 to 96 | A |
| 6 | **Directed one-sided weaves: the same theorem.** When the pairs can be directed so that every knot is a directed cycle, the twist keeps the height's direction of climb, heights shift by a constant under it as around any loop, and T1 to T4 hold word for word with the margin taken over every way around (Theorem K; Lemma K0 reads the condition from the knots). | proved; checked on every such weave with 12 to 48 distinctions (53 up to isomorphism) | A |
| 7 | **Undirected one-sided weaves: not proved.** There the twist reverses the direction of climb and heights flip under it (h ∘ g = κ − h). The extension lemma the pre-registration named is false as phrased; a version with flip-symmetric data heights was sketched by the referee but gives no reading at distance yet. They stay computed. | the gap | A |

**Only for balanced weaves.** Every result here, like those of `RULER-20261111-001` and `LONG-LOOP-20261111-001`, assumes that each
co-knotted pair lies in exactly two knots and each distinction's knots form one ring of six: the height that drives the proofs exists
only there. Where pairs lie in one knot or in three or more, the line knows only this much. NAE still reads some such bases
faithfully: 160 made from balanced weaves by swapping knots (`NAE-SURFACE-20261111-001`) and bases grown with pairs in three knots
(`GROW-COUNT-20261111-001`). But faithfulness falls with each extra defect, none of 1,440 random regular bases was read faithfully,
and where every pair lies in exactly one knot (a Steiner triple system in the literature) NAE has no state at all, since no Steiner
triple system on 7 or more points has a 2-colouring without a monochromatic block (known). No ruler and no height is known there.

## Answer

On two-sided balanced weaves the ruler is a theorem with an exact invariant: bond distance is graph distance + 1 for every distance
below a third of the best winding's margin, and at least min(δ, M/3) + 1 always, so shortcuts are possible only where a bond can go
around a loop more cheaply than it can cross the distance. Weaves with margin above 3 are read faithfully, and they have states
exactly when an allowed winding exists. The same holds on the directed one-sided weaves, about half of the one-sided ones. The proved
range is conservative: the computed record has the equality to distance 3 at M = 9. Undirected one-sided weaves are not proved: their
heights flip under the twist, and the missing piece is an extension lemma that respects the flip.

## Reading

**Interpretation, not a theorem.**
- **Why loops matter.** A constraint between two distinctions can travel two ways: across the distance, as in the open weave, or
  around a loop. The open way costs one distinction per step; the loop's way costs a third of its extra winding cost. The ruler holds
  wherever the first is cheaper, and the shortcuts LONG-LOOP found are the second.
- **The winding is the weave's own.** Every state of a closed weave has a winding, and the margin measures how far the best winding
  keeps loops from being cheap. It is fixed by how the knots meet, so the law reads its weave's shortest loops through it.
- **For question 9.** On a balanced weave of knots alone with long enough loops, the knot law measures distance exactly, as in the
  open weave; the weave's loops show up only as a cutoff at a third of its margin.
- **Direction is what the law sees.** A one-sided weave has a twist. If the pairs can still be directed so that every knot is a
  cycle, the law's heights treat the twist like one more loop; if not, the twist turns heights upside down, and the argument that
  builds a state from a pattern no longer fits. What matters is the direction the law climbs in, not whether the weave is two-sided.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** T0 to T4 for every two-sided balanced weave, and Theorem K for every directed
  one-sided one. **Computed.** The finite checks below; that every two-sided weave to 96 has states; undirected one-sided weaves
  (LONG-LOOP's faithfulness).

## Stress test

The theorems cover every size; `check.py` compares them with every two-sided weave with 12 to 96 distinctions read so far (2,450
readings, including LONG-LOOP's census and its stress test), with brute force on the 136 with 12 to 18 distinctions, and, for directed
one-sided weaves, with brute force on the 60 presentations with 12 to 20 distinctions and new readings of all 53 up to isomorphism
with 12 to 48. Lemma K0 is checked on all 1,665 one-sided presentations with 12 to 48 distinctions (582 directed, all edge glides;
1,083 undirected, all altitude glides). The margin itself was recomputed exactly and compared with an independent wide brute force
on 400 weaves.

## Review

- **First pass** (an independent agent given the proof, the code and the proof for the open weave, with its own brute force). The frozen
  statement T1 to T4 for two-sided weaves (tori) is fully proved: no error in the mathematics and no counterexample. Its findings, all folded in:
  - T1 argued from the empty pattern, which Lemma T2 does not cover; it now uses a one-site pattern.
  - T4's "nothing frozen, no tie" needs only M ≥ 3; noted in the theorem.
  - `check.py` computed M wrongly on 234 weaves (too few windings, too small a box of loop vectors); the margin is now exact and the
    checks were rerun (all pass; four more weaves have M > 3).
  - The pre-registration's note on one-sided weaves was half right: directed ones (edge glides) keep the height's direction of climb
    and the two-sided proof carries over (the referee's criterion matched brute force on 25,200 patterns), while for undirected ones
    (altitude glides) the named extension lemma is false as phrased (52 counterexamples) and holds only with flip-symmetric data
    heights (a sketch, for M_τ > 0). This led to Theorem K and the correction.
- **Second pass** (a fresh agent, on Lemma K1, Theorem K, the section on undirected one-sided weaves and the exact margin in
  `check.py`, with its own construction, state enumeration and tilt enumeration). Theorem K and Lemma K1 proved as written, the
  undirected section claims nothing it does not show, and no false pass in `check.py`. Its fixes, all folded in:
  - the reflection and the margin were both called M; the reflection is now A;
  - Lemma K1's converse lacked the residue line (τ(g) ≡ c(g0) mod 3, from c ∘ A = c); added;
  - "axis along lattice edges" is now "parallel to a lattice edge", and "is not anti-symmetric" is "need not be"; the referee's
    counterexample now names its two distinctions;
  - a mutation dropping the mod-4 condition was added (C12: 18,082 disagreements, so the condition is needed).
  Its own computations agree with the record: the list of directed one-sided presentations to 80 distinctions (1,845), their M, loop
  length and windings; the windings read off the heights of all 29,700 states of the 60 small ones; Lemma T2 per winding on
  1,303,170 patterns; and, beyond the record, T3 at distance 3 on three directed one-sided weaves with M = 12 (64 to 68
  distinctions, every pair: all faithful, every distance-3 pair in a bond of 5 and none of 4). It noted two limits, recorded here:
  C9 measures from one distinction only (its all-pairs runs cover this), and the "no states" side of T1 cannot fail in range, since
  every directed one-sided weave from 12 to 80 distinctions has M ≥ 3.

## Literature and provenance

- **Known.** Quasi-periodic height functions with a slope for periodic tilings and dimers (Kenyon, Okounkov and Sheffield); the
  open weave's extension criterion (`RULER-20261111-001`, with the Kirszbraun-type literature).
- **Classification.** Known-with-delta: the tools are known; the margin and T2 to T4 as statements were not found (bounded search).

## Workspace assumptions

- **Relied on.** A40, A64 (through A63's conditional overturning). **Changed.** None.

## Ratio

- **Substantive.** The proof (T0 to T4, Lemma K0 and Theorem K), its checks (C1 to C12; three runs before the final one, the first
  two exposing bugs in the check), two referee passes.
- **Administrative.** The pre-registration, this note and the closure.

## Corrections

One, to the published pre-registration (logged in `docs/CORRECTIONS.md`, **Not a block**): it said every one-sided weave's heights
flip under the twist (h(gx) = κ − h(x)). That holds only for undirected ones; in directed ones heights shift by a constant, and the
two-sided proof carries over. The error made the one-sided case look harder than it is; corrected, half of it is proved.

Two bugs in the check itself, caught before anything was recorded: the first run's test of allowed windings looked at too few loop
vectors (Lemma T0 made it exact), and the second run's margin was wrong on 234 weaves (too few windings and too small a box of
vectors; found by the referee). The third run computes everything exactly. Recorded in the proof.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the ruler on closed balanced weaves | **Status:** Partially successful | Two-sided and directed one-sided weaves proved with an exact invariant; undirected one-sided weaves not |
| Local direction — NAE's ruler on balanced weaves | Continue | Undirected one-sided weaves need an extension that respects the flip; the exact range is open |
| Broader exploration — G1 on bases of knots alone | Promising pivot available | Everything proved so far needs each co-knotted pair in exactly two knots; the owner's object is unrestricted and infinite: patterns of how knots meet |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The knot law measures balanced weaves exactly below a cutoff fixed by how their knots meet |

**Corrections:** one, Not a block (the pre-registration's note on one-sided weaves). **Goals:** a G1 checkpoint (capability gained),
no goal change. **Assumptions:** none changed.
**Basket:** `GROW-COUNT-20261111-001#2` (the local list of what NAE forbids, 2/3, 2/3), `GROW-COUNT-20261111-001#3` (a note,
1/3, 3/3), `GROW-FACE-20261110-001#1` (2/3, 1/3); taken: none yet; direction 1 below is new and is next.

**Next step:** Research directions — selected: #1 (proposed, not started)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Overlapping bases: what NAE reads where pairs lie in any number of knots | 3/3 — Major | 2/3 — Testable | A census of small bases with no limit on knots per pair, the 160 faithful non-weave bases of B145 and GROW-COUNT's grown bases re-read as objects, and whether the adjacent-apices lemma bounds the overlap a faithful base can carry; infinite periodic patterns next → a faithful base with a pair in three or more knots and its ruler, or none in the frozen family, with what overlap does instead | Selected · go-ahead given (owner, 2026-11-11) |
| 2 | The local list of what NAE forbids (was `GROW-COUNT-20261111-001#2`) | 2/3 — Substantial | 2/3 — Testable | Is faithfulness on balanced weaves exactly "no adjacent apices and margin above 3"? Test on the frozen weaves and small closed ones → a characterization, or a miss | Alternative · deferred |
| 3 | Undirected one-sided weaves: an extension that respects the flip | 1/3 — Modest | 2/3 — Testable | Turn the referee's flip-symmetric extension (M_τ > 0) into a criterion → T2 to T4 there, or a weave where the ruler fails below M/3 | Alternative · deferred |
| 4 | The exact range on balanced weaves | 1/3 — Modest | 2/3 — Testable | Sharpen the bound for bonds that go around a loop (they must also cross the distance) → a range matching the record at M = 9, or a weave where δ = M/3 shortcuts | Alternative · deferred |
| 5 | Write the knots-alone line up as a note (was `GROW-COUNT-20261111-001#3`) | 1/3 — Modest | 3/3 — Ready | Seven epics into one note → a note an expert can check | Alternative · deferred |

1. **Overlapping bases.** Payoff 3: it is the owner's object (2026-11-11: a knot may meet any number of others, and a base is a
   pattern of how knots share distinctions, infinite ones included), and the first test of the knot law beyond two-fold weaves.
   Concreteness 2: the families exist or are enumerable, and the failure line is below; the census code is not yet written.
2. **The local list.** Payoff 2: it would say exactly which balanced weaves the law reads. Concreteness 2.
3. **Undirected one-sided weaves.** Payoff 1: completes the six-around case, most of which is now proved. Concreteness 2.
4. **The exact range.** Payoff 1: a sharper constant. Concreteness 2.
5. **A note.** Payoff 1, concreteness 3.

### The next epic, in outline (its pre-registration freezes the details)

- **Objects.** Finite bases with no limit on how many knots a pair lies in or how many knots a knot meets: every connected base on
  up to a frozen number of distinctions (exhaustive where feasible), the 160 faithful non-weave bases of `NAE-SURFACE-20261111-001`
  and the grown bases of `GROW-COUNT-20261111-001`. Later, infinite bases given by a finite periodic pattern of how knots share
  distinctions (literature: periodic 3-uniform hypergraphs), read between periodic and finite-window bounds with source labels.
- **Failure line, to be frozen.** Prediction from the record (faithfulness falls with each defect): no base in the family in which
  some co-knotted pair lies in three or more knots is read faithfully by NAE beyond a frozen size. A faithful one refutes it, and
  its bond distances and ball growth are then read.
- **Measured.** How faithfulness fails on overlapping bases (frozen, ties, knots that are not bonds, triples bound that no knot
  names), and whether the adjacent-apices lemma (`GROW-COUNT-20261111-001`) bounds the overlap a faithful base can carry.
- **Not here.** What overlapping bases compute belongs to the learning line, restarted on that question.

**Recommendation.** Research directions, #1, a pivot toward the owner's unrestricted object; the owner gave the go-ahead on
2026-11-11, to start once this epic is closed and reported.

## Final report as sent

Sent to the owner on 2026-11-11 at 19:38 UTC and copied here verbatim.

**The ruler on balanced weaves is proved.** Take a closed base in which every co-knotted pair lies in exactly two knots and every distinction in six (drawn: a torus). There, one number decides how not-all-equal reads it: M, the least extra cost of a state's height going once around a loop.

- **States** exist exactly when M ≥ 0.
- **Bond distance** is never below min(δ, M/3) + 1, and it equals graph distance + 1 whenever δ < M/3. A bond can only cheat by going around a loop.
- **Faithful** whenever M > 3.
- **One-sided weaves split in two** (drawn: Klein bottles). If the pairs can be directed so that every knot is a directed cycle, the same theorem holds word for word. If not, heights flip under the twist, and that half stays computed.

Two referees passed it after fixes, and every check passes: two-sided weaves to 96 distinctions, directed one-sided ones to 48.

**Only for two-fold weaves.** All of this needs each co-knotted pair in exactly two knots, because the height only exists there. Beyond that the line knows very little. NAE does read 160 swap-made bases faithfully, and some grown ones with pairs in three knots. But none of 1,440 random regular bases was read faithfully, and where every pair lies in one knot (a Steiner triple system) there is no state at all. Overlap has no ruler and no height yet.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the ruler on closed balanced weaves | **Status:** Partially successful | Two-sided and directed one-sided proved; undirected one-sided not |
| Local direction — NAE's ruler on two-fold weaves | Continue | The undirected half and the exact range remain |
| Broader exploration — G1 on bases of knots alone | Promising pivot available | Everything proved needs two knots per pair; overlapping bases are untested |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The law measures balanced weaves exactly below a cutoff set by how their knots meet |

**Corrections:** one, Not a block. My pre-registration said heights flip under every one-sided twist, but only the undirected ones do. **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** none changed.
**Basket:** the local list of what NAE forbids (2/3, 2/3), bond balls read dimension 2 (2/3, 2/3), other laws (2/3, 2/3); none taken. Direction 1 is new.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Overlapping bases: pairs in any number of knots | 3/3 — Major | 2/3 — Testable | Census of small bases with no limit on knots per pair, plus B145's 160 bases and GROW-COUNT's re-read as objects → a faithful base with a pair in three or more knots and its ruler, or none in the frozen family | Selected · go-ahead given |
| 2 | The local list of what NAE forbids | 2/3 — Substantial | 2/3 — Testable | Is faithfulness on balanced weaves exactly "no adjacent apices, M > 3"? → a characterization, or a miss | Alternative · deferred |
| 3 | The undirected one-sided weaves | 1/3 — Modest | 2/3 — Testable | Turn the referee's flip-symmetric extension into a criterion → T2 to T4 there, or a failure | Alternative · deferred |

It's committed and published ([decision note](https://github.com/jscul/knotlab/blob/main/research/RULER-FLAT-20261111-001/ruler_flat.md)). With your go-ahead I'm starting the overlapping-bases epic now, with its pre-registration and a prior-work check first.
