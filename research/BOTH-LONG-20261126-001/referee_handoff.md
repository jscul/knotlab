# Referee hand-off: starts where both distances grow

Epic `BOTH-LONG-20261126-001`, closed 26 November 2026, referee pending. [What stands](decision.md) ·
[the note](README.md).

1. Rings of n knots grown by ordinary growth (`distances.py`, `rings_dist.jsonl.gz`): odd rings' class reaches read and
   change distance n (from about (n − 3)/2 rounds free, (n − 1)/2 pinned); even rings, one n and the other 2r + 3 or
   2r + 1; neither exceeds n.
2. Sampled starts (`census_dist.jsonl.gz`, `extension_dist.jsonl.gz`): the largest min(read, change) is 4.
3. On odd rings the old ring is both the least change and a class label; the argument that no native reading weights
   by the class character.
Check the two distance computations with your own code (enumeration where small), and the argument.
