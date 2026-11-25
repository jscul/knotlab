"""Independent decision of a conditional product on two complete holder records."""

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import product
from math import prod


MAX_COMPRESSED_PAIRS = 1 << 14


def packed(places):
    return sum(1 << place for place in places)


def binary_basis(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return basis


def eliminate_hidden(rows, visible):
    """Return the row combinations whose hidden columns all cancel."""
    outside = ~visible
    eliminated = {}
    conditions = []
    for row in rows:
        while hidden := row & outside:
            pivot = hidden.bit_length() - 1
            previous = eliminated.get(pivot)
            if previous is None:
                eliminated[pivot] = row
                break
            row ^= previous
        else:
            if row:
                conditions.append(row)
    return tuple(binary_basis(conditions).values())


@dataclass(frozen=True)
class Roles:
    a: frozenset
    b: frozenset
    c: int
    extra: frozenset


class Stage:
    def __init__(self, supports):
        rows = tuple(frozenset(row) for row in supports)
        if any(len(row) != len(support) for row, support in zip(rows, supports, strict=True)):
            raise ValueError('physical places of a row must be distinct')
        self.rows = rows
        self.parity = tuple(packed(row) for row in rows)
        holders = defaultdict(list)
        for index, row in enumerate(rows):
            for place in row:
                holders[place].append(index)
        self.holders = dict(sorted(holders.items()))
        self.peel_cache = {}

    def roles(self, u, v, c):
        if not 0 <= u < v < len(self.rows):
            raise ValueError('expected ordered distinct physical holders')
        supports = self.rows[u], self.rows[v]
        if any(c not in side for side in supports):
            raise ValueError('contact is not a single place shared by both holders')
        x, y = supports
        return Roles(x - y, y - x, c, (x & y) - {c})

    def peel(self, u, v):
        """Remove a row at any place whose other rows have already been removed."""
        if (u, v) in self.peel_cache:
            return self.peel_cache[u, v]
        n = len(self.rows)
        active = [True] * n
        counts = {place: len(holders) for place, holders in self.holders.items()}
        pending = deque(place for place, count in counts.items() if count == 1)
        while pending:
            place = pending.popleft()
            if counts[place] != 1:
                continue
            holder = next(index for index in self.holders[place] if active[index])
            if holder in (u, v) or len(self.rows[holder]) < 2:
                continue
            active[holder] = False
            for dependency in sorted(self.rows[holder]):
                counts[dependency] -= 1
                if counts[dependency] == 1:
                    pending.append(dependency)
        core = tuple(index for index, present in enumerate(active) if present)
        self.peel_cache[u, v] = core
        return core


def verdict(product_holds, a_proper, b_proper, *, method, core_size, roles,
            coherent=True, c_open=True, **details):
    complete = all(value is not None for value in (product_holds, a_proper, b_proper))
    if not complete:
        outcome = 'undecided'
    elif not coherent:
        outcome = 'incoherent'
    elif not roles.a or not roles.b:
        outcome = 'empty-arm'
    else:
        outcome = ''.join(str(int(value)) for value in (product_holds, a_proper, b_proper))
    return {'outcome': outcome, 'product': product_holds, 'proper_a': a_proper,
            'proper_b': b_proper, 'coherent': coherent, 'c_open': c_open, 'method': method,
            'core_rows': core_size, 'a_width': len(roles.a), 'b_width': len(roles.b),
            'extra_shared_width': len(roles.extra), **details}


def parity(stage, core, roles):
    a, b, c = packed(roles.a), packed(roles.b), 1 << roles.c
    visible = a | b | c
    equations = eliminate_hidden((stage.parity[index] for index in core), visible)
    full_rank = len(equations)

    def dimension(target):
        remaining_rank = len(binary_basis(row & ~target for row in equations))
        return target.bit_count() - full_rank + remaining_rank

    dimensions = {key: dimension(mask) for key, mask in (
        ('a', a), ('b', b), ('c', c), ('ac', a | c), ('bc', b | c), ('abc', visible))}
    dc = dimensions['c']
    agree = dimensions['abc'] == dimensions['ac'] + dimensions['bc'] - dc
    proper_a = dimensions['ac'] < dimensions['a'] + dc
    proper_b = dimensions['bc'] < dimensions['b'] + dc
    return verdict(agree, proper_a, proper_b, method='hidden_column_elimination',
                   core_size=len(core), roles=roles, c_open=bool(dc), dimensions=dimensions)


def nae_clauses(rows):
    for row in rows:
        atoms = [place + 1 for place in sorted(row)]
        yield atoms
        yield [-atom for atom in atoms]


def fixed_colouring(stage, core, u, v, roles):
    """Look for one hidden assignment that works for all visible records at c=0."""
    from pysat.solvers import Glucose4

    free_roles = roles.a | roles.b
    conditions = []
    fixed_requirements = []
    for index in core:
        if index in (u, v):
            continue
        hidden = sorted(stage.rows[index] - free_roles - {roles.c})
        if not hidden:
            return False
        has_c = roles.c in stage.rows[index]
        atoms = [place + 1 for place in hidden]
        conditions.append(atoms)
        if not has_c:
            conditions.append([-atom for atom in atoms])
        fixed_requirements.append((atoms, has_c))
    if roles.extra:
        conditions.append([place + 1 for place in sorted(roles.extra)])

    with Glucose4(bootstrap_with=conditions) as solver:
        if not solver.solve():
            return False
        positive = {atom for atom in (solver.get_model() or ()) if atom > 0}
    for atoms, has_c in fixed_requirements:
        if not (any(atom in positive for atom in atoms)
                and (has_c or any(atom not in positive for atom in atoms))):
            raise ValueError('solver gave an invalid fixed colouring')
    if roles.extra and not any(place + 1 in positive for place in roles.extra):
        raise ValueError('fixed colouring did not satisfy the extra shared place condition')
    return True


def nae_holders(core, roles, method):
    if roles.extra:
        return verdict(True, False, False, method=method, core_size=len(core), roles=roles)
    if not roles.a or not roles.b:
        return verdict(None, None, None, method='requires_singleton_check',
                       core_size=len(core), roles=roles, coherent=None, c_open=None)
    return verdict(True, True, True, method=method, core_size=len(core), roles=roles)


def role_profiles(visible, incidence):
    classes = defaultdict(list)
    for place in sorted(visible):
        classes[tuple(incidence[place])].append(place + 1)
    profiles = []
    for atoms in classes.values():
        choices = [tuple(-atom for atom in atoms), tuple(atoms)]
        if len(atoms) >= 2:
            choices.append((atoms[0], *(-atom for atom in atoms[1:])))
        profiles.append(choices)
    return profiles


def profile_assignments(profiles):
    for code in product(*(range(len(profile)) for profile in profiles)):
        yield code, tuple(lit for i, value in enumerate(code) for lit in profiles[i][value])


def flipped(records):
    return {tuple(value if value == 2 else 1 - value for value in record) for record in records}


def exhaustive_nae(stage, core, roles, limit=MAX_COMPRESSED_PAIRS):
    """Check every remaining distinguishable pattern of the two private records."""
    from pysat.solvers import Glucose4

    incidence = defaultdict(list)
    for index in core:
        for place in stage.rows[index]:
            incidence[place].append(index)
    ap = role_profiles(roles.a, incidence)
    bp = role_profiles(roles.b, incidence)
    work = prod(map(len, ap + bp))
    size = len(core)
    if work > limit:
        return verdict(None, None, None, method='compressed_assignment_limit',
                       core_size=size, roles=roles, coherent=None, c_open=None, compressed_pairs=work)
    ar = list(profile_assignments(ap))
    br = list(profile_assignments(bp))
    allowed_a = set()
    allowed_b = set()
    allowed_pairs = 0
    with Glucose4(bootstrap_with=nae_clauses(stage.rows[index] for index in core)) as solver:
        for a, fixed_a in ar:
            for b, fixed_b in br:
                if solver.solve(assumptions=[-(roles.c + 1), *fixed_a, *fixed_b]):
                    allowed_a.add(a)
                    allowed_b.add(b)
                    allowed_pairs += 1
    return verdict(allowed_pairs == len(allowed_a) * len(allowed_b),
                   allowed_a != flipped(allowed_a), allowed_b != flipped(allowed_b),
                   method='exact_incidence_profile_sat', core_size=size, roles=roles,
                   coherent=bool(allowed_pairs), c_open=bool(allowed_pairs), compressed_pairs=work,
                   allowed_compressed_pairs=allowed_pairs)


def classify(stage, law, u, v, c):
    roles = stage.roles(u, v, c)
    core = stage.peel(u, v)
    if law == 'parity':
        return parity(stage, core, roles)
    if law != 'nae':
        raise ValueError(f'unknown knot law: {law}')
    if len(core) == 2 and (roles.extra or roles.a and roles.b):
        return nae_holders(core, roles, 'two_holder_reverse_extension')
    if (roles.extra or roles.a and roles.b) and fixed_colouring(stage, core, u, v, roles):
        return nae_holders(core, roles, 'fixed_hidden_colouring')
    return exhaustive_nae(stage, core, roles)
