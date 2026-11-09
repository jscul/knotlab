"""Library for TIE-LAW-20261109-001A: the directed medial graph D of the regular tessellation {f, m}, read in PSL(2, p).

Rings are the tessellation's vertices (m contacts each), contacts its edges, faces its f-gons. The rotation group is the triangle group
<x, y | x^m = y^2 = (xy)^f = 1>; x turns about a ring, y is the half-turn about a contact. A dart is a group element g (a contact with
one of its rings marked); its contact is g<y>. The arcs of D out of a dart's contact: g x (turn on about the same ring, a V step) and
g y x (switch to the contact's other ring and turn about it, an F step: the route keeps to the same face). Every vertex of D has in- and
out-degree 2, the arcs about a ring form a directed m-cycle and those about a face a directed f-cycle. A route's turn word is its first
letter (a: about the marked ring of the start dart, b: about the other) followed by V or F at each later vertex.

A ball of D is read inside PSL(2, p) for a large prime p = 1 mod 4mf/gcd(m, f) (PLAIN-TIME-20261108-001B's construction): x = diag(l, 1/l)
with l of order 2m, y of trace 0, and tr(xy) = u + 1/u with u of order 2f. The ball is the cover's when the quotient identifies no two
contacts within it; two primes are read and must agree."""
from __future__ import annotations

import collections
import math


def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n ** 0.5) + 1))


def factor(n):
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def root_of_unity(order, p):
    qs = set(factor(p - 1))
    g = next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in qs))
    return pow(g, (p - 1) // order, p)


def prime_for(m, f, start):
    L = 4 * m * f // math.gcd(m, f)
    q = start - start % L + 1
    while not (q > start and is_prime(q)):
        q += L
    return q


class Group:
    def __init__(self, m, f, p):
        self.p, self.h = p, (p - 1) // 2
        inv = lambda a: pow(a, p - 2, p)
        lam, mu = root_of_unity(2 * m, p), root_of_unity(2 * f, p)
        a = (mu + inv(mu)) * inv((lam - inv(lam)) % p) % p
        self.x = self.norm((lam, 0, 0, inv(lam)))
        self.y = self.norm((a, 1, (-1 - a * a) % p, (-a) % p))
        self.yx = self.mul(self.y, self.x)
        self.e = self.norm((1, 0, 0, 1))

    def norm(self, M):
        for v in M:
            if v:
                return M if v <= self.h else tuple((-u) % self.p for u in M)
        return M

    def mul(self, A, B):
        p = self.p
        return self.norm(((A[0] * B[0] + A[1] * B[2]) % p, (A[0] * B[1] + A[1] * B[3]) % p,
                          (A[2] * B[0] + A[3] * B[2]) % p, (A[2] * B[1] + A[3] * B[3]) % p))

    def contact(self, g):
        return min(g, self.mul(g, self.y))


def tau_formula(m, f):
    L = m * f // math.gcd(m, f)
    return L - L // m - L // f + 1


def first_tie(m, f, p, R, limit=4_000_000):
    """BFS counting shortest routes (capped at 3) from one contact: the first distance with a count >= 2, how many contacts tie there
    and their counts; None if no tie to radius R. Also every distance at which a tie occurs."""
    G = Group(m, f, p)
    c0 = G.contact(G.e)
    dist, count = {c0: 0}, {c0: 1}
    rep = {c0: G.e}
    frontier = [c0]
    ties = {}
    for d in range(1, R + 1):
        new = collections.Counter()
        for c in frontier:
            g = rep[c]
            for h in (G.mul(g, G.x), G.mul(g, G.yx)):
                cc = G.contact(h)
                if cc in dist:
                    continue
                if cc not in new:
                    rep[cc] = h
                new[cc] += count[c]
        for cc, k in new.items():
            dist[cc] = d
            count[cc] = min(k, 3)
        t = sorted(min(k, 3) for k in new.values() if k >= 2)
        if t:
            ties[d] = (len(t), t[:4])
        frontier = list(new)
        if len(dist) > limit:
            return ties, d
    return ties, R


def shortest_routes(m, f, p, R, cap=64):
    """every shortest route (as darts and turn words) to every contact within radius R, capped per contact"""
    G = Group(m, f, p)
    c0 = G.contact(G.e)
    dist = {c0: 0}
    paths = {c0: [((G.e,), "")]}
    frontier = [c0]
    for d in range(1, R + 1):
        nxt = collections.defaultdict(list)
        for c in frontier:
            for darts, w in paths[c]:
                g = darts[-1]
                for step, letter in ((G.x, "V"), (G.yx, "F")):
                    h = G.mul(g, step)
                    cc = G.contact(h)
                    if cc in dist and dist[cc] < d:
                        continue
                    lw = letter if w else ("a" if letter == "V" else "b")
                    nxt[cc].append((darts + (h,), w + lw))
        for cc, lst in nxt.items():
            dist[cc] = d
            paths[cc] = lst[:cap]
        frontier = list(nxt)
    return G, dist, paths


def runs(word):
    """ring runs (arcs about one ring: blocks joined by V) and face runs (blocks joined by F) of a turn word"""
    t = word[1:]
    return ([len(s) + 1 for s in t.split("F")] if t else [1]), ([len(s) + 1 for s in t.split("V")] if t else [1])
