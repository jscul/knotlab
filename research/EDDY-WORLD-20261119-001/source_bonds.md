# What the attachment does to the original path distances

Consider the two original shared distinctions between successive background knots, numbered i and j with 0 ≤ i < j ≤ 15. Let I be the path knots from i+1 through j, inclusive. At size one, B has bond distance 1+2(j−i) between these distinctions. On any of the registered attached starts add the following contribution for each attachment at s.

| Location in I | Contribution |
| --- | ---: |
| s−1 | 2 |
| s | 4 |
| s+1 | 2 |

The formula applies to the bare ring, to both isolated-ring rates when joined, to both double placements, and to the cut control. It is exact for every pair on the original path at size one.

**Proof.** Represent a loose distinction by its holder and a bookkeeping exterior, and a shared distinction by its two holders. The parity bonds are exactly the cuts with two connected sides. Choose the side excluding the exterior. Its path holders must be exactly I if its cut contains the two marked shared distinctions. A connected side cannot go around a missing path holder through an appendage joined to the path only at one knot. Both adjoining path places are outside the side. The complement including the exterior is connected since each original knot has at least one loose distinction. On B leave just I on the ordinary side. All its knots are internal to the 17-knot path and have two loose distinctions. Two shared path distinctions and these loose distinctions make the bond. Subtracting one gives the formula.

In a joined start, including an extra part of an attached ring cannot improve the cut. If the attachment is outside I, connectedness already forbids it. If inside, keeping just the attachment cuts two ring meetings. Taking a proper part of the ring still cuts at least two and adds loose distinctions. Taking the entire ring spends more than two such distinctions. For the cut control there are two separate arms at the attachment. Including one partially still cuts a meeting on that arm and adds a loose distinction; including its whole length spends more than the single meeting saved. Thus the least cut again takes precisely I. The funding rule adds two loose distinctions at each of s−1, s and s+1. At s it also cuts the two meetings to the added part. The contributions add when there are two attachments. This proves the claimed increments.

For example, the two outermost shared distinctions of the path have bond distance 31 on B, 39 with one attachment and 47 with two. Two path distinctions on one side with their intervening holders away from the attachment retain their exact old distance. Therefore a long pair spanning the attachment can keep the full increment even when both of its distinctions are far from it. Decay of a ball effect as a function of the marked distinction’s offset and decay of every spanning pair reading are different statements. At size one no original path pair distinguishes the two ring rates or a ring from the funded cut. The whole ball also counts newly present distinctions, so its change alone cannot establish a change of relations among background distinctions.

The independent finite check fixes the path contribution, enumerates every subset of appended knots on the ordinary side, checks connectedness and scores the cut directly. All 840 unordered source pairs in the seven path-bearing cases agree with the formula. The all-size step invariance and the later bond measurements use separate arguments.

[Checker](../../experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/source_bonds.py) · [Exact source tables](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/source_bonds.json)
