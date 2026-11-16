"""Exact finite stored-knot checks for the specified address maps.

``prefix_c after m`` means ``w -> c m(w)`` and ``suffix_c after m``
means ``w -> m(w) c``.  The first bit is the most significant bit.
These checks concern only explicitly stored finite triples.  They make no
claim about native contact or preservation at untested depths.
"""

from operator import index

import numpy as np

from reuse import pattern


def _depth(value, name):
    value = index(value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def _key(key):
    """Validate addressed terms, whose indices have three slots per word."""
    if len(key) != 5:
        raise ValueError("key must contain s, swap, successor0, successor1, placements")
    s = index(key[0])
    if s < 1:
        raise ValueError("the automaton must have at least one state")
    sw, d0, d1 = (tuple(index(x) for x in row) for row in key[1:4])
    if any(len(row) != s for row in (sw, d0, d1)):
        raise ValueError("automaton arrays must agree with s")
    if any(bit not in (0, 1) for bit in sw):
        raise ValueError("root swaps must be bits")
    if any(q < 0 or q >= s for q in d0 + d1):
        raise ValueError("successor state outside the automaton")
    term_count = 3 * (1 + s + s * s)
    placements = set()
    for row in key[4]:
        row = tuple(sorted(index(x) for x in row))
        if len(row) != 3 or len(set(row)) != 3:
            raise ValueError("each placement must have three distinct term indices")
        if row[0] < 0 or row[-1] >= term_count:
            raise ValueError("placement term outside the addressed word table")
        placements.add(row)
    return s, sw, d0, d1, tuple(sorted(placements))


def _words(s):
    return [()] + [(q,) for q in range(s)] + [
        (q, r) for q in range(s) for r in range(s)
    ]


def candidates(s):
    """Return unique syntactic candidates, including bare maps once.

    A bare prefix/suffix and its composition after the empty word are one
    candidate.  Different nonempty words remain separate candidates even
    when their actions happen to coincide for this automaton.
    """
    s = index(s)
    if s < 1:
        raise ValueError("s must be positive")
    out = []
    for family in ("prefix", "suffix"):
        for c in (0, 1):
            for wi, word in enumerate(_words(s)):
                name = f"{family}_{c}"
                if word:
                    name += "_after_" + "_".join(str(q) for q in word)
                out.append({"name": name, "family": family, "c": c,
                            "word": list(word), "word_index": wi})
    return out


def _map_spec(spec, s):
    family = spec["family"]
    c = index(spec["c"])
    word = tuple(index(q) for q in spec["word"])
    if family not in ("prefix", "suffix") or c not in (0, 1):
        raise ValueError("map must specify prefix/suffix and one bit")
    if len(word) > 2 or any(q < 0 or q >= s for q in word):
        raise ValueError("map word must have at most two ordinary states")
    return family, c, word


def _word_map(key, word, source_depth):
    """The level-preserving action, in the source's global vertex order."""
    aut = key[1:4]
    table = np.empty((1 << (source_depth + 1)) - 1, dtype=np.int64)
    for n in range(source_depth + 1):
        offset = (1 << n) - 1
        table[offset:(1 << (n + 1)) - 1] = (
            pattern.addr.action(aut, word, n) + offset
        )
    return table


def _insert_bit(word_table, family, c, source_depth):
    table = np.empty_like(word_table)
    for n in range(source_depth + 1):
        start, stop = (1 << n) - 1, (1 << (n + 1)) - 1
        local = word_table[start:stop] - start
        if family == "prefix":
            local = local + c * (1 << n)
        else:
            local = 2 * local + c
        table[start:stop] = local + (1 << (n + 1)) - 1
    return table


def build_map(key, spec, source_depth=8):
    """Return the image of every global source vertex as an int64 array."""
    key = _key(key)
    source_depth = _depth(source_depth, "source_depth")
    family, c, word = _map_spec(spec, key[0])
    return _insert_bit(_word_map(key, word, source_depth), family, c, source_depth)


def map_vertices(key, spec, vertices):
    """Apply one candidate to a finite iterable of global vertex indices."""
    vertices = [index(v) for v in vertices]
    if any(v < 0 for v in vertices):
        raise ValueError("global vertex indices must be nonnegative")
    if not vertices:
        return []
    source_depth = max((v + 1).bit_length() - 1 for v in vertices)
    table = build_map(key, spec, source_depth)
    return [int(table[v]) for v in vertices]


def _rows(rows, name):
    rows = np.asarray(rows, dtype=np.int64)
    if not rows.size:
        rows = rows.reshape((0, 3))
    if rows.ndim != 2 or rows.shape[1] != 3:
        raise ValueError(f"{name} must have exactly three columns")
    if rows.size and int(rows.min()) < 0:
        raise ValueError(f"{name} contains a negative vertex")
    return rows


def _check_rows(source, target_set, table, target_vertex_count):
    for row_index, row in enumerate(source):
        original = [int(v) for v in row]
        image = [int(table[v]) for v in original]
        ordered_image = sorted(image)
        distinct = len(set(image)) == 3
        if any(v < 0 or (target_vertex_count is not None and
                         v >= target_vertex_count) for v in image):
            reason = "image_outside_target"
        elif not distinct:
            reason = "fewer_than_three_distinct_images"
        elif tuple(ordered_image) not in target_set:
            reason = "image_not_stored_knot"
        else:
            continue
        return {"accepted": False, "checked_knots": row_index + 1,
                "witness": {"reason": reason, "source_knot_index": row_index,
                            "source_knot": original,
                            "image_in_source_order": image,
                            "image_knot": ordered_image,
                            "distinct_images": distinct}}
    return {"accepted": True, "checked_knots": len(source), "witness": None}


def check_map(source_knots, target_knots, table, target_vertex_count=None):
    """Check an explicit finite map, retaining the first failed source knot.

    This low-level interface also admits deliberately malformed maps for
    negative controls.  It does not assume injectivity of the supplied map.
    """
    source = _rows(source_knots, "source_knots")
    target = _rows(target_knots, "target_knots")
    table = np.asarray(table, dtype=np.int64)
    if table.ndim != 1:
        raise ValueError("the map table must be one-dimensional")
    if source.size and int(source.max()) >= len(table):
        raise ValueError("map table does not cover every source vertex")
    if target_vertex_count is not None:
        target_vertex_count = _depth(target_vertex_count, "target_vertex_count")
        if target.size and int(target.max()) >= target_vertex_count:
            raise ValueError("stored target knot lies outside its vertex set")
    target_set = {tuple(sorted(int(v) for v in row)) for row in target}
    return _check_rows(source, target_set, table, target_vertex_count)


def evaluate(key, source_depth=8, target_depth=9):
    """Check every specified map on every stored finite source knot.

    Results are JSON-compatible.  An empty source is marked as vacuous.
    Rejected maps retain their first counterexample in stored source order.
    """
    key = _key(key)
    source_depth = _depth(source_depth, "source_depth")
    target_depth = _depth(target_depth, "target_depth")
    source = _rows(pattern.pattern(key, source_depth), "source_knots")
    target = _rows(pattern.pattern(key, target_depth), "target_knots")
    source_vertex_count = (1 << (source_depth + 1)) - 1
    target_vertex_count = (1 << (target_depth + 1)) - 1
    if source.size and int(source.max()) >= source_vertex_count:
        raise ValueError("stored source knot lies outside its vertex set")
    if target.size and int(target.max()) >= target_vertex_count:
        raise ValueError("stored target knot lies outside its vertex set")
    target_set = {tuple(int(v) for v in row) for row in target}
    word_tables = {}
    accepted, rejected = [], []
    specs = candidates(key[0])
    for spec in specs:
        word = tuple(spec["word"])
        if word not in word_tables:
            word_tables[word] = _word_map(key, word, source_depth)
        table = _insert_bit(word_tables[word], spec["family"], spec["c"], source_depth)
        verdict = _check_rows(source, target_set, table, target_vertex_count)
        record = {**spec, "checked_knots": verdict["checked_knots"]}
        if verdict["accepted"]:
            accepted.append(record)
        else:
            record.update(verdict["witness"])
            rejected.append(record)
    return {
        "schema_version": 1,
        "scope": "exact stored finite knot triples only",
        "composition": "apply ordinary word right to left, then insert c",
        "candidate_interpretation": (
            "4*(1+s+s*s) syntactic candidates; bare maps equal empty-word "
            "composites and are listed once; nonempty words are not merged"
        ),
        "addressing": "v=2**n-1+y; first bit most significant",
        "source_depth": source_depth,
        "target_depth": target_depth,
        "source_vertex_count": source_vertex_count,
        "target_vertex_count": target_vertex_count,
        "source_knot_count": len(source),
        "target_knot_count": len(target),
        "vacuous": not len(source),
        "candidate_count": len(specs),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_maps": accepted,
        "rejected_maps": rejected,
        "nonclaims": ["no semantic contact claim", "no untested-depth claim"],
    }
