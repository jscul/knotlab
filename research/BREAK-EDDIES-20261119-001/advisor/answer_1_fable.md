['claude-fable-5-2']
# Advisor answer 1 (BREAK-EDDIES-20261119-001)

**I could not run or reliably read anything this session, so I have no rule and no numeric predictions for you (questions 2 and most of 5).** Everything below is hand analysis of the numbers in your question.

The shell and file reads returned results that contradict each other:
- the same deterministic script gave different counts on reruns;
- `sha256` of one string came back with two different values from Python and from `sha256sum`;
- existing files were intermittently "not found", and long outputs came back truncated or rearranged.

I wrote nothing in the repository and removed my scratch directory. If this is the machine and not my harness, it could affect your runs too; hashing one file twice would tell you.

## Three things in your data to settle first

1. **Open places change the loop length.** #17 and #20 have the same touches and the same round-1 groups, but W is y^4 (1 + y) against y^2 (1 + y). The only difference is knot 0 with 3 against 5 open places and knot 1 with 4 against 3.
2. **The first counts do not match the round-1 groups.** #17 and #20 share their groups but list 9 and 10 after the knot count. #17 has six groups that are not touching triangles, and #1 has five against a listed 8. Either that entry is not round 1, or round 1 makes more junctions than groups.
3. **The theta's groups are not maximal.** Knots 1, 4 and 5 are pairwise non-touching neighbours of knot 0, which the cluster proof's Fact A makes one valid set of three. Your list has them as three pairs, while #17 lists [1, 5, 7] as a triple. I need to know which reading the growth uses before I can say anything about hyperedges.

## Question 1: which loop

No graph on the round-1 groups alone can give these weights, by point 1. The object has to carry each knot's open places left after round 1.

The loop is also not in the start. In #23 and #25 the touching graph is two triangles joined by the path 4-3-1-2, so the block graph is a tree. The rings appear in round 1:
- 0, j(0,3), 3, j(3,7), 7 and 5, j(1,5), 1, j(1,6), 6 are rings of five;
- 1, j(1,4), 4, 3 and 2, j(2,3), 3, 1 are rings of four.

So the candidate object is the round-1 structure (knots plus first junctions) with leftover open places. In #1 the same reading gives rings of five through knot 6, and W = y^5 (1 + y) matches a bare ring of five. In #23 a ring of five gives only y^3, so two ring knots cost no round. I can't say which two without running it.

## Question 3: the theta

Your counts do not look like a fixed-rate eddy. The ratio sits at 1.4286, 1.4289, 1.4308 for three rounds, then the last two counts leave that trend. Against 1.43 times the previous count, the excess is 0.5, then 36, then 325.

That is the same onset as #6 (34, 49, 94, 489), so I would class the theta with #4 to #6: explosive with a long fuse.

Two further points:
- **Two loops sharing a path stay rational.** In any model with finitely many junction types the series has a determinant denominator. A truly algebraic series needs unboundedly many types.
- **A candidate for the plateau, from four ratios only.** x^5 = x^3 + x^2 + 1 has root 1.4291, which reads as W = y^2 (1 + y) + y^5. The recurrence a_n = a_(n−2) + a_(n−3) + a_(n−5) leaves residuals of −13 to 0 up to the count 920, then +39 and +380. Treat this as numerology until Berlekamp–Massey on the plateau rounds alone confirms it.

## Question 4: the explosive starts

This is a hypothesis from the rule as you state it, with d read as the members that have no open place left.

A junction over p knots with d exhausted members brings d fresh places, so it becomes a knot with d open places. Its neighbours are pairwise non-touching, so they later form a valid set at least as large. Where a pair has two common neighbours, or two groups of three overlap, two such sets can merge and the sizes add. Set size then grows round by round, and the number of valid sets inside a large set with touching pairs multiplies.

Your memory limit supports this: 6 GB at 2,258 junctions in a round means something other than the junction count is large.

To test within memory, record per round the largest valid set and the most fresh places on one junction. Keep fully exhausted, untouched junctions as a counter instead of objects.

## Question 5: predictions I can stand behind

1. The largest valid set stays bounded in all 26 rational starts.
2. **Risky:** it grows without bound in #0, #4, #5 and #6.
3. **Risky:** the theta's round-19 ratio exceeds 2.
4. No linear recurrence of order 8 or less fits the theta's counts through round 18.
5. Each rational annihilator still holds at round 60.
6. Counts do not change when a round's valid sets are processed in reverse order.
7. Raising one knot's open places never lengthens the loop (#17 to #20 is one instance).

If prediction 2 fails, my mechanism for question 4 is wrong and the theta could be a finite two-loop eddy after all.
