# Two occurrences in each role can carry general Boolean satisfiability

Status: Proved

## Standard statement

An input specifies the usual two-branch stages, equalities of positive middle names, identities of hidden edge-padding variables, and a value for every private visible guard. Each of the $2r$ middle positions has one name. Each of the $4r$ binary implication positions has one pad, used in its two strictly ternary half-clauses. These name spaces are disjoint. Unit padding at the endpoints and the local witnesses and guards are private. The decision asks whether **some joint assignment** of all hidden values satisfies the given strict formula.

Even when every middle name occurs in at most two middle positions and every edge-pad name occurs in at most two implication positions, the decision is NP-complete. The number of names that occur twice can grow. The reduction has linear combinatorial size from a listed strict 3-CNF; indexed construction uses linear operations after names have been indexed. There is also a uniform fixed wiring for each source variable count on which varying only the visible switches suffices, of polynomial size in the source length after reindexing the used names. This is a different family from the construction with only two repeated middle names. The bounds count stage positions, so a pad placed twice occurs in four signed half-clauses before switching.

With arbitrary multiplicities there is a complementary algorithm. If $q$ edge-pad names appear in **both** polarities among active single-half implications, indexed decision takes $O(2^q r)$ operations. In particular the decision is linear whenever $q$ is bounded, even with arbitrary joins. This parameter is measured after reading the supplied switches.

## Nearest known result

Boros, Elbassioni, Gurvich and Makino give two directed networks on a shared list of labels for which finding disjoint terminal cuts is NP-complete. Put the two networks in parallel and enable the two copies of each label on opposite values of its bit. A disconnecting assignment selects disjoint cuts. Conversely, given disjoint cuts, disable the respective selected copies and choose the remaining labels arbitrarily. Hardness for two opposite uses in **abstract switching networks** already follows. Our question is whether that capability survives the exact serial stage layout, the simultaneous cap on middle identities and a fixed wiring per source width. The following reduction is direct from the repository's admitted strict 3-SAT theorem. Its use of opposite pad literals is the elementary existential resolution step of Davis and Putnam. [Boros et al., Proposition 14 and Remark 3](https://www.keisu.t.u-tokyo.ac.jp/data/2007/METR07-35.pdf) · [Davis and Putnam](https://web.stanford.edu/class/cs357/DP60.pdf) · [Local strict 3-SAT authority](../../EVIDENCE-001D/EVIDENCE-001D-P001_uniform_strict_3_cnf_sat_completeness_admission/proof.md)

## Encode a clause by two conditional implications

Use abstract Boolean signals $s,t$ fixed to $1,0$. For each source variable $x$ introduce two separate signals $X_x,X_{\neg x}$. Forcing exactly one true takes two disjunctions of implications,
\[
(s\to X_x)\lor(s\to X_{\neg x}),\qquad
(X_x\to t)\lor(X_{\neg x}\to t).
\]
For a source clause $(a\lor b\lor c)$, use
\[
(X_{\neg a}\to X_b)\lor(s\to X_c).
\]
Here $X_a$ denotes the signal for the signed literal $a$, and $X_{\neg a}$ denotes its opposite. Once complements are enforced, the displayed condition is exactly the source clause. It works for any of the eight sign patterns.

Give each disjunction $D_1\lor D_2$ its own hidden pad $p$. Keeping just the appropriate signed half on each of the two implication positions enforces $(D_1\lor p)\land(D_2\lor\neg p)$. If both implications fail these halves require opposite values. If one implication holds, a value of $p$ exists, chosen separately for this disjunction. This proves both directions before compiling signals to stages.

## Compile each abstract signal into actual stages

Allocate one distinct wire name $W_e$ per abstract implication occurrence $e$. Each abstract vertex $v$, including $s,t$, has a block with one middle stage per incident wire end. The input of the whole formula has a fresh endpoint wire pointing into $s$; $t$ has a fresh wire pointing out to the final endpoint. Treat these as extra ports. With $d$ ports, the block has $d+2$ stages and internal boundaries $v_0,\ldots,v_d$.

