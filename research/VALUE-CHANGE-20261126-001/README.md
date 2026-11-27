# Reading a change: is it native, and does it give separated readers a table above the classical bound?

Epic `VALUE-CHANGE-20261126-001`, under G18, at the coordinator's pick after `EVENTUAL-R-20261126-001` and the advisor's
answer on which pairs of values may fail to commute. Part A runs the advisor's three cheap checks of its hand arguments.
Parts B and C take the candidate the coordinator judged closest to the model's own terms, *value against change*: all
values have joint values, and a value and the read of a change that flips it do not. Computed, with an argument; the
advisor consulted read-only in the repository ([question](advisor_question.md), [answer](advisor_answer.md)); referee
pending.

## A. The advisor's three checks ([`check1.py`](check1.py), [`check2.py`](check2.py), [`check3.py`](check3.py))

1. **The commutation conditions of rule R, upheld.** On the 300 sampled census starts of the rule-R study (uniform over
   the census, seed 20261128) grown up to six rounds, every settled pair of knots beyond the start follows the
   advisor's conditions ([output](check1_out.txt)): born in one round 8,684 of 8,684; parent and child 6,013 of 6,013;
   two rounds apart 18,547 of 18,547; three or more apart 22,870 of 22,870. A fifth class the advisor's table left out,
   one round apart but not parent and child (no knot can hold a place of each, since every parent of a birth is a newest
   knot), follows the far-pair rule, not both odd: 19,110 of 19,110. All 134 structures with six rounds of births have a
   settled failing pair, as the advisor's argument says they must.
