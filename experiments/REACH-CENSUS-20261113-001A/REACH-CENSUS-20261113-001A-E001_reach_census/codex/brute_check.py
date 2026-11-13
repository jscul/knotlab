"""Independent G3 checker for the REACH-CENSUS frozen first/last ray.

This module imports only the description-language/limit-state reference, never
ray DP code. ``defs`` arguments are the original (not necessarily usualised)
family; ``ray_cnf`` applies LS.usual before computing its limit. Distinction
identifiers are zero-based, and CNF literals are the corresponding signed
one-based identifiers. All own distinctions are retained, including unused ones.

``ray_cnf`` has BD's four-result interface: clauses, n, top ports, created per
copy. Set ``return_metadata=True`` for a fifth, JSON-friendly metadata result.
``brute`` returns a JSON-friendly record, with an explicit bounded-search status
rather than interpreting a missing witness as absence at every size.
"""

from array import array
from collections import namedtuple
from functools import lru_cache
import importlib.util
import itertools
import os
from pathlib import Path
import time

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
import numpy as np
from pysat.solvers import Solver


_ROOT = Path(__file__).resolve().parents[4]
_LS_PATH = (_ROOT / "experiments/LIMIT-STATE-20261112-001A/"
            "LIMIT-STATE-20261112-001A-E001_limit_states/census.py")
_spec = importlib.util.spec_from_file_location("_reach_brute_limit_state", _LS_PATH)
LS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LS)
L = LS.L

# ``self_call`` distinguishes an actual SELF from a call to an earlier
# self-holding definition. It survives flattening for the frozen ray convention.
FlatCall = namedtuple("FlatCall", "target args self_call")
FlatBody = namedtuple("FlatBody", "index k own calls")


class RaySelectionError(ValueError):
    """The frozen ray is undefined for this family (the S2 settled case)."""


def _self_holding(defs):
    return {i for i, (_, _, calls) in enumerate(defs)
            if any(target == "SELF" for target, _ in calls)}


def flat_body(defs, index=None):
    """Independently inline every non-self-holding callee, depth first.

    Ports come first, then the root's locals, followed by fresh callee locals in
    call order. The returned calls are K or integer-target self-holding calls.
    ``own`` counts every non-port distinction, whether used in a call or not.
    """
    if not defs:
        raise ValueError("a family must contain at least one definition")
    index = len(defs) - 1 if index is None else index
    if not 0 <= index < len(defs):
        raise ValueError("definition index is outside the family")
    selfs = _self_holding(defs)
    k = defs[index][0]
    next_var = k
    out = []

    def inline(i, actual):
        nonlocal next_var
        arity, local_count, calls = defs[i]
        if len(actual) != arity or local_count < 0:
            raise ValueError("definition arity or own-distinction count is invalid")
        env = list(actual) + list(range(next_var, next_var + local_count))
        next_var += local_count
        for target, arguments in calls:
            if any(a < 0 or a >= len(env) for a in arguments):
                raise ValueError("call argument is outside its definition")
            args = tuple(env[a] for a in arguments)
            if target == "K":
                if len(args) != 3:
                    raise ValueError("K requires three arguments")
                out.append(FlatCall("K", args, False))
            elif target == "SELF":
                if arity != 3 or len(args) != 3:
                    raise ValueError("SELF requires a three-port definition")
                out.append(FlatCall(i, args, True))
            else:
                if not isinstance(target, int) or not 0 <= target < i:
                    raise ValueError("a callee must be an earlier definition")
                if len(args) != defs[target][0]:
                    raise ValueError("callee argument count does not match its ports")
                if target in selfs:
                    out.append(FlatCall(target, args, False))
                else:
                    inline(target, args)

    inline(index, tuple(range(k)))
    return FlatBody(index, k, next_var - k, tuple(out))


def _selection(defs, ray):
    if ray not in ("first", "last"):
        raise ValueError("ray must be 'first' or 'last'")
    main = len(defs) - 1
    body_main = flat_body(defs, main)
    selfs = _self_holding(defs)
    if main in selfs:
        source = main
    else:
        # S is fixed by the first call even when the last-call ray is requested.
        source = next((c.target for c in body_main.calls if c.target != "K"), None)
        if source is None:
            raise RaySelectionError("main's flat body has no self-holding call")
    body_s = body_main if source == main else flat_body(defs, source)
    if source == main:
        entries = [j for j, c in enumerate(body_main.calls) if c.self_call]
    else:
        entries = [j for j, c in enumerate(body_main.calls) if c.target == source]
    rays = [j for j, c in enumerate(body_s.calls) if c.self_call]
    if not entries or not rays or body_s.k != 3:
        raise RaySelectionError("the selected S has no three-port SELF ray")
    pick = 0 if ray == "first" else -1
    return body_main, body_s, entries[pick], rays[pick]


