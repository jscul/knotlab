// Simulation core for TWIST-RELATIONS-20261022-001B-E001 (compiled by run.py with gcc -O2).
//
//   simt joint Lh Lv s n seed   n uniform orientations of the torus with periods (Lh, 0) and (s, Lv); each is classified in the
//                               four twist sectors (0,0), (1,0), (0,1), (1,1) on the same orientation (common random numbers)
//
// Torus: the up-neighbour of (x, Lv-1) is ((x - s) mod Lh, 0). A twist p acts on period coefficients by p(a, b) = a px + b py mod 2.
// Twisted sectors live on the double cover (node 2v + sheet): each edge e (tail u, head w, offset parity t) has a fair bit o;
// arcs: o=1: (u,0)->(w,t) and (w,1^t)->(u,1); o=0: (w,t)->(u,0) and (u,1)->(w,1^t). The untwisted sector uses one copy.
// Per sector the projected cyclic edges are classified: contractible, cross, or winding in a primitive class (wa, wb).
// Output: per sector the counts c (contractible), x (cross), inv (some strong component holds both copies of a vertex), mis
// (that test disagrees with the odd-cluster test), class counts w{q}:{a},{b}; and the joint type pattern jt (type per sector:
// 0 contractible, 1 cross, 2/3/4 winding class = (1,0)/(0,1)/(1,1) mod 2), indexed by sum type_q 5^q.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static uint64_t rs[4];
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static uint64_t rnext(void) {
    uint64_t r = rotl(rs[1] * 5, 7) * 9, t = rs[1] << 17;
    rs[2] ^= rs[0]; rs[3] ^= rs[1]; rs[1] ^= rs[2]; rs[0] ^= rs[3]; rs[2] ^= t; rs[3] = rotl(rs[3], 45);
    return r;
}
static inline uint64_t mix(uint64_t z) {
    z += 0x9e3779b97f4a7c15ULL; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
static void rseed(uint64_t seed) { for (int i = 0; i < 4; i++) rs[i] = mix(seed + 0x1234567ULL * (uint64_t)(i + 1)); }

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
static void draw(void) { for (int e = 0; e < 2 * V; e += 64) { uint64_t r = rnext(); for (int k = 0; k < 64 && e + k < 2 * V; k++) ob[e + k] = (r >> k) & 1; } }
static void run_sector(void) { N = TW ? 2 * V : V; tarjan(); }

static long ct[4], cx[4], cinv[4], cmis[4], wc[4][5][9], jt[625], tot;
static int type_of(int kind, int wa, int wb) {
    if (kind == 0) return 0;
    if (kind == 1) return 1;
    int a = ((wa % 2) + 2) % 2, b = ((wb % 2) + 2) % 2;
    return a && !b ? 2 : (!a && b ? 3 : 4);
}
static void one_sample(void) {
    int sec[4][2] = {{0,0},{1,0},{0,1},{1,1}}, T = 0, mul = 1;
    for (int q = 0; q < 4; q++) {
        set_sector(sec[q][0], sec[q][1]); run_sector();
        int wa, wb, odd, kind = classify(&wa, &wb, &odd);
        ct[q] += kind == 0; cx[q] += kind == 1;
        if (kind == 2 && wa <= 4 && wb >= -4 && wb <= 4) wc[q][wa][wb + 4]++;
        if (TW) { int i = 0; for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { i = 1; break; } cinv[q] += i; cmis[q] += i != odd; }
        T += type_of(kind, wa, wb) * mul; mul *= 5;
    }
    jt[T]++; tot++;
}
int main(int argc, char **argv) {
    if (argc != 7 || strcmp(argv[1], "joint")) return 2;
    Lh = atoi(argv[2]); Lv = atoi(argv[3]); S = atoi(argv[4]); long n = atol(argv[5]); rseed(strtoull(argv[6], 0, 10));
    V = Lh * Lv; build(); alloc_graph();
    for (long t = 0; t < n; t++) { draw(); one_sample(); }
    printf("joint n=%ld", tot);
    for (int q = 0; q < 4; q++) {
        printf(" c%d=%ld x%d=%ld inv%d=%ld mis%d=%ld", q, ct[q], q, cx[q], q, cinv[q], q, cmis[q]);
        for (int a = 0; a <= 4; a++) for (int b = -4; b <= 4; b++) if (wc[q][a][b + 4]) printf(" w%d:%d,%d=%ld", q, a, b, wc[q][a][b + 4]);
    }
    for (int i = 0; i < 625; i++) if (jt[i]) printf(" jt%d=%ld", i, jt[i]);
    printf("\n");
    return 0;
}
