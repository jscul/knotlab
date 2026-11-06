/* Line events of twisted double covers on a graph whose edges carry homology coordinates.

   Input (stdin):
     V E K                      vertices, edges, number of homology coordinates (K <= 4)
     u w o_1 .. o_K             E lines: lattice tail u, lattice head w, coordinates of the edge
     S                          number of twists
     a_1 .. a_K                 S lines: twist vectors; the twist of edge e is a.o_e mod 2
   Usage:
     lineev exh LO HI           every orientation with bit mask in [LO, HI) (E <= 63)
     lineev mc SEED COUNT       COUNT uniform random orientations (xoshiro256**, seeded by splitmix64)
   Output: one line per twist s,
     "sector s n=.. c=.. x=.. inv=.. mis=.. w:d_1,..,d_K=count ..."
   and one line per pair of twists s < t that share a line class at least once,
     "joint s t w:d_1,..,d_K=count ...".
   Classification of an orientation in a twist (the double cover: x_e = 1 gives (u,0) -> (w,t) and (w,1-t) -> (u,1), x_e = 0 the reverses):
     an edge is cyclic when its first arc joins two vertices of one strong component (Tarjan); the closing vectors of a union-find over
     cyclic edges generate the period lattices of the clusters;
     c: no nonzero period; x: periods of rank >= 2; w:d: every period on the line through the primitive vector d (first nonzero entry > 0).
   inv counts orientations with a swap-invariant strong component; mis counts disagreements of inv with "some period is odd under the twist"
   (an identity in twisted sectors) and any inv in the untwisted sector. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 160
#define MAXE 480
#define MAXK 4
#define MAXS 16
#define MAXD 4096

static int V, E, K, S;
static int eu[MAXE], ew[MAXE], eo[MAXE][MAXK], tw[MAXS][MAXE], sa[MAXS][MAXK];

static int head[2 * MAXV], nxt[4 * MAXE], to[4 * MAXE], na;
static int idx[2 * MAXV], low[2 * MAXV], comp[2 * MAXV], onst[2 * MAXV], stk[2 * MAXV], sp, cnt, ncomp;
static int cs_v[2 * MAXV], cs_e[2 * MAXV];

static void add(int a, int b) { to[na] = b; nxt[na] = head[a]; head[a] = na++; }

static void tarjan(int n) {
    for (int i = 0; i < n; i++) { idx[i] = -1; onst[i] = 0; }
    cnt = 0; sp = 0; ncomp = 0;
    for (int r = 0; r < n; r++) {
        if (idx[r] >= 0) continue;
        int top = 0;
        cs_v[0] = r; cs_e[0] = head[r]; idx[r] = low[r] = cnt++; stk[sp++] = r; onst[r] = 1;
        while (top >= 0) {
            int v = cs_v[top], e = cs_e[top];
            if (e >= 0) {
                cs_e[top] = nxt[e];
                int w = to[e];
                if (idx[w] < 0) {
                    top++; cs_v[top] = w; cs_e[top] = head[w]; idx[w] = low[w] = cnt++; stk[sp++] = w; onst[w] = 1;
                } else if (onst[w] && idx[w] < low[v]) low[v] = idx[w];
            } else {
                if (low[v] == idx[v]) {
                    int w;
                    do { w = stk[--sp]; onst[w] = 0; comp[w] = ncomp; } while (w != v);
                    ncomp++;
                }
                top--;
                if (top >= 0) { int u = cs_v[top]; if (low[v] < low[u]) low[u] = low[v]; }
            }
        }
    }
}

static int par[MAXV];
static long long pot[MAXV][MAXK];
static int findp(int x, long long *acc) {
    for (int k = 0; k < K; k++) acc[k] = 0;
    while (par[x] != x) { for (int k = 0; k < K; k++) acc[k] += pot[x][k]; x = par[x]; }
    return x;
}
static long long gabs(long long a) { return a < 0 ? -a : a; }
static long long ggcd(long long a, long long b) { a = gabs(a); b = gabs(b); while (b) { long long t = a % b; a = b; b = t; } return a; }

/* global table of line directions */
static int ndir; static int dirv[MAXD][MAXK];
static int dir_index(const long long *d) {
    for (int i = 0; i < ndir; i++) {
        int same = 1;
        for (int k = 0; k < K; k++) if (dirv[i][k] != d[k]) { same = 0; break; }
        if (same) return i;
    }
    if (ndir >= MAXD) { fprintf(stderr, "too many directions\n"); exit(4); }
    for (int k = 0; k < K; k++) dirv[ndir][k] = (int)d[k];
    return ndir++;
}

