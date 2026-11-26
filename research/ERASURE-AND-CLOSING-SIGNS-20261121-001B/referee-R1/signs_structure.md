# Structural certificates for the closing signs

All 294 archived parity closures passed. The check rebuilt incidence from all physical knots at each recorded cut, recovered the complete component of each zero-grant birth, and required every distinction in a closing component to have exactly two holders. It verified the recorded simple meeting count separately from the physical distinction count. It used the named rows and the supplied certificates directly, with no imports from the original implementation. [Physical archive](../../../artifacts/ERASURE-AND-CLOSING-SIGNS-20261121-001B/ERASURE-AND-CLOSING-SIGNS-20261121-001B-E001_closures/panels_histories.json.gz) · [Checker](signs_structure.py) · [Sample records and reductions](signs_structure.json)

| Source weighting | Five connected groups meeting in every pair | Six connected groups meeting three against three | Physical word reductions to the identity with odd prescribed sign |
| --- | ---: | ---: | ---: |
| Labelled trees | 0 | 1 | 5 |
| Connected explosive draws | 0 | 0 | 0 |
| Mixed explosive draws with two additional founding knots | 129 | 0 | 127 |
| Supplementary positive-support draws | 32 | 0 | 0 |
| Total | 161 | 1 | 132 |

For each of the 162 admitting certificates, the listed groups were nonempty, disjoint, and internally connected, and the required meetings were present. All 1,619 listed chains used the exact physical names between successive knots. Nineteen admitting samples contained repeated meetings. Fifteen had one additional name, three had two, and one had three. The structural criterion acts on the simple meeting pattern, with each physical name retained in the checks of incidence and the listed chains. Admission in this check uses the previously adopted connected-group classification. Explicit signed operator products are separate evidence. [Classification and its source](../../FOUR-READINGS-20261120-001A/results.md)

The 132 refusing certificates passed both the cyclic order count (the literature's planar rotation certificate) and a literal cancellation check. The latter starts with one physical word per knot, written in the verified local order. Local commutativity permits the initial ordering. If a product is scalar, then cyclic rotation preserves it since `uv = sI` implies `vu = u⁻¹(uv)u = sI`. Rotate the accumulated word and the next knot's word so that a shared distinction occurs last in the former and first in the latter. Multiplication places the identical involutions together and their square is the identity. After joining every knot, adjacent equal factors can be canceled after further cyclic rotations. Each resulting word is empty, while the signs multiplied on the right give −I. These traces rule out the prescribed products for arbitrary Hermitian involutions on a nonzero carrier. The two recorded steps in each join are left and right rotation offsets. Each remaining cancellation records the rotation offset and the repeated physical name.

A readback of the saved JSON checked all 932 joins and 668 remaining adjacent cancellations against the archived rows. Substituting a wrong physical name on a positive chain and swapping two neighbors in one negative cyclic order each caused rejection. The observed negatives have no repeated meeting. An additional algebraic control inserted one fresh physical name alongside an existing name between the same two knots in a known negative. Both occurrences of the added name canceled, with no change of the odd contradiction. The control was excluded from the population counts.

The 12-closure pilot took 0.13 seconds and reached 68,268 KiB peak resident memory. The complete run took 0.17 seconds and reached 68,336 KiB. Both used one process, one native library thread per library and a 1,843,200 KiB address-space cap. The scoped reproduction below reads the archived physical cuts. [Archived count summary](../../../artifacts/ERASURE-AND-CLOSING-SIGNS-20261121-001B/ERASURE-AND-CLOSING-SIGNS-20261121-001B-E001_closures/history_audit.json)

```sh
ulimit -v 1843200
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
.venv/bin/python -B research/ERASURE-AND-CLOSING-SIGNS-20261121-001B/referee-R1/signs_structure.py
```
