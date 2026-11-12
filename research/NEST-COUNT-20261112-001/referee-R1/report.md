# Referee report NEST-COUNT-R1 (lean, as asked)

**Verdict: Confirmed with fixes: one Narrowing (the Answer's wording), two Not a block.**
- **Every statement is correct.** I checked each proof by reading.
- **The checks pass.** `check.py` passes on rerun (K1, K2, K3; 201 tile sets tile and 99 do not). My own brute force confirms the
  gadgets and the chain.
- **Almost all of it is known mathematics restated for this language.** Only T1(c), the usual limit, is the program's own, and it
  was first argued in LIMIT-ONLY-R1.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_gadgets.py` is mine. It enumerates every state to check the inequality and equality gadgets, the chain for 4 to 8
  places, and the ten knots on five distinctions.
- **Advisor.** The advisor model was not consulted.

## 1. The points asked

**T1(a) and (b) are right.**
- **Complement closure.** Every relation of a three-port definition is closed under complement (NAE is, and conjunction and
  projection keep it), so there are 16 values per self-holding definition.
- **The bounds.** A deterministic map on 16^s values repeats within 16^s steps. Φ is monotone, so Φ^t(TOP) decreases. The lattice
  has height 4 per component, so there are at most 4s strict decreases.
- **The limit.** Compactness applies to the truncations, exactly as LIMIT-ONLY-R1 checked.

**T1(c)'s recurrence argument is right, but its key sentence is too narrow.** "At depth t + 1 the same three distinctions carry a
bottom knot only through a SELF call of the new copy on those arguments."
- **Two other routes.** The recurring bottom knot can also come from a SELF call made inside a copy reached from the new copy
  through a call to another definition, on the new copy's ports. It can also come from a second copy made on the same three
  distinctions.
- **Why the conclusion stands.** Either way the call is a SELF call on its own definition's three ports, so it is a pass-through
  call of that definition. Adding the knot to every copy of every definition with a pass-through call covers both routes.
- **The census agrees.** LIMIT-STATE's `usual()` adds the knot in every such definition, not only the self-holding definition at
  the top.
- **A small slip.** "Present at every depth past j + 1" should be "from depth j + 1 on".

**T2's window claim is right.**
- **Why.** For t > b, levels 0 to b − 1 and their knots are the same at every depth. Everything else hangs from the SELF calls made
  at level b − 1, and each such call meets the window only through its arguments (its insides are fresh), carrying its definition's
  relation at depth t − b, which is X_{t−b}.
- **What follows.** The window's state set is a fixed projection of a function of X_{t−b}. It is an immediate corollary of T1(a).

**The chained long-clause gadget is right.** NAE(x₁, …, x_m) holds iff some a has NAE(x₁, x₂, a) and NAE(¬a, x₃, …, x_m).
- **If not all are equal.** When x₁ ≠ x₂, take ¬a ≠ x₃. When x₁ = x₂ = v, a = ¬v is forced and some later x differs from v.
- **If all are equal to v.** a = ¬v is forced, and NAE(v, …, v) fails.
- **Iterating.** Applied repeatedly, with ¬a made by the inequality gadget, this is `clause()` in `check.py`.
- **Checked.** I confirmed it by enumeration for 4 to 8 places, along with the inequality and equality gadgets.

**P3c holds in both directions.**
- **Tiling to state.** Set r = 0 everywhere and each placed tile's bit to 1, and fill the auxiliaries by the gadgets. Every gadget
  is satisfiable when its relation holds.
- **State to tiling.**
  - The right and up equalities make every reference equal, since the plane is connected that way.
  - "Some tile" is NAE(bits, r), and "not both" is NAE(¬b, ¬b′, r), so exactly one tile is on at each site.
  - The cross-site clauses use the site's own r, which is legitimate once the references are equal, so neighbours match.
  - Complementing every distinction gives the same tiling, read relative to r.
- **What the torus check shows.** It tests the encoding on finite instances. Undecidability then follows from Berger's theorem,
  given that the plane problem is the infinite one, which by compactness is equivalent to tiling every finite square.

## 2. How much is a restatement

| Statement | Status |
| --- | --- |
| T1(a) finite state, eventual periodicity | known: bounded-interface hierarchical descriptions are evaluated bottom-up by finite port tables (Lengauer and Wanke 1988); for hyperedge-replacement grammars, satisfiability is a finite-state ("compatible") property (Courcelle; Habel, Kreowski and Vogler). The 16^s bound is the pigeonhole principle. |
| T1(b) the limit by the greatest fixed point | known: compactness with Kleene iteration on a finite lattice. |
| T1(c) the usual limit | the program's own (LIMIT-ONLY-R1), elementary. |
| T2 the top window | an immediate corollary of T1(a). |
| P3a the inequality gadget | folklore (NAE-SAT reductions). |
| P3b every complement-closed relation | known: NAE is a base of the co-clone IN₂ (Böhler, Reith, Schnoor and Vollmer 2005). Writing it on distinct distinctions is routine. |
| P3c undecidability on Z² | known: Freedman 1998 (k-SAT on Z²) from Berger 1966. NAE reaches it through P3b. |

The note's classification, "known (the mathematics), with delta (its application here)", is accurate. It should still say plainly
that apart from T1(c), nothing here is new mathematics.

## 3. The Answer's wording

**"Nested patterns of our language cannot count" is stronger than what is proved.**
- **What T2 covers.** It is about windows at the top. The note's own Reading says that counting inside the pattern, such as bonds
  between the top and a deep level, is not decided.
- **What the Answer should say.** "cannot count from their ends (or from a fixed top window)".

**"What separates the two is the size of the interface" is suggestive, not proved.** The Scope says as much ("nothing here shows that
counting needs unbounded interfaces"). The Answer should say "one difference between the two is the size of the interface".

## Fixes for the thread

1. **The Answer.**
   - Write "cannot count from their ends or a top window", not "cannot count".
   - Make "what separates the two is the interface size" a reading, as the Scope already does.

   **Narrowing** (worded beyond the proof).
2. **T1(c)'s proof.**
   - Widen "a SELF call of the new copy on those arguments" to a SELF call on its own definition's three ports, made in any copy whose
     ports are those three distinctions, including copies reached through calls to other definitions.
   - Write "from depth j + 1 on".

   The conclusion is unchanged. **Not a block.**
3. **Provenance.** Say that T1(a), T1(b), T2 and P3 restate known results, and that T1(c) is the program's own. **Not a block.**

## Files

| File | What it is |
| --- | --- |
| `ref_gadgets.py` | the referee's brute-force checks of the gadgets and the chain |
| `result_gadgets.json` | its output, all true |
