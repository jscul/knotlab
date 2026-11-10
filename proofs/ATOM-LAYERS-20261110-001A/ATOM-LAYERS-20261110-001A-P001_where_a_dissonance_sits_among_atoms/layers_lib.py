"""Layers through atoms, for ATOM-LAYERS-20261110-001A.

A knot sphere with Fano atoms grown at some of its lines (stuck_lib.grow_any, GROW-STUCK-20261110-001A) has two levels: the triangles
that come from the sphere (upper) and those of each atom (lower, atom j). A line has its triangle's level; a face is upper or in atom j
when every triangle at it is, and a junction otherwise. A dissonance (a violated line, a face where two or more corners agree, an even
face) has the level of its line or face."""
import importlib.util
from collections import Counter
from pathlib import Path

import networkx as nx
from networkx.algorithms import bipartite

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "stuck_lib", ROOT / "proofs/GROW-STUCK-20261110-001A/GROW-STUCK-20261110-001A-P001_a_learner_that_grows_only_when_stuck/stuck_lib.py")
ST = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ST)
SL = ST.SL


class Layered:
    def __init__(self, S, s, x):
        self.S, self.s, self.x = S, list(s), list(x)
        self.levels = ["U"] * S.nt
        self.where = {t: t for t in range(S.nt)}  # original sphere triangle -> current triangle
        self.atoms = 0

    def grow(self, orig_line):
        t = self.where[orig_line]
        S2, s2, x2, chi = ST.grow_any(self.S, self.s, self.x, t)
        j = self.atoms
        lev, where = [], {}
        inv = {cur: o for o, cur in self.where.items()}
        for i, name in enumerate(S2.verts):
            if name[0] == "A":
                lev.append(self.levels[name[1]])
                if name[1] in inv:
                    where[inv[name[1]]] = i
            else:
                lev.append(j)
        self.S, self.s, self.x, self.levels, self.where, self.atoms = S2, s2, x2, lev, where, j + 1

    def K(self):
        return SL.KnotSpace(self.S)

    def face_level(self, v):
        levs = {self.levels[t] for t in range(self.S.nt) if v in self.S.vert[t]}
        if levs == {"U"}:
            return "upper"
        if len(levs) == 1:
            return "atom %d" % next(iter(levs))
        return "junction"

    def defects(self, s=None):
        K = self.K()
        s = self.s if s is None else s
        viol, agree = ST.tally(K, s, self.x)
        out = Counter()
        for i in viol:
            lv = self.levels[K.lines[i]]
            out[("violated line", "upper" if lv == "U" else "atom %d" % lv)] += 1
        for v in range(K.V):
            if agree[v] >= 2:
                out[("over-agreeing face", self.face_level(v))] += agree[v] // 2
            if agree[v] % 2 == 0:
                out[("even face", self.face_level(v))] += 1
        return out

    def learn(self, r, cap=40):
        """the W-lowering learner without growth; returns the defects after each step"""
        path = [self.defects()]
        for _ in range(cap):
            K = self.K()
            if ST.weight2(K, self.s, self.x) == 0:
                break
            e = ST.search(self.S, K, self.s, self.x, r)
            if e is None:
                break
            self.s[e] ^= 1
            path.append(self.defects())
        return path

    def hosts(self):
        """faces that can hold a floor configuration at genus 2: one face with three agreeing corners, every other face one"""
        K = self.K()
        out = Counter()
        for v in range(K.V):
            if K.d[v] < 3:
                continue
            Gr = nx.Graph()
            tops = [("l", i) for i in range(K.n)]
            Gr.add_nodes_from(tops)
            for w in range(K.V):
                for (i, c) in K.corners_at[w]:
                    for slot in range(3 if w == v else 1):
                        Gr.add_edge(("l", i), ("f", w, slot))
            M = bipartite.hopcroft_karp_matching(Gr, top_nodes=tops)
            if sum(1 for u in M if u[0] == "l") == K.n:
                lev = self.face_level(v)
                out["upper" if lev == "upper" else "junction" if lev == "junction" else "atom"] += 1
        return out
