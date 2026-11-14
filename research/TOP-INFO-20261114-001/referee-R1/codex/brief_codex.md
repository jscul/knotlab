# Independent recomputation and critique: TOP-INFO-20261114-001

You are an independent referee's assistant. The study's census code was written by another coding agent, so your recomputation
must be **fresh code** from the notes and the mathematics.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/TOP-INFO-20261114-001A/` or `proofs/TOP-INFO-20261114-001Z/`.
- **You may read:**
  - their data (JSON/JSONL, `census_full/`, `artifacts/TOP-INFO-20261114-001A/.../results.json.gz`) and the study Codex's
    `REPORT.md`;
  - `research/TOP-INFO-20261114-001/{top_info.md, preregistration.md, codex_spec.md, advisor_*.md}`;
  - the proofs `proofs/TOP-INFO-20261114-001B/TOP-INFO-20261114-001B-P001_top_info/proof.md`;
  - READ-RULE's and CARRY-BOUND's notes, proofs and data;
  - the census records `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`.
- **Reuse the earlier referee code.** It is under `research/READ-RULE-20261114-001/referee-R1/codex/` (pumping audit, exact
  relation-free bond search, coverage with R's some-state quantifier), `research/CARRY-BOUND-20261114-001/referee-R1/codex/`
  (`grow_core.py`, `grow_search.py`, `window_audit.py`, `scope_audit.py`) and `research/CENSUS-FORGET-20261114-001/referee-R1/codex/`.
- Write **only** inside `research/TOP-INFO-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 75 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Another job of the study's (a brute-force gate) may still be running on the machine; keep the load at that.
- Deliverable: `research/TOP-INFO-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

### 1. Attack the localisation lemma hardest

It is new and proved in a hurry (proof.md, "Localisation").
1. **The proof's steps.** Check each:
   - the count of member-free stretches, with members counted at their allocating copy;
   - the pigeonhole: a stretch of m·(Π+1) levels gives Π+1 equal states and two of them ≡ 0 mod Π;
   - that cutting keeps the stretch's product (taken from the stretch's top, over the blocks strictly inside) and its carry map, and
     the moved set's projection on every subset;
   - that lengthening the longest stretch restores depth s on the same residue, with the threshold
     s > (C+1)·m·(Π+1) + C;
   - the window bound B = C·m·(Π+1);
   - the wrapper offset.
2. **Side subtrees and the target's subtree.**
   - If a member-free run on the path to one member contains the branch point of another member's path, cutting it deletes that
     member. Is "occupied" defined so that this cannot happen?
   - Does the state need the copy type, and do the cut words stay legal?
   - Is "within C·(m+1) levels of where the subtree branches off" right?
3. **The meaning of "local".** Give the exact statement the proof supports.
   - Since B depends on the unknown C and m can be about 29,000 (Π = m!), say whether the Answer's "every bounded case shows up in a
     bounded window at the top and at the target, is proved" and conclusion 6's "a computable number of levels" are accurate.
   - Say what the lemma adds over the dichotomy. Boundedness was already semi-decidable from it, per READ-RULE's referee.
4. **Try to break it.** In the 65 "middle-member" families, and others, compute exact relation-free least bonds at a few depths.
   Report where their members sit: levels from the root, from the target, and in side subtrees.
   - Is any least bond, or every least bond at some depth, non-local in the proof's sense?
   - Do the 65's bonds really use members strictly between the top and the target, or is that inferred from "neither condition"?

### 2. Attack Theorem P′ (bond-pinning)

1. **The proof and its scope.** Check that T ⊆ main's ports, D ⊆ the covered copy's own distinctions, both shattered and jointly
   non-full, give a bond meeting both, so L(s) ≤ |T| + |D|.
2. **Per residue.** What exactly must hold on a residue for "bond-pinned on every residue" to give boundedness (every large depth,
   or infinitely many depths together with the dichotomy)? Is the census flag computed at the right depths and with the exact
   projection?
3. **The advisor's hiding relation.** Verify it by brute force (correlated, yet no bond holding x inside the ports and x). Check "plain
   pinning and bond-pinning never differ in the census" on a sample by your own code.
4. **Gate T1.** No grower is pinned or bond-pinned at a large depth (0 of 632). Check this on a sample by your own code.

### 3. The two-block window's exactness

Check the claim that the projection onto main's whole block together with c's block equals
{(a, b) : (a, b|ports) ∈ J′_w, b satisfies c's knots and its children's usual limits}. Pay attention to:
- main's own distinctions passed down as arguments and carried by identity, which must be merged;
- the start relation (main's other calls replaced by usual limits; main = S against a wrapper).

Compare with explicit unfolding on a sample by your own code. Verify the 9 newly two-block-bounded undecided families' bounds
directly (relation-free bonds at several depths and every residue).

### 4. The counts

- **The bounded split.** 4,484 + 523 + 65 = 5,072, but the note says "of the 5,074 bounded". Reconcile this against CARRY-BOUND's
  strict, advertised and full counts (5,072 / 5,074 / 5,076) and READ-RULE-R1's 4,484 of 5,067.
- **The two R-bounded families.** For `432127c418b0` and `981fdc202826`, check that Theorem R plus the dichotomy bounds them. Say
  whether this changes CARRY-BOUND's totals, or only adopts its full-admission count.
- **The new in-scope totals.** Recount bounded / growing / undecided (is it 5,085 / 632 / 72?).
- **The rest.** Check 588 = 93 + 9 + 486, the 3,515 overlap, the composition of the 523 (identity against order-label families), and
  the 15 order families that are not bond-pinned (T2).

### 5. Wording

- The Answer's "Pinning ... with nothing carried, as in the order families (another 10%)", given the composition of the 523.
- "88% / 10% / 1.3%": families or weight.
- "Their bonds use members between the top and the target".
- "Information, not carrying".
- Scope: covered targets only, meaning copies of S reached through S calls.

## Report format (`codex_report.md`)

- A verdict line: Confirmed, Confirmed with fixes, or Refuted.
- One short section per point.
- Each fix marked Block, Narrowing or Not a block.
- The files you wrote.
