Advisor consultation for `THIRD-LAYER-20261126-001` (study directory research/THIRD-LAYER-20261126-001; nothing frozen,
nothing run yet). Read docs/ADVISOR_HIVEMIND.md first (your BUILT-BINDING entry and its referee's judgement), then
research/BUILT-BINDING-20261126-001/README.md and decision.md, its referee report and argument note
(research/BUILT-BINDING-20261126-001/referee-R1/report.md, argument_note.md), and the code in
research/BUILT-BINDING-20261126-001/repro.py (rings_start, analyse) and built.py (the 14-knot start). Answer with
counterexamples, built candidates and checks; mark each claim's status; add one dated entry to the hivemind; touch
nothing else.

The coordinator's step (its words, summarized): take a start in which several second-layer knots exist (groups of
rings, each group's ring facts bound by a parity rule) and those second-layer knots share whole-held facts the way
first-layer knots share distinctions; ask whether, after ordinary growth, there is a fact that no single ring and no
single second-layer knot reads (a third-layer whole-held fact), and whether such facts are again bound. Say what the
smallest such start is. Stop at a third layer with a frozen test, or at the reason the step does not repeat.

What stands (refereed): under ordinary parity growth every class fact is a parity on the start's allowed states (the
changes that keep every start value are spanned by pairs and loops of four); every relation among class facts is a sum
of start laws; growth decides which start parities are class facts (the least change flipping a ring's parity grows 5,
7, 9, 11) and gives them new disjoint carriers.

My worry, to attack: the layers then collapse into one linear space. A "third-layer fact" is a sum of second-layer
facts, hence itself a class fact of the first-level reading; "read by no single ring and no single second-layer knot"
is then a statement about supports, and any sum across several second-layer knots qualifies trivially. So the
meaningful version needs the second layer's OWN small changes. Candidate definition: the layer-2 states are the joint
values C2 of the chosen layer-2 facts (a linear code fixed by the start's laws); layer-2 small changes are the
shortest elements of C2 through each layer-2 fact (or the elements of weight at most w); layer-3 facts are nonconstant
parities on C2 even on every layer-2 small change, read by no single second-layer knot. Under this definition C2 is set
by the start alone, so whether layer-3 facts exist would be a property of the start, and growth would act only by
deciding which parities are layer-2 facts. Is that right? Is there a better definition native to the growth (for
example layer-2 small changes read from the stage's own changes, or from the round at which each fact becomes a class
fact)?

Questions.
1. Build the smallest candidate start: second-layer knots (each a group of three rings bound through connecting knots
   with no loose distinction, as in repro.rings_start or the 14-knot start) arranged so that second-layer knots share
   facts (a ring, or a fact, belonging to two groups) and form a cycle at layer 2, so that the layer-2 analogue of a
   ring's class could exist. Give the knots and distinctions explicitly enough to code, with the predicted layer-2
   code C2, its shortest changes, and the predicted layer-3 fact. Note the difficulty I hit by hand: a ring's fact
   comes from the law-sum of a set of dead knots; for one ring to sit in two groups, the two groups' dead-knot sets
   must overlap and their attachments cancel; find a construction where they do, or show none can.
2. Its controls (as for the 14-knot start): what removes the layer-3 fact; what makes it free; what reading kills it.
3. Attack the collapse argument and my definition: counterexamples, and whether "the step does not repeat by itself"
   (a third layer exists only when the start's laws are built in three levels, as codes of codes) is the honest stop.
4. Which all-size proofs already in the record give parts of a general step (for example the closing law, the
   projection lemma, the argument note, the cluster identification of births, the reach bound), and what a precise
   conjecture with hypotheses (connecting knots with no loose distinction, growth using up loose distinctions, least
   flipping change growing with rounds) should say.
