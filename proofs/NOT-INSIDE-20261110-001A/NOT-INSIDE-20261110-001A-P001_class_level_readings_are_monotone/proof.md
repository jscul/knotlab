# Class-level readings are monotone

Status: Theorem M proved by hand (planned and frozen before the run in `research/NOT-INSIDE-20261110-001/preregistration.md`, commit
`904fce672`); census N and check F computed exhaustively by `check.py` (under a second).

## Words

A leaf's law is a signing; its class is that signing up to gauge. Gauge here means flipping an inner point of the leaf together with the
signs on its sides, which changes no line's satisfiability once the point's value is flipped too. Learning writes signings, and which
signing of a class it leaves depends on its path. A network is the leaves' own knot lines together with any further constraints that do not
involve a leaf's signs: host lines, parity names, top constraints, constraints pinning a name. Its reading O is 1 when it has no satisfying
state. A reading is **class-level** when it is the same for every signing of each leaf's class, and **frame-level** when it is computed with
one fixed signing per class.

## Theorem M

Let a leaf be cut into the network at a line and let R_c be the patterns it allows on its three outer points in class c. If the network has
a satisfying state with the leaf in some signing of c, and R_c ⊆ R_{c′}, then it has a satisfying state with the leaf in some signing of
c′. If the leaf is instead a closed component, the same holds whenever c′ is satisfiable.

*Proof.* Let X be the satisfying state. Its pattern on the leaf's outer points is in R_c ⊆ R_{c′}, so under a signing s′ of c′ some values y′
of the leaf's inner points complete it on the leaf's lines. Let g be the set of inner points where y′ and X differ, and flip them in s′:
the result is another signing of c′, and under it X's own inner values satisfy every leaf line, since flipping a point's value together with
its sides changes none of its lines' literals. Nothing else in the network involves the leaf's signs, and X satisfies it all, so X satisfies
the network. For a closed component the same argument runs with no outer points: any satisfying state of c′, gauged onto X's values. ∎

**Corollary.** For leaves that act in one class and are transparent in the others (the class-forced free atoms of
`OTHER-ATOMS-20261110-001`), R_ω has six patterns and every other R_c all eight. So every class-level reading is non-decreasing in each
leaf's acting bit and takes one value on all of a leaf's non-acting classes. No class-level reading negates a stored bit, computes XOR or
NAND of stored bits, or tells two non-acting classes apart. The scope is any network of this kind, of any size; with AND through cuts and OR
through names, what class-level readings can reach is at most the monotone functions of the acting bits.

## Census N: a frame-level NOT exists

With one fixed signing per class (the leaf's torus's labelled class laws) and the leaf cut into the torus (2,0,2):

| Leaf | Points | Satisfying states per class (ω starred) | States in ω and no other class | Explicit network reads |
| --- | --- | --- | --- | --- |
| thin (3,2,2) | 9 | 66, 18*, 24, 60 | 10 | NOT a_1 |
| thin (4,3,2) | 11 | 162, 30, 24*, 168 | 14 | NOT a_1 |
| Fano (7,2,1) | 10 | 30*, 66, 66, 66 | 12 | NOT a_1 |

The explicit network names every point against point 0 and pins each name, by a parity knot on that name taken three times, to its value in
a witness state that only the acting class allows; it has a satisfying state exactly in the acting class. And as theorem M says, a second
signing of a non-acting class (its labelled law with some inner points flipped) gives it a satisfying state there too: the NOT reads the
frame, not the class.

## Check F: the σ readings read the frame

Each of the 718 networks of `CLASS-READ-20261110-001`'s G1 that read {ω, σ} has a satisfying state under some other signing of σ (σ's
labelled law with points flipped). So the reading that singled out σ, and the parity reading noted after `GATES-20261110-001`, are
frame-level; by theorem M no class-level reading can single out a non-acting class.
