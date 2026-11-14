"""Deterministic input manifests for LEVEL-REACH stage 1.

This module constructs descriptions only; importing it does not start a study
or write files.  Term indices, rather than the word indices of ``addr.py``,
occur in placements.  A term's index is ``3 * word_index + letter_index`` with
letter indices ``none, 0, 1`` in that order.

The ``gamma`` implementation and key serialization follow the admitted
ADDR-KNOTS ``addr.py``.  The explicit placement sampler in ``codex_spec.md``
is used: a uniform rank among three-subsets of terms.  The earlier design's
description of per-letter coding is retained in ``implementation_notes``.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random


SCHEMA_VERSION = 1
WEIGHTED_COUNTS = {"P": 1000, "R": 4000}
WEIGHTED_SEEDS = {"P": 20261120, "R": 20261121}


def gamma(rng):
    """Elias-gamma draw by fair coins; return its value and bit count."""
    z = 0
    while rng.random() < 0.5:
        z += 1
    value = 1
    for _ in range(z):
        value = 2 * value + (rng.random() < 0.5)
    return value, 2 * z + 1


def term_count(s):
    """Number of terms in word-major, then ``none, 0, 1`` order."""
    s = int(s)
    if s < 1:
        raise ValueError("an automaton must have at least one state")
    return 3 * (1 + s + s * s)


def normalize_key(key):
    """Validate a term-index key and sort/deduplicate its placements."""
    if len(key) != 5:
        raise ValueError("key must contain s, swap, successor0, successor1, placements")
    s = int(key[0])
    if s < 1:
        raise ValueError("an automaton must have at least one state")
    sw, d0, d1 = (tuple(int(q) for q in row) for row in key[1:4])
    if len(sw) != s or len(d0) != s or len(d1) != s:
        raise ValueError("key state count disagrees with the automaton arrays")
    if any(bit not in (0, 1) for bit in sw):
        raise ValueError("root permutations must be bits")
    if any(q < 0 or q >= s for q in d0 + d1):
        raise ValueError("successor state outside the automaton")
    count = term_count(s)
    placements = set()
    for placement in key[4]:
        triple = tuple(sorted(int(t) for t in placement))
        if len(triple) != 3 or len(set(triple)) != 3:
            raise ValueError("each placement must have three distinct term indices")
        if triple[0] < 0 or triple[-1] >= count:
            raise ValueError("placement term index outside T_s")
        placements.add(triple)
    return s, sw, d0, d1, tuple(sorted(placements))


def key_json(key):
    """Return the normalized key as JSON-compatible lists."""
    s, sw, d0, d1, placements = normalize_key(key)
    return [s, list(sw), list(d0), list(d1), [list(t) for t in placements]]


def key_id(key):
    """SHA-256 of the compact normalized JSON, as in ``addr.py``."""
    raw = json.dumps(key_json(key), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def uniform_automaton(rng, s):
    """Draw swap, successor0, successor1 arrays uniformly, in that order."""
    s = int(s)
    if s < 1:
        raise ValueError("an automaton must have at least one state")
    sw = tuple(int(rng.random() < 0.5) for _ in range(s))
    d0 = tuple(rng.randrange(s) for _ in range(s))
    d1 = tuple(rng.randrange(s) for _ in range(s))
    return sw, d0, d1


def unrank_triple(count, rank):
    """Unrank a three-subset in ``itertools.combinations`` order."""
    count, rank = int(count), int(rank)
    if count < 3 or rank < 0 or rank >= math.comb(count, 3):
        raise ValueError("rank outside the three-subsets of range(count)")
    for first in range(count - 2):
        block = math.comb(count - first - 1, 2)
        if rank >= block:
            rank -= block
            continue
        for second in range(first + 1, count - 1):
            block = count - second - 1
            if rank >= block:
                rank -= block
            else:
                return first, second, second + 1 + rank
    raise AssertionError("valid placement rank was not unranked")


def _sample_placements(rng, s, r):
    count = term_count(s)
    possibilities = math.comb(count, 3)
    ranks = [rng.randrange(possibilities) for _ in range(r)]
    placements = [unrank_triple(count, rank) for rank in ranks]
    return placements, ranks


def random_key(rng, s=None, r=None):
    """Draw an unweighted fixture key for gates, independently of populations.

    Unspecified ``s`` and ``r`` are uniform on 1..5 and 1..9 respectively.
    Explicit ``r=0`` is permitted for empty-pattern fixtures. These fixture
    rules are independent of the panel population rules.
    """
    s = rng.randrange(1, 6) if s is None else int(s)
    r = rng.randrange(1, 10) if r is None else int(r)
    if s < 1 or r < 0:
        raise ValueError("fixture s must be positive and r nonnegative")
    aut = uniform_automaton(rng, s)
    placements, _ = _sample_placements(rng, s, r)
    return normalize_key((s, *aut, placements))


def _automaton_json(aut):
    return [list(row) for row in aut]


def _add_key(keys_by_id, key, membership):
    normalized = key_json(key)
    identifier = key_id(key)
    if identifier not in keys_by_id:
        keys_by_id[identifier] = {
            "id": identifier,
            "key": normalized,
            "memberships": [],
        }
    elif keys_by_id[identifier]["key"] != normalized:
        raise AssertionError("different keys have the same SHA-256 identifier")
    keys_by_id[identifier]["memberships"].append(membership)
    return identifier


def _weighting(s, s_bits, r=None, r_bits=None):
    """Retain exact probability factors as well as logarithmic bit totals."""
    bits = {
        "gamma_s": s_bits,
        "swap": 0,
        "successors": 0.0,
        "gamma_r": 0,
        "placements": 0.0,
    }
    factors = {"dyadic_bits": s_bits, "successor_denominator": 1,
               "placement_denominator": 1}
    if s <= 5:
        bits["swap"] = s
        bits["successors"] = 2 * s * math.log2(s)
        factors["dyadic_bits"] += s
        factors["successor_denominator"] = s ** (2 * s)
    if r is not None:
        bits["gamma_r"] = r_bits
        factors["dyadic_bits"] += r_bits
        if r <= 8:
            possibilities = math.comb(term_count(s), 3)
            bits["placements"] = r * math.log2(possibilities)
            factors["placement_denominator"] = possibilities ** r
    return {
        "bits": bits,
        "total_bits": sum(bits.values()),
        "exact_probability_factors": factors,
        "probability_formula": (
            "2**(-dyadic_bits) / successor_denominator / placement_denominator"
        ),
        "complete_description": s <= 5 and r is not None and r <= 8,
    }


def _weighted(pop, keys_by_id):
    draws = []
    family = "W_" + pop
    seed = WEIGHTED_SEEDS[pop]
    for i in range(WEIGHTED_COUNTS[pop]):
        draw_seed = f"{seed}-{i}"
        rng = random.Random(draw_seed)
        s, s_bits = gamma(rng)
        draw = {"family": family, "index": i, "seed": draw_seed, "s": s}
        if s > 5:
            draw.update(status="rejected", rejection="s > 5",
                        weighting=_weighting(s, s_bits))
            draws.append(draw)
            continue
        aut = uniform_automaton(rng, s)
        draw["automaton"] = _automaton_json(aut)
        r, r_bits = gamma(rng)
        draw["r"] = r
        if r > 8:
            draw.update(status="rejected", rejection="r > 8",
                        weighting=_weighting(s, s_bits, r, r_bits))
            draws.append(draw)
            continue
        placements, ranks = _sample_placements(rng, s, r)
        membership = {"family": family, "index": i, "seed": draw_seed}
        identifier = _add_key(keys_by_id, (s, *aut, placements), membership)
        draw.update(status="accepted", key_id=identifier,
                    placement_ranks=ranks,
                    sampled_placements=[list(t) for t in placements],
                    weighting=_weighting(s, s_bits, r, r_bits))
        draws.append(draw)
    return draws


def _pilot_panel(keys_by_id):
    rng = random.Random("20261122-a")
    roster, draws = [], []
    for a in range(200):
        aut = uniform_automaton(rng, 3)
        item = {"index": a, "s": 3, "automaton": _automaton_json(aut), "lists": []}
        for j in range(2):
            seed = f"20261122-{a}-{j}"
            list_rng = random.Random(seed)
            gamma_value, gamma_bits = gamma(list_rng)
            r = min(1 + gamma_value, 9)
            placements, ranks = _sample_placements(list_rng, 3, r)
            membership = {"family": "E_P", "s": 3, "automaton": a,
                          "list": j, "seed": seed}
            identifier = _add_key(keys_by_id, (3, *aut, placements), membership)
            draw = {**membership, "status": "accepted", "key_id": identifier,
                    "r": r, "gamma_value": gamma_value, "gamma_bits": gamma_bits,
                    "placement_ranks": ranks,
                    "sampled_placements": [list(t) for t in placements]}
            draws.append(draw)
            item["lists"].append({"index": j, "seed": seed, "status": "accepted",
                                  "key_id": identifier, "r": r})
        roster.append(item)
    return {
        "family": "E_P", "s": 3, "automata_count": 200,
        "automaton_sampling": "uniform with replacement from one RNG stream",
        "automaton_rng_seed": "20261122-a", "lists_per_automaton": 2,
        "list_seed_template": "20261122-{a}-{j}",
        "r_rule": "min(1 + gamma(list_rng)[0], 9)", "roster": roster,
    }, draws


def _all_two_state_automata():
    """Enumerate the 64 arrays lexicographically as (swap, d0, d1)."""
    rows = tuple(itertools.product(range(2), repeat=2))
    return itertools.product(rows, rows, rows)


def _registered_panels(keys_by_id):
    panels, draws = [], []
    rng = random.Random("20261123-a")
    sources = (
        (2, 64, 5, _all_two_state_automata(), "lexicographic enumeration", None),
        (3, 1000, 2, (uniform_automaton(rng, 3) for _ in range(1000)),
         "uniform with replacement from one RNG stream", "20261123-a"),
    )
    for s, count, lists, automata, sampling, seed in sources:
        roster = []
        for a, aut in enumerate(automata):
            item = {"index": a, "s": s, "automaton": _automaton_json(aut), "lists": []}
            for j in range(lists):
                list_seed = f"20261123-{s}-{a}-{j}"
                list_rng = random.Random(list_seed)
                gamma_value, gamma_bits = gamma(list_rng)
                r = min(1 + gamma_value, 9)
                placements, ranks = _sample_placements(list_rng, s, r)
                membership = {"family": "E_R", "s": s, "automaton": a,
                              "list": j, "seed": list_seed}
                identifier = _add_key(keys_by_id, (s, *aut, placements), membership)
                metadata = {**membership, "status": "accepted", "key_id": identifier,
                            "r": r, "gamma_value": gamma_value, "gamma_bits": gamma_bits,
                            "placement_ranks": ranks,
                            "sampled_placements": [list(t) for t in placements]}
                draws.append(metadata)
                item["lists"].append({"index": j, "seed": list_seed,
                                      "status": "accepted", "key_id": identifier, "r": r})
            roster.append(item)
        if len(roster) != count:
            raise AssertionError("registered automaton roster has the wrong size")
        panels.append({"family": "E_R", "s": s, "automata_count": count,
                       "automaton_sampling": sampling, "automaton_rng_seed": seed,
                       "lists_per_automaton": lists,
                       "list_seed_template": "20261123-{s}-{a}-{j}",
                       "r_rule": "min(1 + gamma(list_rng)[0], 9)", "roster": roster})
    return panels, draws


def build_population(pop):
    """Build an in-memory, JSON-compatible manifest for P or R.

    ``keys`` is an insertion-ordered list of distinct normalized descriptions,
    each with every accepted sampling membership. ``draws`` contains weighted
    attempts (including rejections) followed by panel-list records (including
    skips). ``panels`` retains all sampled/enumerated automata and list seeds.
    No SAT solver, scientific case computation, or filesystem write occurs.
    """
    pop = str(pop).upper()
    if pop not in WEIGHTED_COUNTS:
        raise ValueError("population must be P or R")
    keys_by_id = {}
    weighted = _weighted(pop, keys_by_id)
    if pop == "P":
        panel, panel_draws = _pilot_panel(keys_by_id)
        panels, ambiguities = [panel], []
    else:
        panels, panel_draws = _registered_panels(keys_by_id)
        ambiguities = []
    draws = weighted + panel_draws
    weighted_accepted = sum(d["status"] == "accepted" for d in weighted)
    panel_accepted = sum(d["status"] == "accepted" for d in panel_draws)
    summary = {
        "weighted_attempts": len(weighted),
        "weighted_accepted": weighted_accepted,
        "weighted_rejected_s": sum(d.get("rejection") == "s > 5" for d in weighted),
        "weighted_rejected_r": sum(d.get("rejection") == "r > 8" for d in weighted),
        "panel_automata": sum(panel["automata_count"] for panel in panels),
        "panel_lists": len(panel_draws),
        "panel_lists_accepted": panel_accepted,
        "panel_lists_skipped": len(panel_draws) - panel_accepted,
        "accepted_memberships": weighted_accepted + panel_accepted,
        "distinct_keys": len(keys_by_id),
    }
    return {
        "schema_version": SCHEMA_VERSION, "population": pop,
        "weighted_seed": WEIGHTED_SEEDS[pop],
        "keys": list(keys_by_id.values()), "draws": draws, "panels": panels,
        "summary": summary, "ambiguities": ambiguities,
        "implementation_notes": [
            "Each W attempt uses its own Random(f'{seed}-{i}'); rejected attempts are not redrawn.",
            "Swap bits precede d0 then d1; a swap is int(rng.random() < 0.5).",
            "Placements are independent uniform ranks in combinations(range(3*(1+s+s*s)), 3), with replacement between placements.",
            "Raw ranks and sampled placements are retained before key placement deduplication.",
            "Weighting totals are ideal code lengths; exact probability factors avoid rounding the logarithmic components.",
            "The explicit codex_spec uniform term-triple sampler is used; design.md's earlier census-code-plus-per-letter wording describes a different code.",
        ],
    }
