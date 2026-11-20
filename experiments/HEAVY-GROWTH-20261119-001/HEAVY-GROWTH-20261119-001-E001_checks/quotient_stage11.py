"""Probe the actual 58,894-child roster of start-11 by exact incidence queries."""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from heapq import heappush, heapreplace
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random
import subprocess
from tempfile import TemporaryDirectory

from quotient_next import HERE, OUTPUT, Quotient, Roster, bits, held_on_quotient, invert, load, touching, trace


class Children:
    def __init__(self, groups, n):
        self.groups = groups
        self.block = invert(n, groups)
        self.full = (1 << len(groups)) - 1
        self.avoid_block = [self.full ^ block for block in self.block]
        self.parent_universe = (1 << n) - 1

    def nonneighbors(self, i, target=None):
        remaining = self.full if target is None else target
        for p in bits(self.groups[i]):
            remaining &= self.avoid_block[p]
            if not remaining:
                break
        return remaining

    @lru_cache(maxsize=512)
    def closed_neighbors(self, i):
        return self.full ^ self.nonneighbors(i)

    def kept_universals(self, preferred, cap):
        intersection = self.parent_universe
        witnesses = []
        tested = 0
        for i in preferred:
            new = intersection & self.groups[i]
            if witnesses and new == intersection:
                continue
            tested += 1
            if not self.nonneighbors(i):
                witnesses.append(i)
                intersection = new
            if tested == cap:
                break
        return witnesses, intersection, tested

    def exhaustive_universal_test(self, cap):
        possible = self.full
        found = []
        intersection = self.parent_universe
        tested = 0
        while possible and tested < cap:
            i = next(bits(possible))
            misses = self.nonneighbors(i)
            tested += 1
            if misses:
                # A particular disjoint child rules out all candidates that miss it.
                other = next(bits(misses))
                possible &= self.closed_neighbors(other)
            else:
                if not found or intersection & self.groups[i] != intersection:
                    found.append(i)
                    intersection &= self.groups[i]
                possible ^= 1 << i
                if not intersection:
                    break
        return found, intersection, tested, possible.bit_count()

    def block_extensions(self, possible, preferred, per_block_cap):
        extensions, unresolved = {}, []
        for p in bits(possible):
            block = self.block[p]
            if not block:
                continue
            rejected = 0
            for i in preferred:
                if self.groups[i] >> p & 1:
                    continue
                if not self.nonneighbors(i, target=block):
                    extensions[p] = i
                    break
                rejected += 1
                if rejected == per_block_cap:
                    break
            if p not in extensions:
                unresolved.append(p)
        return extensions, unresolved

    def exact_block_extension(self, atom, order):
        held = self.block[atom]
        extensions = self.full ^ held
        cuts = []
        for i in order:
            if not held >> i & 1:
                continue
            after = extensions ^ self.nonneighbors(i, extensions)
            if after != extensions:
                cuts.append(i)
                extensions = after
                if not extensions:
                    return None, cuts
        return next(bits(extensions)), cuts

    def residuals_in_only_held_block(self, atom, budget):
        inside = self.block[atom]
        outside = list(bits(self.full ^ inside))
        assert outside
        outside_columns = invert(len(self.block), [self.groups[j] for j in outside])
        profiles = defaultdict(list)
        for i in bits(inside):
            patterns = touching(self.groups[i], outside_columns)
            profiles[patterns].append(i)

        total = 0
        examined = 0
        first, disjoint = None, None
        codes = sorted(profiles, key=int.bit_count)

        def add(code, other):
            nonlocal first, disjoint, total
            left, right = profiles[code], profiles[other]
            if code == other:
                count = comb(len(left),2)
                if count == 0:
                    return
                sample = tuple(left[:2])
            else:
                count = len(left) * len(right)
                sample = (left[0],right[0])
            total += count
            if first is None:
                first = sample
            avoid = set(first)
            if code == other:
                representatives = [i for i in left[:4] if i not in avoid][:2]
            else:
                representatives = [next((i for i in part[:3] if i not in avoid),None) for part in (left,right)]
            if len(representatives) == 2 and None not in representatives:
                disjoint = [first,representatives]

        if 0 in profiles:
            add(0,0)
        exact = True
        for i, code in enumerate(codes):
            if not exact:
                break
            size = code.bit_count()
            for j in range(i+1,len(codes)):
                other = codes[j]
                if size + other.bit_count() > len(outside):
                    break
                if examined == budget:
                    exact = False
                    break
                examined += 1
                if not code & other:
                    add(code,other)
        return total, exact, disjoint, {"inside_children": inside.bit_count(), "outside_children": len(outside),
                                        "distinct_exterior_profiles": len(profiles), "profile_pairs_examined": examined,
                                        "least_exterior_degree": min(code.bit_count() for code in profiles),
                                        "literal_residual_pair": first}

    def local_residuals_and_seed_pools(self, pool, possible_held, universal_exists):
        covered = 0
        residual = []
        best = []
        common = {i: self.closed_neighbors(i) for i in pool}
        for i, j in combinations(pool, 2):
            shared = self.groups[i] & self.groups[j]
            if not shared:
                continue
            intersection = common[i] & common[j]
            cover = intersection.bit_count()
            if len(best) < 512:
                heappush(best, (-cover, i, j, intersection))
            elif cover < -best[0][0]:
                heapreplace(best, (-cover, i, j, intersection))
            if universal_exists and not shared & possible_held:
                continue
            for p in bits(shared & possible_held):
                if intersection & self.block[p] == intersection:
                    residual.append((i, j, p))
                    break
            covered += 1
        return residual, sorted(best, reverse=True), covered

    def disjoint_descendants(self, residual, best, universal_exists):
        for a, b in combinations(residual, 2):
            if not set(a[:2]) & set(b[:2]):
                return {"type": "two_literal_residual_pairs", "seed_pairs": [a, b]}
        for a, b, p in residual:
            avoid = (1 << a) | (1 << b)
            for _, i, j, allowed in best:
                if not avoid & allowed:
                    return {"type": "literal_residual_and_excluding_seed", "seed_pairs": [[a,b,p], [i,j]]}
        if not universal_exists:
            for a, b in combinations(best, 2):
                if not a[3] & b[3]:
                    return {"type": "two_seeds_with_disjoint_common_candidate_sets", "seed_pairs": [a[1:3], b[1:3]]}
        return None

    def separated_children(self, parent_rows, preferred, limit):
        atom_order = sorted(range(len(parent_rows)), key=lambda v: -self.block[v].bit_count())
        seen = set()
        for i in preferred:
            if len(seen) == limit:
                break
            forbidden = touching(self.groups[i], parent_rows)
            if forbidden == self.parent_universe or forbidden in seen:
                continue
            seen.add(forbidden)
            possible = self.full
            for p in atom_order:
                if forbidden >> p & 1:
                    possible &= ~self.block[p]
                    if not possible:
                        break
            if possible:
                j = next(bits(possible))
                assert not self.groups[j] & forbidden
                gap = 1
                while not self.groups[j] & forbidden:
                    expanded = touching(forbidden, parent_rows)
                    assert expanded != forbidden
                    forbidden = expanded
                    gap += 1
                return (i,j,gap),len(seen)
        return None,len(seen)

    def separate_unheld_seeds(self, pool, limit):
        rng = Random(202611194091)
        stencil = {i: self.closed_neighbors(i) for i in pool}
        trials = sorted(((stencil[a] & stencil[b]).bit_count(),a,b) for a,b in combinations(pool,2)
                        if not self.groups[a] & self.groups[b])
        for _,a,b in trials[:limit]:
            seeds = [[a],[b]]
            common = [self.groups[a], self.groups[b]]
            neighborhoods = [stencil[a],stencil[b]]
            marked = [(1 << a), (1 << b)]
            for _ in range(22):
                shared = neighborhoods[0] & neighborhoods[1]
                if not shared and not any(common):
                    return seeds, len(trials)
                best = None
                for side in (0,1):
                    can = neighborhoods[side] & ~(marked[0] | marked[1])
                    candidates = [i for i in pool if can >> i & 1]
                    for _ in range(8):
                        if can:
                            offset = rng.randrange(len(self.groups))
                            above = can >> offset
                            k = offset + next(bits(above)) if above else next(bits(can))
                            candidates.append(k)
                    for i in candidates:
                        row = stencil[i] if i in stencil else self.closed_neighbors(i)
                        new = common[side] & self.groups[i]
                        key = ((shared & row).bit_count(), new.bit_count()-common[side].bit_count(),
                               (neighborhoods[side] & row).bit_count(), i)
                        if best is None or key < best[0]:
                            best = key,side,i,row,new
                if best is None:
                    break
                _,side,i,row,new = best
                seeds[side].append(i)
                marked[side] |= 1 << i
                neighborhoods[side] &= row
                common[side] = new
        return None, len(trials)

    def incompatibility_components(self):
        components = []
        remaining = self.full
        while remaining:
            i = next(bits(remaining))
            pending = [i]
            remaining ^= 1 << i
            for u in pending:
                if not remaining:
                    break
                more = self.nonneighbors(u, remaining)
                remaining ^= more
                pending.extend(bits(more))
            components.append(pending)
        return sorted(components, key=len, reverse=True)

    def incompatible_packing(self, smallest, trials):
        best = []
        rng = Random(202611194210)
        for first in smallest[:trials]:
            path = [first]
            options = self.nonneighbors(first)
            while options:
                candidate = [next(bits(options))]
                for _ in range(20):
                    offset = rng.randrange(len(self.groups))
                    above = options >> offset
                    candidate.append(offset + next(bits(above)) if above else candidate[0])
                following = [(self.nonneighbors(next_child, options),next_child) for next_child in set(candidate)]
                options, selected = max(following, key=lambda row: (row[0].bit_count(),-row[1]))
                path.append(selected)
            if len(path) > len(best):
                best = path
        assert all(not self.groups[a] & self.groups[b] for a,b in combinations(best,2))
        return best

    def induced_incompatibility_matching(self, connected_part, trials):
        rng = Random(202611194316)
        original = sum(1 << i for i in connected_part)
        best = []

        def sample(pool, length):
            picked = {next(bits(pool))}
            for _ in range(length):
                offset = rng.randrange(len(self.groups))
                above = pool >> offset
                if above:
                    picked.add(offset + next(bits(above)))
            return picked

        for trial in range(trials):
            options = original
            matching = []
            while options:
                greatest = None
                for u in sample(options, 32):
                    outside = self.nonneighbors(u, options)
                    if not outside:
                        continue
                    after_u = options ^ outside
                    for v in sample(outside, 8):
                        after = after_u ^ self.nonneighbors(v, after_u)
                        key = (after.bit_count(), -u, -v)
                        if greatest is None or key > greatest[0]:
                            greatest = key,u,v,after
                if greatest is None:
                    break
                _,u,v,options = greatest
                matching.append((u,v))
            if len(matching) > len(best):
                best = matching
        assert all(not self.groups[a] & self.groups[b] for a,b in best)
        assert all(self.groups[u] & self.groups[v] for left,right in combinations(best,2) for u in left for v in right)
        return best


