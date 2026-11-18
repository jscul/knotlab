# Keeping the original eight distinctions

This is the second part of the [local-growth theorem](proof.md). It answers a stronger question than growing a new parity example. The original eight distinctions occupy the eight corresponding positions of an open two-by-two-by-two block, and projecting the completed infinite branch back to them gives exactly their original eight allowed rows. With this finite alignment the ensuing volume exponent is three around every distinction.

## 1. What extending betweenness by itself gives

Write \(B(a,b,c)\) for the rule that \(a=c\) implies \(b=a\). In common binary value conventions the cut states of a finite rectangular box are its two constants and the two orientations of each threshold in each coordinate. This makes the eight-place cut cube \(S\) have eight allowed rows, and every pair of different places has a free projection. Every stated betweenness used below has a constrained triple with free proper projections. This can be checked on the constants and the separating thresholds. The seed is the six-row knot \(B(10,00,01)\).

To complete the first square add its missing distinction \(11\) with \(B(10,11,01),B(00,10,11),B(00,01,11)\). To add a whole layer to an existing box, take a corner \(c\) on the chosen outer slice and the corner \(\bar c\) opposite it in the entire old box. Introduce \(p_c\) with \(B(\bar c,c,p_c)\). On every nonconstant row the value at \(p_c\) is the one at \(c\). At the old constants both values are possible. This creates just the new pair of threshold states. For each other \(x\) in that slice introduce \(p_x\) with
\[
 B(p_c,p_x,x),\qquad B(c,p_c,p_x),\qquad B(c,x,p_x).
\]
On the old cuts \(p_c=c\). If \(c=x\), the first rule fixes \(p_x=x\). If \(c\ne x\), the third fixes the same value. On the new cut \(c=x\ne p_c\), the second fixes \(p_x=p_c\). Each assigned value satisfies the remaining rules. This exhausts the possibilities and preserves every old row. Apply it once through the square to get the actual eight distinctions, and repeat on outer slices for any larger box. The construction supplies its choice of slice. The cut-box control uses only the earlier sorts of one-distinction extensions.

Counting literal disagreements across the cut states gives twice the coordinate step distance: precisely the thresholds between two values separate them. **Bond distance on this same family is two for every distinct pair once it is a proper box.** A pair separated by two or more steps admits a third, intermediate point of a shortest path. For an adjacent pair, extend a path by a step in a different direction with one of the old points in the middle. The resulting projected triple is a betweenness knot, since the three points are distinct and each pair is free. This supplies the matching upper and lower bounds. On the entire nonnegative orthant with all box betweennesses, any nonconstant state changes along a unit edge. On a square it must then be constant on each side parallel to the other direction: an equal diagonal forces both intermediate values to agree. The change propagates across every transverse translate, and betweenness on its line prohibits another change. Every nonconstant state is therefore a single threshold. Two distinct states disagree infinitely, as one may translate a point of difference along a direction used by neither threshold. The infinite cut-only family also lacks finite flips.

## 2. Attaching the eight to a rule that can extend their positions

Use the three cut directions of the eight-state relation in its common binary conventions, choose one corner as root and one direction to distinguish. They identify the eight old bits \(s_v\) with the positions \(v\in\{0,1\}^3\). The two remaining directions may be interchanged. If value conventions at individual places may also be exchanged, choose a reference pair of complementary rows to serve as the constants, and transport the local value conventions with this choice. The relation alone need not distinguish that pair. These are finite choices.

Use \(G\) and \(C\) from the first part. At each of the eight corresponding positions use the **existing bit itself** as the outgoing edge in the distinguished direction. In proof coordinates these eight edges are
\[
 K=\{(v,v+e_3):v\in\{0,1\}^3\}.
\]
The grown system has no auxiliary copy of these bits. Its allowed states are
\[
 Y=\{z\in C:z|_K\in S\}.
\]
The old ternary betweennesses remain present.

At every later site one can likewise observe its outgoing bit in the chosen direction. This identifies 27 actual position bits at side three and 64 at side four, including the original eight in both cases. The additional shared and loose bits implement the junctions. Bond distance is evaluated in the **full** system. If one keeps just these position bits, their marginal is the old eight-state relation times a free choice at every new position. To see this, prescribe every distinguished-direction bit subject only to \(S\), set every second-direction bit to zero, and solve the parity equations successively along each first-direction line for the outgoing bit. Start each line at first coordinate zero, where there is no incoming bit in that direction. This constructs an extension of every prescribed assignment. The other bits at a junction are therefore essential to this reading of dimension.

Here is a local growth presentation of \(Y\). At a match for the fixed eight-place cut template, attach its eight parity junctions in a predecessor-respecting order on the template. Each junction reuses its old distinguished bit, the appropriate inputs shared with earlier junctions, and two fresh outgoing bits in the remaining roles. Its parity equation leaves exactly two lifts per previously allowed row. After this bounded attachment the regular serial move of the first part reads the **parity-junction incidence** and its loose bits. A bit's appearances in old betweenness constraints persist and can be distinguished by their local relations. One can grow the side-three and side-four boxes as exact prefixes. Alternatively fill the finite down-set out to \(I_4\) according to the intended alignment. At this point both ends of every marked edge have been used. Subsequent complete generations follow the local parallel rule with anonymous port assignments.

The initial betweenness additions and the eight-junction attachment are finite templates. If one-addition steps are required, use the finitely many partial templates above, closed under renaming, as the initial alternatives of a single finite rule set. Each reads its bounded matching subpattern. No later rule consults a coordinate or an increasing template. This construction changes the local law after the cut cube. It exhibits a continuation with a chosen alignment, and it makes no uniqueness claim about how the old cube attaches. Nor does it require every later finite marginal to consist of threshold states.

