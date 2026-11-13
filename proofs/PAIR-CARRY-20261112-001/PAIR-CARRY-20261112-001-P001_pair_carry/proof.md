# A bond to every depth in sample 0, line 4710

In this archived branching rule a top distinction and a fresh distinction on the first branch belong to a bond at every positive depth. Write `L(s)` for the smallest such bond when all finite supports anywhere in the infinite pattern are eligible. The construction below gives

```text
max(3, 1 + ceil(s/6)) <= L(s) <= ceil(s/4) + 3,    s >= 2.
L(1) = 3.
```

The first construction below uses a pair of independent input bits and gives a bond of size `floor(s/2)+3`. A second explicit construction improves the upper bound by observing one helper every four levels. The lower bound comes from the accepted forgetting theorem and the verified forgetting length six in this record. Both bounds use the same endpoint convention. The top member may be any initial port and the target may be either new variable of the depth-s copy. Side copies and copies below the target are eligible for the minimum. [Four-level construction and finite table](period_four.md) · [Forgetting theorem](../../BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md) · [Original census](../../../experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/FINDINGS.md)

## The local rule

The input is sample 0, line 4710 of the committed one-definition inventory. Write `a,b,c` for the initial distinctions and `x,y` for the two distinctions introduced by a copy. The three local requirements are

```text
NAE(b,x,y),  NAE(b,x,c),  NAE(b,y,c).
```

`NAE` means not all equal. The recursive calls receive `(x,a,y)`, `(c,b,y)` and `(y,c,b)`, in that order. Each new copy has its own fresh `x,y`. No call passes on all three initial ports. For every assignment to the three inputs, setting `x=y=1-b` satisfies every local requirement. Repeating this choice in the children gives an infinite completion. Hence every triple entering an unopened side call, and the call just after the last specified level, can be extended. This permits exact elimination of those calls in the usual infinite limit. [Source and one-bit comparison](../../../experiments/TWO-LEVEL-BOND-20261112-001/TWO-LEVEL-BOND-20261112-001-E001_paired_levels/FINDINGS.md)

At most one of `x,y,c` can equal `b`. Equivalently,

```text
b = 1 - majority(x,y,c).
```

Index copies on the first branch from zero. Set `x[-2]=b`, `x[-1]=a`, and `y[-1]=c`. At level `i` the full input is `(x[i-1],x[i-2],y[i-1])`. The local requirements at that level are therefore equivalent to

```text
x[i-2] = 1 - majority(x[i], y[i], y[i-1]).                  (1)
```

## The bond and its exact projection

Fix a target depth `s >= 1`, and put `p = s mod 2`. Take the levels `i=p,p+2,...,s`. Observe the top distinction `x[p-2]`, one helper `y[i]` at each of these levels, and the fresh target `x[s]`. These are distinct physical variables. The top member is `b` for even depths and `a` for odd depths. There are `m=floor(s/2)+1` selected levels and `m+2` observed variables.

The exact constraint on these observations is the projection of the chain

```text
NAE(x[i-2], x[i], y[i])   for i = p,p+2,...,s.             (2)
```

Every actual state satisfies (2), since it is one of the three local constraints. To prove the opposite inclusion, take any assignment to the visible variables which (2) admits. Choose its intermediate `x[i]` on the selected parity to realize that chain. At each selected level set `y[i-1]=1-x[i-2]`. For any triple allowed by (2), this makes (1) true: among `x[i],y[i],y[i-1]` at least two bits are opposite to `x[i-2]`. All these choices use different hidden variables.

The remaining `x` values have the opposite parity. Choose `x[s-1]` freely, then solve (1) backwards at `j=s-1,s-3,...` down to the last nonnegative index of that parity. Each equation determines just `x[j-2]` from three already assigned values. For odd `s`, also choose `c=y[-1]` freely before the last step at `j=0`; for even `s`, the first selected level already chose `c=1-b`. The backwards equations end at the other top `x` bit, which is free. This completes the entire finite branch segment. The extension rule above completes every remaining call independently, so the projection is exact in the full infinite pattern.

## The two bits at the cut

There is an explicit two-bit description of these witnesses. At a selected level `i`, its full input has the form `(w,z,1-z)`. The next selected level has input `(v,q,1-q)`. Thus each boundary in this construction carries only the pair of actual bits `(w,z)`. With `h=y[i]`, the combined constraints of the two intervening steps are exactly

```text
NAE(z,q,h),        w = 1 - majority(v, 1-q, h).
```

Here `q=x[i]` and `v=x[i+1]`. The first condition transmits the bond along the selected parity. The second specifies which value of the other input bit is compatible with a chosen continuation. Starting from the last such bit and filling backwards realizes every allowed assignment of the chain. At the initial boundary one top bit is observed. The unused top coordinates are existential witnesses, so choosing these boundary relations places no additional requirement on the observed support.

For example, the visible triple `(z,q,h)=(0,0,1)` satisfies NAE. The backwards equation gives `w=0` for either value of `v`; a prescribed `w=1` would prevent that extension. The freely chosen entry and the backwards fill are essential.

