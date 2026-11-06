/* walls_sample.c — contradiction patterns predicted by simple cycles of the wall graph, on random configurations.

   Usage: walls_sample R L M q0 q1 nsamples seed firstonly c1x c1y c2x c2y ...
   Configurations are drawn uniformly from [0, 2^(2LM)) with splitmix64 started at seed. Output: "samples N", then one line
   "x pattern" for every sampled configuration whose pattern is nonzero. The wall graph and the cycle test are those of walls.c
   (WALLS-WITH-CHOICES-20261024-001B-E001), unchanged.
   Original description of walls.c:
   For every configuration x in [lo, hi) of the placement R on the L x M triangular torus in twist (q0, q1), the program builds the
   wall graph in the constant frame (states: triangle, entry edge, relative left value; a turn is allowed when its lone corner's
   place is free, or pinned with the coin's value on the turn's side), enumerates its simple cycles, and marks an odd class c as
   having an assignment when some cycle has det(c, e) != 0 and no overlap (difference of positions of two visits to one torus
   triangle) in Z c + Z e. With firstonly = 1 each visit is compared only with the first visit to its triangle (control).
   Output: "total N", then "pattern count" lines, the pattern having bit k set when class k contradicts (odd, no good cycle).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXT 64          /* triangles (2 L M) */
#define MAXS (MAXT * 6)  /* states: triangle x entry edge x b */
#define MAXC 24

static int L, M, R, q0, q1, firstonly, ncls, cls[MAXC][2];
static int nt;                                  /* number of triangles */
static int tri_typ[MAXT], tri_i[MAXT], tri_j[MAXT];
/* move tables per (triangle, entry edge): two turns */
static int mv_place[MAXT][3][2], mv_tri[MAXT][3][2], mv_k[MAXT][3][2], mv_dx[MAXT][3][2], mv_dy[MAXT][3][2];
static int freeplace[3], pinned[3], pinval[3], flipped;
static int qf0, qf1;

static int comp(int r) { int o = 0; for (int p = 0; p < 8; p++) if (r >> p & 1) o |= 1 << (7 - p); return o; }
static int lone(int p) {
    for (int k = 0; k < 3; k++) {
        int a = -1, ok = 1;
        for (int m = 0; m < 3; m++) if (m != k) { int v = p >> m & 1; if (a < 0) a = v; else if (v != a) ok = 0; }
        if (ok && a != (p >> k & 1)) return k;
    }
    return -1;
}
static const int UPO[3][2] = {{0, 0}, {1, 0}, {1, 1}}, DNO[3][2] = {{0, 0}, {0, 1}, {1, 1}};
static const int CCW[2][3] = {{0, 1, 2}, {0, 2, 1}};
static void corner(int typ, int i, int j, int place, int *x, int *y) {
    const int (*o)[2] = typ == 0 ? UPO : DNO; *x = i + o[place][0]; *y = j + o[place][1];
}
static int tindex(int typ, int i, int j) { return 2 * (((j % M + M) % M) * L + ((i % L + L) % L)) + typ; }
static int fdiv(int a, int b) { return a >= 0 ? a / b : -((-a + b - 1) / b); }

static void build(void) {
    nt = 2 * L * M;
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) for (int typ = 0; typ < 2; typ++) {
        int t = tindex(typ, i, j); tri_typ[t] = typ; tri_i[t] = i; tri_j[t] = j;
    }
    for (int t = 0; t < nt; t++) {
        int typ = tri_typ[t], i = tri_i[t], j = tri_j[t];
        for (int k = 0; k < 3; k++) for (int turn = 0; turn < 2; turn++) {
            int exk = turn == 0 ? (k + 2) % 3 : (k + 1) % 3;
            int lonek = turn == 0 ? k : (k + 1) % 3;
            int ax, ay, bx, by;
            corner(typ, i, j, CCW[typ][exk], &ax, &ay);
            corner(typ, i, j, CCW[typ][(exk + 1) % 3], &bx, &by);
            /* neighbour across edge (a, b) */
            int found = 0;
            int i0 = ax < bx ? ax : bx, j0 = ay < by ? ay : by;
            for (int t2 = 0; t2 < 2 && !found; t2++) for (int di = -1; di <= 0 && !found; di++) for (int dj = -1; dj <= 0 && !found; dj++) {
                int i2 = i0 + di, j2 = j0 + dj;
                if (t2 == typ && i2 == i && j2 == j) continue;
                for (int k2 = 0; k2 < 3; k2++) {
                    int cx, cy, dx, dy;
                    corner(t2, i2, j2, CCW[t2][k2], &cx, &cy);
                    corner(t2, i2, j2, CCW[t2][(k2 + 1) % 3], &dx, &dy);
                    if ((cx == ax && cy == ay && dx == bx && dy == by) || (cx == bx && cy == by && dx == ax && dy == ay)) {
                        mv_place[t][k][turn] = CCW[typ][lonek];
                        mv_tri[t][k][turn] = tindex(t2, i2, j2);
                        mv_k[t][k][turn] = k2;
                        mv_dx[t][k][turn] = fdiv(i2, L);
                        mv_dy[t][k][turn] = fdiv(j2, M);
                        found = 1; break;
                    }
                }
            }
            if (!found) { fprintf(stderr, "no neighbour\n"); exit(1); }
        }
    }
    /* frame */
    int U = R & comp(R), fr = R;
    flipped = 0;
    if (!(U & 1)) {
        if (U >> 2 & 1) { flipped = 1; fr = 0; for (int p = 0; p < 8; p++) if (R >> p & 1) fr |= 1 << (p ^ 2); }
        else { fprintf(stderr, "no constant frame\n"); exit(1); }
    }
    int Uf = fr & comp(fr);
    for (int k = 0; k < 3; k++) { freeplace[k] = 0; pinned[k] = 0; }
    for (int p = 0; p < 8; p++) {
        int l = lone(p); if (l < 0) continue;
        if (Uf >> p & 1) freeplace[l] = 1;
        else if (fr >> p & 1) { pinned[l] = 1; pinval[l] = p >> l & 1; }
    }
    qf0 = q0 ^ (flipped ? (L & 1) : 0); qf1 = q1 ^ (flipped ? (M & 1) : 0);
}

