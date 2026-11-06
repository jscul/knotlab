"""Assemble knot spaces from pieces along a tree of splices, keeping track of every cut."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs/HUB-GLUE-20261102-001A/HUB-GLUE-20261102-001A-P001_selection_leaves_a_hub_and_pieces_glue"))
import glue_lib as G  # noqa: E402

def assemble(pieces, edges):
    """pieces: list of (lines, signs, n). edges: list of (i, li, j, pj): piece i gives its line li (point side), piece j its point pj
    (line side). Edges are applied in order; each must join the current assembly to a new piece.
    Returns lines, signs, n, piece (point -> piece index), cuts: list of dicts (point_pieces, ports)."""
    lines0, signs0, n0 = pieces[0]
    lines = [tuple(l) for l in lines0]; signs = [list(s) for s in signs0]
    label = {(0, p): p for p in range(n0)}                 # (piece, original point) -> assembly point
    line_of = {(0, k): k for k in range(len(lines0))}      # (piece, original line) -> assembly line index
    piece = {p: 0 for p in range(n0)}
    n = n0
    done = {0}
    cuts = []
    for (i, li, j, pj) in edges:
        new, old = (j, i) if i in done else (i, j)
        assert new not in done and old in done
        H, s, m = pieces[new]
        if new == j:          # the new piece gives a point: the assembly gives line li of piece i (point side = assembly)
            L_idx = line_of[(i, li)]
            L = lines[L_idx]
            through = [k for k, l in enumerate(H) if pj in l]
            others = [k for k, l in enumerate(H) if pj not in l]
            relabel = {}
            for p in range(m):
                if p != pj:
                    relabel[p] = n; piece[n] = new; n += 1
            for p in range(m):
                if p != pj: label[(new, p)] = relabel[p]
            keep_lines = [l for k, l in enumerate(lines) if k != L_idx]
            keep_signs = [s_ for k, s_ in enumerate(signs) if k != L_idx]
            # remap line indices of the assembly after deleting L_idx
            for key, k in list(line_of.items()):
                if k == L_idx: del line_of[key]
                elif k > L_idx: line_of[key] = k - 1
            base = len(keep_lines)
            add_lines, add_signs = [], []
            for k in others:
                add_lines.append(tuple(relabel[q] for q in H[k])); add_signs.append(list(s[k]))
                line_of[(new, k)] = base + len(add_lines) - 1
            joins = []
            for t, k in enumerate(through):
                kept = [(relabel[q], s[k][jj]) for jj, q in enumerate(H[k]) if q != pj]
                joins.append((k, tuple(q for q, _ in kept) + (L[t],), [sg for _, sg in kept]))
            ports = set(L)
            point_side = set(range(n)) - set(relabel.values())
        else:                 # the new piece gives a line li of piece i; the assembly gives point pj of piece j (line side)
            q_asm = label[(j, pj)]
            Lnew = H[li]
            relabel = {}
            for p in range(m):
                relabel[p] = n; piece[n] = new; label[(new, p)] = n; n += 1
            through = [k for k, l in enumerate(lines) if q_asm in l]
            others = [k for k, l in enumerate(lines) if q_asm not in l]
            # delete q_asm from the assembly: renumber points above it
            def rn(p): return p - 1 if p > q_asm else p
            keep_lines = [tuple(rn(p) for p in lines[k]) for k in others]
            keep_signs = [list(signs[k]) for k in others]
            newmap = {}
            for key, k in list(line_of.items()):
                if k in others: newmap[key] = others.index(k)
            line_of = newmap
            label = {key: rn(p) for key, p in label.items() if p != q_asm}
            piece = {rn(p): pc for p, pc in piece.items() if p != q_asm}
            for c in cuts:
                c["points"] = {rn(p) for p in c["points"] if p != q_asm}
                c["ports"] = {rn(p) for p in c["ports"] if p != q_asm}
            n -= 1
            relabel = {p: rn(v) for p, v in relabel.items()}
            base = len(keep_lines)
            add_lines, add_signs = [], []
            for k in range(len(H)):
                if k == li: continue
                add_lines.append(tuple(relabel[q] for q in H[k])); add_signs.append(list(s[k]))
                line_of[(new, k)] = base + len(add_lines) - 1
            joins = []
            for t, k in enumerate(through):
                kept = [(rn(q), signs[k][jj]) for jj, q in enumerate(lines[k]) if q != q_asm]
                joins.append((None, tuple(q for q, _ in kept) + (relabel[Lnew[t]],), [sg for _, sg in kept]))
            ports = {relabel[p] for p in Lnew}
            point_side = set(relabel.values())
        found = None
        for tw in itertools.product((0, 1), repeat=3):
            ls = keep_lines + add_lines + [jn[1] for jn in joins]
            ss = keep_signs + add_signs + [jn[2] + [tw[t]] for t, jn in enumerate(joins)]
            if not G.sat_matrix(ls, ss, n).all(axis=1).any():
                found = (ls, ss); break
        assert found, "no failing sign choice"
        lines, signs = found
        jstart = len(keep_lines) + len(add_lines)
        for t, jn in enumerate(joins):
            if jn[0] is not None: line_of[(new, jn[0])] = jstart + t
        cuts.append({"points": set(point_side), "ports": set(ports)})
        done.add(new)
    return lines, signs, n, piece, cuts


def cut_shape(lines, n, pts):
    """for a point set P of the final space: (number of cut edges, distinct ports, distinct slot lines), where the point side's lines are
    the lines inside P and the cut edges join P's points to the other lines"""
    edges = [(p, i) for i, L in enumerate(lines) for p in L if p in pts and not set(L) <= pts]
    inside = [i for i, L in enumerate(lines) if set(L) <= pts]
    return len(edges), len({p for p, _ in edges}), len({i for _, i in edges}), len(pts) - len(inside)


def closing_signs(lines, signs, n, pts, ports):
    """the point-side contraction (lines inside P plus a closing line through the ports) and a sign choice making it fail"""
    pts = sorted(pts)
    pmap = {p: k for k, p in enumerate(pts)}
    Pl = [tuple(pmap[p] for p in L) for L in lines if set(L) <= set(pts)]
    Ps = [list(s) for L, s in zip(lines, signs) if set(L) <= set(pts)]
    port_t = tuple(pmap[p] for p in sorted(ports))
    for tw in itertools.product((0, 1), repeat=3):
        if not G.sat_matrix(Pl + [port_t], Ps + [list(tw)], len(pts)).all(axis=1).any():
            return Pl, Ps, port_t, list(tw), pmap
    return None
