# Localisation: referee reconstruction and adverse controls

**Verdict: no Block to the existential localisation theorem.** The constants
in the frozen statement are sufficient in the stated injective-call setting.
The short proof omits two arguments that matter: protecting selected side
branches, and obtaining the explicit onset from an *eventual* bound. Both
have repairs below. The direct restoration step is sound when it uses a
short prefix loop, rather than the arbitrary loop used for shortening.

This is a referee review inside `epic TOP-INFO-20261114-001`. It changes no
proof, lifecycle record, definition, or publication. Citations below refer to
`proofs/TOP-INFO-20261114-001B/TOP-INFO-20261114-001B-P001_top_info/proof.md`
unless another path is named. Machine evidence is `localisation_checks.py`
and `localisation_checks.json` in this directory. No study Python was opened
or imported; the concrete synthetic CNF reuses the explicitly permitted
earlier referee's `pumping_audit.py`.

## Findings by exact proof step

| Finding | Class | Assessment |
| --- | --- | --- |
| Lines 51–53: allocating-copy occupancy | **Not a block** | Correct after the earlier referee's repair. A member is assigned once to its allocating invocation; a carried coordinate occurrence is not another member allocation. |
| Lines 54–57: repeated state and residue | **Not a block** | Correct. Include the empty prefix and copy type in the state; compare full relative products and all-port carry maps. There is a simpler bound `m Π`, so the stated `m(Π+1)` is safe. |
| Lines 58–61: exact restoration of the original depth | **Not a block** | Correct with a short loop of length `1≤ell≤m`; `ell` divides `m!`. An arbitrary residue-preserving deleted loop need not allow insertion of exactly `Π`. The short-loop argument below supplies the missing detail. |
| Lines 43–46: `B` and the side bound | **Not a block** | `B=Cm(Π+1)` has no off-by-`C` defect. Side branches need the protected-level argument below; their depth is at most `C(m+1)`. |
| Lines 62–64: what is an occupied side level? | **Not a block, proof repair required** | The definition on lines 51–53 is only for the target word. Extend that same off-path-allocation rule to each retained member path, protecting a branch with a selected allocation off that path. An own-only rule is false: it can delete another member's side branch. The adverse four-member bond detects this failure. |
| Lines 41–43: numerical onset without the eventual-bound onset | **Not a block, proof repair required** | The written proof starts with a witness at `s` and directly proves the conclusion only where `L(s)≤C` already holds. Conservatively it yields `s>max(N,H)` if the bound starts at `N`. The backward-normalisation argument below proves the stronger written onset `s>H`, so no change of constant is required. |
| Preregistration lines 52–55: “some least bond” versus proof “some bond” | **Not a block** | At an eligible depth start with a least bond. Exact-depth restoration and equality of its full selected relation preserve its cardinality, so the result is still least for `L(s)`. |
| Any reading as “every least bond”, a fixed target word, or fixed target identity | **Narrowing** | Unsupported and, for every least bond, false. The target word and lower allocated identities may change. The explicit synthetic family below has arbitrarily nonlocal least bonds and also local least bonds. This does not refute the actual existential statement. |
| `top_info.md` lines 34, 46–48: new semidecision | **Narrowing of significance** | Localisation adds a normal form for bounded witnesses. Positive semidecision of boundedness was already established by the repaired dichotomy; there is no new decision procedure or finite negative certificate. |

## Exact setting and selected relation

Use the setting and finite-support factorisation reconstructed in
`research/READ-RULE-20261114-001/referee-R1/codex/pumping_proof_audit.md:8–117`.
Calls have distinct arguments, own identities are fresh, and a flattened
copy's context meets its subtree only through its ports. Per-call relations
include the source block and exact usual-limit relations of every unchosen
call, leaving the chosen continuation open. For more general repeated-call
arguments, use a complete input/output identity partition and recount `m`;
the current scalar bound must not silently be reused for that larger state.

Write the chosen S copies as `c_0,...,c_n`, with absolute target depth
`s=n+delta`, where `delta=0` for main=S and `delta=1` for the admitted wrapper.
For `i<n`, an allocation collection contains c_i's own allocations and every
allocation in its off-word subtrees. These collections are disjoint. A
collection is occupied if it contains a member of W. Main ports, wrapper
allocations outside the chosen entry, and all allocations at/below c_n are
outside these pre-target collections. Thus their occupied count satisfies

    t <= |W|-2 <= C-2.

The two excluded members are a main port and an own distinction of c_n.
Other members in the target's subtree only strengthen this inequality.

For a member-free run of source copies `c_l,...,c_r`, use interfaces at
`c_l` and `c_(r+1)` and include exactly those source blocks. Do not abstract
a selected block just outside that run. With upper/off-run members U and
retained-lower members D, the selected relation is exactly

    {(u,d): exists alpha,beta,
              A(u,alpha) and M(alpha,beta) and B(beta,d)}.

The interface tuples are proxies for actual identities. Selected free
coordinates remain free coordinates, with the corresponding proxy-equality
constraints; they are not existentially erased. The state records the full
relative relation M, current copy type, and carry map for every input port,
including a port holding a non-main ancestor allocation. Equality of these
states permits a type-correct suffix replacement and an injective renaming
of lower allocations compatible with every retained upper identity.