/* graph for one configuration */
static int nadj[MAXS], adj[MAXS][2], adx[MAXS][2], ady[MAXS][2];
static int sid(int t, int k, int b) { return (t * 3 + k) * 2 + b; }

static int det(int ax, int ay, int bx, int by) { return ax * by - ay * bx; }
static int in_lattice(int dx, int dy, int cx, int cy, int ex, int ey) {
    int D = det(cx, cy, ex, ey);
    return det(dx, dy, ex, ey) % D == 0 && det(cx, cy, dx, dy) % D == 0;
}

static int oddmask, goodmask;
static int path[MAXS], px[MAXS + 1], py[MAXS + 1], onpath[MAXS], it[MAXS];

static void test_cycle(int len, int ex, int ey) {
    if (ex == 0 && ey == 0) return;
    for (int c = 0; c < ncls; c++) {
        if (!(oddmask >> c & 1) || (goodmask >> c & 1)) continue;
        int cx = cls[c][0], cy = cls[c][1];
        if (det(cx, cy, ex, ey) == 0) continue;
        int bad = 0;
        for (int a = 0; a < len && !bad; a++) {
            int ta = path[a] / 6;
            for (int b2 = a + 1; b2 < len; b2++) {
                if (path[b2] / 6 != ta) continue;
                if (firstonly) {           /* compare only with the first visit to this triangle */
                    int first = 1;
                    for (int z = 0; z < a; z++) if (path[z] / 6 == ta) { first = 0; break; }
                    if (!first) continue;
                }
                if (in_lattice(px[b2] - px[a], py[b2] - py[a], cx, cy, ex, ey)) { bad = 1; break; }
            }
        }
        if (!bad) goodmask |= 1 << c;
    }
}

static void enumerate(int ns) {
    for (int s0 = 0; s0 < ns; s0++) {
        if ((goodmask & oddmask) == oddmask) return;
        if (!nadj[s0]) continue;
        int depth = 0; path[0] = s0; px[0] = 0; py[0] = 0; onpath[s0] = 1; it[0] = 0;
        while (depth >= 0) {
            int v = path[depth];
            if (it[depth] < nadj[v]) {
                int e = it[depth]++;
                int w = adj[v][e];
                if (w < s0) continue;
                int nx = px[depth] + adx[v][e], ny = py[depth] + ady[v][e];
                if (w == s0) { test_cycle(depth + 1, nx, ny); if ((goodmask & oddmask) == oddmask) break; continue; }
                if (onpath[w]) continue;
                depth++; path[depth] = w; px[depth] = nx; py[depth] = ny; onpath[w] = 1; it[depth] = 0;
            } else { onpath[v] = 0; depth--; }
        }
        for (int d = 0; d < MAXS; d++) onpath[d] = 0;
    }
}

static unsigned long long sm_state;
static unsigned long long splitmix64(void) {
    unsigned long long z = (sm_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage\n"); return 1; }
    R = atoi(argv[1]); L = atoi(argv[2]); M = atoi(argv[3]); q0 = atoi(argv[4]); q1 = atoi(argv[5]);
    long nsamples = atol(argv[6]); sm_state = strtoull(argv[7], NULL, 10); firstonly = atoi(argv[8]);
    ncls = (argc - 9) / 2;
    for (int c = 0; c < ncls; c++) { cls[c][0] = atoi(argv[9 + 2 * c]); cls[c][1] = atoi(argv[10 + 2 * c]); }
    build();
    oddmask = 0;
    for (int c = 0; c < ncls; c++) if (((qf0 * cls[c][0] + qf1 * cls[c][1]) & 1)) oddmask |= 1 << c;
    int ns = nt * 6;
    int nb = 2 * L * M;
    unsigned long long mask = nb >= 64 ? ~0ULL : ((1ULL << nb) - 1);
    printf("samples %ld oddmask %d\n", nsamples, oddmask);
    for (long n = 0; n < nsamples; n++) {
        unsigned long long x = splitmix64() & mask;
        for (int t = 0; t < nt; t++) for (int k = 0; k < 3; k++) for (int b = 0; b < 2; b++) {
            int s = sid(t, k, b), cnt = 0;
            int coin = (int)((x >> t) & 1) ^ (flipped ? ((tri_i[t] + tri_j[t]) & 1) : 0);
            for (int turn = 0; turn < 2; turn++) {
                int pl = mv_place[t][k][turn];
                int ok = freeplace[pl] || (pinned[pl] && ((pinval[pl] ^ coin ^ b) == turn));
                if (!ok) continue;
                int dx = mv_dx[t][k][turn], dy = mv_dy[t][k][turn];
                int b2 = b ^ ((qf0 * dx + qf1 * dy) & 1);
                adj[s][cnt] = sid(mv_tri[t][k][turn], mv_k[t][k][turn], b2); adx[s][cnt] = dx; ady[s][cnt] = dy; cnt++;
            }
            nadj[s] = cnt;
        }
        goodmask = 0;
        enumerate(ns);
        int pattern = oddmask & ~goodmask;
        if (pattern) printf("%llu %d\n", x, pattern);
    }
    return 0;
}