def ray_metadata(defs, ray="first"):
    """Return ray selection and size data without computing a limit or a DP."""
    body_main, body_s, entry, onward = _selection(defs, ray)
    return dict(
        ray=ray,
        main_index=body_main.index,
        S_index=body_s.index,
        main_ports=body_main.k,
        main_own=body_main.own,
        S_own=body_s.own,
        main_size=body_main.k + body_main.own,
        S_size=body_s.k + body_s.own,
        entry_call=entry,
        ray_call=onward,
        entry_args=list(body_main.calls[entry].args),
        ray_args=list(body_s.calls[onward].args),
    )


def ray_size(defs, s, ray="first"):
    """Number of distinctions in C_0,...,C_s, including all unused ones."""
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be an integer at least one")
    m = ray_metadata(defs, ray)
    return m["main_size"] + s * m["S_own"]


def admissible_depths(defs, max_variables=22, max_depth=10, ray="first"):
    """Frozen G3 depths: 1 through the largest allowed depth, at most ten."""
    m = ray_metadata(defs, ray)
    if m["S_own"]:
        end = min(max_depth, (max_variables - m["main_size"]) // m["S_own"])
    else:
        end = max_depth if m["main_size"] <= max_variables else 0
    return list(range(1, max(0, end) + 1))


def _relation_clauses(arguments, relation):
    """Independently forbid each excluded argument state; bit j is arg j."""
    if len(relation) != 1 << len(arguments):
        raise ValueError("relation arity does not match the call")
    return [[-(v + 1) if (state >> j) & 1 else v + 1
             for j, v in enumerate(arguments)]
            for state, allowed in enumerate(relation) if not allowed]


def ray_cnf(defs, s, ray="first", *, return_metadata=False):
    """CNF on all ray distinctions, with independent flattening/selection.

    The selected outgoing call is expanded into the next copy. Every side call
    and the selected call of C_s is constrained by its target's usual limit G.
    """
    if not isinstance(s, int) or s < 1:
        raise ValueError("s must be an integer at least one")
    usual_defs, _ = LS.usual(defs)
    _, _, limit = L.depth_sequence(usual_defs, L.TOP)
    body_main, body_s, entry, onward = _selection(usual_defs, ray)
    clauses = []
    next_var = body_main.k
    top = list(range(body_main.k))
    ports = top
    created = []
    copy_ports = []
    outgoing_arguments = []
    for depth in range(s + 1):
        body = body_main if depth == 0 else body_s
        selected = entry if depth == 0 else onward
        own = list(range(next_var, next_var + body.own))
        next_var += body.own
        env = list(ports) + own
        created.append((list(top) if depth == 0 else []) + own)
        copy_ports.append(list(ports))
        outgoing = None
        for j, call in enumerate(body.calls):
            args = tuple(env[a] for a in call.args)
            if call.target == "K":
                clauses.append([v + 1 for v in args])
                clauses.append([-(v + 1) for v in args])
            elif j == selected and depth < s:
                outgoing = list(args)
            else:
                clauses.extend(_relation_clauses(args, limit[call.target]))
        if depth < s:
            if outgoing is None:
                raise RaySelectionError("selected call was not found in a ray copy")
            ports = outgoing
            outgoing_arguments.append(list(outgoing))
    result = (clauses, next_var, top, created)
    if return_metadata:
        metadata = ray_metadata(usual_defs, ray)
        metadata.update(s=s, n=next_var, deepest_own=list(created[-1]),
                        copy_ports=copy_ports, outgoing_args=outgoing_arguments,
                        limit={str(i): [bool(x) for x in r] for i, r in limit.items()})
        return (*result, metadata)
    return result


def _enumerate_models(clauses, n, solver_name, partition_variables=12):
    """Enumerate all n-bit solutions using SAT, without accumulating huge CNFs.

    Only distinctions occurring in clauses need SAT decisions. Unused ones are
    explicitly expanded as free choices afterwards. Fixed-prefix partitions
    retain at most 2**partition_variables model-blocking clauses in any solver;
    every full active assignment belongs to exactly one partition.
    """
    if partition_variables < 1:
        raise ValueError("partition_variables must be positive")
    active = sorted({abs(lit) - 1 for clause in clauses for lit in clause})
    if any(v < 0 or v >= n for v in active):
        raise ValueError("CNF contains a distinction outside its declared range")
    inactive = sorted(set(range(n)) - set(active))
    prefix_count = max(0, len(active) - partition_variables)
    prefix, suffix = active[:prefix_count], active[prefix_count:]
    rows = array("I")
    for fixed in range(1 << prefix_count):
        assumptions = [(v + 1) if (fixed >> j) & 1 else -(v + 1)
                       for j, v in enumerate(prefix)]
        with Solver(name=solver_name, bootstrap_with=clauses) as solver:
            while solver.solve(assumptions=assumptions):
                model = solver.get_model()
                true = {lit - 1 for lit in model if lit > 0}
                rows.append(sum(1 << v for v in active if v in true))
                # Prefix is fixed for this solver, so only suffix bits need
                # blocking. An empty suffix blocks its one possible model.
                solver.add_clause([-(v + 1) if v in true else v + 1 for v in suffix])
    active_count = len(rows)
    base = np.frombuffer(rows, dtype=np.uint32)
    if not active_count:
        return base, 0
    if not inactive:
        return base, active_count
    free = np.zeros(1 << len(inactive), dtype=np.uint32)
    numbers = np.arange(len(free), dtype=np.uint32)
    for j, v in enumerate(inactive):
        free |= ((numbers >> j) & 1) << v
    return (base[:, None] | free[None, :]).reshape(-1), active_count


def brute(defs, s, max_size=7, *, ray="first", max_variables=22,
          solver_name="cadical153", partition_variables=12):
    """Least endpoint-spanning minimal constrained projection, through size 7.

    No DP result is used. All satisfying assignments are enumerated first;
    projections are then computed directly from their bit patterns. A witness
    W is accepted exactly when its projection is constrained and every single
    deletion has full projection. ``none up to 7`` is a bounded search result.
    """
    started = time.perf_counter()
    if not isinstance(max_size, int) or not 1 <= max_size <= 7:
        raise ValueError("max_size must be an integer from one through seven")
    n = ray_size(defs, s, ray)
    base = dict(s=s, ray=ray, n=n, max_size=max_size, least_size=None, witness=None)
    if n > max_variables:
        base.update(status="skipped", reason=f"ray distinctions exceed {max_variables}",
                    seconds=time.perf_counter() - started)
        return base
    if n > 22:
        raise ValueError("independent G3 enumeration supports at most 22 distinctions")
    clauses, n, top, created, metadata = ray_cnf(defs, s, ray, return_metadata=True)
    built = time.perf_counter()
    models, active_count = _enumerate_models(clauses, n, solver_name, partition_variables)
    enumerated = time.perf_counter()
    base.update(model_count=len(models), sat_active_model_count=active_count,
                clauses=len(clauses), top=top, deepest_own=created[-1],
                metadata=metadata, build_seconds=built - started,
                enumeration_seconds=enumerated - built)
    if not len(models):
        base.update(status="dead", projection_checks=0, search_seconds=0.0,
                    seconds=time.perf_counter() - started)
        return base
    # Uniformly spaced small subsets establish full projections cheaply in
    # most cases. A non-full sample is always followed by the entire model set;
    # sampling can therefore never certify a constrained projection.
    samples = {}

    def sample_for(size):
        count = min(len(models), max(64, 8 * (1 << size)))
        if count not in samples:
            samples[count] = models[np.linspace(0, len(models) - 1, count, dtype=np.int64)]
        return samples[count]

    def full_on(rows, W):
        projected = np.zeros(len(rows), dtype=np.uint8)
        for j, w in enumerate(W):
            projected |= (((rows >> w) & 1) << j).astype(np.uint8)
        return bool(np.bincount(projected, minlength=1 << len(W)).all())

    @lru_cache(maxsize=None)
    def free(W):
        if len(models) < 1 << len(W):
            return False
        sample = sample_for(len(W))
        if full_on(sample, W):
            return True
        return full_on(models, W)

    top_set, last_set = set(top), set(created[-1])
    found = None
    for size in range(2, min(max_size, n) + 1):
        for W in itertools.combinations(range(n), size):
            if not top_set.intersection(W) or not last_set.intersection(W):
                continue
            if free(W):
                continue
            if all(free(W[:j] + W[j + 1:]) for j in range(size)):
                found = W
                break
        if found is not None:
            break
    ended = time.perf_counter()
    base.update(status="found" if found is not None else f"none up to {max_size}",
                least_size=len(found) if found is not None else None,
                witness=list(found) if found is not None else None,
                projection_checks=free.cache_info().misses,
                search_seconds=ended - enumerated, seconds=ended - started)
    return base
