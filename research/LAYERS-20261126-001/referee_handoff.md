# Referee hand-off

Study `LAYERS-20261126-001`: a check by the thread, computed, referee pending. The rule frozen in `f2a940d3b8` before
its runs; exploration and the two reconciliations before that ([the note](README.md), [the decision](decision.md)).

**Claims.**
1. No start read keeps two independent whole-held facts after one round of parity growth under the ordinary count: every
   census start of three to five knots and 900 fresh starts of six to eight knots ([`frozen.py`](frozen.py),
   `frozen_*.jsonl`, [`score.py`](score.py), [`score.json`](score.json)); the 16 with four or more classes are read in
   [`multi_class.py`](multi_class.py) (labels read knot by knot in 15; one whole-held label in the sixteenth).
2. A ten-knot tree keeps two classes after one round, labelled by the sum of its nine shared distinctions
   ([`checks_tree_and_funding.py`](checks_tree_and_funding.py)); two or three rings joined in one start keep one class
   between them ([`layers.py`](layers.py), [`explore_more.py`](explore_more.py)). So the ring's class is a fact of the
   whole start (a narrowing of the guide's Chapter 12, logged).
3. The frozen one-class-per-piece rule fails in most starts meeting its conditions.
4. Growth adds no check on old distinctions under the ordinary count (the projection of the allowed changes is kept).

**Points to press.** Whether "read knot by knot" (a label some functional on one knot's distinctions represents, even on
every move and not fixed by the laws) is the right test of whole-held; whether the moves (shortest changes, no tie cap)
are computed as in `TWO-CLASS-SIGN-20261126-001` and `BOTH-LONG-20261126-001` (their counts should be reproduced on the
rings); whether 16 testable starts can support "no start keeps two"; the funding rule of the built starts; and the
guide's Chapter 12 wording of the three rungs against what is shown.
