# A six-place support with a different abstract menu

Two alternative six-place supports survive the simple incidence,
bipartite color, input-witness and critical-pair tests at a genuine
width-36 source with one shrinking join. Each gives an empty
abstract menu where the source allows eight triples. The full
short-distance tests below exclude both proposed replacements.

## The finite screen on a named source

Keep every named low junction. The six-place site must hold every
distinction with zero low holders. A distinction with two low holders
is already shared, so each other selected bit must have exactly one
low holder. Pick enough such distinctions to complete the six-place
support. Since the ordinary incidence is simple and bipartite, all
selected low holders are distinct and have the same color in the
connected low graph.

Choose three of the selected low-held bits as inputs. Each of the three
pairs of their holders must have a low common neighbor, with no low
neighbor common to all three. The other three bits are outputs. Let
\(I,O\) be the source input and output sets and \(I',O'\) the proposed
sets. On an unequal support require \(I\cap O'=I'\cap O=\varnothing\).
If \(I\cap I'\ne\varnothing\), also require \(O=O'\). Each retained
support has a named prospective menu computed by the current ordinary
incidence, using the full parent law.

The sources are the shortest one-shrink positive histories saved by
the frontier closure, including its controls using a loose output of
the six-place site, and the two positive prefixes with complementary
last choices. Two controls use the same literal history, giving five
distinct sources. Every source history replays the full growth law.
The enumeration covers every support and orientation meeting the
stated filters for these named sources.

| Literal source | Width | Supports before filters | Retained orientations | Retained orientations with a different menu |
|---|---:|---:|---:|---:|
| First positive after the exceptional join and one shrink | 36 | 924 | 5 | 0 |
| First such positive using a loose exceptional output | 36 | 252 | 5 | 0 |
| First positive when the shrink preceded the exceptional join | 40 | 252 | 2 | 0 |
| First complementary prefix with the exceptional join first | 36 | 924 | 6 | 2 |
| First complementary prefix with the shrink first | 40 | 924 | 1 | 0 |

## The surviving support change

Use the width-36 complementary prefix from the closure. Its high
site is site 9, starting the numbering at zero. Its inputs are
\(\{8,17,19\}\) and outputs \(\{21,22,23\}\). The three holders
of the live triple have loose pairs \(\{30,31\}\), \(\{32,33\}\),
and \(\{34,35\}\), so all eight choices of one bit from each pair
are legal.

Replace input 8 by 34 or 35, with the same outputs
\(\{21,22,23\}\). Both alternatives take inputs at low sites
7, 8 and 15. Their three low pair witnesses are sites 6, 12
and 11, respectively, and there is no low common witness.
The input overlap is \(\{17,19\}\), so the unchanged output set
passes the critical-pair condition. Both alternatives give
empty abstract triple menus. For instance \(\{30,32,34\}\) is
legal in the source and forbidden after either proposed change.
The proposed site meets all three holders of the original loose
pairs via outputs 22 and 23 and via the replaced input. It is
then a common witness for any surviving triple at those holders.

In the original orientation, output 21 goes from site 9 through
the low sites 10 and 11 to site 15 via distinctions 24 and 27.
Insisting on those low directions would make site 15 both a
successor and a parent of the replacement. The full named
history, support and witness lists specify each proposed replacement.

When both the six-place junction and the exterior are required to
have every pair through bond distance five, exactly one of all 924
candidate supports remains on this prefix. It is the true support
with input 8. In particular the replacement would put 17 together
with 34 or 35. Both source pairs have minimum bond size eight,
although a true six-place junction would give a bound of six.
Direct replay recovers all eight legal marks. Thus
the two other choices witnessed a failure of the initial filters.
The surrounding pair distances distinguish them at the predicted
cutoff. [Named comparison](one_shrink.json) · [All-depth proof](terminal_cuts.md)

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh/local.py
~~~

[Replay checker](local.py) · [Named cases and counts](local.json)
