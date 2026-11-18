# Referee report MEET-HIST-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - Every number recomputes exactly in the referee's own code, for five to k = 4 and six to k = 3: the four readings' shares, and
    H(order | line named), which comes to 0.8950, 2.1963 and 3.8788 bits at five.
  - The readings are implemented correctly: NL's mirror quotient, NO's colouring, and N quotiented by the mirror as NL is.
  - The sanity row NO = N holds as a partition of the grown bases at every level.
- **What changes, in wording.**
  - **"The order cannot be read from the states" should be "is mostly not determined".** The conditional entropy is 85% to 90% of
    its maximum, log₂ k!.
  - **The nesting needs only a small part of that order:** 0.22 to 0.36 bits at five, against 0.9 to 3.9 bits unread. That part is
    not recorded either.
  - **"The knots record the nesting directly" says only that the starting knots are still there.**
  - **A preview of B199.** The co-knotted pairs added by growth, read alone and unnamed, carry almost none of the nesting: 0 at five,
    at most 0.04 at six.

## What holds

- **The code (the owner's points 1 and 2).**
  - **U** is the state class.
  - **NL** colours each line distinction by its place and the new ones alike. It takes the lesser form of S and its line reversal.
  - **NO** colours the line alike and each new distinction by its order of growth. The reversal is a line renaming, so it is already
    inside NO.
  - **N** is the least of S and its reversal, so it is quotiented as NL is.
  - **H(N | NL) = H(N) − H(NL).** It is computed from the pooled joint law of (NL, N) and is correct, since N refines NL (checked).
  - **NL is "knowing which distinctions are the line's"** (the owner's doubt). While no state is added, the line's distinctions keep
    their mutual counts, 2 × their steps apart. So knowing them as a set gives their places up to reversal. This is the same argument
    that makes NO = N.
- **A fresh recomputation (the owner's point 3; `referee_hist.py`).**
  - **Method.** The referee's own KF3 engine, with readings by its MEET-DIST-R1 tables: U by registry, NL by the least form over
    orders of the new distinctions and over reversal, NO by VF2 with node colours, and N.

  | n0, k | U | NL | N | H(order \| NL), bits | log₂ k! | I(bare; order \| NL), bits |
  | --- | --- | --- | --- | --- | --- | --- |
  | 5, 2 | 0.6035 | 0.6967 | 1.0 | 0.895 | 1.0 | 0.219 |
  | 5, 3 | 0.3948 | 0.6904 | 1.0 | 2.196 | 2.585 | 0.224 |
  | 5, 4 | 0.2230 | 0.5052 | 1.0 | 3.879 | 4.585 | 0.357 |
  | 6, 2 | 0.6484 | 0.6697 | 0.8313 | 0.914 | 1.0 | 0.223 |
  | 6, 3 | 0.6341 | 0.7091 | 0.9113 | 2.250 | 2.585 | 0.279 |

  - Every share and every H(order | NL) equals the study's results.json to four digits.
  - The NL and N columns equal the referee's MEET-DIST-R1 named numbers ("line named" and "all named"). NO and N give the same
    partition at every level.

## 1. "The order of growth is not readable" (the owner's least sure; wording)

- **What a positive H(order | NL) shows.** The order is not a function of the line-named states.
- **How much is unread.** The size of what is left is the useful measure: 0.895 of 1 bit, 2.20 of 2.58 and 3.88 of 4.58 at five, and
  0.91 of 1 and 2.25 of 2.58 at six. So the states record only about 10% to 15% of the order.
- **The fix.** Write "the states leave 85% to 90% of the order undetermined", not "cannot be read".

## 2. Does the nesting need the whole order? (the coordinator's question; wording)

- **No.** The part of the order that bears on the nesting is
  I(bare; order | NL) = H(bare)·(share_N − share_NL):
  - 0.22, 0.22 and 0.36 bits at five;
  - 0.22 and 0.28 at six.

  That is 6% to 24% of the order's unread entropy.
- **Is that part recorded?** No. It is not recorded either, since share_N > share_NL means exactly that it is not a function of NL.
- **A fair sentence.** "What the distances miss of the nesting is a small part of the order of growth, about 0.2 to 0.4 bits. That
  part is not recorded in the states, nor is most of the rest of the order."
- **What overstates.** "The states don't record the order" says more than is needed. The nesting needs only part of it.

## 3. "The knots record the nesting directly" (the coordinator's question; wording)

- **What it says.** The grown base's knots include the presentation's own knots, by construction. So reading the knots recovers the
  presentation, and with it the nesting. That is "the starting knots are still there", and nothing more.
- **The real question** is B199's: do the knots growth added, without the starting ones, record it?
- **A preview, not B199's frozen test** (`ADD`).
  - **The reading.** The co-knotted pairs that hold a new distinction, as a graph up to renaming, with no states and no names.
  - **The share.**
    - 0.0 at five for k = 1 to 4;
    - 0.0, 0.009 and 0.040 at six for k = 1 to 3.
  - **What follows.** The added pairs' pattern alone carries almost none of the nesting. If B199 finds it in the added knots, it will
    come from those knots read together with the states, or as triples, not from the bare pattern of added pairs.
- **The fix.** Reword the owner's-terms line: "the knots record it" means the starting knots. The added knots alone are B199's open
  question.

## 4. Prior work (the owner's point 4)

- **Known.** The tools are standard: mutual information and conditional entropy.
- **Specific to the program.** The object is. Nothing outside applies.

## Fixes for the thread (listed for the owner, not folded in)

1. **The order.** Write "mostly undetermined (85% to 90% of its entropy)" for "cannot be read". **Not a block.**
2. **What the nesting needs.** Only 0.2 to 0.4 bits of the order bear on the nesting, and that part is not recorded. Say so beside
   "the states don't record the order". **Not a block.**
3. **The knots.** Say "the starting knots record it, by construction". Name B199 as the real question, with this preview: the added
   pairs alone carry about none of it. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, `job.py` and `merge.py`;
  - wrote its own four readings, the shares, the conditional entropy, the nesting-relevant part and the added-pairs preview
    (`referee_hist.py`), on its MEET-ORDERS-R1 and MEET-DIST-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_hist.py`.**
- **`referee_hist_5_4.json` and `referee_hist_6_3.json`.**

Reproduce, from `research/MEET-HIST-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_hist.py 5 4 > referee_hist_5_4.json
../../../.venv/bin/python -B referee_hist.py 6 3 > referee_hist_6_3.json
```
