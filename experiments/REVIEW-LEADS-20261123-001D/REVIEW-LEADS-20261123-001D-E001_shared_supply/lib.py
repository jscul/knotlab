"""Sources, joint starts, tick tracking and the three growth rules for REVIEW-LEADS-20261123-001D-E001.

Recorded code is imported from the scarcity study (raw.py and, through it, the ring fixtures and the archived serial
engine) and is not edited. `engine.py` is the count-level re-implementation that the gate cross-checks against it.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
RESEARCH = ROOT / "research" / HERE.parent.name
sys.path.insert(0, str(HERE))
import engine  # noqa: E402

SCARCITY = ("experiments/TICK-BIRTHS-AND-SCARCITY-20261121-001B/"
            "TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/")
LAWS = ("parity", "nae")
POLICIES = ("unrestricted", "joins_first")
CAP_BIRTHS = 400
CAP_STEPS = 12
MAX_BRANCHES = 20000
SEED = 2026112304


def load(name, relative):
    spec = spec_from_file_location(name, ROOT / relative)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_raw = None


def recorded():
    """The scarcity study's raw.py, imported unchanged. Its `.raw`, `.rings`, `.physical` are the archived engines."""
    global _raw
    if _raw is None:
        _raw = load("scarcity_raw_serial", SCARCITY + "raw.py")
    return _raw


def file_sha256(path):
    return sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Src:
    name: str
    depth: int               # complete parent steps already written in the stage
    stars: tuple             # the presentation (original ring plus its births through `depth`)
    roles: dict              # alone ordinary history: knot id -> (parent ids, fresh count)
    levels: dict             # alone ordinary history: knot id -> parent depth of birth
    ticks: dict              # recorded tick age -> role id (the marked tick of the scarcity study)
    donor: int
    donor_kind: str
    note: str = ""
    _cache: dict = field(default_factory=dict, repr=False, compare=False)

    def needed(self, age):
        """Roles in the ancestry of the tick at `age`, ascending, including the tick."""
        if age in self._cache:
            return self._cache[age]
        ids = {self.ticks[age]}
        todo = [self.ticks[age]]
        while todo:
            for p in self.roles[todo.pop()][0]:
                if p in self.roles and p not in ids:
                    ids.add(p)
                    todo.append(p)
        self._cache[age] = sorted(ids)
        return self._cache[age]

    def future_ticks(self):
        return sorted(a for a in self.ticks if self.ticks[a] >= len(self.stars))


def ring_sources():
    raw = recorded()
    source, roles, levels, stages, targets = raw.ordinary_roles(None, "parity")
    stage5, stage9 = stages[6], stages[10]
    assert len(source) == 8 and len(stage5) == 63 and len(stage9) == 135
    tick_parents6 = roles[targets[6]][0]
    tick_parents10 = roles[targets[10]][0]
    assert all(p < len(stage5) for p in tick_parents6) and all(p < len(stage9) for p in tick_parents10)
    out = {
        "R0": Src("R0", 0, source, roles, levels, dict(targets), 4, "original donor, opposite the marked original"),
        "R0m": Src("R0m", 0, source, roles, levels, dict(targets), 0, "original marked holder with the spare"),
        "R5": Src("R5", 5, stage5, roles, levels, dict(targets), tick_parents6[0], "first parent of tick 6"),
        "R9": Src("R9", 9, stage9, roles, levels, dict(targets), tick_parents10[0], "first parent of tick 10"),
    }
    return out


# ---------------------------------------------------------------------------------------------------------------------
# joint starts
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Joint:
    name: str
    shortfall: int
    stars: tuple
    srcs: list                 # [Src, Src]
    maps: list                 # per source: stage knot id -> joint knot id
    donor: int                 # joint knot id of the shared donor
    origin: dict               # joint knot id -> 'X' | 'Y' | 'D'
    repair: dict = field(default_factory=dict)   # extra loose slots added to neighbours (original-donor merges)


def loose_names(stars):
    holders = Counter(d for s in stars for d in s)
    return holders


