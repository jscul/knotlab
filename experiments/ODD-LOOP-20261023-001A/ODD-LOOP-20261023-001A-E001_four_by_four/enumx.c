// Exhaustive enumerator for ODD-LOOP-20261023-001A-E001 (compiled by run.py with gcc -O2).
//
//   enumx Lh Lv s lo hi   every orientation with bit mask in [lo, hi) of the torus with periods (Lh, 0) and (s, Lv) (edge e is bit e:
//                         edge 2v is the right edge of vertex v, edge 2v+1 its up edge; bit 1 points along the lattice direction),
//                         classified in the four twist sectors (0,0), (1,0), (0,1), (1,1)
//
// Twisted sectors live on the double cover (node 2v + sheet): each edge e (tail u, head w, offset parity t) with bit o gives arcs
// o=1: (u,0)->(w,t) and (w,1^t)->(u,1); o=0: (w,t)->(u,0) and (u,1)->(w,1^t). Per sector the projected cyclic edges are classified:
// contractible, cross, or winding in a primitive class (a, b) with a >= 0. Output per sector: c (contractible), x (cross), inv (some
// strong component holds both copies of a vertex), mis (that test disagrees with the odd-cluster test), and line counts w{q}:{a},{b}.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int Lh, Lv, S, V, PX, PY, TW;
static int *ehead, *er, *eq, *inc_head; static uint8_t *et, *ob;

static void build(void) {
    ehead = malloc(2 * V * sizeof(int)); er = malloc(2 * V * sizeof(int)); eq = malloc(2 * V * sizeof(int));
    et = malloc(2 * V); ob = malloc(2 * V); inc_head = malloc(2 * V * sizeof(int));
    for (int v = 0; v < V; v++) {
        int x = v % Lh, y = v / Lh, X = x + 1, r = 0;
        if (X == Lh) { X = 0; r = 1; }
        ehead[2 * v] = y * Lh + X; er[2 * v] = r; eq[2 * v] = 0;
        if (y + 1 < Lv) { ehead[2 * v + 1] = v + Lh; er[2 * v + 1] = 0; eq[2 * v + 1] = 0; }
        else {
            int Xs = x - S, rr = 0;
            while (Xs < 0) { Xs += Lh; rr--; }
            while (Xs >= Lh) { Xs -= Lh; rr++; }
            ehead[2 * v + 1] = Xs; er[2 * v + 1] = rr; eq[2 * v + 1] = 1;
        }
    }
    for (int e = 0; e < 2 * V; e++) inc_head[2 * ehead[e] + (e & 1)] = e;
}
static void set_sector(int px, int py) {
    PX = px; PY = py; TW = px || py;
    for (int e = 0; e < 2 * V; e++) et[e] = (uint8_t)((((long)er[e] * PX + (long)eq[e] * PY) % 2 + 2) % 2);
}
static inline int outs(int node, int *nb) {
    int k = 0;
    if (!TW) {
        int v = node;
        for (int d = 0; d < 2; d++) { int e = 2 * v + d; if (ob[e]) nb[k++] = ehead[e]; }
        for (int d = 0; d < 2; d++) { int e = inc_head[2 * v + d]; if (!ob[e]) nb[k++] = e >> 1; }
        return k;
    }
    int v = node >> 1, s = node & 1;
    for (int d = 0; d < 2; d++) { int e = 2 * v + d; if ((ob[e] ^ s) == 1) nb[k++] = 2 * ehead[e] + (s ^ et[e]); }
    for (int d = 0; d < 2; d++) { int e = inc_head[2 * v + d], sp = s ^ et[e]; if (ob[e] == sp) nb[k++] = 2 * (e >> 1) + sp; }
    return k;
}