2. **A rule in holders alone cannot sign the eight- or sixteen-knot closure odd; a rule in holders and descent can**
   ([output](check2_out.txt)). On the closures of three- and four-label subsets, which ordinary growth makes from one
   knot of three or four places: among choices of which unheld pairs fail to commute that are unchanged by every symmetry
   of the holders, 4 (three labels) and 8 (four labels) keep every two knots commuting, and none gives an odd sign
   (upheld). Among choices unchanged only by permuting the labels (the founder kept fixed, so descent can be read), an
   odd sign is attainable on both; on the eight-knot closure one class of six pairs suffices (the founder's distinction
   toward one label failing to commute with the distinction from a second label's single knot toward the third). So the
   advisor's conditional ("if no odd solution exists, direction 1 reduces to the start's own pattern") is not met.
3. **Every knot's non-commuting values form an allowed change, upheld** ([output](check3_out.txt)): 56 of 56 knots of
   the ten sampled closers whose knots commute under R (14 of them commute with every value).

## B. What could carry a read of a change?

A *value read* of a set of distinctions is the parity of their values on one allowed word. A *change read* of a set x
asks of the state whether flipping x is allowed: it compares two words, w and w + x. Searching the record for something
that performs or carries such a comparison:

- **A knot's law** constrains one word's values; no knot's law relates two words.
- **A shared distinction between a parent and a child** is one distinction with two holders, read as one value.
- **The growing end** consumes loose distinctions and adds laws; it compares no two words.
- **The record's changes** (the motion study's moves, the classes of the two-class study, the least change that flips
  a whole-held fact in the tower studies) are sets of distinctions whose flip keeps every law: objects of the structure,
  each a fact about the laws alone. Where the record reads one (the free-clocks study's change read), the read is
  recorded as supplied.

So **allowed changes are native as objects, but nothing native reads one.** The record does hold functions of two
allowed words, and every one is supplied: the free-clocks study's unordered pair {s, s + T} (`FREEDOM-CLOCKS-AND-BIRTHS-
20261120-001A`, which already wrote this rule: its counts for a change read with values on other distinctions are the
ones below), and the side-sign study's squared signed sums over completions, which amount to reading every unread
distinction for its change. Under parity a change read's answer depends on no word: certain where the change breaks no
law, an even coin otherwise. What must be carried is how those coins agree between readers.

The least state that carries it is the *coherent counting state*: every allowed word weighted equally and every two
related equally (the literature's equal superposition over the allowed words; a stabiliser state whose certainties are
the knots' laws, read as values, and the allowed changes, read as changes). Its value reads give exactly the counts.
With values and changes each read alone it is no different from a list: draw an allowed word and, independently, a sum
of knot laws, and let a value read answer the first and a change read the second (the literature's rebit result,
Delfosse, Allard Guerin, Bian and Raussendorf, 2015; argued, not computed). It differs from every list only through
*combined questions*, a change of one set read together with a value of another.

## C. Two separated readers on the joined-ring starts ([`css.py`](css.py), [`rings.py`](rings.py), [preregistration](preregistration.md), [tally](tally_out.txt))

**Readers and middle.** The built binding study's joined-ring starts: rings of five (or four) knots, each ring knot
holding two loose distinctions, every pair of rings joined by two connecting knots linked directly or through a chain;
ordinary parity growth, rounds 0 to 2. A reader holds a ring's region (every place of the knots descended from that ring
alone, or only those places no other knot holds: two choices, both run); everything else is the middle. The measure is
e, the number of shared pairs of anticommuting certainties between the readers in the coherent counting state (the
literature's ebits of a stabiliser state, Fattal and others, 2004): e = 0 means their joint table has a list of values
whatever they read; an excess above the classical bound needs e ≥ 1, and certainty in the literature's two-reader game
(Mermin and Peres's square) needs e ≥ 2.

**The separability argument** (by hand, checked on every row). If no knot holds a distinction of each reader, every
allowed change supported on the two readers' distinctions splits into an allowed change of each (at each knot the
change's distinctions lie with one reader), so their shared certainties are value laws only and e = 0: the readers'
joint state is a mixture of products, and no read of any kind gives them an excess. The same holds when the middle is
read for values.

| Pairs of readers | Middle unread | Middle read for values | Middle read for changes, its record sorting the table |
|---|---|---|---|
| Two rings, 78 separated pairs (5 families, 3 rounds, 2 reader choices) | e = 0 on all | e = 0 on all | e = 1 on 74; 0 on the 4 of the family whose chain holds a loose distinction, after round 0 |
| One reader holding two rings, the other the third (24 rows) | e = 0 | e = 0 | **e = 2 on the 18 rows of the three three-ring families without a loose chain**, at every round read; 1 on the loose-chain family |
| Control: two adjacent knots of one ring (not separated; 15 rows) | 1 at round 0, 0 after | 1 at round 0, 0 after | 1 |

- **Where e = 2, the square is certain.** Built from the readers' own reads (changes, values and combined questions on
  their own distinctions), all nine cells of the square are certainties of the sorted state on all 18 rows, and each
  row's and column's reads commute on the first reader's side: the readers win the square's game with certainty, where
  any list of values wins at most 8 of 9. It is a quantum table (a stabiliser state), so it signals nothing and sits at
  the quantum value.
- **What the middle's change reads do.** e with the middle read for changes equals the number of independent value laws
  tying one reader's values to the other's (the advisor's identity, agreeing on all 78 rows): the readers' classical
  value correlation, turned into shared pairs by reading the middle's changes. A chain that never closes (a loose
  distinction in it) gives no such law, and its pair stays at 0.
- **Even one distinction is enough:** reading only the distinction the pair's two connecting knots share for its change,
  the rest unread, gives e = 1 on 36 of 39 pairs (0 on the loose-chain family's first pair).

Predictions (frozen): 1 held on 74 of 78 rows (the 4 others are the loose-chain family after round 0, outside what was
derived); 2 held on 36 of 39 (the 3 others the same chain); 3 held (15 of 15); 4 held on 6 of 8 (the loose-chain
family gives e = 1, not 2); 5 held. A code deviation after the run (the square's pair search) changed no other field.

## So: is reading a change native?

**No, and the table above the classical bound needs three supplied things:** a state that relates allowed words (the
coherent counting state), combined questions (a change of one set read with a value of another), and a middle reader
who reads changes and whose record sorts the table (the literature's event-ready arrangement: Żukowski, Zeilinger, Horne
and Ekert, 1993; not communication, since the middle's setting is fixed and its record does not depend on the readers'
settings, but a third reader). With them, readers whose regions share no knot win the square's game with certainty on
three joined-ring families (one reader holding two rings). Without the middle's change reads, nothing they read gives an excess. This confirms the
advisor's section 4 exactly: separated readers need a supplied preparation or one allowed change running the whole way
between them, and here the change runs through the middle, which someone must read.

## What this does not say

- That anything in growth or the knot test reads a change, or makes the coherent state.
- Anything about not-all-equal, sampled starts, or more than two rounds of growth.
- The three-reader case with the middle as a reader with two settings (the advisor expects a three-reader game of
  certainty at e = 1; not run).

## Scaffolds

The coherent counting state (supplied; the counts alone are its value reads); the reader choices ('places', 'own', two
rings against one: the e = 2 result needs the union); the middle's treatment (unread, values, changes, one distinction);
the families (the built binding study's builder; built starts, not sampled; one with a loose chain as the control that
can fail); the engine (canonical). The separability result is about the model's reads in any state of this kind; the
e = 2 square is about the scaffolds listed.