Consequently the **entire** selected relation is preserved, not merely its
non-fullness. Its projections onto every proper subset are then preserved
too, so a bond remains a bond. Nothing here infers a knot from syntax,
shared labels, or an evaluator.

## Shortening and exact depth restoration

Put `Π=m!` and `K=m(Π+1)`. Prefix states are taken from the top interface of
the particular free run, not from a new unrelated root. There are at most m
of them; copy type is part of each. At the `g+1` prefix boundaries of a run
of g factors, at most `mΠ` pairs `(state, boundary count mod Π)` occur. If
`g>=mΠ`, two such pairs agree. Delete the intervening factor word. It has
positive length divisible by Π, its endpoints have the same type, and the
whole run state is unchanged. Repeating gives length `<mΠ<K`.

For a witness already present at `s>H=(C+1)K+C`, keep one longest free run
unchanged and shorten all others this way. The original longest run has
length at least K (the threshold is deliberately loose), hence exceeds m.
Inspect its first `m+1` prefix states. Some `i<j<=m` agree, so with
`y=word[i:j]` and `ell=j-i`,

    state(t1 y) = state(t1),
    state(t1 y^k) = state(t1) for every k>=0.

This is associativity and prefix stability; y itself need not be an
idempotent semigroup element. Since `1<=ell<=m`, ell divides Π. If all the
other cuts removed a total R, then `R>=0` and Π divides R. Insert `R/ell`
additional copies of y. This restores **exactly s**, leaves all run states
unchanged, and preserves the full selected relation under the allocation
renaming. The result has the same size as the starting bond.

The distinction between these two loops is material. A removable identity
word of length `2Π` preserves the residue but its copies cannot add just Π.
The controls reject that insertion and verify the short-loop repair.

## Main-word constants and the wrapper

Except for the chosen longest run, all runs now have length `<K`. There
are at most t occupied source levels. Before the longest run, the last
occupied source index is at most `tK-1`; after it, the first occupied source
has distance from the target at most `tK`. Thus all occupied source copies
are within `tK` levels of the root or target, allowing the root-side `+1`
when `delta=1`. In particular the stated `B=CK` suffices. The actual
`t<=C-2` gives further slack. Target-own members are anchored at the target,
and selected wrapper allocations are anchored at main.

If every free run had length `<K`, then even the looser `t<=C` would give

    n <= (t+1)(K-1)+t <= (C+1)K-1.

For integer absolute `s>H`, `n=s-delta>=H` when `delta<=1`, a contradiction.
Hence the long-run and short-loop requirements do follow from the displayed
threshold. No extra `+C` is missing from B.

## Repair for the explicit onset

The preceding construction requires a witness at the original depth.
To remove the unknown eventual onset N, take any sufficiently late witness
of size at most C in the desired residue, and choose one of its long free
runs. Preserve a prefix through a short repeated state `i<j<=m`. Its loop
length ell divides Π. Keep this prefix, of length `j<=m`, and shorten only
the suffix of that run by `(state,residue)` cuts, now using the actual state
after the retained prefix as the initial state. Its suffix has length
`<mΠ`, so this saved-loop run has length `<m+mΠ=K`. Every other run can also
be shortened to `<mΠ<K`.

The resulting base depth satisfies

    n_base <= (t+1)(K-1)+t = (t+1)K-1 <= (C-1)K-1,
    s_base = n_base+delta <= (C-1)K < H.

All deletions were multiples of Π. For any prescribed `s>H` in the original
absolute residue, `s-s_base` is a nonnegative multiple of Π. Pump the saved
short loop by that amount. This gives a size-at-most-C bond at **that s**.
Thus the stronger numerical onset in the statement is repairable. To also
obtain a *least* localised bond at s, now take a least bond there and apply
the preceding exact-depth construction. This argument is separate from what
the frozen proof actually wrote.

## Side subtrees: preserve the branches, then shorten

Apply the target-word occupancy rule recursively to each selected member
path. At a source copy on that path, protect the level if either its own
allocations contain a selected member or an off-path child subtree contains
a selected allocation. In particular a branch with selected allocations
in two child subtrees is protected even when it owns no member of W.

On a path to one selected allocation, charge each protected level to one
selected own allocation there, or to one selected allocation in an off-path
subtree. Charges at different levels are distinct because those allocation
collections are disjoint. Include the terminal member's level. There are
therefore at most q such levels when that subtree contains q members.

Between successive protected levels, and from the branch anchor to the
first, all side subtrees are member-free. A run of more than m source levels
repeats a typed relation/carry state and may be shortened without touching
either protected endpoint or any selected side branch. No residue needs
preservation here: these cuts do not change the covered target's depth.
After the cuts, successive protected levels are at most `m+1` levels apart.
Every member is consequently within `q(m+1)<=C(m+1)` of the branch anchor.
Use the same argument in the target subtree with c_n fixed, and for wrapper
side subtrees with main fixed. These cuts preserve the full selected
relation by the same interface argument.

