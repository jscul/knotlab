# Referee report HIDDEN-COPY-R1 (lean, as asked)

**Verdict: Confirmed, with one wording note (Not a block).**
- **The certificate is sound.** The essentially-unary certificate is a correct application of Pálfy's theorem.
- **The wider construction follows from the Galois connection.** It is correct, and after the run.
- **102 of 318 is exact.** I rebuilt the full lattice of invariant equivalences, not one level of joins, and got 102 again. None of
  the automorphism lists was capped.
- **The claims stay within the pairs the capped endo part reached.**

Referee: the background referee thread, 2026-11-12. `ref_partitions.py` holds my own lattice closure. It imports the census's
`hidden_lib` only for the harmonies and their automorphisms, not for the partitions. The advisor model was not consulted.

## 1. The certificate (proof section 2)

**The two facts it rests on.** The stitch R holds the diagonal, so constants are polymorphisms and Pol(R) is its own polynomial
clone. E-small says its unary members are automorphisms or constants.

**Pálfy's theorem applies.** For a finite set of at least 3 elements, with every unary polynomial a permutation or a constant, the
clone is either essentially unary or polynomially equivalent to a vector space over a finite field.

**Each condition excludes the affine branch.** In that branch the unary permutations are {λx + c, λ ≠ 0}.
- **|W| not a prime power** excludes it outright.
- **An intransitive Aut** excludes it, since that group contains every translation.
- **A single |W|-cycle with |W| not prime** excludes it. A translation has order p, so a |W|-cycle needs |W| = p, and λx + c with
  λ ≠ 1 has a fixed point.

**All 318 E-small pairs are certified this way:** 145 by |W| not being a prime power, 140 by a |W|-cycle, 33 by an intransitive Aut.
None needs the binary search, so its failed first start and relaunch (check 4) do not bear on the certificate.

**The elementary remark.** "Constants present and no essential binary polymorphism gives essentially unary" is Jablonskij's lemma:
fixing constants turns an essential function of two or more variables into an essential binary one. It is only needed where Pálfy's
conditions do not decide, which never happened here.

## 2. The wider construction (check 2)

**The gadget relations.** An essentially unary clone with constants consists of Aut applied to one argument, together with the
constants. Its invariant relations are exactly the Aut-invariant relations that hold the diagonal. By the Galois connection (Geiger;
Bodnarčuk, Kalužnin, Kotov and Romov), those are exactly the relations definable from R with hidden copies.

**The mod-3 relation.** An Aut-invariant partition into three classes gives "the classes are all equal or all different": it holds
the diagonal, and every permutation of the classes keeps it. So it is a gadget relation. On the classes it is x + y + z = 0 modulo 3.

**Two and four classes.** A ternary relation of that kind would have to hold the diagonal, and x + y + z = 0 over Z₂ or Z₂² does
not. So these give only the four-member relation, as stated when Aut permutes the classes freely.

**The gadget size.** The bound |W|^m is the standard construction, and existential.

**Frozen or after the run?** After the run: the proof labels section 2 "after the run (the advisor's second check; descriptive and by
known theorems)". The frozen gadget census used Z₂ readouts only.

## 3. Is 102 complete? (check 5)

`after_run_factor.py` joins the principal closures one level deep, and only those with at most 8 classes, so it could miss a
three-class partition. I rebuilt the whole lattice of Aut-invariant equivalences instead: every principal closure, then joins of any
two elements until nothing new appears. All 318 lattices closed, and **exactly the same 102 pairs** have a three-class partition. There
is no disagreement.

None of the 318 automorphism lists was capped, so no partition was counted as invariant under only part of Aut.

## 4. The capped endo part (check 3)

**What was covered.** `assemble_after_cap.py` only gathers the saved rows: 1,001 of 1,267 pairs, 17 of 40 harmonies. Everything
downstream uses those rows.

**The wording mostly fits.** The note says "under every kind set reached" and "every E-small pair reached".

**The one general statement.** "E-small is common for single-orbit harmonies and rare for multi-orbit ones" is a statement about the
17 harmonies the cap reached, in the run's order. It should say so.

## 5. Known and new

**Known.**
- Pálfy's theorem.
- The Galois connection.
- Jablonskij's lemma.
- That diagonal-holding Aut-invariant relations are definable, given an essentially unary clone.

**New.**
- Their application to stitched harmonies.
- The counts.
- The mod-3 relation's existence for six harmonies.

**Proved:** the certificate, the construction and the 102 (given the automorphism groups). **Computed:** the census. No explicit
mod-3 gadget is given.

## Note for the thread (Not a block)

Say that "E-small common for single-orbit, rare for multi-orbit" covers the 17 harmonies the capped endo part reached.
