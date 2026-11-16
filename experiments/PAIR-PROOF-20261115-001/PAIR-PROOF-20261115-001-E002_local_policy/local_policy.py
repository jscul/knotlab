"""Fit cheap pair/corner requests on separate public parent circuits.

propose and fixed_actions only read the unedited physical description and the
current pin change. Neither evaluates a gate. The train-only section computes
outcomes, then leaves whole parent circuits out when choosing radius and menu.
A request has the frozen pair solver's [i,j,base,corner_mask] convention.
"""

from __future__ import annotations

from collections import Counter, namedtuple
from functools import cache
from itertools import combinations


FIELDS = frozenset(("n", "upstream_count", "gates", "frontier", "outputs", "pieces"))
EDIT_FIELDS = frozenset(("gate", "pin", "to"))
ANCHORS = ("zero", "ones", "even", "odd", "low_two_of_four", "high_two_of_four",
           "near", "outside_near", "replacement", "outside_replacement",
           "replacement_and_even_far", "complement_replacement_and_even_far")
CORNERS = (7, 11, 13, 14, 15)
SWAP = (0, 2, 1, 3, 4)
CATEGORIES = 10  # unordered pairs of the four public endpoint roles
SCHEMA = "local-pair-corners-v1"
PLANS = ("half", "within", "priced", "retry", "rank")
SOURCE_DEPENDENCIES = (
    "experiments/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/pair_solver.py",
)
SOURCE_SHA256 = {SOURCE_DEPENDENCIES[0]: "6f0a94e902cdc62316c944880ee4351b325cfea89f5d347fd082da1585510114"}


@cache
def _geometry(m):
    """Inference may cache integer arity geometry only."""
    axes = tuple(range(m))
    pairs = tuple((i, j, (1 << i) | (1 << j)) for i, j in combinations(axes, 2))
    full = (1 << m) - 1
    even = sum(1 << i for i in axes[::2])
    low = sum(1 << i for i in axes if not i & 2)
    return pairs, full, even, low


def _check_public(original, edit):
    if original.keys() != FIELDS or edit.keys() != EDIT_FIELDS:
        raise ValueError("expected the six original public fields and one stripped pin edit")


View = namedtuple("View", "pairs anchors visits balanced m history_reads")


