"""Replay the guarded-clause reduction and check both per-role occurrence bounds."""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations, product
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Edge:
    # full, off, or a disjunction pad and its signed literal; selector indexes source clauses.
    mode: str
    pad: int = 0
    sign: int = 0
    selector: int = -1
    feedback: bool = False


OFF = Edge("off")
ON = Edge("full")


def clauses_on(n):
    return [tuple(i*s for i, s in zip(names, signs)) for names in combinations(range(1, n+1), 3)
            for signs in product((-1, 1), repeat=3)]


def compile_stages(n, clauses, same_sign=False):
    s, t = "source", "sink"
    disjunctions = []
    for x in range(1, n+1):
        disjunctions.extend([((s, x), (s, -x), -1), ((x, t), (-x, t), -1)])
    disjunctions.extend(((-a, b), (s, c), i) for i, (a, b, c) in enumerate(clauses))
    ports = defaultdict(list)
    for row, (first, second, selector) in enumerate(disjunctions):
        for j, ((u, v), sign) in enumerate(zip((first, second), (1, 1 if same_sign else -1))):
            wire = ("wire", row, j)
            ports[u].append((wire, Edge("half", row, sign, selector), OFF))
            ports[v].append((wire, OFF, ON))
    entry, exit_wire = ("endpoint", 0), ("endpoint", 1)
    ports[s].append((entry, OFF, ON))
    ports[t].append((exit_wire, ON, OFF))
    stages = []
    def stage(top=None, bottom=None):
        i = len(stages)
        if top is None:
            top = (("unused", i, 0), OFF, OFF)
        if bottom is None:
            bottom = (("unused", i, 1), OFF, OFF)
        stages.append((top, bottom))
    stage((entry, ON, OFF))
    signals = {}
    for v in [s,t] + [i*signed for i in range(1, n+1) for signed in (1,-1)]:
        feedback = ("feedback", v)
        stage((feedback, OFF, ON))
        signals[v] = len(stages)
        for port in ports[v]:
            stage((("upper", len(stages)), ON, ON), port)
        stage((feedback, Edge("full", feedback=True), OFF))
    stage((exit_wire, OFF, ON))
    assert len(stages) == 4 * len(disjunctions) + 2 * (2*n+2) + 4
    return stages, signals


class StrictTemplate:
    def __init__(self, stages, signals):
        from pysat.formula import IDPool
        self.var = IDPool().id
        self.cnf = []
        self.always = []
        self.optional = defaultdict(list)
        self.observable = []
        self.half_slots = []
        self.stages = stages
        self.signals = {k:self.var(("boundary", i)) for k,i in signals.items()}
        self.middle_uses = Counter()
        self.pad_uses = Counter()
        def half(row, mode, edge=None):
            index = len(self.half_slots)
            witnesses = [self.var(("w", index, j)) for j in range(3)]
            guards = [self.var(("guard", index, j)) for j in range(3)]
            self.cnf.append(witnesses)
            self.cnf.extend([[-e, -w, lit] for e, w, lit in zip(guards, witnesses, row)])
            self.observable.extend(guards)
            self.half_slots.append(guards)
            # Negative assumptions also fix the visibly inactive half-slots.
            if mode == "optional":
                self.optional[edge.selector].extend(guards)
            else:
                self.always.extend([g if mode == "on" else -g for g in guards])
            return guards
        for end, sign in [(0,1),(len(stages),-1)]:
            x = sign*self.var(("boundary",end))
            a,b = [self.var(("endpoint_pad",end,j)) for j in range(2)]
            for u,v in product((-1,1), repeat=2):
                half([x,u*a,v*b],"on")
        self.edge_records = []
        self.feedback_out = []
        for i, branches in enumerate(stages):
            left,right = [self.var(("boundary", h)) for h in (i,i+1)]
            for branch, (name, incoming, outgoing) in enumerate(branches):
                self.middle_uses[name] += 1
                m = self.var(("middle",name))
                for part, (u,v,edge) in enumerate(((left,m,incoming),(m,right,outgoing))):
                    key = ("shared_pad",edge.pad) if edge.mode == "half" else ("edge_pad",i,branch,part)
                    p = self.var(key)
                    self.pad_uses[p] += 1
                    slots = []
                    for sign in (1,-1):
                        active = edge.mode == "full" or (edge.mode == "half" and edge.sign == sign)
                        mode = "optional" if active and edge.selector >= 0 else ("on" if active else "off")
                        guards = half([-u,v,sign*p],mode,edge)
                        if edge.feedback:
                            self.feedback_out.extend(guards)
                        slots.append(guards)
                    self.edge_records.append((u,v,p,*slots))
        assert max(self.middle_uses.values()) <= 2 and max(self.pad_uses.values()) <= 2
        assert all(len(set(abs(x) for x in row)) == 3 for row in self.cnf)
        assert len(self.cnf) == 32*(len(stages)+1)
        assert len(set(self.observable)) == len(self.observable) == 24*(len(stages)+1)

    def guards(self, selected):
        pins = list(self.always)
        for i, guards in self.optional.items():
            pins.extend(guards if i in selected else (-g for g in guards))
        return pins