def merge(name, X, Y, shortfall, repair=None):
    """Identify X's donor with Y's donor. The merged knot holds both supports less `shortfall` loose distinctions."""
    nX = len(X.stars)
    offset = 1 + max(d for s in X.stars for d in s)
    rows = [list(s) for s in X.stars]
    mapY = {}
    nxt = nX
    for k in range(len(Y.stars)):
        if k == Y.donor:
            mapY[k] = X.donor
        else:
            mapY[k] = nxt
            nxt += 1
    new_rows = [None] * (nxt - nX)
    for k, s in enumerate(Y.stars):
        shifted = [d + offset for d in s]
        if k == Y.donor:
            rows[X.donor].extend(shifted)
        else:
            new_rows[mapY[k] - nX] = shifted
    stars = [tuple(r) for r in rows] + [tuple(r) for r in new_rows]
    owners = Counter(d for s in stars for d in s)
    donor = X.donor
    loose = [d for d in stars[donor] if owners[d] == 1]
    for _ in range(shortfall):
        drop = loose.pop()  # a loose distinction of Y's part
        stars[donor] = tuple(d for d in stars[donor] if d != drop)
    repair = repair or {}
    if repair:
        top = 1 + max(d for s in stars for d in s)
        for k, extra in sorted(repair.items()):
            stars[k] = stars[k] + tuple(range(top, top + extra))
            top += extra
    origin = {k: "X" for k in range(nX)}
    for k, m in mapY.items():
        origin[m] = "D" if k == Y.donor else "Y"
    origin[donor] = "D"
    return Joint(name, shortfall, tuple(stars), [X, Y], [{k: k for k in range(nX)}, mapY], donor, origin, repair)


# ---------------------------------------------------------------------------------------------------------------------
# the tracked state: presentation plus the realization of every source's roles
# ---------------------------------------------------------------------------------------------------------------------
class State:
    def __init__(self, joint, real=None, pres=None):
        self.joint = joint
        self.P = pres if pres is not None else engine.Pres.from_stars(joint.stars)
        self.real = real if real is not None else [dict(m) for m in joint.maps]
        self.unreal = None

    def copy(self):
        s = State(self.joint, [dict(r) for r in self.real], self.P.copy())
        return s

    def spend(self, parents, fresh=None):
        child, f = self.P.spend(parents, fresh)
        key = self.P.par[child]
        for i, src in enumerate(self.joint.srcs):
            roles = src.roles
            taken = set(self.real[i].values())
            for age in src.future_ticks():
                for r in src.needed(age):
                    if r in self.real[i] or r < len(src.stars):
                        continue
                    ps = roles[r][0]
                    if all(p in self.real[i] for p in ps) and tuple(sorted(self.real[i][p] for p in ps)) == key \
                            and child not in taken:
                        self.real[i][r] = child
                        taken.add(child)
        return child, f

    def made(self, i, age):
        return self.joint.srcs[i].ticks[age] in self.real[i]

    def lost(self, i, age):
        """Certificate that tick `age` of source i can never be made: a required parent holds no loose distinction
        (or a larger common child excludes a required pair). None when no certificate exists.

        The reason reported for a role is, in this order: a parent with no loose distinction when every parent of the
        role exists (direct); a larger common child (direct); the reason of a required ancestor that is already lost;
        a parent with no loose distinction while another parent of the role is still unmade."""
        src, real, P = self.joint.srcs[i], self.real[i], self.P
        if src.ticks[age] in real:
            return None
        dead = {}
        for r in src.needed(age):
            if r in real or r < len(src.stars):
                continue
            ps = src.roles[r][0]
            realized_all = all(p in real for p in ps)
            exhausted = [p for p in ps if p in real and P.loose[real[p]] == 0]
            dead_anc = [p for p in ps if p not in real and p in dead]
            common_child = None
            if realized_all and len(ps) >= 2:
                key = tuple(sorted(real[p] for p in ps))
                common = set.intersection(*[P.kids[k] for k in key])
                if common:
                    common_child = min(common)
            why = None
            if exhausted and realized_all:
                kind = "exhausted_parent"
            elif common_child is not None:
                why = {"kind": "larger_common_child", "role": r, "role_parents": [real[p] for p in ps],
                       "child": common_child, "child_parents": list(P.par[common_child])}
            elif dead_anc:
                why = dict(dead[dead_anc[0]])
                why["through_role"] = r
            elif exhausted:
                kind = "exhausted_parent"
            else:
                continue
            if why is None:
                p = exhausted[0]
                k = real[p]
                why = {"kind": "exhausted_parent", "role": r,
                       "role_parents_present": [real[q] if q in real else None for q in ps],
                       "parent_knot": k, "parent_role": p, "spending_event": P.spent_last.get(k),
                       "spending_birth": (list(P.log[P.spent_last[k] - 1][0]) if k in P.spent_last else None)}
            dead[r] = why
        return dead.get(src.ticks[age])

    def key(self):
        """Canonical name of the state: births by parent names and fresh counts (parents of searched births are
        either start knots or named births)."""
        names = {}
        for k in range(len(self.joint.stars)):
            names[k] = k
        out = []
        for k in range(len(self.joint.stars), len(self.P)):
            nm = ("b", tuple(sorted(names[p] for p in self.P.par[k])), self.P.fresh[k])
            # identical sibling unary births: disambiguate by count
            names[k] = nm
            out.append(nm)
        return tuple(sorted(out, key=repr))


