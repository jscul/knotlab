# A six-place start reaches partnered growth

A connected parity start with 32 junctions and 78 distinctions reaches the
complete order-three partnered roster in one cheapest round. Its twelve live
junctions have six places each. The other twenty have three. Each two
junctions share at most one distinction. [Literal replay and sampled controls](../../artifacts/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek/witness.json)

## Construction and first round

Take six labels paired as \(01,23,45\). Index the twelve live junctions by the
nonpartner pairs of labels. Give each live junction two loose
distinctions. For each of the eight choices of one label from each partner
pair, a dead three-place junction meets the three indexed junctions from
that choice. For each label \(u\) and each other partner pair \(v,w\), a
separate dead junction meets the two live junctions indexed by \(uv,uw\).
Pair these twelve junctions in six disjoint meetings to give each its third
place. Each live junction then has four shared distinctions besides its two
loose ones.

In the initial roster, two live junctions are candidates exactly when
their indices share a label. Its maximal groups of pairwise candidates are
the six sets of four indexed by a common label and the eight held sets of
three. The six sets of four cover every candidate pair. The law takes both
loose distinctions from every live junction, forming one new junction for
each of the six labels. Each receives four fresh distinctions.

The six new junctions constitute the entire live roster. Each previous live
junction meets exactly the two new junctions named by its index. The maximal
blocks are therefore precisely the twelve nonpartner pairs. All eight
transversals are free and every new junction has the four loose distinctions
its four transversals require. This is the canonical partnered starting
roster of order three, so the previously proved recurrence applies from
this age. [Partnered growth theorem](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md#theorem-1-partnered-starts)

| Age | Junctions | Distinctions | Live junctions | Loose per live junction | Next groups |
|---:|---:|---:|---:|---:|---:|
| 0 | 32 | 78 | 12 | 2 | 6 |
| 1 | 38 | 102 | 6 | 4 | 8 |
| 2 | 46 | 142 | 8 | 5 | 10 |
| 3 | 56 | 262 | 10 | 12 | 24 |

The literal replay builds through age three and reads the 24 groups for
the following round. The archived production engine and independent replay
agree on the parent sets, the allocation of every loose distinction, and
the least fresh counts. Binary elimination gives exactly the even-parity
relation on each presented support, with full single-name erasures and a
nonempty relation. Forgetting all fresh distinctions at each round recovers
the preceding relation exactly. The canonical knot checker also evaluates
representative three- and six-place projections. As readout controls, the
six-junction roster with all transversals free gives eight joins, while the
six-junction roster holding two complementary transversals gives six.

## Fresh weighting

For each of 32 independent samples, choose a uniform perfect matching of the
twelve dead junctions that meet two initial live junctions. There are 10,395
such matchings on the declared labels. Independently permute the junction
and distinction names. Seed `20261119073` gives 32 distinct matchings and 32
successful replays of the same sequence of live counts and loose counts
through age three. The weighting tests this fixed construction with new
meetings between dead junctions and new names. [Executable witness](../../experiments/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek/witness.py)
