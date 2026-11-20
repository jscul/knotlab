"""Check the literal allowed-state projection at each declared starting support."""



def labels(mask):
    out = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


def physical_words(sizes, meetings):
    """Give each recorded meeting its own distinction, even for repeated pairs."""
    n = len(sizes)
    assert n and all(isinstance(size, int) and size >= 3 for size in sizes)
    masks = [0] * n
    owners = []
    near = [set() for _ in sizes]
    for pair in meetings:
        a, b = sorted(pair)
        assert 0 <= a < b < n
        label = len(owners)
        owners.append([a, b])
        masks[a] |= 1 << label
        masks[b] |= 1 << label
        near[a].add(b)
        near[b].add(a)
    seen, pending = {0}, [0]
    while pending:
        new = near[pending.pop()] - seen
        seen.update(new)
        pending.extend(new)
    assert len(seen) == n
    loose = []
    for u, size in enumerate(sizes):
        count = size - masks[u].bit_count()
        assert count >= 0
        for _ in range(count):
            label = len(owners)
            owners.append([u])
            loose.append(label)
            masks[u] |= 1 << label
    assert [mask.bit_count() for mask in masks] == list(sizes)
    assert len(owners) == sum(sizes) - len(meetings)
    return masks, owners, loose


def row_span(masks):
    """Enumerate each original row combination without a graph-based gate."""
    combinations = [0] * (1 << len(masks))
    witnesses = {0: 0}
    for source in range(1, len(combinations)):
        last = source & -source
        word = combinations[source ^ last] ^ masks[last.bit_length() - 1]
        combinations[source] = word
        old = witnesses.get(word)
        if old is None or (source.bit_count(), source) < (old.bit_count(), old):
            witnesses[word] = source
    assert len(witnesses) & (len(witnesses) - 1) == 0
    return witnesses


def qualify(sizes, meetings, *, detail=False):
    masks, owners, loose = physical_words(sizes, meetings)
    span = row_span(masks)
    bad = []
    projections = []
    for u, support in enumerate(masks):
        proper_words = []
        current = (support - 1) & support
        while current:
            if current in span:
                proper_words.append(current)
            current = (current - 1) & support
        # The orthogonal relation projects onto S with exactly the equations
        # in the full span that are supported on S, including the declared row.
        allowed = (1 << support.bit_count()) // (len(proper_words) + 2)
        assert (allowed << (len(proper_words) + 1).bit_length()) == 1 << support.bit_count()
        if detail:
            projections.append(allowed)
        if proper_words:
            word = min(proper_words, key=lambda w: (w.bit_count(), tuple(labels(w))))
            bad.append({"junction": u, "support": labels(support), "smaller_support": labels(word),
                        "source_rows_xored": labels(span[word]), "projected_states": allowed,
                        "full_single_parity_states": 1 << (support.bit_count() - 1),
                        "proper_span_words": len(proper_words)})
    forced = [v for v in range(len(owners)) if 1 << v in span]
    assert not forced or bad
    # The all-zero assignment obeys every homogeneous parity row.
    base = {"canonical": not bad, "K1_all": all(s in span and s for s in masks), "K2_all": not bad,
            "K3_all": True, "physical_junctions": len(masks), "distinctions": len(owners),
            "open_distinctions": len(loose), "span_rank": len(span).bit_length() - 1,
            "K2_failed_junctions": [w["junction"] for w in bad], "forced_distinctions": forced}
    if detail:
        base.update({"literal_supports": [labels(s) for s in masks], "holders_by_distinction": owners,
                     "loose_distinctions": loose, "projected_state_counts": projections, "K2_witnesses": bad})
    return base


def controls():
    clear = qualify([3, 3], [[0, 1]], detail=True)
    assert clear["canonical"] and clear["projected_state_counts"] == [4, 4]
    one_forced = qualify([3, 4], [[0, 1]] * 3, detail=True)
    relation = one_forced["K2_witnesses"][0]
    assert one_forced["forced_distinctions"] == [3] and relation["source_rows_xored"] == [0, 1]
    assert relation["junction"] == 1 and relation["smaller_support"] == [3]
    two_constrained = qualify([3, 5], [[0, 1]] * 3, detail=True)
    relation = two_constrained["K2_witnesses"][0]
    assert not two_constrained["forced_distinctions"] and relation["smaller_support"] == [3, 4]
    assert relation["projected_states"] == 8 and relation["full_single_parity_states"] == 16
    return {"canonical_pair_with_one_meeting": clear, "singleton_counterexample": one_forced,
            "proper_equation_without_forced_distinction": two_constrained}
