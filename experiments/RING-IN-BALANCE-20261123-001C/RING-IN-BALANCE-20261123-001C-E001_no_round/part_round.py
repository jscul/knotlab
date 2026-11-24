"""The part-round law: a move is one complete round of one part (steps 1-8 on that part's
members alone), chosen by a priority among the parts that would make a birth.

Ticket RING-IN-BALANCE-20261123-001C, written from the frozen definitions.

Own time: a start knot has 0, a new knot one more than its parents, and a member that waits
through a move of its part gains one; all members of a part share one own time (checked).

Returns are detected along the line of descent of the start's part: each part created by a move
is compared (colour-refinement hash, then an exact isomorphism test) with each of its ancestor
parts that is past its start. The first such match fixes the part that returns, Y0 (the least
own time s among the matching ancestors); after that, the k-th return is the first part created
that descends from the (k-1)-th return and is the same as it.
"""

import random
import time

import iso
from growth import (make_start, parts_of, past_start, roster_family, compute_groups, round_on,
                    roster_graph, roster_summary, structure_graph, seed_int)

PRIORITIES = ["ALL-IN-TURN", "UNIFORM", "BY-MEMBERS", "LARGEST", "SMALLEST", "MOST-LOOSE", "LEAST-TIME"]


class Part:
    __slots__ = ("pid", "members", "ownt", "parent", "past_start", "would_birth", "nmem", "loose",
                 "hash", "graph", "key", "created_moves", "created_births")


