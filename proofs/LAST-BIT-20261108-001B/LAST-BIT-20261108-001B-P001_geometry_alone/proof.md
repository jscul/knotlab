# A forcing test on geometry alone for the last one-bit decoration

Status: Proved. The reduction is by hand; every finite statement is computed exactly (`check.py` with `forcing_lib.py`, about 25
minutes with 16 workers; no search reached its budget).

Ticket `LAST-BIT-20261108-001B`, 2026-11-08.

## Standard statement

- **The decoration.** Label the pinwheel's tiles with one bit by Conway's cut: under a parent labelled 0 the five children get
  1 0 1 0 1, under a parent labelled 1 they get 0 0 1 1 0. The law lists the labelled collars of decorated supertiles. It is the one
  decoration of 1,024 (up to exchanging the labels) that no crystal tried has escaped (`ONE-BIT-20261108-001`).
- **The route to a proof.** In a plane obeying the law, the tiles group into parents (`COLLAR-PLANE-20261108-001B`), and every
  parent's label is forced. If the parents' collars were always pinwheel collars, the parent tiling would obey the collar law, and
  repeating the argument level by level would show the plane is a pinwheel tiling.
- **The result.** That first step fails at the depth tested: 153 labelled parent collars that are not pinwheel collars survive the
  joint consistency test and exhaustive extension to tile distance 2, and 15 of a sample of 16 survive distance 3.

## Nearest known result

Forcing a hierarchy through forced composition is the method of Mozes (1989), Goodman-Strauss (1998) and Radin (1994). Exhaustive
extension of a local configuration to a fixed radius is standard in tiling searches (it is how deceptions are found). Their use on
this decoration was not found in prior work (no-overlap-found).

## Terms

- **S1.** The labelled collars (Y, p), with Y in the arc-consistent core of the level-one law and p a labelling of Y's tiles, whose
  decorated cut gives every child of Y's central tile a collar of the law, and which survive the joint test of
  `ONE-BIT-20261108-001A`.
- **Exhaustive extension to distance d.** A labelled collar survives when a patch can be grown around it, by completing collars with
  surviving labelled collars, so that every tile within tile distance d of its centre has a complete surviving labelled collar. The
  search is a labelled version of `GROWTH-LAW-20261107-001B`'s growth engine with full backtracking.

## Lemma 1 (soundness)

The parent tiling of a plane obeying the law has all its labelled collars in S1, and around each of them the parent tiling itself
is a patch of every radius. So a collar that fails exhaustive extension at any distance cannot occur, and removing it keeps the
argument sound. ∎

## Theorem 2 (the computation)

For s = 10101 / 00110:
- **Parents are forced.** In no core collar can the central tile's children avoid s(0) and s(1).
- **S1.** 551 labelled parent collars survive the joint test: 310 in the law, 50 pinwheel collars with labels the law does not list,
  and 191 non-key collars.
- **Extension to distance 2.** The first round removes 34 non-key collars; after the joint test is rerun, a second round removes
  none. 153 non-key collars survive.
- **Distance 3, sampled.** Of 16 survivors drawn at random, 15 extend to distance 3 and 1 dies.

*Proof.* Computed. ∎

## What it says

- **The first step of the proof does not go through** at distances 2 and 3. A plane obeying the law may contain parents whose
  collars are not pinwheel collars: either such a plane exists, and the decoration fails (perhaps through a crystal outside the
  families tried), or the defects die at a larger distance than tested.
- **The defects are not small.** Most surviving non-key collars sit inside consistent labelled patches reaching three tiles out at
  the parent level, about seven tiles out at the level of the plane.

## The check

`check.py` computes everything above and writes `result.json` and `survivors.json` (the surviving collars). Controls, each of which
held:
- **The law's own collars survive.** Every labelled key of the law survives the joint test.
- **The extension test keeps what occurs.** For the constant decoration 00000 / 11111, which admits the rhombus crystal, the rhombus
  lattice's collar is in S1 and survives extension to distance 2.

## Nonclaims

- **Not a failure of the decoration.** Surviving a local test does not mean a collar occurs in a plane.
- **Not a proof.** The route stops at its first step; the decoration is not shown to force the pinwheel.