static unsigned long long nC[MAXS], nX[MAXS], nInv[MAXS], nMis[MAXS], nTot[MAXS];
static unsigned long long *line_cnt;            /* [S][MAXD] */
static unsigned long long *joint_cnt;           /* [S][S][MAXD] */

static void classify(const int *x) {
    int lineclass[MAXS];
    for (int s = 0; s < S; s++) {
        int twisted = 0;
        for (int k = 0; k < K; k++) twisted |= sa[s][k];
        na = 0;
        for (int i = 0; i < 2 * V; i++) head[i] = -1;
        for (int e = 0; e < E; e++) {
            int u = eu[e], w = ew[e], t = tw[s][e];
            if (x[e]) { add(2 * u, 2 * w + t); add(2 * w + (1 ^ t), 2 * u + 1); }
            else { add(2 * w + t, 2 * u); add(2 * u + 1, 2 * w + (1 ^ t)); }
        }
        tarjan(2 * V);
        int inv = 0;
        for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { inv = 1; break; }
        for (int v = 0; v < V; v++) { par[v] = v; for (int k = 0; k < K; k++) pot[v][k] = 0; }
        long long g0[MAXK], pu[MAXK], pw[MAXK], d[MAXK];
        int have = 0, rank2 = 0, odd = 0;
        for (int e = 0; e < E; e++) {
            int u = eu[e], w = ew[e], t = tw[s][e];
            if (comp[2 * u] != comp[2 * w + t]) continue;
            int ru = findp(u, pu), rw = findp(w, pw), nz = 0;
            for (int k = 0; k < K; k++) { d[k] = pu[k] + eo[e][k] - pw[k]; if (d[k]) nz = 1; }
            if (ru == rw) {
                if (!nz) continue;
                long long qd = 0;
                for (int k = 0; k < K; k++) qd += (long long)sa[s][k] * d[k];
                if (gabs(qd) & 1) odd = 1;
                if (!have) { for (int k = 0; k < K; k++) g0[k] = d[k]; have = 1; }
                else if (!rank2) {
                    for (int i = 0; i < K && !rank2; i++)
                        for (int j = i + 1; j < K; j++)
                            if (g0[i] * d[j] - g0[j] * d[i] != 0) { rank2 = 1; break; }
                }
            } else {
                par[rw] = ru;
                for (int k = 0; k < K; k++) pot[rw][k] = d[k];
            }
        }
        nTot[s]++;
        lineclass[s] = -1;
        if (rank2) nX[s]++;
        else if (!have) nC[s]++;
        else {
            long long g = 0;
            for (int k = 0; k < K; k++) g = ggcd(g, g0[k]);
            for (int k = 0; k < K; k++) d[k] = g0[k] / g;
            int f = 0;
            while (d[f] == 0) f++;
            if (d[f] < 0) for (int k = 0; k < K; k++) d[k] = -d[k];
            int i = dir_index(d);
            line_cnt[(size_t)s * MAXD + i]++;
            lineclass[s] = i;
        }
        if (inv) nInv[s]++;
        if (twisted ? (inv != odd) : inv) nMis[s]++;
    }
    for (int s = 0; s < S; s++) {
        if (lineclass[s] < 0) continue;
        for (int t = s + 1; t < S; t++)
            if (lineclass[t] == lineclass[s]) joint_cnt[((size_t)s * MAXS + t) * MAXD + lineclass[s]]++;
    }
}