class PartRoundRun:
    def __init__(self, start, law, priority, seed=0, run_id="C1", max_moves=4000, max_knots=20000,
                 max_returns=12, interaction_check=True):
        assert priority in PRIORITIES
        self.start, self.law, self.priority, self.seed = start, law, priority, seed
        self.S = make_start(start)
        self.rng = random.Random(seed_int(run_id, start, law.name, priority, seed))
        self.max_moves, self.max_knots, self.max_returns = max_moves, max_knots, max_returns
        self.interaction_check = interaction_check
        self.parts = {}      # live parts
        self.info = {}       # every part ever made
        self.next_pid = 0
        self.moves = 0
        self.births = 0
        self.move_log = []   # (pid moved, births of the move)
        self.Y = []          # Y0, Y1, ... (part ids)
        self.returns = []
        self.detections = []
        self.off_chain = 0
        self.sweeps = 0
        comps, _ = parts_of(self.S, set(self.S.members))
        for comp in comps:
            self._new_part(comp, 0, None)

    # ------------------------------------------------------------------ parts
    def _new_part(self, members, ownt, parent):
        S = self.S
        for u in members:
            assert S.ownt[u] == ownt, ("own time differs inside a part", u, S.ownt[u], ownt)
        fam = roster_family(S, set(members))
        groups = compute_groups(fam)
        owe = {}
        for G in groups:
            for u in G:
                owe[u] = owe.get(u, 0) + 1
        short = {u for u in members if owe.get(u, 0) > S.h(u)}
        P = Part()
        P.pid = self.next_pid
        self.next_pid += 1
        P.members = tuple(sorted(members))
        P.ownt = ownt
        P.parent = parent
        P.past_start = past_start(S, members)
        P.would_birth = len(short) < len(members)
        P.nmem = len(members)
        P.loose = sum(S.h(u) for u in members)
        P.graph = roster_graph(S, members, fam)
        P.hash = iso.graph_hash(P.graph)
        P.key = P.members[0]
        P.created_moves = self.moves
        P.created_births = self.births
        self.parts[P.pid] = P
        self.info[P.pid] = P
        return P

    def ancestors(self, pid):
        A = self.info[pid].parent
        while A is not None:
            yield A
            A = self.info[A].parent

    def descends(self, pid, anc):
        return pid == anc or anc in self.ancestors(pid)

    # ------------------------------------------------------------------ returns
    def _detect(self, P):
        if not P.past_start:
            return
        matched = []
        for a in self.ancestors(P.pid):
            A = self.info[a]
            if A.past_start and A.hash == P.hash and A.nmem == P.nmem:
                if iso.isomorphism(A.graph, P.graph) is not None:
                    matched.append(A)
        if not matched:
            return
        for A in matched:
            self.detections.append((A.pid, A.ownt, P.pid, P.ownt, self.moves))
        mpids = {A.pid for A in matched}
        if not self.Y:
            A = min(matched, key=lambda A: A.ownt)
            self.Y = [A.pid]
        if self.Y[-1] in mpids:
            prev = self.info[self.Y[-1]]
            if len(self.Y) == 1:
                m0, b0 = prev.created_moves, prev.created_births
            else:
                m0, b0 = self.returns[-1]["moves_total"], self.returns[-1]["births_total"]
            self.Y.append(P.pid)
            self.returns.append({
                "k": len(self.Y) - 1, "ownt": P.ownt,
                "moves_since": self.moves - m0, "births_since": self.births - b0,
                "moves_total": self.moves, "births_total": self.births, "knots": self.S.nknots(),
            })
        else:
            self.off_chain += 1

    # ------------------------------------------------------------------ moves
    def _move(self, pid):
        S = self.S
        part = self.parts.pop(pid)
        res = round_on(S, part.members, self.law, born=part.ownt + 1,
                       interaction_check=self.interaction_check)
        self.moves += 1
        self.births += len(res.births)
        self.move_log.append((pid, len(res.births)))
        desc = {b[0] for b in res.births if b[0] in S.members} | set(res.waiting)
        comps, _ = parts_of(S, desc)
        for comp in comps:
            P = self._new_part(comp, part.ownt + 1, pid)
            self._detect(P)
        return res

    def eligible(self):
        return sorted((p for p in self.parts.values() if p.would_birth), key=lambda p: p.key)

    def _pick(self, cands):
        return cands[self.rng.randrange(len(cands))].pid

    def _choose(self, E):
        pr = self.priority
        if pr == "UNIFORM":
            return self._pick(E)
        if pr == "BY-MEMBERS":
            r = self.rng.randrange(sum(p.nmem for p in E))
            for p in E:
                if r < p.nmem:
                    return p.pid
                r -= p.nmem
            raise AssertionError
        if pr == "LARGEST":
            m = max(p.nmem for p in E)
            return self._pick([p for p in E if p.nmem == m])
        if pr == "SMALLEST":
            m = min(p.nmem for p in E)
            return self._pick([p for p in E if p.nmem == m])
        if pr == "MOST-LOOSE":
            m = max(p.loose for p in E)
            return self._pick([p for p in E if p.loose == m])
        if pr == "LEAST-TIME":
            m = min(p.ownt for p in E)
            return self._pick([p for p in E if p.ownt == m])
        raise ValueError(pr)

    def _done(self):
        if len(self.Y) - 1 >= self.max_returns:
            return "returns"
        if self.moves >= self.max_moves:
            return "moves"
        if self.S.nknots() >= self.max_knots:
            return "knots"
        return None

    def run(self):
        t0 = time.time()
        end = None
        while end is None:
            E = self.eligible()
            if not E:
                end = "stopped" if not self.S.members else "jammed"
                break
            if self.priority == "ALL-IN-TURN":
                self.sweeps += 1
                for p in E:              # every part once (parts made during the sweep wait)
                    end = self._done()
                    if end:
                        break
                    if p.pid in self.parts and self.parts[p.pid].would_birth:
                        self._move(p.pid)
                if end is None:
                    end = self._done()
            else:
                end = self._done()
                if end:
                    break
                self._move(self._choose(E))
        self.end = end
        self.run_time = time.time() - t0
        return end

    def run_sweeps(self, n):
        """ALL-IN-TURN sweeps with the C0 trace numbers after each."""
        out = []
        for s in range(1, n + 1):
            E = self.eligible()
            births = []
            for p in E:
                res = self._move(p.pid)
                births.extend(res.births)
            rec = {"sweep": s, "moves": len(E), "births": len(births),
                   "fresh_total": sum(b[3] for b in births),
                   "births_sorted": sorted([b[1], b[3]] for b in births),
                   "fresh_usable_total": sum(b[4] for b in births)}
            rec.update(roster_summary(self.S))
            out.append(rec)
        return out

    # ------------------------------------------------------------------ end of run
    def least_R(self):
        ts = [p.ownt for p in self.parts.values() if p.would_birth]
        return min(ts) if ts else None

    def analysis(self):
        out = {"end": self.end, "moves": self.moves, "births": self.births, "knots": self.S.nknots(),
               "live_parts": len(self.parts), "returns": self.returns, "detections": len(self.detections),
               "off_chain_detections": self.off_chain, "run_time_s": round(self.run_time, 3)}
        if self.Y:
            Y0 = self.info[self.Y[0]]
            out["Y0"] = {"ownt": Y0.ownt, "members": Y0.nmem, "created_moves": Y0.created_moves}
            if len(self.Y) > 1:
                out["period_ownt"] = self.info[self.Y[1]].ownt - Y0.ownt
            # least s, then least t, over every match found in the run
            if self.detections:
                s_min = min(d[1] for d in self.detections)
                t_min = min(d[3] for d in self.detections if d[1] == s_min)
                out["least_s_t"] = [s_min, t_min]
                out["chain_s_t"] = [Y0.ownt, self.info[self.Y[1]].ownt] if len(self.Y) > 1 else None
            # each return the least own time among the matches of its predecessor
            bad = 0
            for k in range(1, len(self.Y)):
                prev, cur = self.Y[k - 1], self.info[self.Y[k]]
                for (a, at, p, pt, mv) in self.detections:
                    if a == prev and pt < cur.ownt:
                        bad += 1
            out["returns_not_least_t"] = bad
            # moves of parts that came apart: descend from Y0, not on the line Y0 -> Y_last
            path = set()
            q = self.Y[-1]
            while q is not None:
                path.add(q)
                if q == self.Y[0]:
                    break
                q = self.info[q].parent
            ca = 0
            other = 0
            for i, (pid, nb) in enumerate(self.move_log):
                if i < Y0.created_moves:
                    continue
                if pid in path:
                    continue
                if self.descends(pid, self.Y[0]):
                    ca += 1
                else:
                    other += 1
            out["come_apart_moves"] = ca
            out["other_moves_after_Y0"] = other
        return out