def pool(P, policy):
    g, u, _ = P.moves()
    if policy == "unrestricted":
        return set(g) | set(u), g, u
    return (set(g) if g else set(u)), g, u


def donor_proposals(st, policy):
    """Enabled multi-parent proposals through the shared donor."""
    g, u, _ = st.P.moves()
    D = st.joint.donor
    return [x for x in g if D in x]


# ---------------------------------------------------------------------------------------------------------------------
# existential completion of one source's first remaining tick under the recompute rule
# ---------------------------------------------------------------------------------------------------------------------
def find_completion(st, i, age, policy, budget=20000):
    """Depth-first search over births that are roles of source i's tick `age`. Returns (status, path, states)."""
    src = st.joint.srcs[i]
    needed = [r for r in src.needed(age) if r >= len(src.stars)]
    seen = set()
    count = [0]
    result = {"status": "exhausted", "path": None}

    def rec(s, path):
        count[0] += 1
        if count[0] > budget:
            result["status"] = "budget"
            return True
        if src.ticks[age] in s.real[i]:
            result["status"] = "made"
            result["path"] = list(path)
            return True
        k = s.key()
        if k in seen:
            return False
        seen.add(k)
        if s.lost(i, age) is not None:
            return False
        pl, _, _ = pool(s.P, policy)
        for r in needed:
            if r in s.real[i]:
                continue
            ps = src.roles[r][0]
            if all(p in s.real[i] for p in ps):
                key = tuple(sorted(s.real[i][p] for p in ps))
                if key in pl:
                    t = s.copy()
                    t.spend(key)
                    if rec(t, path + [(r, key, t.P.fresh[-1])]):
                        return True
        return False

    rec(st, [])
    return result["status"], result["path"], count[0]


# ---------------------------------------------------------------------------------------------------------------------
# the guarded serial rule: finish each funded parent step; births inside a step in the priority order given
# ---------------------------------------------------------------------------------------------------------------------
def run_guarded(joint, cap_births=CAP_BIRTHS, cap_steps=CAP_STEPS):
    st = State(joint)
    record = {"steps": [], "ticks": {}, "stall": None, "births": 0, "cap": None}
    registered = [(i, a) for i, s in enumerate(joint.srcs) for a in s.future_ticks()]
    for step in range(1, cap_steps + 1):
        status, parents, fresh, shortages = engine.ordinary_layer(st.P)
        if status == "closed":
            record["cap"] = "closed"
            break
        if status == "stall":
            record["stall"] = {"step": step, "shortages": [list(map(int, x)) for x in shortages],
                               "births_before": record["births"]}
            break
        needed_now = {}
        for i, a in registered:
            src = joint.srcs[i]
            for r in src.needed(a):
                if r < len(src.stars) or r in st.real[i]:
                    continue
                ps = src.roles[r][0]
                if all(p in st.real[i] for p in ps):
                    needed_now[tuple(sorted(st.real[i][p] for p in ps))] = a
        order = sorted(range(len(parents)), key=lambda j: (needed_now.get(parents[j], 99), j))
        written = 0
        for j in order:
            if record["births"] >= cap_births:
                record["cap"] = {"births": cap_births, "step_in_progress": step, "written_in_step": written,
                                 "planned_in_step": len(parents)}
                break
            st.spend(parents[j], fresh[j])
            record["births"] += 1
            written += 1
            for i, a in registered:
                if (i, a) not in record["ticks"] and st.made(i, a):
                    record["ticks"][(i, a)] = {"birth": record["births"], "step": step}
        record["steps"].append({"step": step, "planned": len(parents), "written": written})
        if record["cap"]:
            break
    return st, record


