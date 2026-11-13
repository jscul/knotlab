# Mathematical review of the ray-DP rate claims

**Standard statement.** Let a finite directed weighted DP graph have nonnegative integer start, transition and accepting-closing costs. The minimum cost at depth `s` uses exactly `n = s - 1` middle transitions. Let `T` be its complete reachable, acceptance-co-reachable state set, and `t = |T|`. When `T` contains a cycle, its minimum cycle mean `lambda` satisfies

\[
L(s)\geq\lambda(s-t),\qquad
\liminf_{s\to\infty}L(s)/s=\lambda.
\]

Here `L(s) = +infinity` when there is no accepting walk. This is a statement about the ordinary finite weighted DP graph, not native contact or topology. The graph is an analysis representation of the ray-bond calculation.

**Nearest known result.** The finite weighted-automaton/minimum-cycle-mean framework is already named in the supplied pre-registration. The arguments below derive the required special cases directly; they do not admit an external theorem or assess novelty.

**Verdict.** The lower-bound, liminf, progression-boundedness and positive `bounded_all` implications are correct under the stated hypotheses. Wording must preserve an onset depth, extended infinity, one-sided partial-graph information and the distinction between sufficient and necessary boundedness tests. A complete exact test for eventual uniform boundedness is given below. This lane has not read the study implementation or its outputs and does not certify census counts.

## Model and completeness requirements

A start state `i` has finite cost `a(i) >= 0`; all other states have start cost `+infinity`. Each middle transition `e` has cost `w(e) >= 0`. State `v` has minimum accepting-closing cost `b(v) >= 0`, or `+infinity` if no closing accepts. Thus

\[
L(s)=\min\left\{a(v_0)+\sum_{j=1}^{s-1}w(v_{j-1},v_j)+b(v_{s-1})\right\}.
\]

The minimum ranges over actual starts and walks of exactly the stated length. A complete graph requires exhaustive start enumeration, every reachable state and its full set of middle transitions, exact accepting-closing information, and exact state identity. Trimming must use this complete graph. A match at finitely many depths does not establish these conditions.

The supplied `census.py` makes a middle cost zero exactly when `W` is empty. There is one such choice per state, and `advance` is deterministic for a fixed state and `W`. Hence the zero-cost transitions form the deterministic empty-`W` map. A zero-total-cost cycle consists entirely of these transitions, since every transition cost is nonnegative. Conversely every cycle of the empty-`W` map has mean zero. A zero-map successor may leave the trimmed graph; a partial orbit is not a negative certificate.

The source's `10^9` is a stored no-bond sentinel. All asymptotic statements here use genuine extended `+infinity` and unclipped finite integer costs. A literal sentinel-valued sequence, or an implementation that clips all finite costs at `10^9`, cannot be used in the limit theorem. Decoding the finite records must distinguish no bond from an actual finite cost; the finite-depth gate alone supplies no asymptotic theorem about saturated arithmetic.

## Lower bound and liminf

Every accepting walk stays in `T`. Remove closed subwalks until a simple residual walk remains. The residual has at most `t - 1` transitions. Every removed closed subwalk decomposes into simple cycles and therefore has cost at least `lambda` times its length. Nonnegativity bounds the residual, start and closing costs below by zero. With `n = s - 1`,

\[
L(s)\geq\lambda\bigl(n-(t-1)\bigr)=\lambda(s-t).
\]

When the right side is negative, nonnegativity is a stronger bound. When no walk accepts, the inequality holds with `+infinity` on the left. Using the full reachable-state count in place of `t` gives a weaker valid bound. Dropping the additive term to claim `L(s) >= lambda*s` is not justified in general.

A minimum-mean simple cycle exists when the finite trimmed graph contains any cycle. Choose one with length `d`, weight `q`, and `q/d = lambda`. Its membership in `T` supplies a fixed start-to-cycle walk and a fixed cycle-to-accepting-closing walk. Repeating the cycle `k` times gives depths `s_k = h + kd`, for a fixed positive integer `h`, and costs at most `A + kq`, for a fixed finite `A`. Thus the liminf is at most `q/d`. The lower bound makes the liminf at least `lambda`, proving equality even when other depths have value `+infinity`.

