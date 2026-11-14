Verdict: **Confirmed with fixes**.

Independent reconstruction confirms the two all-level states and strengthens
the two-knot observation to an all-level result. Fresh rigidity certificates
confirm the reduced #2 pattern at levels 6, 8, 10 and 12. The original study's
deleted certificates cannot be replayed. Fresh certificate coverage and its
remaining gaps are stated separately below.
State strings list values in integer-address order, starting at address 0.

## 1. Refutations and models

**Block — original-certificate replay.** The permitted registered directories
contain result records but no CNFs, LRAT/DRUP proofs or models. Consequently
there is no original proof-referenced CNF to compare with a reconstructed
one, and no original proof to check independently. Fresh recertification is
reported as fresh recertification. Retaining the actual CNF and certificate
is necessary for archival replay; a checker-success string cannot replace
them. The 294 dead rows have no retained proof/certificate hash fields,
despite the preregistration's promise to retain proof SHA-256 values; their
`pattern_sha256` fields identify patterns, not refutations. See
[the evidence inventory](certificates/inventory.json).

All 28 high-level cells of the seven alternating patterns were rebuilt;
their knot counts and pattern hashes match the registered data. Fresh
models validate **all 13 registered alive cells** against every knot.
Fresh refutations independently validate **12 of the 13 registered dead
cells**. **Narrowing — independent coverage:** #2 at 14 remains unconfirmed.
Its regenerated LRAT has 2,479,205 additions and the study's recorded byte
count, but hint-free RUP replay timed out at both 180 and 600 seconds. A
solver result and matching metadata are not promoted to a checked refutation.

