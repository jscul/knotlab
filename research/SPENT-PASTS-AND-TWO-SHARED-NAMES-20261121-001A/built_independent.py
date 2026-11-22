"""A second count on all built stages using only the previous loose word and actual paid names."""

from collections import Counter
import gzip
import json
from pathlib import Path
import numpy as np

from controls import as_array, bits, clean_and_collision, legal, prob_table

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = next(
    (ROOT / "artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A").glob(
        "*/histories.json.gz"
    )
)


def loose(rows):
    owners = Counter(x for row in rows for x in row)
    return tuple(x for x in sorted(owners) if owners[x] == 1)


def first(rows):
    full = tuple(sorted(set(x for row in rows for x in row)))
    e = loose(rows)
    spent = tuple(x for x in full if x not in e)

    def evaluate(law):
        a = np.zeros((1 << len(spent), 1 << len(e)), dtype=object)
        for i, s in enumerate(bits(len(spent))):
            for j, y in enumerate(bits(len(e))):
                w = dict(zip((*spent, *e), (*s, *y)))
                a[i, j] = int(all(legal([w[x] for x in row], law) for row in rows))
        return a

    return evaluate


def transition(old, axis, factors, final):
    """Contract one real birth at a time, consuming the paid old names exactly once."""
    a = old.reshape((2,) * len(axis))
    axis = list(axis)
    for ins, outs, table in sorted(
        factors, key=lambda row: (len(row[1]) - len(row[0]), row[0])
    ):
        ax = [axis.index(b) for b in ins]
        a = np.tensordot(
            a,
            table.reshape((2,) * (len(ins) + len(outs))),
            axes=(ax, list(range(len(ins)))),
        )
        axis = [j for j in axis if j not in ins] + list(outs)
    assert set(axis) == set(final)
    return a.transpose([axis.index(q) for q in final])


def factors(rows, old_live, law, marks=None):
    children = []
    for row in rows:
        ins = tuple(x for x in row if x in old_live)
        births = tuple(x for x in row if x not in old_live)
        all_new = bits(len(births))
        leg = as_array(
            [[int(legal((*i, *y), law)) for y in all_new] for i in bits(len(ins))]
        )
        if marks is None:
            children.append((ins, births, leg))
            continue
        keep = tuple(b for b in marks if b in births)
        indexed = [births.index(b) for b in keep]
        ignore = [i for i, b in enumerate(births) if b not in keep]
        ordered = leg.reshape((leg.shape[0],) + (2,) * len(births)).transpose(
            [0] + [1 + k for k in indexed + ignore]
        )
        blocks = ordered.reshape((leg.shape[0], 1 << len(keep), 1 << len(ignore)))
        effects = as_array([mat @ mat.T for mat in blocks])
        outs = tuple((k, b) for k in (0, 1) for b in keep)
        children.append((ins, outs, effects))
    return children


def marked(a, live, marks):
    left = [live.index(m) for m in marks]
    right = [i for i, b in enumerate(live) if b not in marks]
    slabs = a.reshape((a.shape[0],) + (2,) * len(live)).transpose(
        [0] + [1 + i for i in right + left]
    )
    v = slabs.reshape(-1, 8)
    return v.T @ v


def run():
    with gzip.open(ARCHIVE, "rt") as f:
        cases = json.load(f)["cases"]
    report = {}
    for case in cases:
        if case["mode"] != "built":
            continue
        identifier, law = case["id"], case["law"]
        stages = case["stages"]
        start = first(stages[0])(law)
        counts = start.sum(axis=0)
        history = []
        previous = ()
        for t, rows in enumerate(stages):
            e = loose(rows)
            if t:
                new = rows[len(stages[t - 1]) :]
                prior = counts
                counts = transition(
                    prior, previous, factors(new, previous, law), e
                ).reshape(-1)
            n = list(map(int, counts))
            assert len(n) == 1 << len(e)
            holder = {
                i: tuple(x for x in sorted(row) if x in e) for i, row in enumerate(rows)
            }
            selected = [
                (f"one holder {i}", w[:3]) for i, w in holder.items() if len(w) >= 3
            ]
            occupied = [w for w in holder.values() if w]
            if len(occupied) >= 3:
                selected.append(("three holders", tuple(w[0] for w in occupied[:3])))
            info = {}
            for role, marks in selected:
                q = marked(counts.reshape(1, -1), e, marks)
                if not t:
                    d = marked(start, e, marks)
                else:
                    out = tuple((k, b) for k in (0, 1) for b in marks)
                    d = transition(
                        prior, previous, factors(new, previous, law, marks), out
                    ).reshape(8, 8)
                assert np.trace(d) == sum(n) and np.trace(q) == sum(x * x for x in n)
                # Full integer Grams encode the 64 setting probabilities without cancellation.
                info[role] = {
                    "marks": marks,
                    "D_gram": d.tolist(),
                    "Q_gram": q.tolist(),
                    "signed_scores": [
                        prob_table(d)["signed_M_bound_two"],
                        prob_table(q)["signed_M_bound_two"],
                    ],
                }
            hist = Counter(n)
            history.append(
                {
                    "age": t,
                    "loose": e,
                    "complete_lex_count_table": n,
                    "count_histogram_number_of_words_at_each_size": {
                        str(j): k for j, k in sorted(hist.items())
                    },
                    "weights": clean_and_collision(
                        n, len(set(b for row in rows for b in row)) - len(e)
                    ),
                    "local_score_and_full_integer_grams": info,
                }
            )
            previous = e
        report[f"{identifier}/{law}"] = history
    return report
