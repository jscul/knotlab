# Proved true rates with side branches

Epic `TRUE-RATE-20261113-001` (`TRUE-BOND-20261113-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead.
Pre-registered with the Codex spec in commit ec6363e35 before the code was written. Code by Codex; the run, a post-hoc certificate,
the cross-checks and this note by the thread. The canonical K1–K3 test is unchanged. Refereed (TRUE-RATE-R1,
`referee-R1/report.md`, commit 7936a22c0): **confirmed with fixes**, three Narrowing and three Not a block.

## Words

As in TRUE-BOND: L(s), the least bond between a port of the top copy C_0 and an own distinction of the depth-s ray copy C_s, members
anywhere in the bottomless pattern; L_ray(s), the same with members on the ray only; λ_true and λ_ray, their long-run rates. A top
port is **carried** when the ray call passes it down unchanged at every level (it sits on a cycle of the map i ↦ a_i, a the ray
call's arguments), so it is an end of every ray copy, by identity. *(After the referee:* under a cycle of positions longer than
one, the port at a given position changes with depth, so a shifted bond holds *a* top port at every depth, not always the same
one. All 20 carried families here have only fixed points; the census has 50 two-cycles.*)*

## The question

Side branches shorten the least bond in at least 62 of the 226 families whose ray bond provably grows. Can a true rate be proved,
and does the true bond still grow?

## The question in standard terms

Minimum cycle means of a least-fixed-point summary graph for least minimal non-shattered sets in an infinite iterated
hyperedge-replacement NAE instance; and, for a carried port, a join-tree (separator) argument for every depth.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The general method proves the true rate only where side branches change nothing.** The uncapped side table closed with a complete graph in 24 of 226 families (150 s each; the four flat ones 1,600 s and 7 GiB each, none closed). All 24 are unshortened, and in all of them λ_true = λ_ray exactly (1/3 in 5, 1/2 in 8, 1 in 10, 2 in 1); no zero-weight cycle. Elsewhere the table grows about tenfold per cost level, and the partial graphs give only upper bounds. The referee recomputed 3 of the 24 from fresh code (105: L(s) = 3 + ⌊s/3⌋; 429: s + 3; 874: 2s + 3); the other 21 rest on this study's records. | proved (24 families) | G passed on the 24 complete graphs (166 partial-graph cells exceed TRUE-BOND's values, as an incomplete graph must); P1 failed (24 < 113); P2 held but only on unshortened families; P3's second part held (24 of 24) |
| 2 | **In 10 families the true bond is at most 3 at every depth while the ray bond grows** at a proved rate (1/2 in 8, 1 in 2): 262, 269, 302, 363, 579, 642, 662, 908, 975, 1144. This was already known: `BRANCH-DEPTH-20261112-001` certified exactly these ten as "exactly three at every positive depth" a day earlier. The certificate here is an independent re-derivation (10 of 10 agree). | proved by finite computation (post hoc, below); known in the program | the refutation the pre-registration named; P3's first part holds (λ_ray − λ_true = 1/2 in the four) |
| 3 | **The cause is a carried top port.** All 10 carry a top port down the ray; the size-3 bond is that port, a local of C_s and a member of a side copy one or two levels below C_s (never on the ray). Of the 20 carried families, the 10 shortened ones are exactly these; the other 10 have no such local bond and grow. BRANCH-DEPTH gave one such case as an example; the count is new. | proved (the 10) | — |
| 4 | **Most bounded reach in the program's census is carried.** Of BRANCH-DEPTH's 432 bounded one-definition rules (of 664), 320 carry a top port down the first ray, all at exactly 3; **112 are bounded without one** (73 at exactly 3, 39 eventually 4). The test is syntactic: it rules out a port passed down unchanged, not a value carried through constraints *(qualified after the referee)*. All 154 of its linear-lower-bound-only rules and 65 of its 69 linear ones carry none. | computed (BRANCH-DEPTH's records, read here) | — |
| 5 | **The same on the last-call ray** (`REACH-CENSUS-20261113-001`'s records): 99 of its 131 families bounded along that ray carry a top port along it, and 99 of the 107 carried ones are bounded; 32 are bounded without one. | computed | — |

## Answer

Much of whether growth survives side branches had been read when TRUE-BOND ran. With arbitrary side support, BRANCH-DEPTH had
classified 76 of these 226 families outright (linear growth in 66, exactly 3 at every depth in 10) and proved a linear lower bound
in 144 whenever a bond exists, leaving existence open there; six were unresolved. *("Largely answered" narrowed after the
referee.)* This study adds exact rates in 24 families (always equal to the ray's) and one finding:
three-quarters of the bounded reach in the census is a top port handed down unchanged, so the bond never crosses depth. The 112
rules bounded without such a port are the candidates for a bounded reach made by the law, once carrying through constraints is
also ruled out.

## The carried-port certificate (post hoc)

Found after the run, not pre-registered; `codex/thread_carried_certificate.py` (thread-written), checked by the advisor.

1. The pattern is a tree of copies glued at ports, so the projection onto subtree(C_s) is the subtree's allowed states with C_s's
   ports in R_s, the projection of the rest onto those ports.
2. R_0 is all eight states, and R_{s+1} is computed from R_s through C_s's knots and its other calls, each replaced by G, the
   bottomless port relation (exact by compactness).
3. In all 20 carried families R_1 = R_0, so R_s is all eight states at every depth, and subtree(C_s) has the same allowed states
   under the shift C_0 → C_s.
4. A satisfiability check on subtree(C_s) to depth 3 (boundary calls as G) finds a size-3 bond with a carried top port, a local of
   C_s and a side-copy member (under a cycle of positions, not the same top port at every depth; all ten use fixed points). It is therefore a bond at every depth: L(s) ≤ 3 for all s ≥ 1, and L(s) = 3 through the depths
   TRUE-BOND reached.

The closest standard fact is global consistency on a join tree (Beeri, Fagin, Maier and Yannakakis 1983), carried to the infinite
unfolding by compactness. The carried port is one distinction shared by every ray copy, so this result is settled by construction
once the start member is allowed to be carried (A81).

## Reading

**Interpretation.** A side branch can shorten a bond, but where a bounded reach comes from a carried port the top member is not
really at the top: it is passed down with the ray. A reach worth measuring starts from a distinction the depth-1 copy does not hold;
the 112 rules bounded without a passed-down port are where a fixed number of members may still tie the top to every depth, unless
a value is carried there through constraints.

## Lag cutoffs and census-only claims

The 226 families; 150 s and 5 GiB per family (two workers), the four flat ones 1,600 s and 7 GiB. Claims 1–3 are proved; claims 4
and 5 count other studies' certified verdicts against a structural test computed here. TRUE-BOND's two SystemErrors (families 248
and 1288) did not recur in this code; their cause is still not recorded.

## The Codex hand-off (for the owner)

- **Quality.** Codex's code was careful and honest about incompleteness. It labelled every partial graph, kept conservative upper
  bounds, and did not guess the ambiguous family list.
- **Friction.** None in the code. Its runner capped commands at 1,190 s and processes at 2.3 GiB (fit for its own session); a
  thread-written wrapper (`codex/thread_long_run.py`) raised the limits without touching the science code.
- **Saved.** All of the summary-graph code. But the method did not reach the families that mattered, and the decisive facts
  (the carried port, BRANCH-DEPTH's prior verdicts) came from reading the data and the program's own records.

## Review

The advisor model reviewed the plan cold before the code (`advisor_review_answer.md`). It also checked the certificate
(`advisor_certificate_answer.md`): sound as a proof by finite computation, settled by construction, with two cross-checks asked for.
v is a local of C_s itself, and w is off the ray (otherwise the ray bond would be bounded too). Both hold in all ten.

**TRUE-RATE-R1** (the referee thread with Codex, fresh code, `referee-R1/report.md`): confirmed with fixes. The shift argument is
sound, and the ten bonds (each a knot under K1–K3, stable with boundaries at depths 2 and 4), the carried counts, the mapping to
BRANCH-DEPTH (664 of 664, line offset +1) and three of the 24 exact rates reproduce. Three Narrowing: cycles of positions change which
top port is carried; "uncarried" is a syntactic test; BRANCH-DEPTH classified 76 outright, not 220. Three Not a block: the other 21
rates rest on this study's records; the missed prior work stays a Narrowing against TRUE-BOND; and the referee's own TRUE-BOND-R1
wording about the four flat families is corrected (logged here as a Narrowing, at the coordinator's request).

## Literature and provenance

Least fixed points (Knuth 1977); minimum cycle means (Karp 1978); join-tree consistency (Beeri, Fagin, Maier and Yannakakis 1983).
In the program: `BRANCH-DEPTH-20261112-001` (members-anywhere bonds on the same 664 rules, with per-rule certificates), and its
follow-ups `PAIR-CARRY-20261112-001` and `TWO-LEVEL-BOND-20261112-001`, missed by TRUE-BOND's and this study's prior-work checks.
Classification: known (claims 2–3, in substance), known-with-delta (claims 1, 4, 5).

## Workspace assumptions

A79 and A80 used; A81 added (the bond may start from a carried port), put under challenge by claims 3–4.

## Ratio

Substantive: the 24 exact rates, the carried-port account and counts. Administrative: the spec, the launches, this note.

## Corrections

Six (`docs/CORRECTIONS.md`, 2026-11-13), all **Narrowing**. At the close: TRUE-BOND's four candidate counter-examples are bounded
by a carried top port, not by side branches carrying the constraint down; TRUE-BOND's "open" answer, its and this study's "not found"
prior-work lines and PROVED-RATE's "says nothing yet about bonds through side branches" missed BRANCH-DEPTH. After the referee: a
cycle of positions carries *a* top port, not always the same one; "uncarried" rules out only the syntactic carry; BRANCH-DEPTH
classified 76 of the 226 outright and proved a conditional lower bound in 144, not "largely answered" for 220; and TRUE-BOND-R1's
"strongest evidence against growth surviving" is narrowed (the four bonds are local by identity).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — proved true rates | **Status:** Partially successful (refereed, confirmed with fixes) | 24 exact rates, all equal to the ray's; the 10 bounded families re-derived; BRANCH-DEPTH had classified 76 of the 226 outright |
| Local direction — the first-ray true bond | Full pivot | Its open part (existence in BRANCH-DEPTH's 144 conditional records) belongs to the BRANCH-DEPTH line |
| Broader exploration — G17 | Searching | The reach depends on the ray (A80) and on the start member (A81) |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Bounded reach splits into carried (identity) and uncarried (112) cases |

**Corrections:** six, all Narrowing (four after the referee). **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:**
A79, A80 used; A81 added, under challenge.
**Basket:** `TRUE-BOND-20261113-001#2` (2/3 Payoff, 3/3 Concreteness), `WITNESS-COUNT-20261112-001#1` (2/3, 3/3),
`PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `BOND-BALLS-20261111-001#2` (2/3, 3/3).

**Next step:** Full pivot — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What bounds the 112 uncarried rules | 2/3 — Substantial: the only bounded reach that is not identity | 3/3 — Ready | For each of BRANCH-DEPTH's 112 uncarried bounded rules (and REACH-CENSUS's 32 on the last-call ray), locate the bond's members and test whether a top bit is carried by forced equality through knots → a second mechanism, or every case reduced to carrying | Selected · awaiting go-ahead |
| 2 | Exact rates for the shortened families | 1/3 — Incremental: BRANCH-DEPTH's lower bounds stand | 1/3 — Conjectural | Find a summary that composes across one level without the tenfold growth → exact λ_true in the 62 shortened families, or a proof that none is finite | Alternative · parked |

1. Payoff 2: it separates a bounded reach made by the law from one made by identity. Concreteness 3: the certificates and the
   carried-port test exist; only the member search is new. The coordinator judges overlap with the BRANCH-DEPTH and REACH-CENSUS
   lines.
2. Payoff 1, Concreteness 1: the table grows tenfold per level, and no composing summary is known.

**Recommendation.** Full pivot from the first-ray true bond (its open part belongs to the BRANCH-DEPTH line); #1 if the coordinator
gives the go-ahead, otherwise stop here.
