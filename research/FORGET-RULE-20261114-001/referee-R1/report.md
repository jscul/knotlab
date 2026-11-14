# Referee report FORGET-RULE-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with one Block on Rule A as written.**

**The Block.** The stated rule lets a port in F be peeled even when it is an argument of the call being followed, and that version
is false. Codex built a living family outside the census where it certifies forgetting, but no power of the relation is
rectangular.

**The repaired rule.** Never peel an argument of the call, including a port in F. It survives a search of about 240,000 living
families outside the census with no false certificate. It also reproduces **every field** of the held-out and training tables, so the
study's computation evidently used the guarded rule. The results stand; the rule's text and proof must be repaired.

**What else holds.**
- **Rule N** holds, with a living or nonempty premise to state.
- **Climbing paths.** Top-down tracking sees every path that climbs back up.
- **The generic start.** It is necessary, and it fixes the 8 training errors before the held-out read: `rule_A.py` was committed at
  16:36:25 and `heldout.json` written at 16:36:48 (referee check).

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the freeze chronology.
  - Read the proof's points (b) and (c), and agrees with Codex.
  - Missed the argument guard on first reading.
  - Classified the fixes.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, built the rules fresh, ran the search and
  recounted the census, in about 17 minutes. It opened none of the study's Python and wrote only in `codex/`, starting with
  `codex/codex_report.md`. The 12 MB `heldout_fresh.jsonl` is committed gzipped.
- **Advisor.** The advisor model was not consulted.

## 1. The objects gate

It reports `missing ## Prior work in the program section`. Stage 1 was frozen at 00:28 UTC on 2026-11-14, after the rule was
introduced at 17:36 UTC on 2026-11-13, so the section is owed. **Not a block** (process). Add it.

## 2. Rule A as written (Codex)

**What the text says.** The stage-2 text reads: "That distinction must be an own distinction not among call i's arguments, or a port
in F." Read literally, the "not among the arguments" guard applies only to own distinctions.

**The counterexample.** S(p0, p1, p2) with own u, v: NAE(p0, p1, p2), NAE(p0, p2, v), SELF(p1, u, v), raw
`[[3,2,[["K",[0,1,2]],["K",[0,2,4]],["SELF",[1,3,4]]]]]`. It is living, and N is acyclic.
- **What literal A does.** It reaches M empty after 3 calls, peeling port 1 at the second step, although that port is the next
  argument 0.
- **What the relation does.** It is R = NAE(a, b, c) ∧ d = b ∧ NAE(a, c, f), and its powers alternate with period two without ever
  becoming rectangular. This is checked exactly and by a separate pure-set implementation.
- **An isomorphism-free witness.** Since the family has isomorphic presentations in the census (all outside the study population),
  Codex also gives a second witness with no isomorphic presentation there.
- **What the guarded rule does.** It rejects both.

**The repair.** eligible(v) = v not among call i's arguments, and (v an own distinction or a port in F).

**The search.**

| Pool, outside the census | Living, decided exactly | Literal A false certificates | Guarded A certificates | Guarded false certificates or bound failures |
| --- | ---: | ---: | ---: | ---: |
| exhaustive grids plus random one- and two-definition families | 192,332 | 60 | 18,125 | 0 / 0 |
| two-definition helpers with 3 to 6 ports | 46,117 | 3 | 7,017 | 0 / 0 |

**On the census.** The literal rule also gives 1,502 and 266 wrong r bounds. On the census itself, literal A certifies 1,372 held-out
families with 273 wrong bounds, so the literal H2 and H3 would fail. The guarded rule reproduces the published numbers exactly.

**The verdict.** **Block** (Rule A's statement and proof as written). The census results computed with the guarded rule stand.

## 3. The proof, repaired (the referee and Codex)

**(a) Peeling is exact under the guard.**
- **The invariants.** F contains no top-port identity and nothing a retained upper constraint touches. A peeled distinction is never
  in the next frontier.
- **Why that suffices.** A peeled distinction then occurs in exactly one constraint of the whole stretch. That constraint (NAE, or a
  relation full on every two coordinates) projects to the full relation on the rest.
- **What skipping upper layers does.** Not revisiting upper layers only skips peels, so the rule stays conservative.

**(b) Top-down tracking sees every path.** It joins the frontier partition induced by everything above with the new block's
components. Any excursion into upper layers enters and leaves through a frontier whose connectivity is already recorded. Codex
checked 34,764 transitions on 5,794 six-layer words against complete-prefix connectivity, including the x ≠ y gadget. **Not a
block.**

**(c) The generic start is necessary.** A start conditioned on main gives 8 false certificates in training (and 9 in the held-out
half), and the generic start rejects all 17. The fix was frozen before the held-out read (section 1 of the summary above). **Not a
block.**

**(d) Rectangularity and growth have different premises.** Rules N and A and H1 to H4 are statements about relations alone. Reading
forgetting as a growing free-bond lower bound needs the gap argument, which covers copies of S reached through S calls, with
2 + ⌊(s − 1)/r⌋ for wrappers. CENSUS-FORGET-R1 found that it does not cover other recursive definitions with own distinctions or a
delayed S. **Narrowing.**

## 4. Rule N (Codex)

It holds on every living family tested, and on all 12,772 census families. The proof needs a living or nonempty premise: an
unsatisfiable family with an identity cycle has an empty, hence rectangular, relation. State the premise. **Narrowing.**

## 5. The held-out read (Codex)

**The rebuild.** All 12,772 blocks and 26,243 per-call relations were rebuilt fresh, together with every exact decision. All match
CENSUS-FORGET, and the 66 capped are decided non-forgetting.

**The guarded rule reproduces every field.**
- **H1.** No violation.
- **H2.** 1,051 certificates, none false, all within their r bounds.
- **H3.** 1,051 of 2,861 = 36.7%, against 37.1% in training, with each stratum within 8 points.
- **H4.** 2,096 of 2,096 chains and 765 of 817 non-chains (93.6%) without an identity cycle forget. **Not a block.**

## Fixes for the thread

1. **Repair Rule A's text and proof.** Excluding every argument of the followed call from peeling, including F ports, is the
   operative rule. Cite the counterexample to the literal reading, and state the invariants. **Block** (the statement as written).
2. **Rule N.** State the living or nonempty premise. **Narrowing.**
3. **Scope the reading of A as growth** to copies of S reached through S calls, with the shift for wrappers. **Narrowing.**
4. **Add the prior-work section** that the objects gate requires. **Not a block.**

## Files

`codex/`: Codex's brief, report and evidence. That covers `independent_rules.py`, `search_counterexamples.py`, `wide_search.py`,
`validate_counterexample.py`, `counterexample.json`, `structural_and_boundary_controls.*`, `recount_heldout.py`,
`audit_starts_and_counts.py`, `check_prefix_invariant.py`, `prefix_invariant.json`, `proof_critique.md`, and the summaries.
`heldout_fresh.jsonl` is committed gzipped.