static int N, *idx, *low, *comp, *stk, *cs_node, *cs_it; static uint8_t *onst;
static void tarjan(void) {
    int counter = 0, sp = 0, ncomp = 0, nb[4];
    for (int i = 0; i < N; i++) { idx[i] = -1; onst[i] = 0; }
    for (int r = 0; r < N; r++) {
        if (idx[r] >= 0) continue;
        int csp = 0; cs_node[csp] = r; cs_it[csp] = 0; csp++;
        idx[r] = low[r] = counter++; stk[sp++] = r; onst[r] = 1;
        while (csp) {
            int v = cs_node[csp - 1], it = cs_it[csp - 1], k = outs(v, nb), pushed = 0;
            while (it < k) {
                int w = nb[it++];
                if (idx[w] < 0) { cs_it[csp - 1] = it; cs_node[csp] = w; cs_it[csp] = 0; csp++; idx[w] = low[w] = counter++; stk[sp++] = w; onst[w] = 1; pushed = 1; break; }
                else if (onst[w] && idx[w] < low[v]) low[v] = idx[w];
            }
            if (pushed) continue;
            if (low[v] == idx[v]) { int w; do { w = stk[--sp]; onst[w] = 0; comp[w] = ncomp; } while (w != v); ncomp++; }
            csp--;
            if (csp) { int p = cs_node[csp - 1]; if (low[v] < low[p]) low[p] = low[v]; }
        }
    }
}

static int *par; static long *pa, *pb;
typedef struct { long a, b, d; int rank; } Lat;
static Lat *lat;
static long gcdl(long a, long b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { long t = a % b; a = b; b = t; } return a; }
static void hnf(long (*m)[2], int k, Lat *out) {
    for (int i = 1; i < k; i++)
        while (m[i][0]) { long q = m[0][0] / m[i][0]; m[0][0] -= q * m[i][0]; m[0][1] -= q * m[i][1];
            long t0 = m[0][0], t1 = m[0][1]; m[0][0] = m[i][0]; m[0][1] = m[i][1]; m[i][0] = t0; m[i][1] = t1; }
    long g2 = 0;
    for (int i = 1; i < k; i++) g2 = gcdl(g2, m[i][1]);
    if (m[0][0] < 0) { m[0][0] = -m[0][0]; m[0][1] = -m[0][1]; }
    if (m[0][0] == 0) { g2 = gcdl(g2, m[0][1]); out->rank = g2 ? 1 : 0; out->a = 0; out->b = g2; out->d = 0; return; }
    if (g2 == 0) { out->rank = 1; out->a = m[0][0]; out->b = m[0][1]; out->d = 0; return; }
    long b = m[0][1] % g2; if (b < 0) b += g2;
    out->rank = 2; out->a = m[0][0]; out->b = b; out->d = g2;
}
static void lat_add(Lat *L, long p, long q) {
    long m[3][2]; int k = 0;
    if (L->rank >= 1) { m[k][0] = L->a; m[k][1] = L->b; k++; }
    if (L->rank == 2) { m[k][0] = 0; m[k][1] = L->d; k++; }
    m[k][0] = p; m[k][1] = q; k++;
    if (k == 1) { if (p < 0 || (p == 0 && q < 0)) { p = -p; q = -q; } L->rank = (p || q) ? 1 : 0; L->a = p; L->b = q; L->d = 0; return; }
    hnf(m, k, L);
}
static int find(int v, long *oa, long *ob2) {
    long a = 0, b = 0; int r = v;
    while (par[r] != r) { a += pa[r]; b += pb[r]; r = par[r]; }
    long ca = a, cb = b; int u = v;
    while (par[u] != u) { long na = ca - pa[u], nb2 = cb - pb[u]; int p = par[u]; par[u] = r; pa[u] = ca; pb[u] = cb; ca = na; cb = nb2; u = p; }
    *oa = a; *ob2 = b; return r;
}
static int parity(long a, long b) { return (int)((((a * PX + b * PY) % 2) + 2) % 2); }
static void join(int u, int w, long r, long q) {
    long ua, ub, wa, wb; int ru = find(u, &ua, &ub), rw = find(w, &wa, &wb);
    if (ru == rw) { long da = ua + r - wa, db = ub + q - wb; if (da || db) lat_add(&lat[ru], da, db); return; }
    par[rw] = ru; pa[rw] = ua + r - wa; pb[rw] = ub + q - wb;
    if (lat[rw].rank >= 1) lat_add(&lat[ru], lat[rw].a, lat[rw].b);
    if (lat[rw].rank == 2) lat_add(&lat[ru], 0, lat[rw].d);
}
// classify the current sector; kind 0 contractible, 1 cross, 2 winding (class wa,wb; odd under the twist)
static int classify(int *wa_o, int *wb_o, int *odd_o) {
    for (int v = 0; v < V; v++) { par[v] = v; pa[v] = pb[v] = 0; lat[v].rank = 0; }
    for (int e = 0; e < 2 * V; e++) {
        int u = e >> 1, w = ehead[e];
        int cyc = TW ? comp[2 * u] == comp[2 * w + et[e]] : comp[u] == comp[w];
        if (cyc) join(u, w, er[e], eq[e]);
    }
    int cross = 0, odd = 0, wind = 0, wa = 0, wb = 0;
    for (int v = 0; v < V; v++) {
        if (par[v] != v) continue;
        Lat *L = &lat[v];
        if (L->rank == 2) { cross = 1; if (parity(L->a, L->b) || parity(0, L->d)) odd = 1; }
        else if (L->rank == 1) {
            long g = gcdl(L->a, L->b), a = L->a / g, b = L->b / g;
            if (a < 0 || (a == 0 && b < 0)) { a = -a; b = -b; }
            wind = 1; wa = (int)a; wb = (int)b;
            if (parity(L->a, L->b)) odd = 1;
        }
    }
    *wa_o = wa; *wb_o = wb; *odd_o = odd;
    return cross ? 1 : (wind ? 2 : 0);
}
static void alloc_graph(void) {
    N = 2 * V;
    idx = malloc(N * sizeof(int)); low = malloc(N * sizeof(int)); comp = malloc(N * sizeof(int));
    stk = malloc(N * sizeof(int)); cs_node = malloc(N * sizeof(int)); cs_it = malloc(N * sizeof(int)); onst = malloc(N);
    par = malloc(V * sizeof(int)); pa = malloc(V * sizeof(long)); pb = malloc(V * sizeof(long)); lat = malloc(V * sizeof(Lat));
}
static void run_sector(void) { N = TW ? 2 * V : V; tarjan(); }

