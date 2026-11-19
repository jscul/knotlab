"""The fresh starts of the frozen test (none grown before the freeze)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covermodel as M  # noqa: E402
J = M.J
R5 = J.ring_edges(5)


def ring(n, off):
    return J.ring_edges(n, off)


def starts():
    S = {}
    # F1: 5-5 through a path of two knots
    S['F01-5-5-P2'] = (12, R5 + ring(5, 5) + [(0, 10), (10, 11), (11, 5)], {})
    # F2: 5-7 by a shared knot (ring 2 passes through ring 1's knot 0)
    S['F02-5-7-K'] = (11, R5 + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 0)], {})
    # F3: 5-7 by a path of one knot
    S['F03-5-7-P1'] = (13, R5 + ring(7, 5) + [(0, 12), (12, 5)], {})
    # F4: a chain of three rings of five, B joined to A at B's knot 5 and to C at B's knot 7
    S['F04-chain3-57'] = (15, R5 + ring(5, 5) + ring(5, 10) + [(0, 5), (7, 10)], {})
    # F5: the same with B's joints at its knots 5 and 6 (neighbours)
    S['F05-chain3-56'] = (15, R5 + ring(5, 5) + ring(5, 10) + [(0, 5), (6, 10)], {})
    # F6: three rings of five through one knot (knot 0)
    S['F06-three-K'] = (13, R5 + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 0)] + [(0, 9), (9, 10), (10, 11), (11, 12), (12, 0)], {})
    # F7: two rings of seven joined by two shared distinctions (0-7 and 3-10)
    S['F07-7-7-DD'] = (14, J.ring_edges(7) + ring(7, 7) + [(0, 7), (3, 10)], {})
    # F8: 5-5 by a distinction with a surplus distinction at a far knot of each ring
    S['F08-5-5-D-s2s8'] = (10, R5 + ring(5, 5) + [(0, 5)], {'2': 1, '8': 1})
    # F9: 9-5 by a shared knot
    S['F09-9-5-K'] = (13, J.ring_edges(9) + [(0, 9), (9, 10), (10, 11), (11, 12), (12, 0)], {})
    # F10: a ring of five with a second cycle through a path of four knots from knot 0 to knot 2
    S['F10-theta-P4'] = (9, R5 + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 2)], {})
    # F11: a ring of five carrying a lone knot with two surplus distinctions, joined to a ring of seven by a distinction
    S['F11-5L-7-D'] = (13, R5 + ring(7, 5) + [(2, 12), (0, 5)], {'12': 2})
    # F12: 7-7 by a path of one knot
    S['F12-7-7-P1'] = (15, J.ring_edges(7) + ring(7, 7) + [(0, 14), (14, 7)], {})
    # F13: three rings of five each joined by a distinction to one central knot
    S['F13-bouquet'] = (16, R5 + ring(5, 5) + ring(5, 10) + [(0, 15), (5, 15), (10, 15)], {})
    # F14 (control, one cycle): a ring of nine with lone knots of 2 and 3 surplus distinctions at knots 0 and 4, a surplus at knot 6
    S['F14-n9-control'] = (11, J.ring_edges(9) + [(0, 9), (4, 10)], {'9': 2, '10': 3, '6': 1})
    # F15: two rings of five joined by two paths of one knot (0-a-5 and 2-b-7)
    S['F15-5-5-two-paths'] = (12, R5 + ring(5, 5) + [(0, 10), (10, 5), (2, 11), (11, 7)], {})
    # F16 (the advisor's falsifier): a ring of eight with a lone knot on knots 1, 3, 5, 7 (two windings that never meet)
    S['F16-ring8-four-lone'] = (12, J.ring_edges(8) + [(1, 8), (3, 9), (5, 10), (7, 11)], {})
    # F17 (the advisor's falsifier): two rings of five sharing knot 0, plus a path of three knots from knot 2 to knot 6
    S['F17-5-5-K-path3'] = (12, R5 + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 0)] + [(2, 9), (9, 10), (10, 11), (11, 6)], {})
    return S


def outside():
    """Starts outside the model's scope (a group of three in round 1), grown for the record; no prediction."""
    return {'X01-5-5-DD-0-5-2-7': (10, R5 + ring(5, 5) + [(0, 5), (2, 7)], {}),
            'X02-theta-P2': (7, R5 + [(0, 5), (5, 6), (6, 2)], {}),
            'X03-ring7-chord-P2': (9, J.ring_edges(7) + [(0, 7), (7, 8), (8, 3)], {})}


if __name__ == '__main__':
    for k, (n, e, sp) in starts().items():
        ok, why = M.in_scope(n, e, sp)
        nv, B = M.blocks_of(n, e, sp)
        print(k, ok, why, J.bare_sizes(n, e, sp), M.model_counts(n, e, sp, 10) if ok else '')