# ---------------------------------------------------------------------- P2: against complete rounds
_REF = {}
_REFG = {}


def reference_structure(start, law, R):
    key = (start, law.name)
    S, done, halted = _REF.get(key, (None, 0, False))
    if S is None:
        S = make_start(start)
    while done < R and not halted:
        if not S.members:
            halted = True
            break
        res = round_on(S, S.members, law, born=done + 1)
        done += 1
        if res.stalled or not res.births:
            halted = True
    _REF[key] = (S, done, halted)
    return S


def reference_graph(start, law, R):
    key = (start, law.name, R)
    if key not in _REFG:
        S = reference_structure(start, law, R)
        g = structure_graph(S, [k for k in range(S.nknots()) if S.born[k] <= R], lambda k: S.born[k])
        _REFG[key] = (g, iso.graph_hash(g))
        if len(_REFG) > 64:
            _REFG.pop(next(iter(_REFG)))
    return _REFG[key]


def p2_check(run):
    t0 = time.time()
    R = run.least_R()
    if R is None:
        return {"R": None, "same": None, "note": "no part would still make a birth"}
    S = run.S
    knots = [k for k in range(S.nknots()) if S.born[k] <= R]
    g1 = structure_graph(S, knots, lambda k: S.born[k])
    h1 = iso.graph_hash(g1)
    g2, h2 = reference_graph(run.start, run.law, R)
    same = False
    if h1 == h2:
        same = iso.isomorphism(g1, g2) is not None
    return {"R": R, "knots_compared": len(knots), "hash_equal": h1 == h2, "same": same,
            "time_s": round(time.time() - t0, 3)}
