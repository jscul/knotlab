"""An ordinary incremental repair that prices widths before constructing candidate circuits."""
from functools import cache
from itertools import combinations

from parent_engine import _finish, _local_sources, _measure, _partition, _select


PAIRS = tuple(combinations(range(8), 2))


@cache
def _separates(truth):
    """Pairs of local assignments separated by this three-variable wire."""
    return sum(1 << i for i, (a, b) in enumerate(PAIRS)
               if ((truth >> a) ^ (truth >> b)) & 1)


def _location(state, work):
    if state.edit is None:
        return None
    support = state.supports[state.edit["to"]]
    groups = set()
    for record in state.parent.pieces:
        work["support_filter_records"] += 1
        group = record["inputs"]
        if all(support & (1 << j) for j in group):
            groups.add(group)
    work["support_filter_matches"] += len(groups)
    if len(groups) == 1:
        work["support_filter_unique"] += 1
        return groups.pop()
    return None


def _exact_first(state, work, hint):
    preferred = hint if hint is not None else _location(state, work)
    incumbent = None
    if preferred is not None:
        candidate = _partition(state, work, preferred)
        if candidate["eligible"]:
            incumbent = candidate
    selected = _select(state, work, preferred, incumbent)
    if selected is None:
        raise ValueError("no jointly essential triple")
    group, width = selected["triple"], selected["width"]
    bits = sources = None
    if width == 2:
        # Generic two-wire separator. The code assigns no special role to an old bit.
        classes = selected["classes"]
        need = sum(1 << i for i, (a, b) in enumerate(PAIRS) if classes[a] != classes[b])
        candidates = {}
        for entry in _local_sources(state, work, group):
            mask = _separates(entry["truth"]) & need
            if mask:
                candidates.setdefault(mask, entry)
        for (left, a), (right, b) in combinations(candidates.items(), 2):
            work["generic_source_pair_tests"] += 1
            if left | right == need:
                bits, sources = (a["truth"], b["truth"]), (a["wire"], b["wire"])
                work["generic_source_pair_found"] += 1
                break
    return _finish(state, work, group, bits=bits, source_wires=sources)


def ordinary_exact(state, hint=None):
    return _measure(state, _exact_first, hint)