If `lambda > 0`, every existing ray bond satisfies a uniform linear lower bound with an additive constant. This does not ensure that ray bonds exist at every depth, nor that `L(s)/s` has a limit. For example the controls contain `lambda = 1` with ratios tending to 1 and 2 on the two depth parities. In particular, a minimum cycle mean is a liminf rate, not an exact common rate for all residues.

If `T` is acyclic, every accepting walk has at most `t - 1` middle transitions, so `L(s) = +infinity` for all `s > t`. If `T` is empty, there is no accepting walk at any depth. In these cases `lambda` is undefined/`None`; the extended liminf is `+infinity`. Absence of an accepting ray bond is not a bond of size zero.

## Zero mean and the sufficient every-depth test

On a complete finite graph, `lambda = 0` if and only if a productive zero-cost cycle exists. A fixed prefix and suffix around that cycle give a finite uniform bound on an arithmetic progression of depths. This implication needs no finiteness of the other depths. It does not establish eventual uniform boundedness over all depths: a control has cost 2 for even middle lengths and `n + 2` for odd middle lengths; another has `+infinity` for odd middle lengths.

For `bounded_all`, fix a genuine reachable prefix of length `p` to a state `m`. Suppose its empty-`W` orbit enters a cycle after `h` further transitions, and every state of that cycle has a finite accepting-closing cost. At every middle length `n >= p + h`, follow the prefix and then the zero-cost orbit for the remaining transitions and close at the resulting cycle phase. The total cost is at most

\[
C=a(\text{start})+w(\text{prefix})+
\max_{v\text{ on cycle}}b(v).
\]

Consequently `L(s) <= C` for every `s >= p + h + 1`. This is **eventual** every-depth boundedness; it does not assert finite values at earlier depths. The two-state onset control has `bounded_all = true`, `L(1) = +infinity`, and `L(s) = 2` for all `s >= 2`.

The test is not necessary. With zero map `a0 -> a1 -> a0`, only `a0` closing, start `a0`, and a positive-cost self-transition at `a0`, both length parities have bounded accepting walks although neither zero cycle phase set closes everywhere. A second control waits on a nonclosing zero self-transition, then takes a positive-cost exit to a closing state. Thus `bounded_all = false` must not be reported as unboundedness, or as boundedness *only* on a progression.

## Exact eventual uniform boundedness

The following finite method is necessary and sufficient for existence of finite constants `C,N` such that `L(n+1) <= C` for every `n >= N`.

1. In the **complete productive graph**, let `Z` contain all states on zero-cost cycles. Let `P` be the least common multiple of their lengths. For the deterministic empty-`W` map these are its ordinary finite cycles. If `Z` is empty, eventual uniform boundedness is false.
2. Form the finite reachability product `(v,r,h)`, where `v` is a productive state, `r` is middle length modulo `P`, and `h` says whether a state of `Z` has been visited. Initialize each actual start at residue 0, setting `h` immediately if the start belongs to `Z`.
3. Permit **every original middle transition**, including positive-cost transitions, before and after the first zero-cycle visit. Increment `r` at every transition and retain the visit flag. An accepting product state has `h = true` and finite closing cost.
4. The property holds exactly when every residue `0,...,P-1` occurs in a reachable accepting product state.

**Sufficiency.** For each residue `r`, choose one witness walk of length `n_r`, cost including start and closing `C_r`, which visits a zero cycle of length `d_r`. As `d_r` divides `P`, insert arbitrarily many groups of `P/d_r` traversals of that cycle at no cost. Hence every length `n >= max_r n_r` is accepted at cost at most `max_r C_r`, by using its residue's witness and inserting `n-n_r` zero-cost transitions. The depth onset is `1 + max_r n_r`. The chosen finite witness may traverse several zero cycles; only one of them needs to be designated for unbounded repetition. Arbitrary finite positive-cost prefixes and suffixes are essential to completeness of this criterion.

**Necessity.** Suppose total cost is at most `C`. There are at most `floor(C)` positive-cost middle transitions, since all positive transition weights are integers at least 1. If the walk visits no state of `Z`, each maximal zero-cost segment has at most `t - 1` transitions: any repetition would give a zero-cost cycle. Therefore its total middle length is at most