def controls():
    rim = [3,6,12,9]
    cycle = Children(rim, 4)
    assert cycle.kept_universals(range(4), 10)[0] == []
    residual, best, _ = cycle.local_residuals_and_seed_pools(list(range(4)), 15, False)
    assert len(residual) == 4 and cycle.disjoint_descendants(residual, best, False)
    enlarged = Children(rim + [15], 4)
    universal, possible, _ = enlarged.kept_universals((4,0,1,2,3), 10)
    assert universal == [4] and possible == 15 and enlarged.nonneighbors(4) == 0
    all_meet = Children([3,6,5],3)
    assert all_meet.kept_universals((0,1,2),10)[:2] == ([0,1,2],0)


def score(binary, work, path):
    known = next(r for r in load("quotient_check")["targets"] if r["case"] == "start-11")
    roster = Roster(path, known["blocks_file"]["sha256"])
    q = Quotient(roster.rows, [1 << u for u in range(roster.n)])
    maxima, receipt = trace(binary, work, q, 5_000_000)
    held = held_on_quotient(q, roster.blocks)
    assert receipt["complete"] and len(maxima) == known["counted_candidate_maxima"]
    assert len(held) == known["held_maxima"] and not known["offshoots"] and not known["residual_pairs"]
    legal = [g for g in maxima if g not in held]
    assert len(legal) == known["births"] and len(set(legal)) == len(legal)
    children = Children(legal, q.n)
    preferred = sorted(range(len(legal)), key=lambda i: (-legal[i].bit_count(), i))
    separation, separate_search = children.separated_children(q.rows, reversed(preferred), 12_000)
    universals, possible, checked = children.kept_universals(preferred, 2048)
    universal_remaining = None
    if not universals:
        universals, possible, extra_tested, universal_remaining = children.exhaustive_universal_test(4096)
        checked += extra_tested
    assert all(all(legal[i] & group for group in legal) for i in universals)
    extensions, unresolved = children.block_extensions(possible, preferred, 32) if universals else ({}, list(bits(possible)))
    exact_blocks = {}
    exact_held = None
    exact_residual = None
    physical_residual_witness = None
    if universals and len(unresolved) <= 8:
        exact_held = []
        for atom in unresolved:
            extension,cuts = children.exact_block_extension(atom, reversed(preferred))
            exact_blocks[atom] = {"extension_child": extension, "nonextension_cuts": cuts}
            if extension is None:
                exact_held.append(atom)
            else:
                asserted = legal[extension]
                mark = 1 << atom
                assert not asserted & mark and all(asserted & group for group in legal if group & mark)
                extensions[atom] = extension
        unresolved = exact_held
        if len(exact_held) == 1:
            count, done, proof, info = children.residuals_in_only_held_block(exact_held[0], 15_000_000)
            exact_residual = {"count": count,"complete": done, **info}
            if proof:
                physical_residual_witness = {"type": "two_exact_residual_pairs_in_the_only_held_block",
                                             "age_eight_trace_indices": proof,
                                             "physical_parent_seed_groups": [[hex(q.to_physical(legal[i])) for i in row]
                                                                              for row in proof]}
    empty_residual = exact_residual is not None and exact_residual["complete"] and exact_residual["count"] == 0
    next_complete = bool(universals) and (not unresolved or empty_residual)
    report = {"stage": "start-11-age08", "precursor_sha256": roster.digest, "physical_children": len(legal),
              "precursor_traces": receipt, "universal_candidates_tested": checked,
              "universal_candidates_remaining_after_exact_exclusions": universal_remaining,
              "universal_witness_children": universals, "candidate_held_atoms": list(bits(possible)),
              "candidate_holding_classes_of_physical_age_seven_parents": {
                  p: list(bits(q.members[p])) for p in bits(possible) if universals
              },
              "verified_block_extensions": extensions, "held_atoms_unresolved": unresolved,
              "exact_block_tests": exact_blocks, "exact_held_atoms": exact_held,
              "exact_residual_in_unique_held": exact_residual,
              "separated_support_search_sets": separate_search,
              "separated_actual_children": separation,
              "next_stage_complete_with_whole_block": True if next_complete else None,
              "disjoint_grandchildren": physical_residual_witness}

    if separation:
        i,j,gap = separation
        report["last_noncomplete_from_separation"] = 7+gap
        report["at_least_two_births_through_age"] = 8+gap
        report["separated_actual_children_physical_hex"] = [hex(q.to_physical(legal[u])) for u in (i,j)]

    if next_complete:
        components = children.incompatibility_components()
        sizes = Counter(map(len,components))
        factors = sum(count for size,count in sizes.items() if size >= 2)
        packing = children.incompatible_packing(list(reversed(preferred)), 96)
        matching = children.induced_incompatibility_matching(components[0], 20)
        report.update({"incompatibility_component_size_histogram": dict(sizes),
                       "nontrivial_incompatibility_components": factors,
                       "incompatible_packing_age_eight": packing,
                       "induced_incompatibility_matching_age_eight": matching,
                       "induced_incompatibility_matching_trials": 20,
                       "births_age_nine_lower_bound": max(len(packing),1 << factors,1 << len(matching)),
                       "incompatible_packing_parent_sizes": [q.to_physical(legal[i]).bit_count() for i in packing]})

    if not next_complete and not physical_residual_witness:
        pool = sorted(set(preferred[-128:] + preferred[:40] + preferred[::len(legal)//120]),
                      key=lambda i: (legal[i].bit_count(), i))
        maybe = sum(1 << p for p in unresolved)
        residual, best, tested = children.local_residuals_and_seed_pools(pool, maybe, bool(universals))
        witness = children.disjoint_descendants(residual, best, bool(universals))
        report.update({"pool_size": len(pool), "candidate_seed_pairs": tested,
                       "fresh_residual_pairs_certified": len(residual), "disjoint_grandchildren": witness})
        if not witness and not universals:
            seeds, trials = children.separate_unheld_seeds(pool, 72)
            if seeds:
                common_neighborhoods = []
                for seed in seeds:
                    common, allowed = q.full, children.full
                    for index in seed:
                        common &= legal[index]
                        allowed &= children.closed_neighbors(index)
                    assert not common and all(allowed >> index & 1 for index in seed)
                    common_neighborhoods.append(allowed)
                assert not common_neighborhoods[0] & common_neighborhoods[1]
                report["disjoint_grandchildren"] = {"type": "two_unheld_seeds_with_disjoint_common_neighborhoods",
                                                     "age_eight_trace_indices": seeds,
                                                     "physical_parent_seed_groups": [[hex(q.to_physical(legal[i])) for i in row]
                                                                                      for row in seeds]}
            report["unheld_seed_start_pairs_in_pool"] = trials
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    args = parser.parse_args()
    controls()
    with TemporaryDirectory(prefix="heavy-quotient-stage11-") as tmp:
        work = Path(tmp)
        binary = work / "trace"
        subprocess.run(["c++", "-O3", "-march=native", "-std=c++20", "-Wall", "-Wextra",
                        HERE / "quotient_trace.cpp", "-o", binary], check=True)
        result = score(binary, work, args.input_dir / "start-11-age07.txt")
    (OUTPUT / "quotient_stage11.json").write_text(json.dumps(result, indent=2) + "\n")
    print({k: v for k, v in result.items() if k not in ("candidate_held_atoms", "held_atoms_unresolved", "verified_block_extensions")})


if __name__ == "__main__":
    main()
