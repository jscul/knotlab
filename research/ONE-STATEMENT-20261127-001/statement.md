# One statement for both layers


> **Referee R1: refuted, two Blocks** ([report](referee-R1/report.md)). The census counts hold and extend: one marked
> not-all-equal presentation on 7,074 of 7,075 census starts, every competitor class tried (other knot counts, two-place
> rules, disconnected, repeated supports) adding none; but the one ambiguity has no loose distinction, so the census
> never tested family recovery under not-all-equal. **Block:** in general it fails: two connected ten-knot
> presentations with the same 209,952 states and the same two loose distinctions have two families and one (each has
> two redundant laws; [witness](referee-R1/family_witness.json)). **Block:** at the second layer the loose set does not
> choose the basis: of 11 possible loose sets, 8 select one basis and 3 admit four each, with different knot sizes
> (3, 3, 3, 6 against 3, 3, 4, 5); the 20 bases come from four different completions. **Narrowings:** under parity the
> entailment holds with the cost restricted to changes holding exactly one loose distinction of each family and no other
> (a seven-knot start gives 8 against 6 for the earlier pair cost); the completion adds the parity law on the loose set
> (often of fewer than three places), and Whitney's twists cover the two-connected case; under not-all-equal the parity
> argument is what is not available, other recovery results hold (an earlier all-size classification covers connected
> presentations with every law essential, `THREE-READERS-AND-GROWTH-20261120-001B`); a3 as frozen measured law
> distinctions, 92 against 40, reversing the prediction (the carrier count 36 against 40 was not what the frozen code
> measured); what recurses: on the ring witness each family's live knots form a path that growth lengthens by one,
> and ordinary growth does permit a two-place birth that closes (three laws on abl, cdm, abcd give one on lm).

`ONE-STATEMENT-20261127-001`, part (b). A statement with its sources; what is proved, what is computed and what is our
choice are marked.

**The statement.** Under parity a presentation is a completed system with one knot left out, and the loose set names
that knot. Add to a start one knot holding every loose distinction: every distinction is then held twice, the laws of
all the knots sum to nothing, and the allowed states are those of the completed system. Leaving out any one of its knots
gives back the same allowed states; the loose set says which one was left out. Two presentations with the same allowed
states are completed systems with the same cycles, so by Whitney's theorem they differ by twists at two-point cuts
(Whitney 1933; in the record, `STATES-GROWTH-20261119-001`, refereed: every one of parity's 145 same-state pairs whose
completed systems are three-connected has the same completed system with a different knot left out). The same holds at
the second layer: the nine facts of three rings of four, with their relations, are again a completed system (each
relation a knot, the one relation among the start's families its own), and the tree and the loop are two ways of leaving
it as knots.

**What the loose set fixes, and why that agreement is not evidence.** With the loose set marked the reader can name the
start's families and their tree from the allowed states alone: two loose distinctions have one holder exactly when
flipping both is an allowed change; two holders are candidates exactly when some allowed change of four distinctions
holds one loose distinction of each and no other; and the cost of the least change holding one loose distinction of each
of two families is the pair cost (`TREE-PROOF-20261127-001`). Each of these is a fact about the allowed changes and the
loose set, so every presentation of the pair gives the same families and the same tree. That is entailed. The census
check that found it on all 7,075 starts (`MARKED-LOOSE-20261127-001`) and the held-out starts read so far therefore checks
the code, not the model.

**What is ours.** "At most two holders" at the second layer (each fact in at most two relations) is our requirement,
copied from the first layer, where the engine imposes it (a distinction has at most two holders). Of the 840 bases of the
relations among the nine facts, it keeps 20, of which 12 meet in a ring and one is the tree (part (a), a1). The model
imposes nothing at the second layer, so this is a scaffold (register entry A306). [R1: there are 11 possible loose sets; eight select one basis each and three admit four each.] Which of the 20 to take is
then the choice of which facts are loose, the second layer's version of the reader's question. A preference for shorter
relations does not choose either: shorter in places favours the tree, shorter in carrier distinctions can favour the
four-place relation (rings of 10, 4 and 4: 36 against 40), and shorter in the laws behind it favours the tree again
(40 against 92) (a3).

**What growth does to the second layer** (part (c)). It is not a start of its own: read as one, the tree presentation
grows four three-place births and closes at round 3, while on the grown witness the nine facts gain a two-place copy of
each family fact every round and never close. So the second layer is not grown by the first layer's law: no recursion
here.

**Where something could be learned** (part (d)). Under not-all-equal no law is a sum of others, so the parity argument above is not available [R1: other
recovery results hold there], and whether the allowed states with the loose set marked fix the knots, the families and the tree is a
question about the model. Its run is in `README.md`, part (d).