\[
\lfloor C\rfloor+(\lfloor C\rfloor+1)(t-1)
=(\lfloor C\rfloor+1)t-1.
\]

Every sufficiently long bounded-cost accepting walk must consequently visit `Z`. If all sufficiently large lengths have such a walk, each residue modulo `P` has an accepting marked product state. This proves necessity. Conversely a missing residue proves that along that residue the costs tend to `+infinity`, allowing absent walks. More quantitatively, when `t > 0`, any accepting walk in a missing residue avoids `Z`, so its cost is at least `max(0, ceil(s/t)-1)` at depth `s`.

Equivalently, take the unary finite automaton on `(v,h)` that accepts walks visiting `Z` before accepting closure, with arbitrary original transitions. Its accepted length language must be cofinite. Unary subset iteration is another exact decision method. Neither construction is an efficiency guarantee: `P` or the subset state space can be large. Exhaustive completion of the original and product reachability is required for a negative result. A finite collection of explicit witnesses covering all residues is already a positive certificate.

## Partial graphs and transfer to the true least bond

Let `H` be an authentic retained subgraph, with exact retained start/closing information and only genuine middle transitions. Its accepting walks are a subset of the full graph's. Thus `L_H(s) >= L(s)`. If `H` has a productive cycle, the complete full graph has one, and `lambda_H >= lambda`; this is the correct one-sided cycle-mean inequality. A positive partial mean supplies no positive lower bound for the full minimum. The controls contain a partial mean 1 and full mean 0 whose finite DP values agree through depths 1, 2 and 3; the first difference is depth 4. An arbitrarily long finite-prefix agreement can be obtained by lengthening the omitted continuation.

Positive witnesses survive incompleteness. A verified reachable zero cycle with a verified route to acceptance gives bounded costs on a progression. Since all full costs are nonnegative, it also proves global liminf zero directly, and forces the full minimum cycle mean to be zero whenever that finite-graph quantity is used. A verified all-closing zero cycle and reachable prefix give an eventual all-depth bound even if other graph regions remain unexplored. The residue construction likewise gives a positive bound when explicit authentic witnesses cover its chosen period. Missing cycles, missing residues or a failed sufficient test on an incomplete graph do not give global negative conclusions.

Finally, `L_true(s) <= L_ray(s)` because ray bonds are a restricted collection of bonds. An eventual finite upper bound on `L_ray` transfers to `L_true`. A linear lower bound on `L_ray` does not transfer: minimization over additional side-branch candidates can stay bounded. No conclusion here changes the canonical knot test or proves a native-topology, physical, or complexity claim.

## Consequence of the lead's additional certificates

The lead reports complete independent recomputation and exact eventual-boundedness certificates for 56 of the 112 cases previously described only by a zero mean and a failed `bounded_all` test: all 46 formerly flat cases in that group, plus 10 other cases. Conditional on those per-family certificates, the previous 305 sufficient positives plus these 56 additional positives imply **at least 361 eventually uniformly bounded families**. The remaining 56 zero-only cases receive no extrapolated classification. This paragraph records lead-supplied evidence; this mathematical lane has not opened those computation outputs or independently checked their per-family counts.

## Controls and provenance

[`math_controls.json`](math_controls.json) contains 12 independently specified finite weighted-graph controls, exact simple-cycle enumeration, an independent min-plus recurrence through 32 depths, and exact product-residue reachability. All assertions passed in one standard-library Python process. Complete fixtures have a deterministic unique zero-cost transition at every state; the partial fixture deliberately omits one continuation. These are mathematical controls, not claims that particular NAE definitions realize each fixture. Uniform statements are proved above; finite computation does not replace them.

The controls include a sharp lower bound, different positive rates on two residues, zero-mean progression-only bounds with both finite and absent alternatives, an onset exception, positive transitions before and after a zero-cycle visit, two zero cycles whose lengths jointly cover all large lengths, an acyclic productive graph, and an incomplete graph passing a finite-prefix gate. Deliberately false strengthened claims are rejected by their matched controls.

This is a separately authored AI-subagent audit inside the same task, not human review or external replication. No study implementation was imported, and no output in the forbidden study `codex/` directory was opened. No lifecycle, shared-document or canonical-definition change was made by this lane.