- At the opening stage, use a block-private middle $G_v$ with only $G_v\to v_0$ enabled. At the closing stage enable only $v_d\to G_v$, using its second occurrence. Give the other middle slots fresh names and disable their implications.
- In port stage $j$, the upper route has a fresh middle and both implications enabled, so $v_{j-1}\to v_j$. Together with the two end stages this forces **all** $v_j$ and $G_v$ to the same Boolean value. Assigning all the upper middles this value satisfies the route.
- Use the lower middle position of a source port for $W_e$. Enforce $v_{j-1}\to W_e$ with the specified single padding literal and disable $W_e\to v_j$. At its destination port use $W_e$ again, enable $W_e\to v_j$ unconditionally, and disable $v_{j-1}\to W_e$. With $p$ fixed, eliminating $W_e$ enforces precisely the intended conditional implication. Choose $W_e=1$ if its source is true and its condition makes the implication live, and $0$ otherwise.
- At a separate first stage enable only $x_0\to W_s$ and at a separate last stage only $W_t\to x_r$. The corresponding ports impose $W_s\to s$ and $t\to W_t$ unconditionally. The original endpoint groups are on. Thus $s=1,t=0$. Block separators impose no link between successive blocks, since no active implication enters or leaves their common external boundary.

On every unconditional edge keep both halves, on a disabled edge keep neither, and on a conditional edge keep exactly the indicated half. Use fresh pads on every other edge. For every kept half set all three guards true; for a discarded half set all three false. For an arbitrary truth assignment of the signal variables, the guarded witness triple has an extension exactly when every kept half is satisfied. One witness selects a true literal, or a switched-off position. Consequently the entire construction is ordinary guarded strict 3-CNF with the designated visible input fixed. It reflects and preserves existence of a solution, including the endpoint attachments.

Each $W_e$, $G_v$ and endpoint wire occurs in exactly two middle positions. All remaining middles occur once. A disjunction's pad occurs in exactly two implication positions, once on each condition; every other edge pad is fresh. If there are $h$ disjunctions and $v$ abstract vertices including $s,t$, there are $2h$ conditional implications. The number of stages is $4h+2v+4$ (two external stages, two terminal ports, two block-end stages per vertex, and two port stages per implication). Every stage contributes a constant number of raw strict clauses and switches. The strict input is in NP by guessing and checking a full assignment. The admitted reduction source is NP-complete, proving the claim.

For a fixed source size $n$, allocate in advance the $2n$ complement disjunctions and one optional disjunction for each of the $8\binom n3$ possible clauses on distinct names. Select a clause by keeping its two conditional halves. For an absent clause turn off both. No other wire, signal, pad or sign changes. The schedule and guard vector have size $O(n^3+n)$ and are uniformly constructible. Reindex the source's used variables first, so binary notation for a large unused name cannot cause a superpolynomial expansion. The per-instance construction instead uses one disjunction per listed clause.

## Regroup by the signs of shared pads

If either endpoint unit is inactive, an all-equal assignment to all route signals satisfies the remaining implication requirements; select the value that respects any active endpoint. Otherwise read the two half activations per implication. A double activation always enforces the implication. Zero active halves impose nothing. A single half has the form $D\lor L_p$. Whenever all such literals of a pad have the same sign, set the pad to satisfy that sign. This only removes implications, preserving any possible solution, even when that pad also appears on unconditional edges. Enumerate the values of the $q$ remaining pads. At each assignment retain the unconditional and live single-half implications; their consistency with the two endpoints is exactly failure of reachability from the true endpoint to the false one. If no path exists, set precisely the reachable signals true and choose the local witnesses. This proves the stated time and $O(r)$ working-space bound for indexed names. In a compiled formula with all disjunctions selected, every disjunction supplies its own two-sided pad, so $q$ can grow. No bound on unrestricted SAT running time follows from either direction.

## Checks

The [checker](check.py) compares the projection of actual guarded strict formulas with every selected subset of the eight signed three-variable clauses and with larger instances. It checks the occurrence caps from the compiled stage list, recovers source solutions from returned raw assignments, forces prescribed source assignments for the three-variable corpus, tests the two-use rule on arbitrary activations, and includes changed-polarity and removed-feedback controls. The counts are recorded in [checks.json](checks.json).