# ---------------------------------------------------------------------------------------------------------------------
# the recompute-after-every-birth rule: branching at births contested at the shared donor
# ---------------------------------------------------------------------------------------------------------------------
def contest_leaves(joint, policy):
    """All states reached by resolving the births contested at the shared donor.

    A birth is contested when the shared donor has more enabled multi-parent proposals than loose distinctions;
    every such proposal is a branch. States are merged by canonical key; `ways` counts the choice sequences."""
    start = State(joint)
    layer = {start.key(): (start, 1, [])}
    leaves = {}
    nodes = 0
    while layer:
        nxt = {}
        for key, (st, ways, example) in layer.items():
            nodes += 1
            D = joint.donor
            props = donor_proposals(st, policy)
            if len(props) <= st.P.loose[D]:
                leaves[key] = (st, ways, example)
                continue
            for g in props:
                t = st.copy()
                t.spend(g)
                k = t.key()
                if k in nxt:
                    old = nxt[k]
                    nxt[k] = (old[0], old[1] + ways, old[2])
                else:
                    nxt[k] = (t, ways, example + [g])
        layer = nxt
    return leaves, nodes


def strict_contest_leaves(joint, policy):
    """The preregistration read literally: a birth is contested only when the donor has ONE loose distinction left and
    at least two enabled multi-parent proposals need it. Until then the proposals through the donor are written in
    ascending order of their parent lists (the tie rule of the scarcity study). Added after the primary results as a
    second reading; see deviations.md."""
    start = State(joint)
    layer = {start.key(): (start, 1, [])}
    leaves = {}
    nodes = 0
    D = joint.donor
    while layer:
        nxt = {}
        for key, (st, ways, example) in layer.items():
            nodes += 1
            props = donor_proposals(st, policy)
            if len(props) <= st.P.loose[D]:
                leaves[key] = (st, ways, example)
                continue
            choices = props if st.P.loose[D] == 1 else [min(props)]
            for g in choices:
                t = st.copy()
                t.spend(g)
                k = t.key()
                if k in nxt:
                    old = nxt[k]
                    nxt[k] = (old[0], old[1] + ways, old[2])
                else:
                    nxt[k] = (t, ways, example + [g])
        layer = nxt
    return leaves, nodes


# ---------------------------------------------------------------------------------------------------------------------
# leaves of the contest tree: fair continuation at the donor, then the classification of every registered tick
# ---------------------------------------------------------------------------------------------------------------------
def fair_complete_donor(st, policy):
    """Weak fairness at the donor: every enabled multi-parent proposal through it is written, ascending, and then
    each leftover loose distinction pays an offered unary birth, until the donor holds no loose distinction."""
    D = st.joint.donor
    written = []
    guard = 0
    while st.P.loose[D] > 0 and guard < 200:
        guard += 1
        g, u, _ = st.P.moves(limit_depth=CAP_STEPS)
        through = sorted(x for x in g if D in x)
        if through:
            choice = through[0]
        elif policy == "unrestricted" and (D,) in u:
            choice = (D,)
        elif policy == "joins_first" and not g and (D,) in u:
            choice = (D,)
        else:
            break
        st.spend(choice)
        written.append(choice)
    return written


def classify_leaf(leaf, policy, budget=20000):
    """Outcome of every registered tick at one leaf of the contest tree.

    made: some order of births from the leaf makes the first registered tick (witness kept);
    lost: after the fair continuation at the donor a required parent holds no loose distinction (certificate), or a
          larger common child excludes a required pair; otherwise open."""
    joint = leaf.joint
    out = []
    fair = leaf.copy()
    fair_written = fair_complete_donor(fair, policy)
    for i, src in enumerate(joint.srcs):
        ticks = src.future_ticks()
        row = {}
        for n, age in enumerate(ticks):
            entry = {"tick_age": age}
            if leaf.made(i, age):
                entry["status"] = "made"
                entry["how"] = "already written at the leaf"
            elif n == 0:
                status, path, states = find_completion(leaf, i, age, policy, budget)
                entry["search_states"] = states
                if status == "made":
                    entry["status"] = "made"
                    entry["how"] = "firing completion found"
                    entry["completion_births"] = [(int(r), list(k), int(f)) for r, k, f in path]
                else:
                    entry["search"] = status
            if "status" not in entry:
                cert = fair.lost(i, age)
                if cert is not None:
                    entry["status"] = "lost"
                    entry["certificate"] = cert
                elif fair.made(i, age):
                    entry["status"] = "made"
                    entry["how"] = "written in the fair continuation"
                else:
                    entry["status"] = "open"
            row[age] = entry
        out.append(row)
    return out, fair_written


