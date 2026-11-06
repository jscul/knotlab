"""Fano blocks and cycles of Fano blocks (THREEFOLD-SPACES-20261030-001C); uses threefold_lib of ticket A.

A Fano block is a Fano plane minus one line; its three ports are the points of the missing line.  A cycle of k blocks joins block i to
block i+1 (indices mod k) by the line (port 0 of i, port 1 of i, port 2 of i+1).  A twist complements one incidence of a connecting line."""
import threefold_lib as T

FANO = T.FANO
T14_FOUND = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 7, 8), (1, 9, 10), (2, 7, 9), (2, 8, 10), (3, 5, 11), (3, 6, 12), (4, 5, 12),
             (4, 6, 11), (7, 10, 13), (8, 9, 13), (11, 12, 13)]          # the twisted system found by SAT at 14 points, twist at (0, 0)


def block(off):
    return [tuple(p + off for p in l) for l in FANO if l != (0, 1, 2)], (off, off + 1, off + 2)


def cycle_of_blocks(k):
    """returns (lines, connecting line indices); no relabelling, so incidences stay addressable"""
    lines, ports = [], []
    for i in range(k):
        L, P = block(7 * i)
        lines += L
        ports.append(P)
    conn = []
    for i in range(k):
        a, b = ports[i], ports[(i + 1) % k]
        conn.append(len(lines))
        lines.append((a[0], a[1], b[2]))
    return lines, conn, ports


def core_colourable(k, twisted_lines=0):
    """the core of a cycle of k blocks: x_i != x_(i+1) for each connecting line, = instead for a twisted one"""
    for bits in range(1 << k):
        x = [(bits >> i) & 1 for i in range(k)]
        ok = True
        for i in range(k):
            want_equal = i < twisted_lines
            if (x[i] == x[(i + 1) % k]) != want_equal:
                ok = False
                break
        if ok:
            return True
    return False
