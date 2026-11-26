Read docs/ADVISOR_HIVEMIND.md first and follow its rules. When you have answered, add one entry for this consultation under its consultations marker, and a standing fact only if you checked it in the record.

Study: LAYERS-20261126-001 (just opened; nothing frozen). Please read these before answering:
- research/TWO-CLASS-SIGN-20261126-001/README.md and decision.md (the sign, defined: S, moves, H, classes; rings gain two classes in round 1; the class on rings is the parity of the whole old ring)
- research/TWO-CLASS-SIGN-20261126-001/classes.py (how S, moves and classes are computed)
- research/BOTH-LONG-20261126-001/distances.py (the graph reading: knots as vertices, shared distinctions as edges, loose distinctions as edges to one unconstrained vertex; allowed changes are the cycles)
- research/BASES-WITHIN-20261112-001/bases_within.md (nesting by hand: the pattern above reads exactly the law below)
- publication/knotlab/INTUITIONS.md, lessons 12.1 to 12.3 (the owner's principle and the question as posed)

The question (the coordinator's, on the owner's "emergence can show up in multiple places and layers"): under parity, do the classes of several rings that share knots or grow together obey a knot rule among themselves (K1 to K3 on the class values), so the rings act as knots of a larger pattern that keeps a fact no single ring holds?

My draft argument, which I want you to attack:
(A) Under parity and ordinary growth, a round never changes the projection of the allowed states onto the old distinctions: every new knot has at least one fresh distinction of its own (f = max(D, 3 - p, 1)), so each new parity constraint can be met for any old state by its own fresh distinction; the closing birth that takes every loose distinction is implied by the present constraints by definition. So every joint relation among functionals of old distinctions, in particular among the rings' class labels, is fixed by the start (or the stage) and is never made by growth.
(B) A ring's class label is the parity of its shared distinctions, a cycle of the graph. A sum of labels is constant on S exactly when it lies in the row space of the knots' constraints, whose elements are, in the graph reading, the cut of a set K of knots plus the loose distinctions of K. With loose values free, K must hold no loose distinction, so only dead knots; a sum of cycles that equals the cut of a set of dead knots is an edge set both a cycle and a cut (the literature's bicycle space over two values). So for rings of live knots, a relation among ring labels holds only when the cycles themselves add to zero (a theta: one ring is the sum of the others, not independently witnessed), and a relation made by the constraints needs dead knots and a bicycle.
(C) Classes are cosets of H; labels must be constant on moves. A relation modulo H is a dependency of long cycles modulo short ones, still linear.

Please answer, in prose under 900 words:
1. Is (A) right? Check it against the code of the growth engine the two-class study used (forbid.grown, and whatever engine it calls): is there any birth under parity whose constraint has no fresh distinction of its own and is not implied? Quote the lines.
2. Is (B) right, including the bicycle step? Give a smallest start, if one exists, with rings of live knots whose ring labels obey a relation on S that is not an identity of edge sets; or one with dead knots where a bicycle makes a relation among three ring labels that passes K1 to K3.
3. If (A) and (B) hold, the honest outcome is an argument that under parity, with ordinary growth, the layers stack only through the cycle space's own identities and bicycles fixed at the start. Is there a reading of "layer" that this misses and that the record supports: new cycles among grown knots whose labels involve fresh distinctions, classes that appear only after growth (the rings gain classes in round 1, so H changes), or the not-all-equal law?
4. What is the cheapest frozen test that could refute the argument on the census (with the counts it would read), and what known mathematics should I cite (bicycle space, concatenated codes, the Tutte polynomial at (-1, -1))?