def source_state(row):
    """lost if any registered tick of the source is lost, else made if all are made, else open."""
    st = [e["status"] for e in row.values()]
    if "lost" in st:
        return "lost"
    if all(s == "made" for s in st):
        return "made"
    return "open"


# ---------------------------------------------------------------------------------------------------------------------
# ordinary growth of a joint start
# ---------------------------------------------------------------------------------------------------------------------
def run_ordinary(joint, last_step, max_births=100000, check_steps=3):
    """Whole ordinary parent steps. Returns the state and a per-step record. The first `check_steps` steps are
    compared with the archived `literal_turn`."""
    phys = recorded().physical
    st = State(joint)
    stars = joint.stars
    rec = []
    total = 0
    registered = [(i, a) for i, s in enumerate(joint.srcs) for a in s.future_ticks()]
    ticks = {}
    for step in range(1, last_step + 1):
        status, parents, fresh, shortages = engine.ordinary_layer(st.P)
        row = {"step": step, "status": status}
        if status != "extend":
            row["shortages"] = [list(map(int, s)) for s in shortages]
            rec.append(row)
            break
        if step <= check_steps:
            ref_status, births, _ = phys.literal_turn(stars, "parity")
            assert ref_status == "extend"
            assert tuple(b.parents for b in births) == tuple(parents), "archived plan differs"
            assert tuple(len(b.fresh) for b in births) == tuple(fresh), "archived fresh counts differ"
            stars = stars + tuple(b.support for b in births)
            row["archived_literal_turn_agrees"] = True
        for g, f in zip(parents, fresh, strict=True):
            st.spend(g, f)
        total += len(parents)
        row["births"] = len(parents)
        row["cumulative"] = total
        row["live_after"] = sum(1 for k in range(len(st.P)) if st.P.loose[k])
        for i, a in registered:
            if (i, a) not in ticks and st.made(i, a):
                ticks[(i, a)] = step
        rec.append(row)
        if total > max_births:
            row["stopped"] = "cumulative births passed the cap"
            break
    return st, rec, ticks


def alone_joint(src):
    """A source on its own, wrapped so that the tracker and the rules can run on it."""
    n = len(src.stars)
    return Joint(src.name, 0, src.stars, [src], [{k: k for k in range(n)}], src.donor, {k: "X" for k in range(n)})


# ---------------------------------------------------------------------------------------------------------------------
# cross-check of the count-level engine against the archived implementation
# ---------------------------------------------------------------------------------------------------------------------
def crosscheck(stars, law, policy, seed, births, nsource=None):
    """Random walk of `births` writes. At each state the archived `facts`/`pool` and `apply` must agree with `engine`:
    same multi-parent proposals, same unary proposals, same fresh count. Returns the number of states compared."""
    import random
    raw = recorded()
    rng = random.Random(seed)
    ns = len(stars) if nsource is None else nsource
    P = engine.Pres.from_stars(stars)
    cur = tuple(stars)
    compared = 0
    for _ in range(births):
        _, loose, children, anc, byp, multi, unary = raw.facts(cur, ns)
        g, u, _ = P.moves()
        assert tuple(sorted(multi)) == tuple(sorted(g)), "multi-parent proposals differ"
        assert tuple(sorted(unary)) == tuple(u), "unary proposals differ"
        assert [len(loose.get(k, ())) for k in range(len(cur))] == P.loose[:len(cur)], "loose counts differ"
        choices = raw.pool(multi, unary, policy)
        if not choices:
            break
        pick = rng.choice(sorted(choices))
        cur, row = raw.apply(cur, ns, pick, law)
        child, fresh = P.spend(pick)
        assert fresh == len(row["fresh"]), "fresh count differs"
        compared += 1
    return compared
