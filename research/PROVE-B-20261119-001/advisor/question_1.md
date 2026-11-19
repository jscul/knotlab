I am trying to PROVE Claim B and want your best proof route, or the precise obstruction. Rigorous, concrete; bets at the end.

Setting (as before). Connected arrangement a; graph G = (J ∪ {o}, E), distinctions = edges, loose = edges to o; table T(x,y) =
(min |B| over bonds B of G containing x, y) − 1. Live junctions L = those with a loose edge. The law's round (complete rounds,
cheapest counts) makes new junctions N; n ∈ N has parent set P(n) ⊆ L (k = |P(n)|), takes one loose edge x_{n,u} from each parent
(rerouted u–n), and gets f(n) ≥ 1 fresh edges n–o (fewest counts: f = max(d, 3−k, 1), d = number of next-round groups n lies in).
R = (L, loose counts, the family F of subsets of L met by one junction). Lemma A (proved, refereed): N, the P(n) and f(n) are
functions of R. Claim B: if φ is a table isometry a → b keeping R (loose onto loose, live stars onto live stars, F onto F via
ψ), then its extension φ' (new junctions matched by ψ of parent sets) is an isometry of the next tables T(a'), T(b').

Evidence: true on 36,060 carried-pair matchings and on all 1,746,752 census self-symmetries (open stages, rounds 1-7, at most 14
junctions) that keep R without carrying the equations, 1,630,590 of them breaking holder classes (parallel-edge classes). Most of
those stages have two junctions sharing two distinctions. False for joins made by hand across matched junctions of static
collisions (where R is not kept); offshoots by hand never break it.

What I have (please check):
Split formula (Lemma C). Bonds of G' are δ'(S ∪ T), S ⊆ J, T ⊆ N, S ∪ T connected, complement (with o) connected, and
|δ'(S∪T)| = |δ(S)| + Σ_{n∈T} (f(n) + |P(n)∖S| − |P(n)∩S|). Old edge membership: shared edge e ∈ δ' iff e ∈ δ(S); loose x_{n,u} ∈ δ'
iff [u ∈ S] ≠ [n ∈ T]. T = ∅ gives the old bonds (Theorem 3: T' ≤ T on old pairs).
Lemma O (offshoots, k = 1): a junction n ∈ T costs ≥ f − 1 ≥ 1 extra, so T'(old,old) = T, and T'(fresh_n, y) = T(x_{n,u}, y) +
f(n) − 1 (or n's star); so offshoot-only rounds satisfy Claim B for any isometry keeping loose per live junction.
Discounts (k ≥ 2): with P(n) ⊆ S, n ∈ T saves k − f(n) ≥ 1 when d < k. Connected S gives T'(x,y) ≤ W(x,y; loose of P(n)) − k + f −
1, W = smallest bond containing x, y and one loose edge of each parent (a (2+k)-way reading). Disconnected S glued by n gives a path
form, e.g. k = 2: T'(x,y) ≤ T(x, x_{n,u}) + T(x_{n,v}, y) + f − 1 (if the two inner sides are disjoint and non-adjacent).

Reached-stage structure available (PARENT-RULE, proved): live junctions pairwise do not meet; each live junction meets only its
parents (older junctions); any two parents of a new junction are backed by a common older junction holding no loose distinction;
peeling gives the previous stage; in a reached open stage the live junctions' non-loose edges go to the previous layer only.

Questions.
1. Is there a proof of Claim B for reached stages? E.g. show the (2+k)-way readings W at parent sets are functions of T and R
   in reached stages, or that the minimum in the split formula is always attained by a form computable from T and R.
2. If not, what is the smallest configuration (junction count, sharing, which group) where an R-keeping isometry could fail,
   so a hunt can target it? Is it necessarily outside reached stages (e.g. needs the start layer)?
3. The holder-breaking extensions: why would they extend at all? (They are not code isomorphisms even locally.)
4. Bets: Claim B true for all reached stages; true for all connected arrangements.
