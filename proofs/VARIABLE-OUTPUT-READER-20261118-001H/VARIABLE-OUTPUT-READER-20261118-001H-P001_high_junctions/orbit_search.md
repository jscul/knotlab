# Exact symmetries of targeted high-junction presentations

The search found same-presentation symmetries through \(K=5\) that carry
legal triples to forbidden ones. Every presentation tested has its full
triple menu preserved through \(K=6\) and at full distance. The finite
scope consists of the named continuations of two seven-junction cores,
at widths 27 through 45, with at least one five- or six-place junction
and a nonempty legal triple menu. [Producer](orbit_search.cpp) · [Exact records](orbit_search.json)

## Design and coverage

The first two families duplicate one old holder, place two three-parent
caps that overlap on the other two holders, and add a join on the caps.
The two exclusive parents and this new junction form a legal triple.
Named follow-ups connect the new junction to an old parent and then
across to a cap, or place a third cap on the legal triple. The pair fan
uses three pair joins with overlapping parent sets, then joins across
them. The last family uses opposite-color caps on consecutive groups
and links two distinct parents of one to the other cap. Both fresh
counts are tested where the named plan permits. The generator checks
every move against the current parent rule and discards exact duplicate
literal incidence records within each family.

| Family | High records | With legal triples | Width range | First preserving \(K=5\) | First preserving \(K=6\) |
|---|---:|---:|---:|---:|---:|
| Symmetric competing caps | 7,480 | 4,088 | 27–39 | 921 | 3,167 |
| Staggered competing caps | 5,944 | 2,552 | 27–39 | 921 | 1,631 |
| Overlapping pair fan | 2,872 | 2,552 | 27–39 | 2,360 | 192 |
| Opposite-group caps | 8,105 | 7,913 | 27–45 | 3,073 | 4,840 |
| Total | 24,401 | 17,105 | 27–45 | 7,275 | 9,830 |

For each table the search checks transposition generators within each
class of distance twins and one lift of every exact isometry of the
quotient. These generate all table symmetries. It checks full distance
first, then decreases the cutoff until finding an opposing symmetry.
That same symmetry works at every smaller cutoff. A renaming of a legal
high-junction fixture passed all pair and menu checks. Removing one of
its transported verdicts produced the deliberately planted conflict.
[Predecessor's exact comparator](../../VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/compare.cpp)

## A width-27 witness

The symmetric example has eleven junctions. Its caps are born on
\((4,5,6)\) and \((4,5,7)\), with two and three fresh distinctions,
respectively. The next join is on the two caps and makes three fresh.
The marks \(19,20,24\) are loose at \(6,7,10\). The first pair has an
earlier witness at 2 or 3, and the other pairs use caps 8 and 9. There
is no common witness of all three. Transposition \((16\ 20)\) sends
the marks to \(16,19,24\). Distinction 16 is shared by 7 and 9, which
forbids that triple.

All 351 capped pair entries agree through \(K=5\) under this
transposition. It moves \(K(12,16)=6\) to \(K(12,20)=7\), so the
observation through six distinguishes this map. The exact automorphism
group through six has 24 elements and preserves the menu. The full map
changes 16 pair entries and transports an ordinary check outside the
equation space. High sites 8, 9 and 10 all survive physical
single-distinction cuts that retain the marks. In the other three
recorded representatives the high sites also survive such cuts.

Independent replay used literal rule checks and the parity span for each
representative. It reproduced every pair entry and both marked verdicts.
An independently implemented exact quotient search also verified universal
menu preservation at the next cutoff for each representative.
[Literal replay](../../VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh/six_check.py) · [Independent quotient search](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_classes.py)

## Reproduction

Use a C++20 compiler from the repository root. The serial run took
7.59 seconds and used 9,392 KiB peak resident memory.

```sh
proof=proofs/VARIABLE-OUTPUT-READER-20261118-001H/VARIABLE-OUTPUT-READER-20261118-001H-P001_high_junctions
scratch=$(mktemp -d)
g++ -std=c++20 -O3 -march=native -pthread "$proof/orbit_search.cpp" -o "$scratch/orbit_search"
"$scratch/orbit_search"
```