Without the off-path clause this is false, not just a missing estimate.
The control relation obtained from

    NAE(p,a,q) and NAE(q,b,z), with q hidden,

is a four-member bond on `{p,a,b,z}`: it excludes exactly the states
`0011` and `1100`, and every proper subset is full. Allocate a in one arm
and b,z in another below a branch whose own selected set is empty. An
own-only cut through that branch deletes the first arm. Treating a as a
dangling retained coordinate makes all 16 states possible and destroys the
bond. Protecting the branch, and preserving the same q at the interface,
keeps the 14-state relation and all 16 subset projections. This is a genuine
mathematical adverse control, not just a malformed metadata record.

## Quantifiers: an explicit nonlocal least bond

This synthetic control was constructed for the audit, not extracted from
the 65 middle-member families. It has one recursive type, distinct raw call
arguments, no other own-bearing recursive definition, and no delayed entry:

    S(p,q,r): own x;
              NAE(p,q,x), S(p,q,x), S(p,x,q).

All eight port assignments extend. For a quick extension rule, assign each
otherwise unprescribed fresh own value opposite p. Let x_s be the own
distinction reached by taking the first recursive call s times. In its
second-call subtree take the first call repeatedly to an arbitrary own
z_i. The exact projection onto `{p,x_s,z_i}` is NAE3. Set q opposite p to
admit any value of x_s, respect the one displayed NAE at z_i, and extend all
remaining fresh choices as above. Every pair of this triple is full.

The actual reachable relation/carry algebra has `m=6`, `Π=720`, and full
usual-limit mask. Checking all six transfer states shows all three
main-port/target-own pairs are full at every covered target, excluding any
eligible 2-bond. Hence these 3-bonds are least. Nevertheless i is arbitrary.

The concrete raw-CNF check uses `C=3`, `K=4326`, `B=12978`, `H=17307`, and
`s=17308`. Its selected word is first-call^17308, second-call, first-call^22.
The far member is 23 levels below x_s, exceeding `C(m+1)=21`; the nearer
member at descent one gives the identical NAE3 relation. The 17,336-variable,
34,666-clause CNF and its canonical clause hash are reproducible from the
script and recorded JSON. All eight subset projections agree, and all 18
root-port/target-own pair checks across the six states are full.

Thus **every least bond is local** is false even beyond the numeric
threshold. The actual theorem says that **some** bond has the normal form;
the near 3-bond supplies exactly that. Localising a given witness may change
the covered target word and target identity. It makes no claim for every
copy at a fixed depth or for an observer-fixed target word.

## Supported theorem, delta, and remaining gap

Subject to the exact finite-state semantics above, the supported statement
is: if `L(s)<=C` eventually on one residue of `m!`, then for every integer
`s>(C+1)m(m!+1)+C` on that residue there exists a least bond for L(s), of
size at most C, with at most one long member-free run on its target word;
its other occupied levels are within `Cm(m!+1)` of root or target, and its
selected off-word allocations are within `C(m+1)` of their protected branch
anchors. The target word and lower identities may change during the proof.

This is a useful normal form, particularly for side-subtree supports. The
earlier dichotomy already gave positive semidecision by enumerating a
finite-support long-gap bond and its repeated-state certificate; see
`pumping_proof_audit.md:159–197`. Localisation does not add an effective
uniform bound on C, a decision procedure, a finite certificate of growth,
eventual periodicity of the exact L values, or a theorem about every target
word. With `m=29359` in an earlier sample even `m!` is enormous; “computable”
does not imply a practical census algorithm. The present proof's m must be
recounted over the required copy types, rather than reusing a single-type
sample's m without checking.

The advisor's occupied-level finite-type proposal at lines 66–71 remains
an unproved route. Its first condition can detect the existence of a crossing
bond of bounded size, but deleting occupied levels must also preserve the
two endpoint roles and the relevant fullness conditions. No finite-type
closure or bound on the least bounded C was proved here. There is no claim
of undecidability, external novelty, P versus NP, physical structure, or a
change to the canonical knot test.

## Actual checks and limits

Run:

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/TOP-INFO-20261114-001/referee-R1/codex/localisation_checks.py

The final run passed in under one second with approximately 39 MiB peak
RSS and a 2 GiB address-space cap, one process, no child pool or network.
It checked 74 residue-preserving shortenings, 80 exact original-depth
restorations, 640 recoveries of prescribed absolute depths, 24,624 extreme
endpoint/wrapper arithmetic cases, a stable-prefix/non-idempotent loop,
illegal copy-type deletion, side-branch erasure, disconnected non-main
interface identity, an alternating-type selected call tree, and the concrete
synthetic least-bond CNF above. Negative controls were run and rejected by
computed mathematical differences.

The fresh finite checks use separate algorithms authored in the same
research task (**V1**); the synthetic CNF additionally reuses an allowed
earlier referee helper, with that dependency disclosed. This is neither
external replication nor a formal-kernel proof. The uniform theorem rests
on the symbolic reconstruction, not on the finite counts. External novelty
was not assessed; no network or external theorem admission was used.