Each ordinary step leaves four lifts per old row. Completing all future vertices in any down-set exhaustion extends every old assignment to an infinite one. In particular \(Y_K=S\). Another proof is that deleting \(K\) from \(G\) leaves it connected: horizontal motions allow any affected vertical column to be bypassed. The finite constraint lemma then gives \(C_K=\{0,1\}^8\). For a side-\(n\) open parity box containing the attachment, the pure parity relation has \(2^{2n^3}\) rows, equally many over each of the 256 old tuples by linearity. Restricting to the eight cut rows leaves \(2^{2n^3-5}\). It leaves \(2^{49}\) rows at side three and \(2^{123}\) at side four.

## 3. The ruler survives the finite restriction

**Upper bound on ball size.** In \(C\), finite observations whose anchors are at sup distance greater than one have independent projections, by the square argument in the first part. The eight anchors of \(K\) have diameter one. If \(A,B\) have anchor separation greater than three, at least one, say \(B\), is at distance greater than one from \(K\). In \(C\), \(B\) splits from \(A\cup K\). Restricting \(K\) to the nonempty relation \(S\) preserves independence between the resulting projections on \(A\) and \(B\). Thus \(Y\) splits at range three. Any minimal constrained support must be connected by steps of size at most three among its anchors: a separation into two farther pieces would factor the projection, and K2 makes both factors free. Consequently
\[
 |B_Y(e,r)|\le3(6r+1)^3 .
\]
This proof covers nonlinear dependencies introduced by the old cut relation.

**Producing bonds from each center to a growing set of targets.** Let \(P\) be a finite coordinatewise nondecreasing path. Suppose no edge internal to \(P\) is marked, and at most two marked edges meet its cut \(F=\partial P\). The exterior of \(P\) stays connected even after all of \(K\) is deleted. From any outside point the two positive horizontal rays cannot both meet \(P\), by monotonicity. They traverse no marked edge, so one escapes a box containing both \(P\) and \(K\). The exterior of the box is connected. The path remains connected as well. Hence deleting \(F\cup K\) leaves exactly these two components. By the finite constraint lemma the only nonzero parity check in \(C\) on \(F\cup K\) is the full parity of \(F\). Every even assignment on \(F\) extends to a row of \(S\) on \(K\), since at most two values of the latter are prescribed and every pair in \(S\) is free. The finite marginal characterization gives an actual full solution for the combined assignment. Thus \(Y_F\) is exactly even parity, a K1–K3 knot. Taking \(P=\{v\}\) proves this for **every junction's star**, since each star meets at most two marks and the exterior argument still applies.

Fix any distinction \(e\). Unless it is a bottom marked edge, start at its coordinatewise upper endpoint \(a\). For a bottom mark, start at the lower endpoint instead. There is a monotone path to \(b=\max(a,(2,2,3))\) taking at most seven steps, whose internal edges avoid \(K\) and whose cut meets at most two marks. Here are all the cases.

- At height zero in the marked two-by-two footprint, leave the footprint horizontally by a shortest exit before increasing height. This visits at most two bottom marked sites, with one marked edge incident at each.
- At height one in the footprint, this starting case comes only from an unmarked horizontal edge. At least one horizontal coordinate is one, since the start is its upper endpoint. Exit in that direction in one step. The initial site has just two incident marks.
- At height two in the footprint, move up immediately. At most one mark touches the initial site. Above height two the path is clear. Outside the footprint a monotone horizontal coordinate already at least two keeps it clear.

In each case complete the path monotonically to \(b\) after escaping. Its cut contains \(e\). For a bottom mark the other endpoint stays behind when the path first exits horizontally. In the other cases monotonicity excludes the lower endpoint. Continue monotonically to any \(b+t\) with \(t\in\mathbb N^3\), then stop. Any of the three positive edges \(f\) there is in the cut. The path length is at most \(7+\sum t_i\). Counting at most six edges per vertex and subtracting both incidences of each internal path edge bounds \(|F|-1\) by \(4\sum t_i+33\). Therefore for integer \(r\ge33\)
\[
 3\binom{\lfloor(r-33)/4\rfloor+3}{3}
 \ \le\ |B_Y(e,r)|\ \le\ 3(6r+1)^3 .
\]
This applies to every old and new distinction and to arbitrarily large radii. Counting only the observed position bits inside each full-system ball still gives cubic growth, since the construction of the lower bound includes one such bit at every target. The constants are bounds.

**Finite-change witnesses.** Every unmarked horizontal edge lies on a horizontal square avoiding \(K\). Every unmarked vertical edge lies above the marks or in a column with a horizontal neighbor also outside the marked footprint at that height. The corresponding square avoids \(K\). Flipping the square preserves any solution. For each marked edge, connect its two endpoints by a finite path in \(G\setminus K\). The edge and this path give an even finite change touching only that mark among the eight. Sum the eight changes mod two. This simultaneously flips all marked bits, and \(S\) is closed under complementation. It therefore preserves \(Y\) and flips each marked distinction at every solution. No circuit value serves as a magnitude in the ruler calculation.

## Controls and scope

The [literal replay](cut_control.py) starts from one betweenness triple, verifies the square and all five moves through the eight-place cube, then extends the old cut relation to 27 and 64 distinctions without using a parity equation. For the different, aligned parity construction it independently parameterizes its complete open finite relation. It checks all 256 tuples before imposing \(S\), exactly the original eight afterward, and every star at sides three and four. Restricting instead to the two constant rows destroys a full star projection, a control for the use of freedom on pairs in the proof. The infinite-volume conclusion uses the preceding inequalities.
