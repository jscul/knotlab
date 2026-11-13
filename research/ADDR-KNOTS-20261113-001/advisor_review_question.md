You are an advisor reviewing a frozen design before a registered census runs. Find holes, things settled by construction that the design treats as open, predictions that cannot fail or cannot be checked, statistical flaws in the matched-density design, and spec errors a coder would trip on. Be concrete and brief (under 1,000 words). Also judge the new words listed at the end. You reviewed the first design earlier (your answer: one knot rule always lives; dense rules needed; activity probably adds nothing at matched density). Below: the proof note, the pre-registration and the Codex spec.

Context on the program's words: "distinction" = Boolean variable, "knot" = three-place not-all-equal constraint, "state" = an allowed assignment (so automaton states cannot be called states), "depth" is taken by the glossary for holes, "move" is taken for growth steps. The program avoids words from two- or three-dimensional space (tile, surface, lattice...) for its own objects, giving the literature's name once.

New words proposed: "address" (a binary word), "level n" (addresses of length n), "relabeling" (an automaton state / the tree automorphism it defines), "knot rule" (a triple of words in the relabelings), "part" (addresses sharing their last letters; the literature's tile), "joining knots" (knots holding addresses inside and outside a part), "activity" kept as the literature's term. Are these good? Any collision or better choice?

Specific questions:
1. Is the matched-density comparison sound: binning by knots per address at level 12, Bonferroni over eligible cells, the "differs / same / unclear" rule, E as primary? Is density at level 12 the right matching variable, or should it be the minimum/mean over levels, or should the comparison be a logistic regression with density as a covariate?
2. Is H-bound (bounded die less at matched density) a reasonable rival to H-dens? Which do you now expect, and why?
3. P3 (bounded first deaths by level 8), P4 (late exponential deaths at >= 9), P5 (>= 85% of weight alive): are the thresholds sensible or arbitrary? Anything settled by construction?
4. The Lemma A proof: any remaining hole (ports that are list members are now handled by recording each port's lists)?
5. The parts: I first wrote "a part = addresses sharing a prefix" in an unpublished report, then corrected to "sharing their last letters" (tiles), since automata read first letters first. Is the corrected statement right, including that the joining count J_n (knots holding addresses ending in 0 and in 1) is bounded for bounded activity and grows otherwise?
6. Spec: the conflict budget (2M, CaDiCaL 1.9.5 via pysat), the lifted phase hint, fixing one variable for complement symmetry, the activity algorithm (Sidki's cycle criterion), V-act-class thresholds (theta_40/theta_39 >= 1.25 for exponential with s <= 5): any error?

=== PROOF NOTE ===
# Growing interfaces: shared lists, one knot rule, finite types

Proof note of `ADDR-KNOTS-20261113-001B` (epic `ADDR-KNOTS-20261113-001`; G17, with G1), 2026-11-13, written by Claude at the
coordinator's go-ahead before the census of `ADDR-KNOTS-20261113-001A` ran. The canonical K1–K3 test is unchanged; every knot below
is a three-place not-all-equal knot on three distinct distinctions. **Referee pending.**

## Why

`NEST-COUNT-20261112-001` proved that every nested pattern of the A79 language is finite-state, because each nested copy meets the
rest through three distinctions, and read the contrast with the plane as "the interface size is what separates decidable nesting
from undecidable" (an interpretation). The owner's recursion picture asks for nested parts that depend on the larger pattern. This
note settles, before any census, what two natural ways of letting a part meet a growing number of its container's distinctions do
by construction.

## 1. Shared lists stay finite-state (Lemma A)

**The language.** A description of the A79 language (`SHORT-DESC-20261112-001`'s `dlang.py`: definitions with ports, own
distinctions, calls of K, of earlier definitions and of SELF, to a depth t), with h **lists** added. A self-holding definition may
also make three new kinds of call:

- **enlist (p, c):** its own distinction p goes on list c for every copy nested inside this copy (its descendants);
- **list knots**, read against the members of the lists that this copy sees: (c; p, q), a knot (u, p, q) for every member u of
  list c; (c, c′; p), a knot (u, u′, p) for every two distinct members u of c and u′ of c′; (c, c′, c″), a knot on every three
  distinct members, one from each list.

A copy **sees** the members enlisted by the copies that contain it (its ancestors), never its own or a sibling's. So the number of
the container's distinctions that a part's knots touch grows with depth, without bound.

**Lemma A.** For every definition D and depth t, whether a copy of D at depth t, with everything nested inside it, allows a state,
given the values on its ports and on every list member it sees, depends on the members only through their **profile**: for each
nonempty set S of lists and each value b, the number of seen members other than its ports lying on exactly the lists S with value
b, capped at 3, together with the set of lists each port lies on (a port can be a member, enlisted by an ancestor and passed down).
So what a definition allows at depth t is a set R_t(D) of pairs (port values, profile), a subset of a fixed finite set, and
R_t = Φ(R_{t−1}) for a fixed map Φ built from the description. Hence, as in `NEST-COUNT-20261112-001` T1: life at depth t is
eventually periodic in t, with preperiod plus period at most the number of possible tuples (R(D))_D; the bottomless pattern is
decided by a greatest fixed point; and the top reads depth only modulo the period. *Proved.*

*Proof.* (i) A list knot placed by the copy holds or fails according to the values of the members it names and of the copy's own
distinctions. Each form names at most three distinct members, and the forms quantify over all members of the named lists, so
whether every knot of the form holds depends only on which (lists held, value) combinations occur, and with what multiplicity up
to 3 (three distinct members of one combination are needed only by the third form), with the ports' own values and lists known
separately because a knot skips a member that coincides with one of its own places. That is the profile. (ii) The profile a child
copy sees is the parent's profile with the parent's newly enlisted distinctions added, so it is a function of the parent's profile
and the parent's own values. (iii) Siblings see the same profile and nothing of each other's lists, so given the parent's values
their subpatterns are independent, exactly as SELF copies are in the A79 language. (iv) So the set of (port values, profile)
under which a depth-t copy of D lives is computed from the same sets for the definitions it calls at depth t − 1 (and the knot at
depth 1) by a fixed map. The domain is finite, so the sequence R_t is eventually periodic; the fixed-point statements are
`NEST-COUNT-20261112-001`'s T1(b) word for word, with the profile carried alongside the port values. ∎

**What follows.** A part can meet an unbounded number of its container's distinctions and the pattern is still finite-state. What
keeps it finite is that the part treats all members of a list alike: it can tell apart at most a bounded number of different
ways of being met. So the size of the interface is not what separates decidable from undecidable nesting; the number of different
ways a part can be met is. *This narrows NEST-COUNT's reading (logged in `docs/CORRECTIONS.md`, Narrowing, for the list forms
above only).* The classical form of this is the literature's clique-width and rank-width (Courcelle, Makowsky and Rotics 2000;
Courcelle and Oum 2007): bounded rank keeps monadic second-order questions decidable; Lemma A is the plain not-all-equal case of it,
known in kind.

**Direct influence by construction.** If the top enlists a distinction u₀ on list c and every self-holding copy places a knot form
on c, then at every depth a knot holds u₀ together with that copy's own distinctions: influence across depth at one knot, put in by
the list, as a carried top port is (A81).

## 2. Knots placed by relabelings of addresses

**The object.** An **address** is a word over the letters {0, 1}; **level n** is the set of addresses of length n. A **relabeling**
of a finite automaton (the literature's states of an invertible Mealy automaton, which define automorphisms of the tree of words)
reads an address from its first letter, keeps or swaps that letter, and hands the rest of the address to a next relabeling chosen
by the letter read. A **knot rule** is a triple (g₁, g₂, g₃) of relabelings or products of relabelings; at level n it places the
knot {g₁(x), g₂(x), g₃(x)} for every address x of length n whose three images are distinct. Relabelings keep length and act on
first letters before later ones, so dropping the last letter of every address sends level n + 1's knots onto triples of level n.

**Proposition B0 (one rule on two letters always lives).** For any three automorphisms g₁, g₂, g₃ of the binary tree of words, the
level-n pattern of the single rule (g₁, g₂, g₃) allows a state at every level n. *Proved.*

*Proof,* by induction on n. Each gᵢ either swaps the first letter of every address or of none (its root letter permutation σᵢ). If
the σᵢ are not all equal, the three images of every address do not all have the same first letter; give every address its first
letter as its value, and every knot holds both values. If they are all equal, every knot lies inside the addresses with one first
letter h, and those knots are the level-(n − 1) pattern of the single rule (g₁|_a, g₂|_a, g₃|_a) on the remaining letters, where
a = h ⊕ σ is the first letter read and gᵢ|_a is the relabeling handed the rest; the two halves share no knot. Level 1 has two
addresses and no knot. ∎

A second proof (the advisor model's): with y = g₁(x) the knots are {y, g y, g′ y}, every cycle of a permutation of a level of the
binary tree has length a power of two, so even, and an alternating value along a cycle extends along shortest paths to it.

**Remarks.** (a) The proposition needs one rule. With several rules the root letters can disagree from rule to rule, and patterns
die: the exploratory run in `research/ADDR-KNOTS-20261113-001/exploratory/` found 336 of the 5,832 three-relabeling automata with
all four triples of {identity, three relabelings} dying within level 10 (*computed, exploratory, not registered*). (b) It needs two
letters. On seven letters the single rule (e, a, a³), with a adding 1 modulo 7 to the first letter and leaving the rest, places on
every seven addresses that differ only in their first letter the knots {x, x + 1, x + 3}, which is the Fano pattern (the
difference set {0, 1, 3} modulo 7), so it is dead at every level. *Proved; checked.* (c) In general a smallest dead pattern needs
at least as many knots as distinctions (Seymour 1974), and one rule places at most one knot per address, so with one rule only an
exactly balanced dead part can occur; whether one occurs on three to six letters is open (on three letters with two relabelings
none to level 6, exploratory).

**Where a part meets the rest.** The words sharing their last k letters v form a **part** (the literature's tile): inside it, a rule
acts on the free first letters as at level n − k, and a knot leaves the part only where a relabeling handed the tail changes it. The
number of such knots is governed by how many addresses of each length hand a relabeling a non-identity one (the literature's
activity, Sidki 2000): bounded activity gives parts joined by a bounded number of knots at every level (the literature's finitely
ramified case), polynomial activity a number growing as a power of the level, exponential activity one growing exponentially. A
part's inner knots are the same at every tail; how it is joined to the rest depends on its tail. Bartholdi 2022 (Groups Geom.
Dyn.) proved the domino problem decidable on the bounded case and undecidable on a linear-activity example, and conjectured, for
contracting groups, decidable exactly when finitely ramified. *Known.* Whether the not-all-equal law on the bounded case is
finite-state by Bartholdi's construction, applied to knots instead of edges, is expected but not proved here.

## 3. Finite types (a remark, unchecked)

Let definitions take definitions as arguments (the literature's higher-order recursion schemes), every definition with a bounded
number of ports. A ground definition denotes a relation on its ports; a definition of higher type denotes a function between finite
sets of such denotations, again a finite set. If depth t is the number of unfoldings, each depth replacing every recursive call by
the definition at depth t − 1, then the denotations at depth t are a fixed function of those at depth t − 1 on a finite set, so life
is eventually periodic in t. *My argument, unchecked; flagged for the referee.* The advisor model held the opposite view (decidable
but not periodic in depth). It may be right if depth is measured instead as the longest chain of nested copies in the expanded
pattern, which higher-order schemes can make grow like 2^t, so that a fate read along that measure need not repeat.

## Prior work

Treewidth and hyperedge replacement, clique-width and vertex replacement (Courcelle and Engelfriet, *Graph Structure and Monadic
Second-Order Logic*, 2012); Courcelle, Makowsky and Rotics 2000; Courcelle and Oum 2007; Seymour 1974 (on minimal non-two-colourable
hypergraphs); Sidki 2000 (activity); Bartholdi 2022 (*Monadic second-order logic and the domino problem on self-similar graphs*);
Barbieri and Sablik 2016; Bondarenko et al. 2008 (groups of three-state two-letter automata). **Ours:** the not-all-equal law on these
patterns, Lemma A's profile argument in this language, B0's first-letter induction, and the narrowing of NEST-COUNT's reading.
Classification: known in kind (Lemma A, the remark on finite types), known-with-delta (B0 and its two limits).

## Checks

`check.py` (run `.venv/bin/python -B check.py`): B0 on every automaton with at most two relabelings and every triple of words of
length at most 2 in its relabelings, and on 2,000 random (three-relabeling automaton, triple) pairs, levels 1 to 10, by SAT; the
Fano rule dead at levels 1 to 4 on seven letters. Lemma A and §3 are by hand only.

=== PRE-REGISTRATION ===
# Pre-registration: knots placed by relabelings of addresses

Epic `ADDR-KNOTS-20261113-001` (G17 Typical and rare meeting patterns, with G1; program topology, group spacing), 2026-11-13, at the
coordinator's go-ahead after John confirmed the direction ("Yes, let's proceed with that", 16:39 UTC). Written before any registered
run. The census `ADDR-KNOTS-20261113-001A` is computed by code Codex writes from [codex_spec.md](codex_spec.md) and run by the
thread; the proof note `ADDR-KNOTS-20261113-001B` is [proof.md](../../proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md).
The canonical K1–K3 test is unchanged.

## The question

Every nested study so far let a part meet the rest through a fixed number of distinctions, and `NEST-COUNT-20261112-001` proved
such patterns finite-state. The owner's recursion picture is the excluded case: "the nested structures depend on the larger
structures to know where they are ... for logic, it can hop around." Under a description weighting in the spirit of A79, among
not-all-equal patterns whose knots are placed by a small automaton on addresses, so that parts meet the rest through a number of
knots that may grow with the level: how common is each fate (resolves to nothing, lives a while and ends, lives at every level
read), and does how fast the joining grows change the fates once knot density is matched?

## The question in standard terms

For two-colourability (NAE-3-SAT) of the 3-uniform hypergraphs {g₁x, g₂x, g₃x} on {0,1}ⁿ, with g's words of length at most 2 in
the states of a random invertible binary Mealy automaton: the satisfiability profile over n = 1..12, by Sidki activity class
(finitary, bounded, polynomial, exponential) at matched hyperedge density, under a prefix-code sampling.

## Words

From the proof note: **address**, **level** n (addresses of length n), **relabeling** (the literature's automaton state, here the
map on addresses it defines), **knot rule** (a triple of words in the relabelings), **part** (the addresses sharing their last
letters), **joining knots** (knots holding addresses in a part and outside it), **activity** (the literature's term, Sidki 2000: how
many addresses of each length hand a relabeling a non-identity one). "Level" is used instead of "depth", which the guide's glossary
gives to holes. A level is not a growth: level n + 1 is a new pattern lying over level n, so A72's "adding knots never brings a state
back" does not apply and a return is possible in principle (P2 tests it).

## The object and the weighting (frozen; details in the spec)

- **Automaton:** s relabelings, each a swap bit and two successors; two letters.
- **Words:** e and the words of length 1 and 2 in the relabelings (1 + s + s² words; `q r` means r first, then q).
- **Description:** an automaton and a list of r knot rules, each an unordered triple of distinct words. The level-n pattern is the
  union over rules of the knots {g₁x, g₂x, g₃x}, x of length n, kept when the three addresses are distinct.
- **Weighting (A79's kind):** fair coins; s by Elias gamma (s ≤ 5, else rejected and counted), each swap bit 1 bit, each successor
  uniform, r by Elias gamma (r ≤ 8), each rule uniform among the C(1 + s + s², 3) triples; weight 2^−length.
- **Populations.** **W:** 40,000 fair-coin draws (seed 20261113). **E:** every automaton with s = 3 (5,832) with 3 rule lists each,
  and every automaton with s ≤ 2 (66) with 30 rule lists each, rule lists drawn by the rule code with r = 1 + Elias gamma (so r ≥ 2,
  capped at 9), seed 20261114. E exists for power in the matched-density comparison; W gives the weights.

## Settled by construction (before the run)

- **B0** (proved): one rule (one word triple) on two letters lives at every level. So every description with one distinct rule, and
  every s = 1 description (its three words give one triple), lives. The run reports the share of weight settled this way.
- **Finite-state where bounded** (expected, from Bartholdi 2022's construction applied to knots; not proved here): bounded and
  finitary activity give parts joined by a bounded number of knots.
- **Lemma A** (proved): the other way to let a part meet a growing number of distinctions, uniform shared lists, stays finite-state;
  it is not censused.

## Measures

Per description and level n = 1..12: the knot set (deduplicated), its size, the verdict (alive, dead, or **undecided** when the
solver's conflict budget runs out), and the joining count J_n (knots holding addresses ending in 0 and in 1). Then:

- **Fate within level 12:** F0 no knot at any level read; F1 resolves to nothing (dead at its first level with knots); F2 ends
  (alive at some level, dead at a later one); F3 alive at every level read; FU undecided (a level with no verdict leaves the class
  open). Undecided is its own cell, never folded into alive. A return (dead, then alive at a later level) is flagged.
- **Density** ρ = knots at level 12 / 4,096.
- **Activity class** (exact, from the automaton, over the relabelings the rules use): finitary, bounded, polynomial of degree d, or
  exponential, by the strongly connected parts of the non-identity relabelings (spec, "Activity"). The measured joining growth
  (J_10, J_11, J_12) is reported beside it as a check, not used to classify.

## Predictions and failure criteria (frozen)

Shares are reported raw, given s ≥ 3, and given density bin, by count (distinct descriptions) and by weight (W's draws).

| # | Prediction | Fails if |
| --- | --- | --- |
| P1 | Every description with one distinct rule is alive at every level read (B0). | Any is dead: a bug; the run is invalid until fixed. |
| P2 | No return: no description is dead at a level and alive at a later one. | Any return (reported as a finding). |
| P3 | Bounded and finitary descriptions that die first die by level 8. | Any first death at levels 9 to 12 among them. |
| P4 | Late ends exist: some exponential description first dies at level 9 or later. | None does. |
| P5 | Under the weighting, at least 85% of W's draws with a knot are alive at every level read. | Below 85%, or undecided above 5%. |
| H-dens | (the advisor's) At matched density, activity adds nothing to the death share. | Some eligible cell "differs" (below). |
| H-bound | (the thread's) At matched density ρ ≥ 1.5, bounded descriptions die less often than exponential ones. | Some eligible bounded-against-exponential cell at ρ ≥ 1.5 is "same" or has bounded higher. |

**Matched-density design (the study's core, frozen).** Population E, distinct descriptions, F0 excluded, FU excluded and counted.
Density bins [0, 1), [1, 1.5), [1.5, 2), [2, 2.5), [2.5, 3), [3, 4), [4, 6), [6, ∞). In each bin, the death share of a class is the
share of F1 or F2. A comparison of class C against exponential is **eligible** in a bin when both have at least 30 decided
descriptions there and fewer than 10% undecided. Δ = share(C) − share(exponential), with a 95% Newcombe–Wilson interval, Bonferroni
over all eligible cells (all classes, all bins). A cell **differs** when the corrected interval excludes 0 and |Δ| ≥ 0.10; is
**same** when the uncorrected interval lies within [−0.10, 0.10]; else **unclear**. H-dens and H-bound are rivals; both can fail.
If no bounded-against-exponential cell at ρ ≥ 1.5 is eligible, H-bound is **not testable at s ≤ 3**, reported as such (bounded
automata in this language then cannot make dense patterns often enough to compare). W is read the same way as a secondary, by
weight, and never overrides E.

## Validation gates (in the spec; any failure invalidates the run)

V-act (relabeling action against a recursive reference), V-sat (verdicts against brute force at levels ≤ 4, and two solvers on
levels 9 and 10), V-B0 (the proof note's check), V-act-class (exact activity against counted active sections to length 20),
V-code (s and r frequencies against Elias gamma), V-resume (a killed and restarted run gives identical records).

## Stop rule

One Codex hand-off, one registered run by the thread, its frozen summary, a referee hand-off; report and hold. Nothing is claimed
beyond level 12, two letters, five relabelings, words of length 2, or the stated weighting. A finite census proves no all-level
statement.

## Prior work and what is ours

Known: Bartholdi 2022 (domino and monadic second-order logic on self-similar graphs: decidable when bounded, undecidable on a
linear-activity example; conjecture for contracting groups); Sidki 2000 (activity); Bondarenko et al. 2008 (three-state two-letter
automata); D'Angeli, Donno and Nagnibeda (Ising and dimers on Schreier graphs); Seymour 1974; random NAE-3-SAT's threshold near 2.1
knots per distinction. Ours: the not-all-equal law on these patterns, the description weighting over automata and rules, the fate
census within level 12 and the matched-density comparison. Novelty to be checked again at close.

## Advisor

Consulted twice before freezing: on the design ([advisor_design_question.md](advisor_design_question.md),
[advisor_design_answer.md](advisor_design_answer.md): B0 and the rival prediction H-dens are its) and on this file and the spec
([advisor_review_question.md](advisor_review_question.md), [advisor_review_answer.md](advisor_review_answer.md)).

## Exploratory runs disclosed

Before this file: the four scripts in [exploratory/](exploratory/) (single rules on two and three letters; all four single-relabeling
triples at s = 3 to level 10; the activity split), reported to the coordinator. Their populations and rule language differ from the
registered ones (no products of relabelings, no weighting).

=== CODEX SPEC ===
# Codex specification: knots placed by relabelings of addresses (ADDR-KNOTS-20261113-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it: write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/` (CODEX below). Modify, move or delete
  no other file. Run no git command that changes anything.
- Use `.venv/bin/python -B` (numpy and python-sat are installed). At most **4 processes** at a time; keep total memory under about
  8 GB. Other studies share the machine. Touch no process you did not start.
- Repository material only; no network. You may read
  `proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/` (`proof.md`, `check.py`) and
  `research/ADDR-KNOTS-20261113-001/preregistration.md`. Do not read `research/ADDR-KNOTS-20261113-001/exploratory/`.
- **Do not run the full job.** Write the code, run the validation gates and the smoke run below, and stop. The full run is launched
  by the thread from your runner, so it must be resumable and independent of your session.

## Objects

- **Addresses.** Level n is the set of binary words of length n, stored as integers 0 .. 2ⁿ − 1 with the **first letter the most
  significant bit**. "Dropping the last letter" is `x >> 1`; "the last letter" is `x & 1`.
- **Automaton.** s relabelings 0 .. s − 1; relabeling q has a swap bit `sw[q]` and successors `d0[q]`, `d1[q]`. Applied to an
  address it reads letters from the first: at each letter b it outputs `b ^ sw[q]` and moves to `d0[q]` if b = 0, else `d1[q]`.
- **Words.** The identity `e` (written `()`), the words of length 1 `(q,)`, and of length 2 `(q, r)`, which applies **r first,
  then q**. The word list W_s is in exactly this order: `()`, then `(0,)` .. `(s−1,)`, then `(q, r)` in lexicographic order of
  (q, r). |W_s| = 1 + s + s².
- **Knot rule.** An unordered triple of three distinct words of W_s, stored as a sorted triple of their indices in W_s.
- **Description.** (s, sw, d0, d1, rules), rules a list of r knot rules (repeats allowed). Its **key** is (s, sw, d0, d1, the sorted
  set of distinct rules); two draws with equal keys are the same distinct description.
- **Level-n pattern.** For every rule (w₁, w₂, w₃) and every address x of length n, the triple (w₁(x), w₂(x), w₃(x)), kept when the
  three are distinct, as a sorted triple; the pattern is the set of kept triples (deduplicated over rules and addresses).

## The weighting and the two populations

Fair coins, as in `experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py` (read it for
`gamma`; do not import it). Each draw i uses its own `random.Random(f"{seed}-{i}")`. Bits: Elias gamma counts its bits; a uniform
choice among k options costs log₂ k bits (fractional).

1. s = gamma; if s > 5, the draw is **rejected (s)**: record it with its bits and stop.
2. For q = 0 .. s − 1: `sw[q]` one fair bit (1 bit); `d0[q]` uniform in range(s); `d1[q]` uniform in range(s) (log₂ s bits each).
3. r = gamma; if r > 8, **rejected (r)**. For each of r rules: a uniform 3-subset of range(|W_s|): draw it as a uniform index into
   the list of all 3-subsets in `itertools.combinations` order (log₂ C(|W_s|, 3) bits).
4. Total bits = the sum. The draw's weight is 2^−bits; sampling by these coins samples descriptions by weight.

- **Population W:** draws i = 0 .. 39,999 with seed `20261113`.
- **Population E:** every automaton with s = 3 in the order `for sw in product((0,1), repeat=3): for d0 in product(range(3),
  repeat=3): for d1 in product(range(3), repeat=3)` (5,832), with 3 rule lists each; then every automaton with s = 1 and s = 2 in the
  same order (2 + 64), with 30 rule lists each. A rule list for automaton number a, list j, uses `random.Random(f"20261114-{a}-{j}")`:
  r = 1 + gamma, capped at 9 (if 1 + gamma > 9, set r = 9 and record `r_capped: true`), then r uniform 3-subsets as in step 3.
  Record its bits as in the weighting (for reference only; E is not weighted).

Compute each distinct key once (both populations share a cache keyed by the description key); every draw record points to its key.

## Activity (exact)

Over the relabelings U that occur in the description's rules (letters of its words, the identity word contributing none):

1. q is **trivial** when no relabeling reachable from q (through d0, d1, including q itself) has swap bit 1.
2. Build the graph on the non-trivial relabelings reachable from U, with an edge q → d0[q] and an edge q → d1[q] whenever that
   successor is non-trivial (two parallel edges when d0[q] = d1[q] is non-trivial).
3. Strongly connected components. A component is **cyclic** if it contains at least one edge (a self-loop counts).
4. If some cyclic component has more edges than vertices (parallel edges counted): **exponential**. Otherwise every cyclic component
   is one simple cycle. If there is no cyclic component: **finitary**. Else the degree d = (the largest number of cyclic components
   on one path of the component graph) − 1: d = 0 **bounded**, d ≥ 1 **polynomial** with degree d.
   (If U is empty, every rule uses only `()`, which cannot happen since a rule has three distinct words; still, guard it.)

## Per description, per level n = 1 .. 12

- `knots_n`: the size of the level-n pattern.
- `join_n`: the number of its knots holding an address ending in 0 and one ending in 1.
- `verdict_n`: alive (1), dead (0), or undecided (null):
  - If the pattern is empty: alive.
  - Otherwise a SAT instance on variables 1 .. 2ⁿ (variable x + 1 for address x): for each knot (a, b, c) the clauses
    [a+1, b+1, c+1] and [−a−1, −b−1, −c−1]; plus the unit clause [m+1] for m the smallest address in any knot (complement symmetry;
    state this in REPORT.md).
  - Solver: pysat `Cadical195`. Conflict budget **2,000,000** per instance via `conf_budget` and `solve_limited`; if it returns
    None, undecided. Record the conflicts used if the binding exposes them (else null) and the wall time.
  - Phase hint: if level n − 1 was alive with model M, set phases so that address x takes M's value at x >> 1 (the lifted state). If
    the binding's phase setting is unavailable, skip the hint and say so.
- **Compute every level 1 .. 12, also after a death** (a return must be detectable).

## Per-description derived fields (also written by the runner)

- `fate`: F0 if no level has a knot; else let the levels with knots be read in order: F1 if the first level with knots is dead; F2
  if some level is alive and a later level is dead; F3 if every level with knots is alive; **FU** if a null verdict leaves the class
  open (e.g. alive to 11 and null at 12; or null at the first level with knots). A null after a determined F1 or F2 does not change
  the class but sets `undecided_after: true`. `return: true` when some level is dead and a later level alive.
- `first_death`: the first dead level or null. `rho = knots_12 / 4096`. `single_rule: true` when the key has one distinct rule.
- `activity`, `degree`, and `join_growth` from (join_10, join_11, join_12): "constant" if all equal; "x1.6" if join_12 ≥ 1.6 join_11
  and join_11 ≥ 1.6 join_10; else "other".

## Output layout (resumable)

- `CODEX/addr.py`: the library (sampler, action, words, pattern, activity, SAT).
- `CODEX/run_census.py --workers K --out DIR`: builds both populations' draw lists deterministically, writes `DIR/draws.jsonl.gz`
  (one record per draw: population, index, rejected cause or key, bits, r_capped), then processes distinct keys with K worker
  processes, appending one JSON line per finished key to `DIR/keys/worker-<k>.jsonl` (all fields above, per-level arrays), flushing
  after each line. On restart it reads every finished key and skips it. Memory per worker under 1.5 GB.
- `CODEX/summarize.py DIR`: reads the draws and keys and writes `DIR/summary.json` and `DIR/summary.md` with exactly the tables of
  the pre-registration ("Measures", "Predictions and failure criteria", "Matched-density design"): fate shares raw, given s ≥ 3, and
  given each density bin, by count (distinct keys) and by weight (W's draws, rejected draws excluded and counted); the B0-settled
  share of W's weight; first-death histograms by activity class; the matched-density cells (eligibility, Δ, both intervals,
  differs / same / unclear) for each class against exponential on E, then on W by weight as secondary; and each prediction's
  verdict by its frozen criterion. Use exactly the pre-registration's bins, thresholds, eligibility rule and Bonferroni correction
  (Newcombe–Wilson hybrid score interval for a difference of two proportions; Bonferroni by dividing 0.05 by the number of eligible
  cells).

## Validation gates (run all; write results to `CODEX/validation.json` and `REPORT.md`)

- **V-act:** for 200 random automata (s ≤ 5) and every word of W_s, the vectorised action on all addresses of length ≤ 8 equals a
  plain recursive implementation written independently in `CODEX/reference.py`.
- **V-sat:** 1,000 random (description, level ≤ 4) instances: the verdict equals brute-force enumeration of all 2ⁿ value
  assignments; and 300 instances at levels 9 and 10 drawn from E: Cadical195 and Glucose4 agree on every instance both decide.
- **V-B0:** every E or W description with `single_rule: true` in the smoke run is F3 (also run the proof note's `check.py` read-only
  as a script and report its printed line; do not let it write: copy it into CODEX first and run the copy).
- **V-act-class:** for 500 random automata (s ≤ 5, U = all relabelings), count θ_n = max over q in U of the number of addresses of
  length n that hand q a non-trivial relabeling, n = 1 .. 40, and check: finitary ⇔ θ_40 = 0; bounded ⇔ θ_n constant and positive for
  n = 30 .. 40; exponential ⇔ θ_40 / θ_39 ≥ 1.25; otherwise polynomial. Any disagreement with the exact class fails the gate.
- **V-code:** over W's 40,000 draws (sampling only, no SAT), the frequencies of s and r agree with Elias gamma (P(n) = 2^−(2⌊log₂ n⌋+1))
  by a chi-square test at 0.01, cells with expected count ≥ 5.
- **V-resume:** a smoke run of 300 keys (the first 150 distinct keys of E and of W) with 4 workers, killed after about half the keys
  finish and restarted, gives the same records (ignoring wall times) as an uninterrupted run of the same keys.

## Smoke run

The 300 keys of V-resume, all levels. Report: wall time per key (mean, max, by level), undecided count, and an estimate of the full
run's time at 8 workers. Then stop.

## REPORT.md

What you wrote, how to launch the full run (exact command), every gate's result, the smoke timings, any binding limitation (conflict
counts, phases), and "Ambiguities" (empty if none).
