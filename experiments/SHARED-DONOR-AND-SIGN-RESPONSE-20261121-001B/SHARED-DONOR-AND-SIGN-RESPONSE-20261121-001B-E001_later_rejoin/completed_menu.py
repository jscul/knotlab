"""Reconstruct the old words and compare complete, signed four-choice operations."""

from collections import defaultdict
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import gzip
import json
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
ARCHIVE = (
    ROOT
    / "artifacts/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A-E001_sign_records/archived_events.json.gz"
)
AUDIT = ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001/merger_audit.json"


def mask(bits):
    return sum(1 << v for v in bits)


def locations(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def local_groups(holdings, words):
    common = set.intersection(*words)
    different = set.union(*words) - common
    grouped = defaultdict(list)
    for b in sorted(different):
        owners = tuple(i for i, h in enumerate(holdings) if b in h)
        grouped[owners].append(b)
    assert len(grouped) == 2 and all(
        len(owner) == 1 and len(values) == 4 for owner, values in grouped.items()
    )
    return [tuple(v) for _, v in sorted(grouped.items())]


def geometry(holdings, nodes):
    states = {node["id"]: set(node["word"]) for node in nodes}
    mids = sorted(e["target"] for e in nodes[11]["enabled_events"])
    assert mids == [n["id"] for n in nodes if n["depth"] == 10]
    groups = local_groups(holdings, [states[i] for i in mids])
    coordinates = {
        w: tuple(next(i for i, b in enumerate(g) if b in states[w]) for g in groups) for w in mids
    }
    assert len(set(coordinates.values())) == 16 and len(mids) == 16
    for w in mids:
        assert all(len(set(g) & states[w]) == 1 for g in groups)
    newer = [set(), set()]
    all_outputs = set()
    arc = []
    centers = [set(), set()]
    for w in mids:
        assert len(nodes[w]["enabled_events"]) == 8
        for event in nodes[w]["enabled_events"]:
            y = event["target"]
            assert Fraction(event["chance_given_source"]) == Fraction(1, 8)
            erased = states[w] - states[y]
            born = states[y] - states[w]
            assert len(born) == 1 and mask(erased | born) == int(event["event_id"])
            slots = [i for i, g in enumerate(groups) if erased & set(g)]
            assert len(slots) == 1
            slot = slots[0]
            b = next(iter(born))
            newer[slot].add(b)
            all_outputs.add(y)
            centers[slot].update(event["at_knots"])
            arc.append((w, y, slot, b))
    newer = [tuple(sorted(row)) for row in newer]
    assert all(len(g) == 4 for g in newer)
    for g in newer:
        assert len({tuple(i for i, h in enumerate(holdings) if b in h) for b in g}) == 1
        assert len([i for i, h in enumerate(holdings) if g[0] in h]) == 1
    assert all(len(c) == 1 for c in centers)
    outcoords = {}
    for w, y, c, b in arc:
        address = (c, coordinates[w][1 - c], newer[c].index(b))
        if y in outcoords:
            assert outcoords[y] == address
        outcoords[y] = address
    assert len(outcoords) == len(set(outcoords.values())) == 32
    assert sorted(all_outputs) == [n["id"] for n in nodes if n["depth"] == 11]
    assert {
        b
        for b in all_outputs
        if (12, b) in {(w, y) for w, y, c, d in arc} and (13, b) in {(w, y) for w, y, c, d in arc}
    } == {32, 33, 34, 35}
    return (
        mids,
        sorted(all_outputs),
        coordinates,
        outcoords,
        groups,
        newer,
        [next(iter(c)) for c in centers],
        arc,
    )


def exact_ports(effects, outputs, unit, first, second):
    """effects are integer Gram numerators, for all old words simultaneously."""
    rows = []
    for word, g in zip(outputs, effects):
        a = int(g[first, first])
        b = int(g[second, second])
        off = int(g[first, second])
        row = dict(
            word=word,
            singleton_a=str(Fraction(a, unit)),
            singleton_b=str(Fraction(b, unit)),
            dephased=str(Fraction(a + b, 2 * unit)),
            plus=str(Fraction(a + b + 2 * off, 2 * unit)),
            minus=str(Fraction(a + b - 2 * off, 2 * unit)),
            off_diagonal=str(Fraction(off, unit)),
        )
        assert (
            min(Fraction(row[k]) for k in ("singleton_a", "singleton_b", "dephased", "plus", "minus"))
            >= 0
        )
        rows.append(row)
    keys = ("singleton_a", "singleton_b", "dephased", "plus", "minus")
    assert all(sum(Fraction(r[k]) for r in rows) == 1 for k in keys)
    target = next(r for r in rows if r["word"] == 32)
    return dict(
        fine_outputs=rows,
        target={k: target[k] for k in keys},
        complement={k: str(1 - Fraction(target[k])) for k in keys},
        target_signed_contrast=str(Fraction(target["plus"]) - Fraction(target["minus"])),
    )


def full_operations(geom):
    mids, outs, coords, oc, groups, newer, centers, arcs = geom
    nc = len(mids)
    nr = len(outs)
    prior = np.zeros((nr, nc), dtype=np.int16)
    for w, y, c, b in arcs:
        prior[outs.index(y), mids.index(w)] = 1
    assert np.all(prior.sum(axis=0) == 8)
    stencil = {
        "matched_reflection": np.array([[1 - 2 * int(j == i) for i in range(4)] for j in range(4)]),
        "binary_characters": np.array(
            [[(-1) ** ((i & j).bit_count()) for i in range(4)] for j in range(4)]
        ),
        "positive_roots": np.ones((4, 4), dtype=np.int16),
    }
    operations = {}
    old_a, old_b = map(mids.index, (12, 13))
    nonnegative = []
    for key, H in stencil.items():
        V = np.zeros_like(prior)
        for w, y, c, b in arcs:
            V[outs.index(y), mids.index(w)] = H[newer[c].index(b), coords[w][c]]
        assert np.array_equal(V * V, prior)
        gram = V.T @ V
        record = dict(
            local_integer_stencil=H.tolist(),
            amplitude_numerators=V.tolist(),
            squared_column_denominator=8,
            gram_numerators=gram.tolist(),
            normalized=bool(np.array_equal(gram, 8 * np.eye(nc, dtype=np.int16))),
        )
        if record["normalized"]:
            E = np.einsum("oi,oj->oij", V, V, optimize=False)
            record["reports"] = exact_ports(E, outs, 8, old_a, old_b)
            phase = -np.ones(nr, dtype=np.int16)
            phase[::2] = 1
            rephased = V * phase[:, None]
            assert np.array_equal(E, np.einsum("oi,oj->oij", rephased, rephased))
            column = V.copy()
            column[:, old_b] *= -1
            swapped = exact_ports(np.einsum("oi,oj->oij", column, column), outs, 8, old_a, old_b)
            for left, right in zip(record["reports"]["fine_outputs"], swapped["fine_outputs"]):
                assert (left["plus"], left["minus"]) == (right["minus"], right["plus"])
            record["one_input_phase_reversed_target"] = swapped["target"]
        else:
            record["selected_pair_inner_product"] = str(Fraction(int(gram[old_a, old_b]), 8))
            for s in (1, -1):
                projected = V[:, old_a] + s * V[:, old_b]
                nonnegative.append(str(Fraction(int(projected @ projected), 16)))
            record["signed_total_output_masses_plus_minus"] = nonnegative
        operations[key] = record
    # One pre-distinguished destination sibling across all four spectator values.
    # Use integer denominator 24. The distinguished center has one bright effect
    # and three equal effects on its orthogonal complement. The other center is diagonal.
    chosen_center, _, marked = oc[32]
    effects = np.zeros((nr, nc, nc), dtype=np.int16)
    ranks = []
    for iy, y in enumerate(outs):
        center, other, j = oc[y]
        indices = [ix for ix, w in enumerate(mids) if coords[w][1 - center] == other]
        assert [int(prior[iy, i]) for i in indices] == [1] * 4
        off = (3 if j == marked else -1) if center == chosen_center else 0
        block = np.full((4, 4), off, dtype=np.int16)
        np.fill_diagonal(block, 3)
        effects[iy][np.ix_(indices, indices)] = block
        eigenvalues = [3 + 3 * off, 3 - off, 3 - off, 3 - off]
        assert min(eigenvalues) >= 0
        ranks.append(sum(e > 0 for e in eigenvalues))
    assert np.array_equal(effects.sum(axis=0), 24 * np.eye(nc, dtype=np.int16))
    assert np.array_equal(np.diagonal(effects, axis1=1, axis2=2), 3 * prior)
    operations["active_one_output_effects"] = dict(
        effect_numerators=effects.tolist(),
        denominator=24,
        fine_effect_ranks=ranks,
        reports=exact_ports(effects, outs, 24, old_a, old_b),
        chosen_center=centers[chosen_center],
        physical_mark=newer[chosen_center][marked],
    )
    # A physically dephased center and four-way offset. Each individual setting is a
    # bijection on its center's 16 output words, hence already a scalar isometry.
    fixed = {}
    mean = np.zeros_like(prior)
    for c in range(2):
        for k in range(4):
            V = np.zeros_like(prior)
            for w, y, cc, b in arcs:
                if cc == c and newer[c].index(b) == (coords[w][c] + k) % 4:
                    V[outs.index(y), mids.index(w)] = 1
            assert np.array_equal(V.T @ V, np.eye(nc, dtype=np.int16))
            mean += V * V
            E = np.einsum("oi,oj->oij", V, V)
            fixed[f"{centers[c]}/{k}"] = dict(
                targets_by_input=[outs[i] for i in np.argmax(V, axis=0)],
                reports=exact_ports(E, outs, 1, old_a, old_b),
            )
    assert np.array_equal(mean, prior)
    diagonal = np.zeros((nr, nc, nc), dtype=np.int16)
    for i in range(nc):
        diagonal[:, i, i] = prior[:, i]
    operations["classical_uniform_center_and_shift"] = dict(
        conditional=fixed, reported=exact_ports(diagonal, outs, 8, old_a, old_b)
    )
    return dict(
        input_ids=mids,
        output_ids=outs,
        old_slot_by_input=coords,
        output_center_slot_surviving_old_and_new=oc,
        old_loose_groups=groups,
        new_loose_groups=newer,
        corrective_centers=centers,
        arch_legal_support=prior.tolist(),
        operations=operations,
    )


def census():
    """All +/- 4 by 4 real stencils, with the equal route magnitudes fixed."""
    bitmaps = np.arange(65536, dtype=np.int32)
    signs = (1 - 2 * ((bitmaps[:, None] >> np.arange(16)) & 1)).astype(np.int16).reshape(-1, 4, 4)
    grams = np.einsum("noi,noj->nij", signs, signs, optimize=False)
    proper = np.all(grams == 4 * np.eye(4, dtype=np.int16), axis=(1, 2))
    legal = signs[proper]
    votes = legal[:, 0, 0] * legal[:, 0, 1]
    assert all(np.all(np.abs(H.T @ H) == 4 * np.eye(4)) for H in legal)
    row_products = legal[:, :, 0] * legal[:, :, 1]
    assert np.all(np.sum(row_products, axis=1) == 0) and np.all(np.sum(row_products == 1, axis=1) == 2)
    return dict(
        all_stencils=len(bitmaps),
        normalized_stencils=len(legal),
        normalized_bitmaps=bitmaps[proper].tolist(),
        sign_encoding="bit 4*y+i is one for a negative (y,i) entry",
        target_contrast_at_ranks_0_0_and_1={
            "+1/4": int(np.sum(votes == 1)),
            "-1/4": int(np.sum(votes == -1)),
        },
        rank_one_word_effects_invariant_to_all_independent_output_relabelings=int(
            np.sum(np.all(row_products == row_products[:, 0, None], axis=1))
        ),
    )


def labelled_recodings():
    """Compare a fixed matching with simultaneous transport of both physical name rosters."""
    permutations_of_four = tuple(permutations(range(4)))
    reflection = np.ones((4, 4), dtype=int) - 2 * np.eye(4, dtype=int)
    fixed = []
    for outgoing in permutations_of_four:
        for incoming in permutations_of_four:
            transported = np.empty_like(reflection)
            for y in range(4):
                for i in range(4):
                    transported[outgoing[y], incoming[i]] = reflection[y, i]
            # Acting on the two rosters and on the stored matching is a recoding.
            for y in range(4):
                for i in range(4):
                    assert transported[outgoing[y], incoming[i]] == reflection[y, i]
            if np.array_equal(transported, reflection):
                fixed.append((outgoing, incoming))
    assert len(fixed) == 24 and all(a == b for a, b in fixed)
    return dict(
        independent_old_and_new_rename_pairs=len(permutations_of_four) ** 2,
        unchanged_fixed_reflection_pairs=fixed,
        pairs_preserving_the_transported_matching=len(permutations_of_four) ** 2,
    )
