"""Affine-geometry cover obstructions for the 21-unit scalar-DAG lower bound (F2^6)."""

import json
from collections import Counter, defaultdict
from itertools import combinations


FULL = (1 << 64) - 1
STANDARD_LAGRANGIAN = (1 << 8) - 1  # b=0 for words (a_0,a_1,a_2,b_0,b_1,b_2).


def require(ok, why):
    if not ok:
        raise ValueError(why)


def points(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def packed(values):
    return sum(1 << v for v in values)


def polar(x, y):
    return (((x & 7) & (y >> 3)) ^ ((y & 7) & (x >> 3))).bit_count() & 1


def translate(set_, delta):
    return packed(x ^ delta for x in points(set_))


def geometry():
    caps, directions = {}, set()
    for a, b in combinations(range(1, 64), 2):
        if (a ^ b) <= b or polar(a, b):
            continue
        isotropic = packed((0, a, b, a ^ b))
        for c in range(4):
            enclosure = packed(x for x in range(64) if (polar(x, a) | (polar(x, b) << 1)) == c)
            if c == 0:
                for x in points(enclosure & ~isotropic):
                    directions.add(isotropic | translate(isotropic, x))
            left = enclosure
            while left:
                hole = translate(isotropic, next(points(left)))
                cap = enclosure ^ hole
                require(cap not in caps and cap.bit_count() == 12, 'duplicate or malformed cap')
                caps[cap] = enclosure, hole
                left &= ~hole
    planes = {translate(direction, x) for direction in directions for x in range(64)}
    require((len(caps), len(directions), len(planes)) == (5040, 135, 1080), 'incomplete geometry')
    return caps, planes


def generators():
    # The first family preserves b=0. Translation preserves the directions;
    # the other operations in the first family are linear symplectic maps.
    stabilizer = [[x ^ (1 << i) for x in range(64)] for i in range(3)]
    stabilizer += [[x ^ (v if polar(x, v) else 0) for x in range(64)] for v in range(1, 8)]
    for i in range(3):
        for j in range(3):
            if i != j:
                stabilizer.append([x ^ (((x >> j) & 1) << i) ^ (((x >> (i + 3)) & 1) << (j + 3))
                                   for x in range(64)])
    general = stabilizer + [[x ^ (1 << j) for x in range(64)] for j in range(3, 6)]
    for i in range(3):
        general.append([x ^ (((1 << i) | (1 << (i + 3))) if ((x ^ (x >> 3)) & (1 << i)) else 0)
                        for x in range(64)])
    for mapping in general:
        require(len(set(mapping)) == 64, 'noninvertible symmetry')
        require(all((mapping[x] ^ mapping[y] ^ mapping[0]) == mapping[x ^ y]
                    and polar(mapping[x] ^ mapping[0], mapping[y] ^ mapping[0]) == polar(x, y)
                    for x in range(64) for y in range(64)), 'mapping is not affine symplectic')
    require(all(packed(f[x] for x in range(8)) == STANDARD_LAGRANGIAN for f in stabilizer),
            'a first-cap symmetry moved the distinguished Lagrangian')
    return stabilizer, general


def orbit(seed, maps):
    seen, todo = {seed}, [seed]
    while todo:
        current = todo.pop()
        entries = tuple(points(current))
        for mapping in maps:
            moved = packed(mapping[x] for x in entries)
            if moved not in seen:
                seen.add(moved)
                todo.append(moved)
    return seen


class Cover:
    def __init__(self, caps):
        self.at = defaultdict(list)
        self.at_three = defaultdict(list)
        self.calls = Counter()
        for cap in sorted(caps):
            values = tuple(points(cap))
            for v in values:
                self.at[v].append(cap)
            for key in combinations(values, 3):
                self.at_three[key].append(cap)

    def possible(self, uncovered, budget):
        self.calls[budget] += 1
        if not uncovered:
            return True
        need = uncovered.bit_count() - 12 * (budget - 1)
        if budget < 1 or need > 12:
            return False
        first = next(points(uncovered))
        if budget == 1:
            keep = self.at[first]
            if uncovered.bit_count() >= 3:
                seq = points(uncovered)
                keep = self.at_three[next(seq), next(seq), next(seq)]
            return any(not (uncovered & ~cap) for cap in keep)
        # A successful cover has a member containing the first missing point;
        # its gain must leave at most 12*(budget-1) points for the others.
        return any((uncovered & cap).bit_count() >= need and self.possible(uncovered & ~cap, budget - 1)
                   for cap in self.at[first])


def six_positive_caps():
    # Original predecessor's six directly terminal guards, in independent pair coordinates.
    cover = [0] * 6
    for x in range(64):
        a0, a1, a2, b0, b1, _ = (x >> j & 1 for j in range(6))
        z = (a0 & b0) ^ (a1 & b1)
        for j, allowed in enumerate((b0 == b1 and not z, b0 == 1 and z == a0, b1 == 1 and z == a1)):
            if allowed:
                cover[3 * a2 + j] |= 1 << x
    return cover


def verify():
    caps, lagrangians = geometry()
    stabilize, general = generators()
    require(orbit(STANDARD_LAGRANGIAN, general) == lagrangians, 'missed a distinguished Lagrangian')
    require(orbit(min(caps), general) == set(caps), 'missed a distinguished cap')
    disjoint = {cap for cap in caps if not cap & STANDARD_LAGRANGIAN}
    shapes = Counter((cap & STANDARD_LAGRANGIAN).bit_count() for cap in caps)
    require(shapes == {0: 756, 1: 1792, 2: 2128, 4: 350, 8: 14}, 'unexpected overlap counts')
    search = Cover(caps)
    roster = []
    while disjoint:
        seed = min(disjoint)
        equivalent = orbit(seed, stabilize)
        require(equivalent <= disjoint, 'invalid first-cap orbit')
        search.calls.clear()
        require(not search.possible(FULL & ~STANDARD_LAGRANGIAN & ~seed, 4),
                'five caps and a Lagrangian actually cover')
        roster.append({'seed': seed, 'orbit_size': len(equivalent),
                       'calls_by_remaining_budgets_1_to_4': [search.calls[i] for i in range(1, 5)]})
        disjoint -= equivalent
    require([r['orbit_size'] for r in roster] == [84, 672], 'first-cap orbits incomplete')
    witness = six_positive_caps()
    require(len(set(witness)) == 6 and set(witness) <= caps.keys(), 'positive controls are not distinct caps')
    union = 0
    for row in witness:
        union |= row
    require(union == FULL and Cover(witness).possible(FULL, 6), 'failed to accept genuine six-cap cover')
    # With two caps and five Lagrangians the source-mass equality demands a
    # partition. A Lagrangian disjoint from a cap cannot visit the cap's hole.
    anchor = min(caps)
    enclosure, hole = caps[anchor]
    require(all(not (plane & enclosure) for plane in lagrangians if not plane & anchor),
            'a disjoint Lagrangian enters the missing four-coset')
    mutual = [cap for cap, (_, other_hole) in caps.items()
              if not (anchor & cap) and not (hole & ~cap) and not (other_hole & ~anchor)]
    require(not mutual, 'two disjoint caps cover both omitted four-cosets')
    return {'status': 'passed', 'maximal_caps': len(caps), 'lagrangian_cosets': len(lagrangians),
            'stabilizer_generators': len(stabilize), 'general_generators': len(general),
            'disjoint_first_cap_orbits': roster, 'one_lagrangian_plus_five_caps_covers': False,
            'six_cap_positive_witness': witness, 'two_cap_five_lagrangian_partition': False,
            'disjoint_second_caps_covering_both_holes': len(mutual)}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