static long ct[4], cx[4], cinv[4], cmis[4], wc[4][9][17];
int main(int argc, char **argv) {
    if (argc != 6) return 2;
    Lh = atoi(argv[1]); Lv = atoi(argv[2]); S = atoi(argv[3]);
    unsigned long long lo = strtoull(argv[4], 0, 10), hi = strtoull(argv[5], 0, 10);
    V = Lh * Lv; build(); alloc_graph();
    if (2 * V > 63) return 3;
    int sec[4][2] = {{0,0},{1,0},{0,1},{1,1}};
    for (unsigned long long m = lo; m < hi; m++) {
        for (int e = 0; e < 2 * V; e++) ob[e] = (m >> e) & 1;
        for (int q = 0; q < 4; q++) {
            set_sector(sec[q][0], sec[q][1]); run_sector();
            int wa, wb, odd, kind = classify(&wa, &wb, &odd);
            ct[q] += kind == 0; cx[q] += kind == 1;
            if (kind == 2) { if (wa > 8 || wb < -8 || wb > 8) return 4; wc[q][wa][wb + 8]++; }
            if (TW) { int i = 0; for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { i = 1; break; } cinv[q] += i; cmis[q] += i != odd; }
        }
    }
    printf("enum n=%llu", hi - lo);
    for (int q = 0; q < 4; q++) {
        printf(" c%d=%ld x%d=%ld inv%d=%ld mis%d=%ld", q, ct[q], q, cx[q], q, cinv[q], q, cmis[q]);
        for (int a = 0; a <= 8; a++) for (int b = -8; b <= 8; b++) if (wc[q][a][b + 8]) printf(" w%d:%d,%d=%ld", q, a, b, wc[q][a][b + 8]);
    }
    printf("\n");
    return 0;
}
