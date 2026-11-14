**Verdict:** a full proof for every n in two hours is unlikely. I could not prove rigidity by hand, but two hours is enough to find out whether a uniform proof exists, and I'd spend it on route A below.

## What I checked by hand
- `A = q1q1 x` has `A1 = x1`, `A2 = x2`, `Ai = xi + x(i-2) + 1`, and your three XOR facts hold.
- Parities, with `s = x(n-1) + xn`: `p(A) = s + n`, `p(q2q0 x) = s + n + 1`, and `p(q0 x) = xn + n + 1` except at `x = 0^n` and `0^(n-1)1`. The exceptional cases sit at the short tails, consistent with your two bad knots.
- So every knot contains a structurally opposite pair plus a third point: `{A, q2q0x}` in placement 1, `{A, A+e2}` in placement 2, `{A+e1+e2, q2q0x}` in placement 3. The third point picks the apex.
- In placement 2 the apex is `A` when `x(n-1) = 0` and `A+e2` when `x(n-1) = 1`.
- Flipping `A2` flips every even letter of `x`. So the two placement-2 knots over the pair `{A, A+e2}` have different apexes when n is odd and the same apex when n is even.

## (2) Linear algebra: no, not generically
The constraint allows (0,1,0), (1,0,0), (1,1,1), and their sum (0,0,1) is forbidden, so the relation is not affine. It is NAE with one negated place, which has no useful closure operation. Any proof must use the automaton.

A cleaner statement of rigidity: each knot says "the apex agrees with at least one base". Rigidity then means no proper non-empty set S such that both S and its complement are closed under "both bases in ⇒ apex in". Your finding (i) says one-sided closed sets are plentiful, so any refutation must branch.

## (4) The obstruction
- "Unique NAE solution up to complement" has no generic short certificate.
- Propagation is inert until two values are fixed.
- The drop-last-letter map does not carry solutions down, so there is no obvious inductive hypothesis.
- The prefix route fails too: sections of the three placements leave the placement set (the section of `q1q1` at 0 is `q2q2`), and a knot's members can start with different letters. After k letters you are coupling 2^k functions.

## Route A (most promising): measure the branching depth, then make it automatic
1. Look at the LRAT sizes you already have for n = 7..14. Polynomial growth means a uniform bounded-depth proof probably exists. Roughly doubling per level means stop.
2. Fix `g(u) = 0`, `g(v) = 1` for pairs differing by `e2`, and by `e1` and `en`. Record whether unit propagation refutes it, or depth-1 or depth-2 failed-literal probing does, and at which addresses.
3. If depth ≤ 2 suffices at every n with addresses that are regular in n, the certificate is automatic relations `Eq_k(u,v)` ("forced equal at stage k"), with closure and totality checked by a product automaton, as for the parity state.

The natural first lemma is "no e2-defect": `g(A) = g(A+e2)` for all `A`. A defect at `{A, A+e2}` turns placement-2 knots into unit equalities: at odd n it forces `g(A) = g(q0 x_A)` and `g(A+e2) = g(q0 x')`; at even n it forces only one side. That gives a concrete parity-of-n asymmetry to test.

Once defects are excluded, placement 2 vanishes and g lives on words modulo letter 2. Test whether placements 1 and 3 alone are rigid on that quotient. If they are, and by propagation, the proof splits into two lemmas, each an automaton check.

## Route B: induction n → n+2 through the tail
Write `f(x.ab)` as four functions on level n. The knots over a level-n triple differ only by the last-letter twists, which the final states determine.

- **Tail lemma:** `f(x.ab) = f(x.00) + a + b`. Test it at small n by asking the solver which tail pairs it forces first.
- If it holds, `F = f(·.00)` solves a level-n system with twists read from a finite state. I checked that the twists are not trivial: tail parities differ between members and depend on letters n-3..n.
- The induction therefore needs a strengthened hypothesis: rigidity, or death, of each member of a finite family of twisted patterns. Enumerate that family at n = 5..9 and check each. If the family closes under the two-letter step, this is your product-automaton certificate.

The risk is that the tail lemma is as hard as the theorem. The four knots `K1(1^(n-3)0ab) = {x, x+en, q2q0x}` are the only ones I found that tie tail pairs directly.

## Route C: connectivity
Rigidity is equivalent to the forced-equality graph being connected. If route A yields forced invariances under a few moves (`e2`, `x → q0x`, …), finish by showing those moves act transitively on the level. That is a group fact about the automaton, checkable per level and plausibly provable by sections.

## Stop rule
If step 1 shows exponential LRAT growth and step 2 needs probing depth that grows with n, record rigidity as computed for n ≤ 14 and conjectured beyond. Then only the twisted-family check in route B is still worth running.
