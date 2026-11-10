# Growth, then learning

Status: B1 exact (SAT over every state); B2 computed. `check.py` (1 second), ticket B of
`research/NATIVE-ATOM-20261110-001/preregistration.md`, frozen in commit `4a6ce578f` before any run.

## B1 (exact)

At the flat state of the first line-orbit representative of K_2 and of K_3, the uniform rule σ(Fano, 000) grows an atom that acts as its
line, and the grown torus has no satisfying state: the dissonance is kept, now held by the atom. σ(thin (2,1,2), 000) grows a transparent
atom, and the grown torus has a satisfying state: growth alone resolves. As claim U says.

## B2 (computed)

K_3 with two thin (2,1,2) atoms grown by the uniform rule (at l0 and the first line at the largest distance, on each of the three line
orbits; genus 2, floor one unit). Both atoms start transparent. From the grown law's first satisfying state, the frozen targeted search
wrote {0}, {1} and {0} in turn, each followed by a one-point disturbance and the learner M1 (random.Random(106)).

| Line orbit | Start | Writes | Exact writes | Held |
| --- | --- | --- | --- | --- |
| 6 | none acting | 3 | 3 | 3 |
| 9 | none acting | 3 | 3 | 3 |
| 10 | none acting | 3 | 3 | 3 |

Every address was written exactly and held. So a uniform growth that grows only transparent thin atoms still gives learning something to
write: learning winds an atom's handle into its unsatisfiable class, and the atom then remembers. Computed on K_3 only.