static uint64_t rs[4];
static uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static uint64_t next64(void) {
    uint64_t r = rotl(rs[1] * 5, 7) * 9, t = rs[1] << 17;
    rs[2] ^= rs[0]; rs[3] ^= rs[1]; rs[1] ^= rs[2]; rs[0] ^= rs[3]; rs[2] ^= t; rs[3] = rotl(rs[3], 45);
    return r;
}
static uint64_t splitmix(uint64_t *z) {
    uint64_t r = (*z += 0x9e3779b97f4a7c15ULL);
    r = (r ^ (r >> 30)) * 0xbf58476d1ce4e5b9ULL;
    r = (r ^ (r >> 27)) * 0x94d049bb133111ebULL;
    return r ^ (r >> 31);
}

static void print_dir(int i) {
    for (int k = 0; k < K; k++) printf(k ? ",%d" : "%d", dirv[i][k]);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: lineev exh LO HI | lineev mc SEED COUNT\n"); return 2; }
    if (scanf("%d %d %d", &V, &E, &K) != 3 || V > MAXV || E > MAXE || K > MAXK || K < 1) { fprintf(stderr, "bad header\n"); return 3; }
    for (int e = 0; e < E; e++) {
        if (scanf("%d %d", &eu[e], &ew[e]) != 2) return 3;
        for (int k = 0; k < K; k++) if (scanf("%d", &eo[e][k]) != 1) return 3;
    }
    if (scanf("%d", &S) != 1 || S > MAXS) return 3;
    for (int s = 0; s < S; s++) for (int k = 0; k < K; k++) if (scanf("%d", &sa[s][k]) != 1) return 3;
    for (int s = 0; s < S; s++)
        for (int e = 0; e < E; e++) {
            long long p = 0;
            for (int k = 0; k < K; k++) p += (long long)sa[s][k] * eo[e][k];
            tw[s][e] = (int)(gabs(p) & 1);
        }
    line_cnt = calloc((size_t)MAXS * MAXD, sizeof *line_cnt);
    joint_cnt = calloc((size_t)MAXS * MAXS * MAXD, sizeof *joint_cnt);
    if (!line_cnt || !joint_cnt) return 6;
    static int x[MAXE];
    if (!strcmp(argv[1], "exh")) {
        if (E > 63) return 5;
        unsigned long long lo = strtoull(argv[2], 0, 10), hi = strtoull(argv[3], 0, 10);
        for (unsigned long long m = lo; m < hi; m++) {
            for (int e = 0; e < E; e++) x[e] = (m >> e) & 1;
            classify(x);
        }
    } else if (!strcmp(argv[1], "mc")) {
        uint64_t z = strtoull(argv[2], 0, 10);
        unsigned long long n = strtoull(argv[3], 0, 10);
        for (int i = 0; i < 4; i++) rs[i] = splitmix(&z);
        for (unsigned long long i = 0; i < n; i++) {
            for (int e = 0; e < E; e += 64) {
                uint64_t r = next64();
                for (int b = 0; b < 64 && e + b < E; b++) x[e + b] = (r >> b) & 1;
            }
            classify(x);
        }
    } else return 2;
    for (int s = 0; s < S; s++) {
        printf("sector %d n=%llu c=%llu x=%llu inv=%llu mis=%llu", s, nTot[s], nC[s], nX[s], nInv[s], nMis[s]);
        for (int i = 0; i < ndir; i++)
            if (line_cnt[(size_t)s * MAXD + i]) { printf(" w:"); print_dir(i); printf("=%llu", line_cnt[(size_t)s * MAXD + i]); }
        printf("\n");
    }
    for (int s = 0; s < S; s++)
        for (int t = s + 1; t < S; t++) {
            int any = 0;
            for (int i = 0; i < ndir; i++) if (joint_cnt[((size_t)s * MAXS + t) * MAXD + i]) { any = 1; break; }
            if (!any) continue;
            printf("joint %d %d", s, t);
            for (int i = 0; i < ndir; i++) {
                unsigned long long v = joint_cnt[((size_t)s * MAXS + t) * MAXD + i];
                if (v) { printf(" w:"); print_dir(i); printf("=%llu", v); }
            }
            printf("\n");
        }
    return 0;
}
