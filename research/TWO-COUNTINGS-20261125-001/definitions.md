# Two countings of a structure's allowed states: definitions ("TD")

Epic `TWO-COUNTINGS-20261125-001`, ticket `TWO-COUNTINGS-20261125-001A`. These definitions build on the shared
definitions ([SD](../RING-IN-BALANCE-20261123-001/definitions.md), cited by line) and those of the study of parts that
meet again ([FD](../PARTS-MEET-AGAIN-20261124-001/definitions.md), cited by section), and change nothing in them. The
canonical K1–K3 test is unchanged. Data files: `research/TWO-COUNTINGS-20261125-001A/` (structures.json,
construction_orders.json, census_index.json) and [the table](table.json).

## 0. Words

- Kept from SD and FD: structure, knot, place, distinction, holder, loose, shared, start, birth, join, offshoot, fresh
  distinction, round, law, ration, treatment, take, eligible, the choice, parent, the birth record.
- **State**, **allowed state**: the glossary's. The record's "word" appears only in citations.
- **Counting**: our rule that gives a weighting of states. **Weighting**: what a counting gives (the glossary's word,
  said with what it weights: of states, of meeting patterns, of histories).
- **Counting from the finish**, **counting from the start**, **counting from stage s**: section 3.
- **The first observer**, **the second observer**: each a supplied list of distinctions; nothing observes. (The
  literature's names are given once, in the claim.)
- **Start with its states**: a start with the weighting of its states.
- **Funding** (the record's word, cited only): a round makes its births; under STALL it makes none when a member is
  short (SD lines 42–43). **All-or-none funding**: the whole round makes its births or none.
- **Keyed setting** (the record's phrase, THIRD-HOLDER-20261123-001A, "a setting keyed to an old value").
- Not used: words of space for the program's objects ("far", "where ... sit", "elsewhere"); "typical", "rare",
  "likely" without a weighting; "chance" (say "weight"); "reads" except in the owner's sense; the banned words of the
  common brief; "fix" for a counting (say "decides the counting").
- The record's other names: counting from the finish = "uniform present words", "uniform stage", "every allowed word
  counted equally", "complete reached-word weighting"; counting from the start = "old-word weighting", "the control
  weighting", "equally lifted start", "inherited", "transported", "recursive division", "forward weighting".

## 1. Structures and histories

1. Knot laws: even, odd ("parity"), not-all-equal. A structure may hold knots of several laws.
2. **Allowed states** A(S).
3. **A history** H = (S_0, ..., S_t): a start and, for j ≥ 1, the knots added at stage j (a round, one birth, or the
   supplied setting knots). F_j: the distinctions first held at stage j (fresh); every other place of a knot added at
   stage j is an **old place**.
4. **Completions.** For o in A(S_(j−1)), c_j(o) is the number of assignments of F_j that with o satisfy every knot added
   at stage j. A knot added with nothing fresh gives 0 or 1. A stage **extends** when c_j(o) ≥ 1 for every o. If A(S_0)
   is empty no counting is defined.
5. **Product.** When the knots of stage j have disjoint private fresh sets, c_j(o) = Π_i c_(j,i)(o).
6. **A common stage** of several histories: an index s such that S_0, ..., S_s are the same in all of them.

## 2. Three weightings, kept apart

1. Of states (what a counting gives).
2. Of meeting patterns or starts (the copier study's W1, W2).
3. Of histories (the weight of each history given its start: uniform over a law's open choices; the copier study's T1,
   T2; for a keyed setting, the supplied rule g assigns each old state its history, 4.5).

## 3. The countings

1. **Counting from the finish** on H: each state of A(S_t) has weight 1/|A(S_t)|.
2. **Counting from the start** on H, defined only when every stage extends: w in A(S_t) has weight
   (1/|A(S_0)|) · Π_(j=1..t) 1/c_j(w|_(j−1)).
3. **Counting from stage s**, s a common stage of the histories compared: (1/|A(S_s)|) · Π_(j>s) 1/c_j(w|_(j−1)). On a
   hand-built structure taken as its own start, with the two setting knots as one stage, the family has two members
   (s = 0, s = 1). With the setting knots as two stages there is a third, the **mixed stage** (after one side's setting
   knot, before the other's), common only to the histories sharing that side's setting: defined and reported, not
   predicted.
4. **Lost weight.** Where some c_j(o) = 0, the unconditioned weights sum to less than 1 and no score is defined on them.
   **Counting from the start, renormalised**: the weights divided by their sum, per history. In a pooled statement it
   changes the weighting of histories (each history's share is multiplied by its kept weight). With renormalising,
   counting from the start contains counting from the finish (start: every distinction with no knot; then every knot
   added with nothing fresh). Along a law's history of TD 5 no weight is lost (every birth has a fresh distinction).
5. **Pooled over histories.** Counting from the finish pooled: each pair (history h, state of A(S_h)) once, giving h the
   weight |A(S_h)|/Σ|A(S_h)|, not uniform over the setting pairs when the totals differ. Per history: a supplied ν
   times the counting on each.

## 4. Settings, records, scores

1. **Setting knots** (REVIEW-LEADS-20261123-001C, `preregistration.md:47`): the first observer's setting a adds
   nae(x1, x2, za) for a = 0 and nae(x1, x3, za) for a = 1, za fresh; the second observer's b adds nae(y1, y2, zb) for
   b = 0 and nae(y1, y3, zb) for b = 1. **Option pairs** on the 11-knot structure (SETTING-AS-REREAD-20261123-001A, its
   options: the distinctions each observer's live knot shares): the first observer's options are x2, x3, c and the
   second's y2, y3, t; an option pair is two of them, the first taken at setting 0. The nine pairs: (x2,x3), (x2,c),
   (x3,c) against (y2,y3), (y2,t), (y3,t).
2. **Records**: (x1, x2, x3, za) and (y1, y2, y3, zb) unless a study froze another.
3. **Change from the other's setting**: the largest total-variation distance between a record's distributions under
   the other observer's two settings, over both observers and both own settings. **Hidden**: that change is 0
   exactly. Relative to the declared record.
4. **Score and its exact method.** E00 + E01 + E10 − E11 maximized over the four placements of the minus sign and over
   a declared class of outcome functions; an outcome function depends on its own observer's record and own setting
   only. Record **values** mean the record values with nonzero weight.
   - **All two-valued functions** (contains the constants): enumerate every pair (f0, f1) of ±1-valued functions on
     the values of the record with fewer values, f1 fixed to +1 on its first value (an overall sign); for each pair
     and sign placement, the other side's best response is Σ_v |σ_0 L_0(v) + σ_1 L_1(v)| over its values v, where
     L_b(v) = Σ_u f_a(u) P_ab(u, v) with the signs σ of the placement; all in exact rationals.
   - **Parities of a nonempty set of record bits** (no constant): each observer picks, for each own setting, one of
     the 2^k − 1 parities of its k record bits; enumerate all (2^k − 1)^4 choices with the four sign placements,
     exactly.
5. **Keyed setting**: g is a function from the first observer's allowed old patterns of (x1, x2, x3) to {0, 1}; every
   such g is run (16 on the 11-knot structure, whose first observer has 4 allowed patterns; every function of the
   three old values, 256, on the 18-knot structure, as THIRD-HOLDER-20261123-001A did), with the second observer's setting fixed at each value. The supplied
   rule g assigns each old state its history. Counting from the start: P(w) = (1/|A(S_0)|) / c(o; g(o), b) for each w
   extending old state o under the setting pair (g(o), b). Counting from the finish, pooled: each w of A(S_(g(o), b))
   with its old part o counts once, normalised over all such w for fixed b. Reported: the largest change of the second
   record between two functions g.

## 5. The laws (registered)

1. ORDINARY = (ORD, STALL); Q-OLDEST, Q-NEWEST, Q-ALL (every round-1 choice); RING-LAW = (CAP-3, CANCEL-WAIT, RELEASE);
   COPY-LAW(CANCEL-RETIRE) = (FLOOR1, CANCEL-RETIRE, RELEASE), alone and with MET(OLDEST); parity and not-all-equal;
   closing IMPLIED (FD 2.8).
2. **Value-blind**: the next structure is a function of the structure, the names, the birth record and any sampled
   takes, of no state. Every law of 5.1 is.

## 6. Registered structures

`structures.json`: 33 structures (the 11-knot start and its four finished structures; the smallest gain of
ONE-PARENT-REREAD-20261123-001A as the part, the part after the rule-Q round, and four finished structures;
THIRD-HOLDER-20261123-001B's 7-knot, 8-knot and pencil 9-knot structures with their finished structures; the 18-knot
structure of THIRD-HOLDER-20261123-001A with its finished structures; and the two 10-knot **starts** of
SETTING-AS-REREAD-20261123-001A, for which no finished structures are registered: their three rule-Q births are made by
the run, part 2).

## 7. Settled statements the engine checks

1. **Renaming** carries every counting. **The 4n renumberings** of a start with n distinctions: list its distinctions
   by name in increasing order; for k = 0..n−1 rotate the list left by k; take each rotation as it is and reversed
   (2n lists); take the start's knots as listed and reversed (× 2); the distinction at position i of the list is given
   name i, and the knots are listed in the stated order. **Grow again**: grow the renumbered start under the same law.
2. **Factorization** (1.5).
3. **The exact agreement rule**, while the two countings agree before round j: they agree after it exactly when
   Π_i m_i(o) is the same for every allowed old state o, where for a not-all-equal birth with f_i fresh distinctions
   m_i(o) = 2^(f_i) − 1 if its old places are all equal in o and 2^(f_i) otherwise, and for a parity birth with f_i ≥ 1
   fresh distinctions m_i = 2^(f_i − 1) (an implied parity birth: 1). Only the occurring patterns of (e_1, ..., e_m),
   e_i = [old places all equal], matter; they are enumerated exactly by a SAT solver with blocking clauses on the
   indicators of the births whose e_i varies. A birth with no old places (only in construction orders) is not covered;
   construction orders are counted by enumeration.
4. **One birth, f fresh distinctions**, the countings agreeing before it: with p the weight before the birth of the
   old states whose old places are all equal, the total-variation distance after it is p(1 − p)/(2^f − p).

## 8. Orders and examples

1. **Construction orders** (`construction_orders.json`, its index meanings in the file): each knot is added in the
   listed order, bringing as fresh the distinctions no earlier knot holds; counted from the start renormalised; the
   same order for all four setting pairs. **A setting knot brings only its own fresh distinction** when every other
   place of it, for both of that observer's settings, is held by an earlier knot in the order.
2. **Examples** (on the 11-knot start, counted from the start, records as 4.2 unless said):

   | # | Breaks | Example | Record of the first observer |
   | --- | --- | --- | --- |
   | E0 | none | the setting knots of 4.1 | (x1,x2,x3,za) |
   | E1 | the premise (no start before the settings) | counting from the finish | (x1,x2,x3,za) |
   | E2 | h1′, and h4's first clause as a consequence | construction order 11 of `eleven_registered_400` | (x1,x2,x3,za) |
   | E3 | h2 (renormalised) | the first setting knot nae(x1, x2 or x3, s1), nothing fresh | (x1,x2,x3,s1) |
   | E4 | h3′ | both setting knots hold one fresh z: nae(x1, x2 or x3, z), nae(y1, y2 or y3, z) | (x1,x2,x3,z); second (y1,y2,y3,z) |
   | E5 | h4, first clause (renormalised) | a later even(za, zb, x1), nothing fresh | (x1,x2,x3,za) |
   | E6 | h4, record clause | the first record holds zb | (x1,x2,x3,zb) |
   | E7 | h4, record clause | a later even(zb, w, x1), w fresh | (x1,x2,x3,w) |

## 9. The lemma's hypotheses, in checkable form

For the four setting pairs' histories H_ab, a common stage s before the first setting knot, setting knots K_A(a),
K_B(b) (TD 4.1), later stages after them:

- **h0**: S_0..S_s are identical in the four histories, and the counting starts at a common stage ≤ s.
- **h1′**: every place of each setting knot other than the distinctions it brings as fresh is held in S_s; what it
  brings as fresh is the same for both of that side's settings and is held by no knot of the other side's setting.
- **h2**: c ≥ 1 for every state of S_s under every setting pair at the setting stage(s); or, under renormalising, the
  lost-weight rule below.
- **h3′**: the fresh sets of K_A(a) and K_B(b) are disjoint, and no later knot holds fresh distinctions of both.
- **h4**: no later stage loses weight except as allowed by the lost-weight rule; and each record holds only
  distinctions held in S_s and its own side's setting-fresh distinctions.
- **Lost-weight rule** (the form for counting from the start, renormalised): whether a state is lost, at any stage,
  depends on its part on S_s alone.

## 10. The knot test

**In the whole structure** (SD lines 128–139; FD 7; the canonical foundation of the program): the induced relation of
a knot is the set of assignments of its places that extend to an allowed state of the whole structure, every other
distinction quantified away; K1, K2, K3 tested on it (forgetting reading) by `knotlab.knots.check_knot`, and by the
canonical command `PYTHONPATH=tools python3 -B -m knotlab check --cnf ... --loops ... --contact ... --witnesses ...`
with every other distinction a witness. **On its own**: the same test on the knot's own rule alone. **Knots in the
whole** of a table row: "all", "fails (rule, K2)", or "not tested".

## 11. Scaffolds (each supplied; each with its swap or "none")

| Scaffold | Swap |
| --- | --- |
| The two countings and the family from a common stage | every common stage reported |
| Uniform weight on a start's states | none needed by the lemma (any setting-free weighting of old states) |
| Hand-built structures as their own starts | construction orders from nothing, disclosed |
| Equal division at a birth | the other counting |
| ν uniform over histories in pooled rows | ν by finished totals (counting from the finish pooled) |
| The settings, observers, records and outcome classes as frozen by each study | none |
| The laws of TD 5 | none |
| The 100 census starts and 3 rounds of the engine check | none |
