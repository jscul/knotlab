"""Independent rank, projection, preparation and later-growth checks."""

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GROWTH_SOURCE = ROOT / "experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A"


def bits(names):
    return sum(1 << b for b in names)


def names(mask):
    return [i for i in range(mask.bit_length()) if mask >> i & 1]


def basis(rows):
    pivot = {}
    for row in rows:
        while row:
            k = row.bit_length() - 1
            if k not in pivot:
                pivot[k] = row
                break
            row ^= pivot[k]
    return tuple(pivot[k] for k in sorted(pivot, reverse=True))


def contained(target, pivots):
    for row in pivots:
        if target & (1 << (row.bit_length() - 1)):
            target ^= row
    return target == 0


def reveals(rows, observable, panel):
    """A parity of a lawful word is determined by observing these physical marks."""
    return contained(observable & ~panel, basis(row & ~panel for row in rows))


def mask_counts(rows, observable):
    # All equivalent parity readouts are observable plus a combination of holding equations.
    representatives = [observable]
    for row in basis(rows):
        representatives += [mask ^ row for mask in representatives]
    return Counter(mask.bit_count() for mask in representatives)


def native_menus(holdings):
    # Independent brute-force check. Finding a move by size four for every bit
    # certifies the minimum and exhausts its ties.
    marks = sorted(set().union(*map(set, holdings)))
    syndromes = {b: bits(k for k, holding in enumerate(holdings) if b in holding) for b in marks}
    by_address = {b: set() for b in marks}
    for size in range(1, 5):
        unfinished = {b for b in marks if not by_address[b]}
        if not unfinished:
            break
        for support in combinations(marks, size):
            syndrome = 0
            for b in support:
                syndrome ^= syndromes[b]
            if syndrome == 0:
                move = bits(support)
                for b in support:
                    if b in unfinished:
                        by_address[b].add(move)
    assert all(by_address.values())
    return by_address, set.union(*by_address.values())


def source(n):
    return [[(i - 1) % n, i, n + 2 * i, n + 2 * i + 1] for i in range(n)]


def certificate(n, original, grown):
    # At each old holder, associate its two shared marks with different private
    # marks. At each new holder do the same with its inherited and fresh marks.
    disjoint = [{i} for i in range(n)]
    color = {}
    for holding in original:
        shared = sorted(b for b in holding if b < n)
        private = sorted(set(holding) - set(shared))
        for old, paid in zip(shared, private, strict=True):
            disjoint[old].add(paid)
            color[paid] = old
    for holding in grown[n:]:
        paid = sorted(b for b in holding if b in color)
        fresh = sorted(set(holding) - set(paid))
        assert len(paid) == len(fresh) == 2
        for b, f in zip(paid, fresh, strict=True):
            disjoint[color[b]].add(f)
    words = [bits(s) for s in disjoint]
    old_set = (1 << n) - 1
    assert sum(map(len, disjoint)) == len(set.union(*disjoint)) == 5 * n
    for w in words:
        assert (w & old_set).bit_count() == 1
        assert all((w & bits(h)).bit_count() % 2 == 0 for h in grown)
    return words


def growth_checks(holdings, new_holdings, old_set):
    prior = [bits(h) for h in holdings]
    rows = [bits(h) for h in new_holdings]
    full_mask = bits(sorted(set().union(*map(set, new_holdings))))
    old_mask = bits(sorted(set().union(*map(set, holdings))))
    fresh_mask = full_mask ^ old_mask
    old_rank = len(basis(prior))
    rank = len(basis(rows))
    assert rank - old_rank == len(basis(row & fresh_mask for row in rows))
    assert all((row & old_set).bit_count() % 2 == 0 for row in rows)
    assert old_set.bit_count() % 2 == 1
    assert not reveals(rows, old_set, full_mask ^ old_set)
    detecting = sum(reveals(rows, old_set, row) for row in rows)
    singles = sum(reveals(rows, old_set, 1 << b) for b in names(full_mask))
    # Projection on a holding supplies just its own parity equation.
    for holding, row in zip(new_holdings, rows):
        assert rank - len(basis(check & ~row for check in rows)) == 1
        assert len(set(holding)) == len(holding)
    return {
        "holdings": len(rows), "marks": full_mask.bit_count(), "allowed_dimension": full_mask.bit_count() - rank,
        "extensions_per_previous_word": 1 << (fresh_mask.bit_count() - rank + old_rank),
        "detecting_singletons": singles, "detecting_single_holdings": detecting,
        "all_marks_outside_original_shared_set_jointly_blind": True,
    }


