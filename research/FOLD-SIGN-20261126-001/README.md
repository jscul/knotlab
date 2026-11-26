# Time as a fold: is there a sign on the path of reading?

Epic `FOLD-SIGN-20261126-001`, under G18, at the coordinator's pick with the owner's intuition: "It is possible that
time itself being a fold is kind of like a 'meta' abstraction of the simulation. It feels like we're missing something
for 'quantum' angle to work." An argument, reviewed with the advisor ([question](advisor_question.md),
[answer](advisor_answer.md)); referee pending.


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** On 28 starts and 241 history
> prefixes (two growth programs agreeing), all 66 with twin births have sign-imbalance zero; of the 175 without twins,
> 148 have zero, 23 have +1, 2 have −1 and 2 have +2. **Narrowings:** ordinary growth adds no orders, but earlier studies
> did supply mixtures and signed sums over orders (the reordering line), so "nothing in the record sums over orders"
> holds for the laws, not for the record; order independence holds for complete readings of a fixed birth map (an
> allocation among interchangeable distinctions, or demand recomputed during growth, can change the end); the twin swap
> cancels when the two births are exchanged alone, not with their children; a supplied sign needs no comparison
> direction; a character gives a sign only on one orbit of readings, and one end can have imbalance 2 from one start and
> 0 from another; equal characters at the two ends need a transport law. Logged in `docs/CORRECTIONS.md`.
## The question (the coordinator's)

In ordinary growth with no added rule, is there any quantity defined on the path of reading (the order of births between
two ends that agree) that is well defined, takes two values and multiplies along paths? If so, does it put a sign across
a split, so that two ways of reaching one configuration can cancel? Stop at such a quantity with a frozen test, or at an
argument that every path quantity of the recorded laws is trivial.

## A. Signs on the orders of one history (an argument)

The states are the order ideals of a history's births (what has been born so far); a step adds one birth b to an ideal I;
a path quantity is c(I, b) = ±1, multiplied along a path, and it may read I as well as what the step makes.

1. **Squares decide.** Any two paths between the same ends are joined through squares (two independent births added in
   either order); the literature's name for this state graph is a median graph, and its filled cube complex is
   contractible. So c is the same along every path between two ends exactly when it is +1 around every square.
2. **What the law makes at a step does not depend on the order** (prior work, refereed: every order respecting the
   prerequisites builds the same births with the same parents, inputs, fresh counts and places). So a c computed only
   from the step's output is c(b), and its product depends only on the ends.
3. **Twins give +1.** If a renaming fixes I and exchanges two independent births a and b (twin offshoots of one parent,
   for instance), any c that renamings do not change has c(I, a) = c(I, b) and c(I + a, b) = c(I + b, a): the square
   is +1. No native sign exists on exchangeable pairs.
4. **Distinguishable pairs give a sign only by a choice.** Independent births that differ in a native attribute (depth in
   the prerequisites, fresh count, number of places) do admit −1 on their square: count the pairs ordered against that
   attribute (inversions). That c is path-dependent, so "every path quantity is trivial" is false as stated. But each
   such sign is the choice of an attribute and of a direction of it, which the law does not make; the exchange sign of
   the reordering line (swapping two independent occupied births costs −1) is one such choice, already stopped as
   supplied.
5. **And nothing sums over orders.** A sign cancels something only where contributions are added. The law adds nothing
   over orders: it makes one end, the same in every order. So even a chosen sign on paths cancels nothing until a rule
   sums the paths.

## B. Two lines of descent that reach one end (analysis; not run here)

Different readings of an end's descent (which knots are start knots, who is whose parent) are related by renamings of
the end, and the renamings of an end are native. Which two-valued character of them weights a reading is not: the parity
of a renaming on knots, on shared distinctions or on all distinctions are three choices (on all distinctions, swapping
two loose distinctions of one knot is odd, so the sign is ill defined almost everywhere). That a nontrivial character sums
to zero over a group is group theory, and choosing the sign character over the trivial one is the literature's choice
between fermions and bosons, which its configuration space offers without deciding (Laidlaw and DeWitt 1971; Leinaas
and Myrheim 1977). And the sign does not travel along growth: with signs of steps that renamings do not change, a renaming
that maps one growth path to another has the same sign on the end as on the start; if it fixes the start, its sign is +1,
so a twin exchange of odd parity on knots is consistent only with −1 on the twins' square, which is again the exchange
sign. The test written for this part (`fold.py`: renaming groups of grown ends, their stabilizers, odd renamings that
exchange two separated parts) is kept, not run: the swap symmetries of meeting patterns are the subject of another
thread, and the advisor expects the test to be close to foregone (twins in nearly every end).

## The stop

**No quantity of the recorded laws on the path of reading gives a usable sign without a supplied choice.** On the orders
of one history a sign needs a chosen attribute or the exchange rule (A3, A4); on the readings of one end it needs a chosen
character, and carried along growth it reduces to the exchange sign or to the start's own sign (B). And the deeper gap is
the one the owner named: **what is missing is not the sign but the sum.** The model folds time away: every order of
births reaches the same end, the end does not record the order, and nothing adds the orders. A quantum rule keeps every
order and adds them with weights that can cancel (the literature's sum over histories: Feynman, *Reviews of Modern Physics* 20, 367, 1948). The program has signs it
can supply; it has no rule that sums over histories.

**Intuition (an exact link, not evidence).** The signed count of a history's reading orders, each order weighted by the
exchange sign (its inversions against a fixed listing), is a known invariant of a partial order, its sign-imbalance; it is
zero ("sign-balanced") whenever two independent births are twins, which is the twin lemma above (Ruskey, *Journal of Combinatorial Theory B* 54, 77, 1992; Stanley,
"Some remarks on sign-balanced and maj-balanced posets", *Advances in Applied Mathematics* 34, 880, 2005). So the first rule that would sum histories with a sign
already has a literature: the program's histories would be weighted by their sign-imbalance, and every history with two twin births would cancel (histories without twins need not). The
cheapest test: compute the sign-imbalance of the histories ordinary growth makes from small starts, and see whether any
survives a twin.
