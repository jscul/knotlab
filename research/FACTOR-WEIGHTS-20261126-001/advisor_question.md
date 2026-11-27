You are consulted read-only from the repository root. Read docs/ADVISOR_HIVEMIND.md first (today's entries on the
change-read and third-reader studies). Attack, not verdict: counterexamples and checks.

Context. THIRD-READER-20261126-001 (research/THIRD-READER-20261126-001/README.md, part A) showed that readers whom no
knot joins share nothing a list cannot give, in any state whose amplitude (or weighting) is a product of one factor per
knot. The one way out left is a weighting that does not factor over knots. The coordinator asks: do the record's own
weightings factor? New epic FACTOR-WEIGHTS-20261126-001 (nothing run yet).

(a) The two countings (docs/RESEARCH_GOALS.md B324; research/TWO-COUNTINGS-20261125-001/): every finished
configuration counted equally, and a random start that then grows (each old word's weight divided equally among its
completions). My argument that the second factors over the grown structure's knots: the births of one round have
disjoint fresh distinctions, so an old word's completions are a product over that round's births, and a birth's count
depends only on its own inputs (under not-all-equal 2^f minus one if its inputs are all equal, 2^f otherwise; under
parity 2^(f-1)); so the grown weighting is the start's uniform weighting times one factor per birth, a function of that
birth's places. The 20/9 excess (SETTING-AS-REREAD-20261123-001, A240) then came from settings being distinctions of
the state, not from a non-factoring weighting. Counterexamples? The forbidding arms (one fewer, arity floor), where some
old words have no completion? Waiting births on the recent line's engine?

(b) Bound whole-held facts (research/THIRD-LAYER-20261126-001/referee-R1/: three rings of four, split attachments,
double links; facts R, S, T (whole rings) and P, Q (the first ring's alternating families), relations R+S+T = 0 and
P+Q+R = 0, which are sums of knot laws). A weighting restricted to one value of such a fact does not factor over knots.
My argument that the separability argument still gives nothing for readers set on different rings: restricting the
coherent counting state to f = v keeps the CSS form, with changes those allowed changes x with x.f = 0; a cross change
on two ring regions splits into two allowed changes, and each still has even overlap with f, because no change local to
one ring flips a bound fact (x_1 . (R+S+T) = 0 and S, T lie off ring 1, so x_1 . R = 0). The general criterion I propose:
restricting to f breaks separability for readers A, B exactly when some change local to A and some change local to B
each flip f (then f = {a, b}, the parity of two values on the two sides, already does it: the literature's projection
onto a joint parity). Does anything in the model ever restrict to one value of a fact without fixing every value of its
carrier (a closed start's class is fixed by its start values, but those fix the whole start word, a product of
factors)?

Checks I intend (attack them and add the cheapest discriminating ones):
1. Exhaustive on small census starts, parity and not-all-equal, the three arms, one and two rounds: the grown weighting
   of every word against the product of per-knot factors.
2. On the referee's three-ring start at rounds 1, 4, 5 and 6: every change local to one ring's region against each of
   the five facts and their sums; e for ring readers in the coherent state restricted to each fact's value.
3. A control that can fail: two rings joined by nothing, restricted to the parity of one loose distinction of each: e = 1.
4. Beside it, the coordinator's cheap check: the event-ready square on sampled census starts (grown two rounds, regions
   by lineage of start knots), the share of separated pairs with two shared pairs.
Questions: is (a) right (including forbidding arms and waiting)? Is (b)'s criterion right, and is there any recorded
weighting or reading that restricts to a fact's value alone? Is "every recorded weighting factors over knots" provable
from the engines, and which lines of code would a referee check?