| Pattern key | Registered dead levels in 13–16 | Fresh RUP replay |
| --- | --- | --- |
| `03702b84…` | 14,16 | both pass |
| `06473cf2…` | 13,15 | both pass |
| `333f0477…` | 14,16 | both pass |
| `40f24dbd…` | 13,15 | both pass |
| `91c75673…` (#2) | 14 | unconfirmed: checker timeouts |
| `cf32542e…` | 13,15 | both pass |
| `f4fd01e9…` (#3) | 13,15 | both pass |

The six additional cases across five other patterns yield four checked
dead verdicts, one checked alive verdict and one budget-undecided case
(`d3ce4bc6…` at 16, registered alive). There are no decided disagreements.
Altogether 34 cells were reconstructed and 30 freshly certified: 16 dead
and 14 alive. Exact cases, budgets and certificate links are in
[the sample ledger](certificates/audit_summary.json); the original two R1
undecided cells were rebuilt but not solved.

The independent earlier referee's `check_rup_fast` validates RUP additions
without solver code or LRAT hints. Every fresh certificate CNF is built
from both NAE clauses per distinct-image knot, plus the specification's
complement-symmetry unit at the smallest used address. Exact complement
invariance of the unconditioned formula is checked, so the conditioned
refutation also establishes unrestricted death. The Fano control passes;
non-RUP, malformed, truncated and out-of-bounds proofs are rejected, as are
invalid/incomplete models. Reversing composition order is also detected.
This confirms sampled mathematics, while the archival block above remains.

## 2. R2: the all-level states

**Confirmed.** Direct fresh computation checks every level 1–22. Address
parity satisfies #2 at every odd level >=3; first letter XOR last letter
satisfies #3 at every even level >=2.

The independent uniform argument follows each placement's three residual
map words, the three state-computation memories, three bits recording
whether each pair of full images has ever differed, length parity, and
length capped at the minimum. The identity is the empty word and copies
each input letter. A violating configuration requires three distinct
images and three equal state values. Induction on the input prefix proves
this interpretation. Exhausting the finite reachable configurations finds
no violation: the per-placement counts are `39,19,27` for #2 and
`19,27,25,27,35,29,23,27,27` for #3. See
[the uniform proof](automata/uniform_proof.md) and
[the explicit automata](automata/product_automata.json).

**Not a block — identity and dropped knots.** Both rules are essential and
are enforced here. At input `010`, #2's placement `[1,9,10]` has images
`101,101,000`, correctly dropped. Replacing the actual identity by map 0
also produces a false counterexample. Both deliberate errors are detected.
The study's mathematical statements handle these cases correctly; its
forbidden implementation and its reported count `27` were not audited.

## 3. R4: exactly two knots

**Confirmed for all even n>=4.** Enumeration through 22 finds exactly the
two stated violations. The fresh product automaton proves that retained
violating inputs are exactly the language `(00)+1(0|1)` for placement
`[0,8,10]`, and none for the other two placements: every comparison has
empty symmetric difference.

For `x=0^(n-2)1b`, the three images are
`0^(n-2)1b`, `00 1^(n-4)0(1+b)`, and `0 1^(n-3)0b`, with `1+b` read
modulo two. They are pairwise distinct. The third alone has second letter
1, and its last letter distinguishes b=0 from b=1. Thus there are exactly
two **unordered knots**, not merely two generating occurrences. An
independent algebraic derivation is in the uniform proof.

**Not a block — reduced level 16.** Removing these knots leaves parity and
its complement as explicit states at every even level >=4. This also
settles existence at 16 despite the registered SAT timeout and the original
`R4_holds: false` field. It proves no rigidity or death by itself.

## 4. R5: rigidity

**Confirmed independently at 6,8,10,12.** For the reduced pattern, parity
passes every knot. Fixing `X_0=0` and blocking the complete parity assignment
gives UNSAT at all four levels. The fresh DRUP proofs pass the earlier
independent RUP checker, with respectively 53, 654, 6,487 and 47,750
accepted additions. Complement symmetry then proves exactly parity and its
complement. Level 4 is a checked nonrigid control. Evidence:
[verified results](rigidity/verified_results.json).

The implication is valid with its full premises: if the reduced pattern
is rigid, its two known states are parity and complement; both violate the
deleted knots, so neither extends to a full-pattern state. The full pattern
is dead at that level.

**Narrowing — uniform rigidity remains open.** A product checking one
proposed state does not quantify over all assignments. With
`t_x=s_x XOR parity(x)`, each retained knot, whose majority-parity pair is
a,b and minority address c, says `t_a=t_b => t_c=t_a`. Uniform rigidity
would require a finite induction proving that these implications force t
constant at every even level >=6. Such a finite argument could suffice;
none is established by the finite SAT certificates or the R2 automaton.
The study records rigidity through 14; this audit freshly certifies through
12. See [the exact implication and remaining obligation](rigidity_argument.md).

## 5. Wording and evidence limits

**Narrowing.** The registered high-level R1 data contain 13 alive, 13 dead
and two undecided cells, rather than 28 decided cells. The gaps are
`333f0477…` at 15 and `91c75673…` at 16. The totals 775 cases, 420 alive,
294 dead, 61 undecided recount correctly. These are data summaries, not an
independent replay of all 775 cases.

**Narrowing.** “No state of this automatic kind exists for the other five”
must mean “none was found among the particular feature automata tried.”
The search establishes neither nonautomaticity nor nonexistence for all
automata of up to 424 states.

**Narrowing.** The reading's unqualified “the only states are the address's
parity and its complement” and “forces ... at every odd level” exceed the
evidence. Fresh checked #2 states different from both exist at n=3 and 5;
for example at 3, `01101000`. The study's positive odd-level rigidity
records start at 7 and stop at 13; level 15 is alive but rigidity is
undecided. Separately, `333f0477…` at 15 has undecided existence. The five
families therefore do not have an all-level rigidity theorem. Conclusion 4
also needs R5's lower bound of level 4 for the other families: #3 already
has checked noncomplementary states `0011` and `0110` at level 2. Omitting
the lower bound is false even within the levels read. See
[the checked wording counterexamples](wording_results.json).

**Not a block.** The justified uniform conclusions are R2, the exact
two-knot result proved here, existence after deleting those knots, and the
conditional rigidity-to-death implication. The remaining alternation and
rigidity claims require their stated finite ranges and explicit gaps. No
all-even death theorem follows. The supplied source descriptions are not
enough to independently assess the literature/novelty assertions; no
network search was performed.

## Files written

- This report, `audit_plan.json`, `audit_summary.json`, `execution_notes.json`,
  `wording_audit.py`, `wording_results.json`, and `delivery_validation.json`.
- `rigidity_audit.py`, `rigidity_verify.py`, `proof_capture_control.py`, `rigidity_argument.md`, and
  `rigidity/` with fresh CNFs, compressed DRUP proofs and JSON results.
- `automata/`: fresh product, vectorized and scalar-check scripts, the
  readable uniform proof, explicit automata, JSON results and validation.
- `certificates/`: fresh reconstruction/certification scripts, the permitted
  earlier referee's checker, retained new certificates/models and JSON results.

All authored files and retained evidence are confined to this referee
directory. **Not a block — execution deviation:** initial PySAT proof
tracing used the library's default unlinked temporary streams in `/tmp`,
contrary to the strict output-location rule. They closed with their solvers;
the replay scripts now explicitly redirect temporary streams into this
directory. The initial checker compilation may also have used compiler
scratch in `/tmp`. No unrelated files were modified. Forbidden study source was
neither opened nor imported. No Git mutation, publishing or network operation
was performed. The evidence is independently implemented relative to the
study (V2), not external replication or a trusted-kernel proof.