def allowed_sources(n, clauses, selected):
    return [value for value in range(1 << n) if all(any(
        bool(value & (1 << (abs(lit)-1))) == (lit>0) for lit in clauses[i]) for i in selected)]


def source_pins(raw, n, value):
    return [raw.signals[x] * (1 if value >> (x-1) & 1 else -1) for x in range(1,n+1)]


def truth_from_model(raw, n, model):
    ones = {x for x in model if x > 0}
    return sum((raw.signals[x] in ones) << (x-1) for x in range(1,n+1))


def positive_reach(edges, u, v):
    adj = defaultdict(list)
    for a,b in edges:
        adj[a].append(b)
    seen = {u}
    todo = deque([u])
    while todo:
        for nxt in adj[todo.popleft()]:
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return v in seen


def group_by_pad(raw, pins):
    ones = {x for x in pins if x > 0}
    block_on = lambda gs: all(g in ones for g in gs)
    if not all(block_on(gs) for gs in raw.half_slots[:8]):
        return True, 0
    fixed, conditional, polarities = [], [], defaultdict(set)
    for u,v,p,gs_plus,gs_minus in raw.edge_records:
        plus, minus = block_on(gs_plus), block_on(gs_minus)
        if plus and minus:
            fixed.append((u,v))
        elif plus or minus:
            conditional.append((u,v,p,plus))
            polarities[p].add(plus)
    mixed = [p for p,signs in polarities.items() if len(signs) == 2]
    values = {p:next(iter(signs)) for p, signs in polarities.items() if len(signs) == 1}
    for bits in product((False, True),repeat=len(mixed)):
        values.update(zip(mixed,bits))
        live = fixed + [(u,v) for u,v,p,plus in conditional if values[p] != plus]
        if not positive_reach(live,raw.var(("boundary",0)),raw.var(("boundary",len(raw.stages)))):
            return True, len(mixed)
    return False, len(mixed)