This distinguishes two readings of carrying two bits. The construction works with two independent bits on the specified boundaries of a witnessing assignment. Dropping an arbitrary third input from every possible full port assignment requires a stronger equality of extension tables. In the last study that distinction was decisive for one bit. The [literal port tests](pair_tables.py) check it directly for pairs here. [Earlier extension failure](../../../experiments/TWO-LEVEL-BOND-20261112-001/TWO-LEVEL-BOND-20261112-001-E001_paired_levels/FINDINGS.md)

For instance the raw pair `(b,c)` determines all possibilities for `(x,y)` one level later, independently of the value of `a`. In the next copy those outputs occupy slots 0 and 2. At two levels none of the nine choices of two input slots and two outgoing slots has that equality across all full inputs. There is a longer isolated link: at three levels the pair in slots 1 and 2 determines a four-member knot with outgoing slots 0 and 2, whose projection allows 14 of the 16 words. The proof of (2) uses exact extension of the whole observed support, which the backwards construction establishes despite this obstruction.

## Why every observed distinction is essential

Write `z_0` for the top bit, `z_m` for the fresh target and `h_0,...,h_(m-1)` for the helpers in order. A constraint `NAE(z_j,z_(j+1),h_j)` forces `z_(j+1)=1-z_j` when `h_j=z_j`. When `h_j` differs from `z_j`, either next value is available. Once either intermediate value is possible, both next values are possible for every remaining helper.

The projected chain excludes exactly two assignments. For a chosen top value `t`, the excluded helpers are `t,1-t,t,...` and the excluded target equals the **last helper**. Every other word is realizable. For one selected level the excluded words are `000,111`. For two, in the order (top, first helper, second helper, target), they are `0011,1100`. The two forbidden words are complements. This establishes whole-set binding (K1). After deleting any one distinction, every assignment to the others has two completions that differ in one bit, so at most one can be forbidden (K2). Allowed words exist (K3). This proves the claim at every depth after quantifying all the side copies in the full infinite pattern.

## Holding the same top bit at every depth

One may also require the top endpoint to be `b` at every depth. For even `s` the preceding construction already does this. For odd `s` start with the even chain through level `s-1`. At its last level interchange the roles of `x[s-1]` and `y[s-1]`, which occur symmetrically in (2). Observe `x[s-1]` as the last even helper. Use `y[s-1]` as a hidden bit shared with one more knot, `NAE(y[s-1],x[s-2],y[s])`. Its helper is `x[s-2]` and its fresh target is `y[s]`.

For the reverse inclusion, use the earlier even extension up to the last even level, including `c=1-b`. The last opposite-parity value `x[s-2]` was free at the start of the backwards fill of that segment. Start that fill at the value prescribed by the appended knot. Set `x[s]=1-x[s-2]` at the odd target. Equation (1) there reduces exactly to the appended NAE. All root and side requirements therefore extend, and the same proof of K1–K3 applies to this longer chain. In particular the depth-one support in the order `(b,x[0],a,y[1])` excludes just `0011` and `1100`. The fixed-`b` size is at most `ceil(s/2)+3` for every positive `s`.

## Consequence for the 154 records

The archived census places precisely sample 0, line 4710 in its 154 cases with a conditional linear lower bound. For this rule every positive depth now has an upper construction as well. Updating that single case brings the number with proved linear growth to **70** out of 664 and leaves **153** of the original 154 conditional cases. The 432 bounded cases and nine other unresolved cases complete the same sample. These counts refer to recorded rules. The exact minimum with arbitrary side support at general depth remains open.

At fixed size the [unrestricted decision procedure](../../BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/proof.md) tests every finite placement, including helpers anywhere in side copies or below the target. At budget three its accepted depths are exactly 0 and 1. At budget four they are exactly 0 through 4. The two computations reach repeated states with period one. Combining these exclusions with the four-level construction gives the exact unrestricted minima at depths 1 through 8: **3, 4, 4, 4, 5, 5, 5, 5**. Depth zero is auxiliary to the tests. [Raw projection and fixed-budget results](result.json)

The conclusion concerns finite projected supports in the allowed states. The fixed recursive presentation supplies the first-branch depth. Source labels for flips at a specified infinite solution are outside this result. Finite checks accompany the symbolic construction. The local advance over the accepted single-bit obstruction is an all-depth proof for this particular rule; no field-wide novelty claim is needed.

## Reproduce the checks

Run from this workspace with its Python environment. The first command checks the original local rule, both alternating-level constructions, every deletion through depth 14, and the unrestricted decisions for sizes three and four. The second checks the exact table for the shorter construction and queries the original clauses independently. The third tests equality of projected output tables for fixed full inputs.

```sh
study=proofs/PAIR-CARRY-20261112-001/PAIR-CARRY-20261112-001-P001_pair_carry
.venv/bin/python -B "$study/check.py"
.venv/bin/python -B "$study/marked_support.py" --max-depth 32
python3 -B "$study/pair_tables.py"
```