def conjugate_control():
    """Quantum benchmark only, on normalized uniform even/odd class states.

    Ignoring a common normalization, the input coordinates are 1 and +/-i.
    The benchmark observable first assigns the parity sign, exchanges the
    classes by the lawful full toggle, and multiplies amplitudes by i.
    """
    results = []
    for arm in (1, -1):
        amplitudes = (1, arm * 1j)
        after = (-1j * amplitudes[1], 1j * amplitudes[0])
        assert tuple(arm * a for a in amplitudes) == after
        assert all(abs(a) == 1 for a in amplitudes)
        results.append({"relative_imaginary_sign": arm, "fixed_ordinary_parity_plus": "1/2",
                        "supplied_quantum_observable_eigenvalue": arm})
    return results


def run_size(n, advance):
    original = source(n)
    pulse_before, old_moves = native_menus(original)
    growth, grown = advance(original, "parity")
    assert growth["status"] == "grown" and growth["births"] == n
    assert all(child["fresh"] == 2 and child["parents"] == 2 for child in growth["new"])
    old_set = (1 << n) - 1
    rows = list(map(bits, grown))
    counts = Counter(b for h in grown for b in h)
    closed = [set(h) for h in grown if all(counts[b] == 2 for b in h)]
    recovered = bits(b for b in counts if counts[b] == 2 and sum(b in h for h in closed) == 2)
    assert recovered == old_set
    pulse_after, moves = native_menus(grown)
    for b in range(n):
        assert all((mask & old_set).bit_count() % 2 == 1 for mask in pulse_before[b])
        assert all((mask & old_set).bit_count() % 2 == 0 for mask in pulse_after[b])
    assert all((mask & old_set).bit_count() % 2 == 0 for mask in moves)
    dimensions = 5 * n - len(basis(rows)), len(basis(moves))
    assert dimensions == (3 * n, 3 * n - 1)
    odd_words = certificate(n, original, grown)
    weights = mask_counts(rows, old_set)
    assert min(weights) == n
    # Each holder meets at most two of the disjoint odd words. A minimal
    # old-holder cover reads the entire designated set.
    assert all(sum(bool(h & w) for w in odd_words) <= 2 for h in rows)
    holders_needed = (n + 1) // 2
    assert any(all(any(row >> b & 1 for row in subset) for b in range(n))
               for subset in combinations(rows[:n], holders_needed))

    before = pulse_before[0]
    after = pulse_after[0]
    neighbor = 1
    p_early = Fraction(sum(w >> neighbor & 1 for w in before), len(before))
    p_late = Fraction(sum(w >> neighbor & 1 for w in after), len(after))
    # Uniformly choose a shortest move every tick and toss an independent
    # fair coin to apply it. A single-bit sign expectation decays by this
    # multiplier. A nonzero difference survives any finite number of ticks.
    attenuation = 1 - Fraction(sum(w >> neighbor & 1 for w in moves), len(moves))
    assert p_early == 0 and p_late > 0 and 0 < attenuation < 1
    any_negative = Fraction(sum((w & old_set).bit_count() % 2 for w in old_moves), len(old_moves))
    assert any_negative == Fraction(4, 5)

    data = {
        "source_knots": n, "source_marks": 3 * n, "source_states": 1 << (3 * n - len(basis(map(bits, original)))),
        "source_shortest_moves": len(old_moves), "grown_shortest_moves": len(moves),
        "all_addresses_checked": n, "sign_early_late": [-1, 1],
        "dimension_allowed_and_mixed": dimensions, "states_per_preparation": 1 << dimensions[1],
        "minimum_detecting_marks": min(weights), "minimum_mark_parity_read_count": weights[n],
        "minimum_detecting_whole_holdings": holders_needed, "disjoint_odd_supports": list(map(names, odd_words)),
        "unmixed_one_probability_on_neighbor_early_late": [str(p_early), str(p_late)],
        "per_tick_multiplier_of_that_difference_under_lazy_walk": str(attenuation),
        "unaddressed_early_negative_probability": str(any_negative),
        "conjugate_phase_benchmark": conjugate_control(),
        "growth_stages": [growth_checks(original, grown, old_set)],
    }
    current = grown
    for _ in range(2):
        event, later = advance(current, "parity")
        if later is None or len(later) > 150:
            data["growth_stop"] = event["status"] if later is None else "150-holder cap"
            break
        data["growth_stages"].append(growth_checks(current, later, old_set))
        current = later
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, choices=(5, 7), nargs="+", default=[5, 7])
    args = parser.parse_args()
    family, = GROWTH_SOURCE.glob("*-E001_*")
    sys.path.insert(0, str(family))
    from ordinary import advance

    print(json.dumps([run_size(n, advance) for n in args.size], indent=2))


if __name__ == "__main__":
    main()