def check():
    from pysat.solvers import Solver
    counts = Counter()
    rng = random.Random(314504)
    for n in (3,4,5):
        clauses = clauses_on(n)
        stages, signals = compile_stages(n,clauses)
        raw = StrictTemplate(stages,signals)
        counts[f"fixed_stages_n{n}"] = len(stages)
        if n==3:
            selections = [set(i for i in range(8) if mask >> i & 1) for mask in range(256)]
        elif n == 4:
            universe = set(range(len(clauses)))
            selections = [set(), universe]
            # Forbid exactly all assignments except the designated bit tuple.
            for value in range(16):
                selections.append({i for i,clause in enumerate(clauses)
                                   if value in allowed_sources(n,[clause],{0})})
            for density in (0.2,0.4,0.6,0.8):
                selections.extend({i for i in universe if rng.random()<density} for _ in range(24))
        else:
            # Use additional names in actual selected clauses, including unsatisfiable
            # examples with the eight clauses on a single triple as a certified core.
            first_triple = set(range(8))
            universe = set(range(len(clauses)))
            selections = [set(), universe, first_triple]
            for _ in range(12):
                extra = {i for i in universe - first_triple if rng.random() < 0.15}
                selections.extend((extra, extra | first_triple))
        with Solver(name="g3",bootstrap_with=raw.cnf) as solver:
            for selected in selections:
                expected = allowed_sources(n,clauses,selected)
                pins = raw.guards(selected)
                assert len(pins)==len(raw.observable) and len(set(map(abs,pins)))==len(pins)
                found = solver.solve(assumptions=pins)
                assert found == bool(expected)
                counts[f"raw_{'sat' if found else 'unsat'}_n{n}"] += 1
                if found:
                    assert truth_from_model(raw,n,solver.get_model()) in expected
                test_sources = range(1 << n) if n==3 else [rng.randrange(1<<n) for _ in range(3)]
                for value in test_sources:
                    assert solver.solve(assumptions=pins+source_pins(raw,n,value)) == (value in expected)
                    counts["pinned_source_checks"] += 1
            if n==3:
                pins = raw.guards(set(range(8)))
                all_on = {p for p in pins if p > 0}
                assert set(raw.feedback_out) <= all_on
                feedback_set = set(raw.feedback_out)
                assert solver.solve(assumptions=[-p if p in feedback_set else p for p in pins])
                counts["removed_feedback_mutation_restores_sat"] = 1
                assert group_by_pad(raw,pins) == (False,14)
                counts["mixed_pad_branches_in_unsat_test"] = 1 << 14

    stages, signals = compile_stages(3,clauses_on(3),same_sign=True)
    wrong = StrictTemplate(stages,signals)
    with Solver(name="g3",bootstrap_with=wrong.cnf) as solver:
        pins = wrong.guards(set(range(8)))
        assert solver.solve(assumptions=pins) and group_by_pad(wrong,pins)==(True,0)
        counts["same_sign_mutation_restores_sat"] = 1
    # Random visible masks, including partial three-switch activations and
    # non-selector halves of the physical graph. Set both endpoints on for
    # most cases; unused private pads alter the graph, never its occurrence caps.
    stages, signals = compile_stages(2,())
    raw = StrictTemplate(stages,signals)
    with Solver(name="g3",bootstrap_with=raw.cnf) as solver:
        for pins, expected in [(list(raw.observable), False), ([-g for g in raw.observable], True)]:
            assert group_by_pad(raw,pins) == (expected,0)
            assert solver.solve(assumptions=pins) == expected
            counts["all_switch_controls"] += 1
        for i in range(600):
            pins = []
            for j,gs in enumerate(raw.half_slots):
                enabled = 7 if j<8 and i%6 else rng.choice((0,3,5,6,7,7,7))
                pins += [g if enabled >> k & 1 else -g for k,g in enumerate(gs)]
            expected, q = group_by_pad(raw,pins)
            assert solver.solve(assumptions=pins) == expected
            counts["generic_grouped_switch_checks"] += 1
            counts["max_mixed_on_generic_checks"] = max(counts["max_mixed_on_generic_checks"],q)
    assert counts["raw_unsat_n3"]==1 and counts["raw_sat_n3"]==255
    return {"status":"passed",**counts}


if __name__ == "__main__":
    try:
        import pysat
    except ImportError:
        exe = ROOT / ".venv" / "bin" / "python"
        if not exe.is_file() or Path(sys.executable).absolute()==exe:
            raise
        raise SystemExit(subprocess.call([str(exe),"-B",__file__,*sys.argv[1:]]))
    result = check()
    path = Path(__file__).with_name("checks.json")
    if sys.argv[1:] == ["--record"]:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        assert result == json.loads(path.read_text())
    print(json.dumps(result,sort_keys=True))
