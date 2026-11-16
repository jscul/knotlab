"""Blind ordering of eligible Boolean input triples from two packed output tables.

For a group summarized by one bit h, write each consumer at a fixed outside
assignment as b XOR (a AND h). On edges in group direction i, the unordered
output transition counts equal the number of i-edges toggling h times one
common vector of outside transitions. The normalized vectors therefore agree
for all three group inputs. Agreement alone does not establish a valid group.

A policy pays for per-axis summaries and promotes at most one triple. The
complete supplied order remains available to the independent exact search.
Only the supervised fit sees examples of minimizing groups.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb, gcd
from typing import NamedTuple


VERSION = "axis-transitions-v1"
CHANNELS = ("marginals", "joint", "transitions")
GATES = (4, 10, 20, 35, 56, 84)
PROBE_UNITS = 24
COUNTERS = ("orders", "lexical_returns", "feature_calls", "axis_profiles", "axis_masks_built",
            "layouts_built", "layout_cache_hits", "packed_shifts", "packed_xors", "packed_ands",
            "packed_popcounts", "axis_normalizations", "bucket_visits", "shape_scale_probes",
            "candidate_tuple_visits", "promotions", "estimated_feature_units")
SOURCE_DEPENDENCIES = ()


def _model(channel, gate, shapes=()):
    return {"version": VERSION, "channel": channel, "min_eligible": gate,
            "shape_priority": [list(shape) for shape in shapes]}


def zero_model():
    return _model("lexical", 0)


def fixed_model():
    return _model("joint", GATES[0])


def default_model():
    return fixed_model()


def model_hash(model):
    data = json.dumps(model, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return sha256(data).hexdigest()


class _Layout(NamedTuple):
    axes: tuple
    complete: bool


class _Features(NamedTuple):
    buckets: tuple
    units: int


def _shape(values):
    # Each direction in a three-input cube has four edges. A sufficient
    # ternary bit gives these three nonzero masses a common outside factor.
    a, b, c = sorted(values)
    scale = gcd(gcd(a, b), c)
    if scale and c <= 4 * scale:
        return a // scale, b // scale, c // scale
    return None


def _promoted(groups, first):
    yield first
    for group in groups:
        if group != first:
            yield group


class Ranker:
    """Each instance owns its arity-only geometry cache and cumulative work."""

    def __init__(self, n, model=None):
        if type(n) is not int or n < 3:
            raise ValueError("triple ordering requires n >= 3")
        model = fixed_model() if model is None else model
        if model["version"] != VERSION or model["channel"] not in ("lexical", *CHANNELS):
            raise ValueError("unsupported ordering model")
        self.n, self.channel = n, model["channel"]
        self.gate = model["min_eligible"]
        self.shapes = tuple(tuple(s) for s in model["shape_priority"])
        if type(self.gate) is not int or self.gate < 0 or len(self.shapes) > 2:
            raise ValueError("invalid ordering model bounds")
        if any(len(s) != 3 or any(type(x) is not int or not 1 <= x <= 4 for x in s) or
               s != tuple(sorted(s)) or gcd(*s) != 1 for s in self.shapes):
            raise ValueError("invalid local influence shape")
        self._masks, self._layouts = {}, {}
        self._full = None
        self._work = dict.fromkeys(COUNTERS, 0)

    def work_counters(self):
        return self._work.copy()

    def ledger(self):
        return {"counters": self.work_counters(), "layouts": len(self._layouts),
                "axis_masks": len(self._masks)}

    def _mask(self, axis):
        mask = self._masks.get(axis)
        if mask is None:
            if self._full is None:
                self._full = (1 << (1 << self.n)) - 1
            mask = self._masks[axis] = self._full // ((1 << (1 << axis)) + 1)
            self._work["axis_masks_built"] += 1
        return mask

    def _layout(self, eligible):
        layout = self._layouts.get(eligible)
        if layout is None:
            axes = tuple(sorted(set().union(*eligible)))
            layout = self._layouts[eligible] = _Layout(axes, comb(len(axes), 3) == len(eligible))
            self._work["layouts_built"] += 1
        else:
            self._work["layout_cache_hits"] += 1
        return layout

    def _features(self, outputs, axes):
        a, b = outputs
        mode = self.channel
        buckets = {}
        parity = (a ^ b) if mode == "transitions" else 0
        for axis in axes:
            stride, mask = 1 << axis, self._mask(axis)
            da = (a ^ (a >> stride)) & mask
            db = (b ^ (b >> stride)) & mask
            if mode == "marginals":
                ca, cb = da.bit_count(), db.bit_count()
                profile = (ca, cb)
                magnitude = max(ca, cb)
            elif mode == "joint":
                ca, cb, both = da.bit_count(), db.bit_count(), (da & db).bit_count()
                profile = (ca, cb, both)
                magnitude = ca + cb - both
            else:
                both = da & db
                a_only, b_only = da ^ both, db ^ both
                ca, cb, cc = a_only.bit_count(), b_only.bit_count(), both.bit_count()
                a_b1 = (a_only & b).bit_count()
                b_a1 = (b_only & a).bit_count()
                opposite = (both & parity).bit_count()
                # For a single toggle, the other output is fixed. For a
                # double toggle the endpoints are either 00/11 or 01/10.
                profile = (ca - a_b1, a_b1, cb - b_a1, b_a1, cc - opposite, opposite)
                magnitude = ca + cb + cc
            scale = gcd(*profile)
            signature = tuple(v // scale for v in profile) if scale else profile
            buckets.setdefault(signature, []).append((axis, magnitude))
        count = len(axes)
        work = self._work
        shifts = 2 * count
        xors = (4 * count + 1) if mode == "transitions" else 2 * count
        ands = {"marginals": 2, "joint": 3, "transitions": 6}[mode] * count
        pops = {"marginals": 2, "joint": 3, "transitions": 6}[mode] * count
        work["feature_calls"] += 1
        work["axis_profiles"] += count
        work["packed_shifts"] += shifts
        work["packed_xors"] += xors
        work["packed_ands"] += ands
        work["packed_popcounts"] += pops
        work["axis_normalizations"] += count
        # One unit per packed operation, normalized vector, and axis insertion.
        units = shifts + xors + ands + pops + 2 * count
        return _Features(tuple(b for b in buckets.values() if len(b) >= 3), units)

    @staticmethod
    def _choose(features, layout, eligible, shapes):
        """Return one proposal and measured integer bookkeeping counts."""
        buckets = features.buckets
        best = None
        visits = probes = tuples = 0
        if not layout.complete:
            # A caller may supply an arbitrary sorted subset. Score precisely
            # those triples so that every returned proposal is admissible.
            index = {axis: (i, mass) for i, bucket in enumerate(buckets) for axis, mass in bucket}
            for group in eligible:
                tuples += 1
                data = [index.get(a) for a in group]
                if any(x is None for x in data) or not data[0][0] == data[1][0] == data[2][0]:
                    continue
                category = _shape([x[1] for x in data]) if shapes else None
                priority = shapes.index(category) if category in shapes else len(shapes)
                key = (priority, len(buckets[data[0][0]]), group)
                if best is None or key < best:
                    best = key
        else:
            for bucket in buckets:
                visits += 1
                # Prefer isolated compatible groups. Within each category,
                # choose the first admissible labeled triple as a stable tie.
                group = tuple(row[0] for row in bucket[:3])
                key = (len(shapes), len(bucket), group)
                if best is None or key < best:
                    best = key
                if not shapes:
                    continue
                if len(bucket) == 3:
                    tuples += 1
                    category = _shape(row[1] for row in bucket)
                    if category in shapes:
                        key = (shapes.index(category), 3, group)
                        if key < best:
                            best = key
                    continue
                # Find the first triple with an empirical relative influence
                # shape using mass bins. No traversal of all triples is needed.
                by_mass = {}
                for axis, mass in bucket:
                    by_mass.setdefault(mass, []).append(axis)
                for priority, shape in enumerate(shapes):
                    if priority > best[0]:
                        break
                    low, middle, high = shape
                    for mass, low_axes in by_mass.items():
                        probes += 1
                        scale, remainder = divmod(mass, low)
                        if remainder or not scale:
                            continue
                        mid_axes = by_mass.get(middle * scale)
                        high_axes = by_mass.get(high * scale)
                        if mid_axes is None or high_axes is None:
                            continue
                        second = int(low == middle)
                        third = int(low == high) + int(middle == high)
                        if len(mid_axes) <= second or len(high_axes) <= third:
                            continue
                        group = tuple(sorted((low_axes[0], mid_axes[second], high_axes[third])))
                        tuples += 1
                        key = (priority, len(bucket), group)
                        if key < best:
                            best = key
        return (None if best is None else best[2]), visits, probes, tuples

    def order(self, outputs, eligible):
        """Stream each caller-supplied triple exactly once; ties retain lexical order."""
        if not isinstance(eligible, tuple) or (eligible and not isinstance(eligible[0], tuple)):
            eligible = tuple(tuple(g) for g in eligible)
        work = self._work
        work["orders"] += 1
        if self.channel == "lexical" or len(eligible) < max(2, self.gate):
            work["lexical_returns"] += 1
            return iter(eligible)
        layout = self._layout(eligible)
        features = self._features(outputs, layout.axes)
        chosen, visits, probes, tuples = self._choose(features, layout, eligible, self.shapes)
        work["bucket_visits"] += visits
        work["shape_scale_probes"] += probes
        work["candidate_tuple_visits"] += tuples
        work["estimated_feature_units"] += features.units + visits + probes + tuples
        if chosen is None or chosen == eligible[0]:
            work["lexical_returns"] += 1
            return iter(eligible)
        work["promotions"] += 1
        return _promoted(eligible, chosen)

    def full_ranking(self, outputs, eligible):
        return list(self.order(outputs, eligible))


def _training_rows(train_public, grade_by_id):
    rows, masks_by_n, consumed = [], {}, set()
    for public in train_public:
        identifier, n, outputs = public["id"], public["n"], tuple(public["outputs"])
        if identifier in consumed:
            raise ValueError("duplicated public training ID")
        consumed.add(identifier)
        grade = grade_by_id[identifier]
        width = grade.get("width", grade.get("min_width"))
        positives = grade["minimizers"] if "minimizers" in grade else grade["min_triples"]
        positives = frozenset(tuple(sorted(g)) for g in positives)
        if type(n) is not int or n < 3 or len(outputs) != 2:
            raise ValueError("training needs two n-input packed tables")
        if n not in masks_by_n:
            full = (1 << (1 << n)) - 1
            masks_by_n[n] = (full, tuple(full // ((1 << (1 << i)) + 1) for i in range(n)))
        full, masks = masks_by_n[n]
        if any(type(t) is not int or not 0 <= t <= full for t in outputs):
            raise ValueError("incomplete public training table")
        axes = tuple(i for i, mask in enumerate(masks)
                     if all((t ^ (t >> (1 << i))) & mask for t in outputs))
        eligible = tuple(combinations(axes, 3))
        indexed = {g: i for i, g in enumerate(eligible)}
        if (eligible and (type(width) is not int or width not in (1, 2, 3) or not positives)
                or not eligible and width is not None or not positives <= indexed.keys()):
            raise ValueError("invalid minimum-width labels for the public training tables")
        first = min((indexed[g] for g in positives), default=0)
        rows.append((n, outputs, eligible, indexed, positives, first, width == 1))
    return rows


def _learn_shapes(records):
    """Task-balanced enrichment of labeled minimizing triples over all candidates."""
    positive, exposure, cases = Counter(), Counter(), Counter()
    for row, _, features in records:
        _, _, eligible, _, good, _, _ = row
        if not eligible:
            continue
        mass = {}
        bucket_id = {}
        for i, bucket in enumerate(features.buckets):
            for axis, weight in bucket:
                mass[axis], bucket_id[axis] = weight, i
        positive_in_task, eligible_in_task = Counter(), Counter()
        for group in eligible:
            a, b, c = group
            if a not in mass or b not in mass or c not in mass or not bucket_id[a] == bucket_id[b] == bucket_id[c]:
                continue
            shape = _shape((mass[a], mass[b], mass[c]))
            if shape is None:
                continue
            eligible_in_task[shape] += 1
            if group in good:
                positive_in_task[shape] += 1
        for shape, count in eligible_in_task.items():
            exposure[shape] += Fraction(count, len(eligible))
        for shape, count in positive_in_task.items():
            positive[shape] += Fraction(count, len(good))
            cases[shape] += 1
    # One quarter task of symmetric smoothing. Two distinct training cases
    # must support any learned shape. Counts and sorting are exact rationals.
    prior = Fraction(1, 4)
    enriched = [s for s in positive if cases[s] >= 2 and positive[s] > exposure[s]]
    enriched.sort(key=lambda s: (-(positive[s] + prior) / (exposure[s] + prior), -positive[s], s))
    report = [{"shape": list(s), "positive_task_mass": float(positive[s]),
               "candidate_task_mass": float(exposure[s]), "supporting_tasks": cases[s]}
              for s in sorted(exposure)]
    return tuple(enriched[:2]), report


def _score(records, proposals, gate):
    units = saved = all_saved = paid = promoted = 0
    for (row, _, _), (candidate, cost) in zip(records, proposals):
        _, _, eligible, indexed, good, original, early = row
        if len(eligible) < gate:
            continue
        paid += 1
        units += cost
        if candidate is None:
            continue
        position = indexed[candidate]
        promoted += int(position != 0)
        if candidate in good:
            gain = original
        else:
            gain = -int(position > original)
        all_saved += gain
        if early:
            saved += gain
    return {"objective_units": PROBE_UNITS * saved - units, "early_group_attempts_saved": saved,
            "first_minimizer_positions_saved_all": all_saved, "feature_units": units,
            "tasks_scored": paid, "training_promotions": promoted}


def fit(train_public, grade_by_id):
    """Return (JSON-serializable model, diagnostics); no inference reads grades or IDs.

    Rows have id, n and outputs=(packed0,packed1). Grades have width and
    minimizers, listing every minimizing triple. min_triples is also accepted.
    The integer objective is frozen explicitly in the module and fit receipt.
    """
    rows = _training_rows(train_public, grade_by_id)
    empty = {"objective_units": 0, "early_group_attempts_saved": 0, "first_minimizer_positions_saved_all": 0,
             "feature_units": 0, "tasks_scored": 0, "training_promotions": 0}
    best_model, best_score = zero_model(), empty
    best_key = (0, 0, 0, 0, 0)
    candidates = [{"model": best_model, **empty}]
    enrichment = {}
    for mode_index, channel in enumerate(CHANNELS, 1):
        engines, records = {}, []
        for row in rows:
            n, outputs, eligible, *_ = row
            if n not in engines:
                engines[n] = Ranker(n, _model(channel, GATES[0]))
            eng = engines[n]
            if eligible:
                layout = eng._layout(eligible)
                features = eng._features(outputs, layout.axes)
            else:
                layout, features = _Layout((), True), _Features((), 0)
            records.append((row, layout, features))
        priority, enrichment[channel] = _learn_shapes(records)
        for length in range(len(priority) + 1):
            shapes = priority[:length]
            predictions = []
            for row, layout, features in records:
                _, _, eligible, *_ = row
                first, visits, probes, tuples = Ranker._choose(features, layout, eligible, shapes)
                predictions.append((first, features.units + visits + probes + tuples))
            for gate in GATES:
                model = _model(channel, gate, shapes)
                score = _score(records, predictions, gate)
                candidates.append({"model": model, **score})
                # Lexical wins a zero-score tie. Otherwise prefer less actual
                # feature work, fewer learned categories, cheaper channels
                # and the higher activation threshold wherever scores tie.
                key = (score["objective_units"], -score["feature_units"], -length, -mode_index, gate)
                if key > best_key:
                    best_model, best_score, best_key = model, score, key
    fixed = fixed_model()
    fixed_score = next(r for r in candidates if r["model"] == fixed)
    diagnostics = {
        "model_sha256": model_hash(best_model), "training_tasks": len(rows),
        "early_stop_tasks": sum(r[-1] for r in rows),
        "minimum_triple_labels": sum(len(r[4]) for r in rows),
        "probe_value_units": PROBE_UNITS,
        "objective": "24 times saved width-one group attempts minus estimated feature work on all tasks",
        "feature_work": ("One unit per packed operation, normalized axis vector, axis insertion, "
                         "compatible bucket visit, shape-scale probe and candidate tuple visit. "
                         "The deployment timer also charges geometry, iteration and all Python overhead."),
        "fit_score": best_score, "fixed_score": {k: v for k, v in fixed_score.items() if k != "model"},
        "fixed_model": fixed, "zero_model": zero_model(),
        "delta_from_fixed": {k: {"from": fixed[k], "to": best_model[k]}
                             for k in fixed if fixed[k] != best_model[k]},
        "delta_from_lexical": {k: {"from": v, "to": best_model[k]}
                               for k, v in zero_model().items() if v != best_model[k]},
        "candidate_count": len(candidates), "candidates": candidates, "shape_fit": enrichment,
    }
    return best_model, diagnostics