def _view(original, edit, radius):
    """Distance zero is the three directly visible pin sources.

    Each further step follows one NAND fan-in. Arriving at a published bit
    or port exposes the three associated stage axes. All pieces have the same
    treatment. An encountered frontier wire is a terminal even if that wire
    was synthesized upstream. No output values, fan-out scan or wire-ID
    parameters are involved.
    """
    frontier = original["frontier"]
    m = len(frontier)
    physical = original["gates"]
    first_gate = original["n"] + 2
    first_stage = first_gate + original["upstream_count"]
    edit_gate, pin = edit["gate"], edit["pin"]
    if pin not in (0, 1) or not first_stage <= edit_gate < first_gate + len(physical):
        raise ValueError("invalid edited pin address")
    a, b = physical[edit_gate - first_gate]
    sources = ((a, b)[pin], (b, a)[pin], edit["to"])
    stage = {wire: 1 << i for i, wire in enumerate(frontier)}
    associations = {}
    for piece in original["pieces"]:
        group_mask = sum(1 << axis for axis in piece["inputs"])
        for wire in (piece["bit"], *piece["ports"]):
            associations[wire] = associations.get(wire, 0) | group_mask

    def visible(seed):
        layer, seen, axes = {seed}, set(), 0
        for step in range(radius + 1):
            following = set()
            for wire in layer:
                axes |= associations.get(wire, 0) | stage.get(wire, 0)
                if step < radius and wire >= first_stage and wire not in stage:
                    following.update(physical[wire - first_gate])
            seen.update(layer)
            layer = following - seen
            if not layer:
                break
        return axes, len(seen)

    observed = [visible(s) for s in sources]
    old, mate, new = (entry[0] for entry in observed)
    visits = sum(entry[1] for entry in observed)
    raw_pairs, full, even, low = _geometry(m)
    near = old | mate | new
    mixed = new | (even & ~near)
    anchors = (0, full, even, full ^ even, low, full ^ low,
               near, full ^ near, new, full ^ new, mixed, full ^ mixed)
    # The labels are types, never fitted identities. Higher type goes first
    # when interpreting an asymmetric three-corner request.
    roles = [3 if (1 << i) & new else 2 if (1 << i) & old
             else 1 if (1 << i) & mate else 0 for i in range(m)]
    local_order = sorted(range(m), key=roles.__getitem__, reverse=True)
    local_half = sum(1 << i for i in local_order[::2])
    pairs = []
    for i, j, bits in raw_pairs:
        ri, rj = roles[i], roles[j]
        high, low_role = (rj, ri) if ri < rj else (ri, rj)
        category = high * (high + 1) // 2 + low_role
        local_within = (local_half & bits) in (0, bits)
        pairs.append((i, j, bits, category, ri < rj, not ((i ^ j) & 1), local_within))
    size = (m // 2) * ((m - 1) // 2)
    return View(pairs, anchors, visits, size, m, m + 6 * len(original["pieces"]))


def _ordered(view, recipes, split, plan):
    """Each row retains a geometry index for the train-only audit replay."""
    inside, outside = [], []
    for p, row in enumerate(view.pairs):
        recipe = recipes[row[3]]
        item = (-recipe[2], p)
        (inside if row[5 + split] else outside).append(item)
    if plan == "rank":
        selected = sorted(inside + outside)[:view.balanced]
    else:
        inside.sort()
        if plan == "half":
            selected = inside[:(len(inside) + 1) // 2]
        elif plan == "priced":
            # Give a direction at most m-2 groups. Eight work units per group
            # and twelve per test are the same scale as the training proxy.
            # Restrict speculative cross-half requests to half a balanced set.
            options = inside + sorted(outside)[:(len(inside) + 1) // 2]
            selected = [(s, p) for s, p in options if -s * 8 * (view.m - 2) > 12 * 256]
        else:
            selected = inside
    result = []
    for _, p in selected:
        result.append((p, 0))
    if plan == "retry":
        for _, p in sorted((-recipes[view.pairs[p][3]][5], p) for _, p in selected):
            result.append((p, 3))
    return result


def _action(view, recipes, p, offset):
    i, j, bits, category, swapped, _, _ = view.pairs[p]
    anchor, mask_index = recipes[category][offset:offset + 2]
    actual = SWAP[mask_index] if swapped else mask_index
    return [i, j, view.anchors[anchor] & ~bits, CORNERS[actual]]


def propose(model, original, edit):
    """Return ordered, ungraded tests to be executed by the ordinary solver."""
    _check_public(original, edit)
    if model["schema"] != SCHEMA:
        raise ValueError("unknown local policy schema")
    if model["plan"] == "none":
        return []
    view = _view(original, edit, model["radius"])
    recipes = model["recipes"]
    return [_action(view, recipes, p, offset) for p, offset in
            _ordered(view, recipes, model["split"], model["plan"])]


def fixed_actions(original, edit):
    """Untrained same-menu rule, two complementary settings on balanced pairs.

    Raise replacement-associated inputs, lower the other visible ones and
    alternate unassociated inputs. Then reverse every outside bit. Four
    corners give either possible orientation an opportunity to certify.
    """
    _check_public(original, edit)
    view = _view(original, edit, 1)
    actions = []
    for anchor in (10, 11):
        for i, j, bits, _, _, _, local_within in view.pairs:
            if local_within:
                actions.append([i, j, view.anchors[anchor] & ~bits, 15])
    return actions


# All subsequent code is training-only. No imports, fixtures or tables from
# the training engine are needed when the two inference functions run.
@cache
def _train_engine():
    import hashlib
    import importlib.util
    from pathlib import Path
    import sys
    path = Path(__file__).resolve().parents[3] / SOURCE_DEPENDENCIES[0]
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256[SOURCE_DEPENDENCIES[0]]:
        raise RuntimeError("training label engine changed")
    name = "pair_solver"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    if Path(module.__file__).resolve() != path.resolve():
        raise ImportError("training engine name resolves to another file")
    return module


def _certificate(code, requested):
    seen = cert = 0
    for corner in range(4):
        bit = 1 << corner
        value = 1 << ((code >> (2 * corner)) & 3)
        if requested & bit and not seen & value:
            seen |= value
            cert |= bit
            if cert.bit_count() == 3:
                return cert
    return 0


@cache
def _lookup():
    certificates = tuple(tuple(_certificate(code, mask) for mask in CORNERS)
                         for code in range(256))
    slots = tuple(tuple(i for i, cert in enumerate(row) if cert) for row in certificates)
    swapped = tuple(tuple(SWAP[i] for i in row) for row in slots)
    return certificates, (slots, swapped)


def _corners(i, j, base):
    x, y = 1 << i, 1 << j
    return (base, base | x, base | y, base | x | y)


class _Observed:
    def __init__(self, tables):
        self.tables = tables
        self.rows = {}
        self.settings = {}

    def code(self, i, j, base):
        key = (i, j, base)
        code = self.settings.get(key)
        if code is None:
            code = 0
            for k, row in enumerate(_corners(i, j, base)):
                value = self.rows.get(row)
                if value is None:
                    value = ((self.tables[0] >> row) & 1) | (((self.tables[1] >> row) & 1) << 1)
                    self.rows[row] = value
                code |= value << (2 * k)
            self.settings[key] = code
        return code


Trial = namedtuple("Trial", "width active pending stars prices observed")


def _training_trial(engine, state):
    selected, work = engine.select_only(state, "no-proof")
    width = selected["width"]
    if not work.get("compact_exact_alternatives") and width != 2:
        return Trial(width, False, 0, (), (), None)
    axes = engine._engine._shared(state, Counter())
    geometries = engine._compact._layouts(state.m, axes)
    stars, indices, _, _ = engine._stars(state.m, axes)
    pending = ((1 << len(geometries)) - 1) ^ (1 << indices[selected["triple"]])
    # On generic wider-to-two transitions fewer distinct solver cutoffs can
    # run than there are verifier alternatives. In this case credit only
    # verifier work; the proxy is conservative about ambiguous solver work.
    solver_all = work.get("compact_exact_alternatives", 0) == len(geometries) - 1
    copies = int(width == 2) + int(solver_all)
    joint = state.tables[0] | (state.tables[1] << (1 << state.m))
    bins = Counter()
    for k, (_, mask, remaining) in enumerate(geometries):
        if not pending & (1 << k):
            continue
        first, second, read = joint & mask, -1, 1
        for shift in remaining:
            value = (joint >> shift) & mask
            read += 1
            if value != first and value != second:
                if second >= 0:
                    break
                second = value
        if copies and width == 2:
            # One visit and the actual packed column alignments per pass.
            bins[copies * (2 + read)] |= 1 << k
    return Trial(width, True, pending, stars, tuple(bins.items()), _Observed(state.tables))


def _empty_stats():
    return [[0] * (1 + len(ANCHORS) * len(CORNERS)) for _ in range(CATEGORIES)]


def _label(view, trial, stats):
    if trial.observed is None:
        return ()
    codes = []
    success = _lookup()[1]
    for i, j, bits, category, swapped, _, _ in view.pairs:
        observations = tuple(trial.observed.code(i, j, anchor & ~bits) for anchor in view.anchors)
        codes.append(observations)
        if trial.width != 2:
            continue
        row = stats[category]
        row[0] += 1
        for a, code in enumerate(observations):
            offset = 1 + a * len(CORNERS)
            for mask_index in success[swapped][code]:
                row[offset + mask_index] += 1
    return codes


def _pooled(families):
    total = _empty_stats()
    for stats in families:
        for pooled, individual in zip(total, stats):
            for k, value in enumerate(individual):
                pooled[k] += value
    return total


def _recipes(total, excluded=None):
    """Categorical success with eight pooled pseudo-observations.

    Scores are fixed-point probabilities in 256ths. A fourth corner needs
    eight more score units (one extra read for about 32 useful requests).
    Ties favor earlier context and fewer corners. Each backup complements
    its first setting and independently chooses its corner mask.
    """
    if excluded is None:
        stats = total
    else:
        stats = [[v - h for v, h in zip(all_row, held)]
                 for all_row, held in zip(total, excluded)]
    pooled = tuple(map(sum, zip(*stats)))
    prior = [value * 256 // max(1, pooled[0]) for value in pooled[1:]]
    recipes = []
    for row in stats:
        denominator = row[0] + 8
        qualities = [(256 * hits + 8 * prior[k]) // denominator - 8 * (k % 5 == 4)
                     for k, hits in enumerate(row[1:])]
        first = max(range(len(qualities)), key=qualities.__getitem__)
        a, slot = divmod(first, len(CORNERS))
        backup_start = (a ^ 1) * len(CORNERS)
        backup = max(range(backup_start, backup_start + len(CORNERS)), key=qualities.__getitem__)
        recipes.append([a, slot, qualities[first], a ^ 1, backup % len(CORNERS), qualities[backup]])
    return recipes


def _replay(view, trial, codes, recipes, menu):
    """Deterministic price of a held-out parent's ordered, physically tested menu.

    The two row caches are independent. Only the first three distinct
    outcomes are submitted to the checker; a fourth row is paid by search.
    The geometric work of making advice is paid even on one-bit early exits.
    """
    score = -(1 + view.visits + (view.history_reads + len(view.pairs) + 3) // 4
              + (len(menu) + 1) // 2)
    if not trial.active:
        return score
    pending, seen, verified = trial.pending, set(), set()
    certificate = _lookup()[0]
    for p, offset in menu:
        if not pending:
            break
        star = trial.stars[p]
        if not star & pending:
            continue
        i, j, bits, category, swapped, _, _ = view.pairs[p]
        anchor, slot = recipes[category][offset:offset + 2]
        slot = SWAP[slot] if swapped else slot
        mask, code = CORNERS[slot], codes[p][anchor]
        rows = _corners(i, j, view.anchors[anchor] & ~bits)
        score -= 6 + mask.bit_count()
        for k, row in enumerate(rows):
            if mask & (1 << k) and row not in seen:
                seen.add(row)
                score -= 2
        proof = certificate[code][slot]
        if not proof:
            continue
        pending &= ~star
        if trial.width == 2:
            score -= 5 + proof.bit_count()
            for k, row in enumerate(rows):
                if proof & (1 << k) and row not in verified:
                    verified.add(row)
                    score -= 2
    gained = trial.pending & ~pending
    return score + sum(price * (gained & bits).bit_count() for price, bits in trial.prices)


def _record_key(case):
    # Repeated copies of an original with different edit lists stay in the
    # same holdout block. A key is never used by the learned predictor.
    return (case["n"], case["upstream_count"], tuple(map(tuple, case["gates"])),
            tuple(case["frontier"]), tuple(case["outputs"]))


def fit(cases, radii=(0, 1, 2, 4)):
    """Return a JSON-serializable model and a leave-one-parent-out fit receipt."""
    import hashlib
    import json
    radii = tuple(sorted(set(radii)))
    if not radii or any(type(r) is not int or not 0 <= r <= 8 for r in radii):
        raise ValueError("offer one or more integer radii between 0 and 8")
    parents = {}
    for case in cases:
        if case.keys() != FIELDS | {"edits"}:
            raise ValueError("fit takes stripped originals with a stripped edits list")
        original = {k: case[k] for k in FIELDS}
        for edit in case["edits"]:
            _check_public(original, edit)
        parents.setdefault(_record_key(original), []).append((original, case["edits"]))
    engine = _train_engine() if parents else None
    training = []
    counts = Counter()
    for shared_original in parents.values():
        family = []
        for original, edits in shared_original:
            parent = engine._engine.Parent(original)
            for edit in edits:
                trial = _training_trial(engine, parent.edit(edit))
                family.append((original, edit, trial))
                counts[str(trial.width)] += 1
        training.append(family)
    model = dict(schema=SCHEMA, radius=0, split=0, plan="none", recipes=[])
    by_config, updates = [], []
    best = (0, 0)
    for radius in radii:
        blocks = []
        for family in training:
            stats, trials = _empty_stats(), []
            for original, edit, trial in family:
                view = _view(original, edit, radius)
                trials.append((view, trial, _label(view, trial, stats)))
            blocks.append((stats, trials))
        totals = _pooled(stats for stats, _ in blocks)
        final_recipes = _recipes(totals)
        supported = [k for k, row in enumerate(totals) if row[0]]
        updates.append(dict(radius=radius, supervised_pair_examples=sum(row[0] for row in totals),
                            supported_categories=len(supported),
                            changed_from_fixed_primary=sum(final_recipes[k][:2] != [10, 4]
                                                           for k in supported),
                            fitted_recipes=final_recipes))
        scores = Counter()
        for excluded, trials in blocks:
            recipes = _recipes(totals, excluded)
            for view, trial, codes in trials:
                for split in (0, 1):
                    for plan in PLANS:
                        if plan == "rank" and split:
                            continue
                        menu = _ordered(view, recipes, split, plan)
                        value = _replay(view, trial, codes, recipes, menu)
                        scores[split, plan, "mixed"] += value
                        if trial.width == 2:
                            scores[split, plan, "primary"] += value
        for split in (0, 1):
            for plan in PLANS:
                if plan == "rank" and split:
                    continue
                primary = scores[split, plan, "primary"]
                mixed = scores[split, plan, "mixed"]
                by_config.append(dict(radius=radius, split=split, plan=plan,
                                      two_bit_units=primary, mixed_units=mixed))
                # Positive primary benefit is required. Mixed savings resolve
                # positive ties; iteration then favors smaller radius/menus.
                if len(blocks) >= 2 and primary > 0 and (primary, mixed) > best:
                    best = primary, mixed
                    model = dict(schema=SCHEMA, radius=radius, split=split, plan=plan,
                                 recipes=final_recipes)
    unique_settings = sum(len(t.observed.settings) for family in training
                          for _, _, t in family if t.observed)
    unique_rows = sum(len(t.observed.rows) for family in training
                      for _, _, t in family if t.observed)
    raw = json.dumps(model, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    meta = dict(schema=SCHEMA, trained_parents=len(training), trained_edits=sum(counts.values()),
                training_width_counts=dict(counts), label_unique_pair_settings=unique_settings,
                label_unique_current_rows=unique_rows, radii=list(radii),
                validation="leave-one-original-parent-out, all sibling edits together",
                objective="positive two-bit packed-work saving; mixed score breaks positive ties",
                accounting="both exact visits and actual columns, six units per attempted action, "
                "one per requested row and two per new row per independent reader, five per emitted "
                "proof, upfront radius visits and menu construction on every edit",
                early_width_one="after a late one-bit result, charge executed menu with zero credit",
                selected_two_bit_units=best[0], selected_mixed_units=best[1],
                candidates=by_config, recipe_updates=updates,
                parent_block_edit_counts=[len(family) for family in training],
                null_two_bit_units=0, null_mixed_units=0,
                anchor_names=list(ANCHORS), corner_masks=list(CORNERS),
                recipe_columns=["primary_anchor", "primary_oriented_mask_index", "primary_score",
                                "complement_anchor", "backup_oriented_mask_index", "backup_score"],
                model_sha256_canonical=hashlib.sha256(raw).hexdigest())
    return model, meta
