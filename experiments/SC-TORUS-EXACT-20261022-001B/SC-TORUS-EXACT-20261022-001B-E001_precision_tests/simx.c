// Simulation core for SC-TORUS-EXACT-20261022-001B-E001 (compiled by run.py with gcc -O2).
//
//   simx sector Lh Lv s px py n seed   one twist sector: topology counts of the projected cyclic edges
//   simx crn    Lh Lv s n seed         the four sectors (0,0),(1,0),(0,1),(1,1) on common random numbers
//   simx dir    L n seed               untwisted L x L: directed horizontal and vertical winding, both signs
//
// Torus: periods w1 = (Lh,0), w2 = (s,Lv); the up-neighbour of (x,Lv-1) is ((x-s) mod Lh, 0). A twist p acts on period
// coefficients by p(a,b) = a*px + b*py mod 2. Twisted sectors live on the double cover (node 2v+sheet): each edge e (tail u,
// head w, offset parity t) has a fair bit o; arcs: o=1: (u,0)->(w,t) and (w,1^t)->(u,1); o=0: (w,t)->(u,0) and (u,1)->(w,1^t).
// The untwisted sector uses one copy: o=1: u->w, o=0: w->u.
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

// ---- directed winding (untwisted, L x L, no shear): positive-cycle detection with cut-crossing weights
static int *dist, *dq; static uint8_t *inq;
static int positive_cycle(int horizontal, int sign) {
    int head = 0, tail = 0, qn = V + 1, count = V;
    for (int v = 0; v < V; v++) { dist[v] = 0; inq[v] = 1; dq[tail++] = v; }
    while (count) {
        int v = dq[head]; head = (head + 1) % qn; count--; inq[v] = 0;
        int x = v % Lh, y = v / Lh, nb[4], w8[4], k = 0;
        int r = y * Lh + (x + 1) % Lh, l = y * Lh + (x + Lh - 1) % Lh, u = ((y + 1) % Lv) * Lh + x, d = ((y + Lv - 1) % Lv) * Lh + x;
        if (ob[2 * v]) { nb[k] = r; w8[k] = (horizontal && x == Lh - 1) ? 1 : 0; k++; }
        if (!ob[2 * l]) { nb[k] = l; w8[k] = (horizontal && x == 0) ? -1 : 0; k++; }
        if (ob[2 * v + 1]) { nb[k] = u; w8[k] = (!horizontal && y == Lv - 1) ? 1 : 0; k++; }
        if (!ob[2 * d + 1]) { nb[k] = d; w8[k] = (!horizontal && y == 0) ? -1 : 0; k++; }
        for (int i = 0; i < k; i++) {
            int w = nb[i], nd = dist[v] + sign * w8[i];
            if (nd > dist[w]) {
                dist[w] = nd;
                if (nd > (horizontal ? Lv : Lh)) return 1;
                if (!inq[w]) { inq[w] = 1; dq[tail] = w; tail = (tail + 1) % qn; count++; }
            }
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *mode = argv[1];
    if (!strcmp(mode, "sector")) {
        Lh = atoi(argv[2]); Lv = atoi(argv[3]); S = atoi(argv[4]); int px = atoi(argv[5]), py = atoi(argv[6]);
        long n = atol(argv[7]); rseed(strtoull(argv[8], 0, 10)); V = Lh * Lv; build(); alloc_graph(); set_sector(px, py);
        long contr = 0, cross = 0, wodd = 0, weven = 0, h = 0, vv = 0, hv = 0, cons = 0, inv = 0, mism = 0; long wc[5][9]; memset(wc, 0, sizeof wc);
        for (long t = 0; t < n; t++) {
            draw(); run_sector();
            int wa, wb, odd, kind = classify(&wa, &wb, &odd);
            if (TW) { int i = 0; for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { i = 1; break; } inv += i; if (i != odd) mism++; }
            if (kind == 0) contr++;
            else if (kind == 1) { cross++; h++; vv++; hv++; }
            else { if (odd) wodd++; else weven++; if (wa) h++; if (wb) vv++; if (wa && wb) hv++; if (wa <= 4 && wb >= -4 && wb <= 4) wc[wa][wb + 4]++; }
            if (!odd) cons++;
        }
        printf("sector n=%ld contr=%ld cross=%ld wind_odd=%ld wind_even=%ld hwrap=%ld vwrap=%ld hvwrap=%ld cons=%ld invariant=%ld mismatch=%ld",
               n, contr, cross, wodd, weven, h, vv, hv, cons, inv, mism);
        for (int a = 0; a <= 4; a++) for (int b = -4; b <= 4; b++) if (wc[a][b + 4]) printf(" w%d,%d=%ld", a, b, wc[a][b + 4]);
        printf("\n");
        return 0;
    }
    if (!strcmp(mode, "crn")) {
        Lh = atoi(argv[2]); Lv = atoi(argv[3]); S = atoi(argv[4]); long n = atol(argv[5]); rseed(strtoull(argv[6], 0, 10));
        V = Lh * Lv; build(); alloc_graph();
        int sec[4][2] = {{0,0},{1,0},{0,1},{1,1}};
        long c[4] = {0}, x[4] = {0}; double d1 = 0, d2 = 0, s1 = 0, s2 = 0;
        for (long t = 0; t < n; t++) {
            draw();
            double ind[4], sym[4];
            for (int q = 0; q < 4; q++) {
                set_sector(sec[q][0], sec[q][1]); run_sector();
                int wa, wb, odd, kind = classify(&wa, &wb, &odd);
                c[q] += kind == 0; x[q] += kind == 1;
                ind[q] = kind == 0; sym[q] = q == 0 ? (kind == 0) : 0.5 * ((kind == 0) + (kind == 1));
            }
            double d = ind[0] - ind[1] - ind[2] + ind[3], ds = sym[0] - sym[1] - sym[2] + sym[3];
            d1 += d; d2 += d * d; s1 += ds; s2 += ds * ds;
        }
        printf("crn n=%ld c00=%ld c10=%ld c01=%ld c11=%ld x00=%ld x10=%ld x01=%ld x11=%ld dsum=%.1f dsq=%.1f ssum=%.2f ssq=%.2f\n",
               n, c[0], c[1], c[2], c[3], x[0], x[1], x[2], x[3], d1, d2, s1, s2);
        return 0;
    }
    if (!strcmp(mode, "dir")) {
        Lh = Lv = atoi(argv[2]); S = 0; long n = atol(argv[3]); rseed(strtoull(argv[4], 0, 10)); V = Lh * Lv;
        ob = malloc(2 * V); dist = malloc(V * sizeof(int)); dq = malloc((V + 1) * sizeof(int)); inq = malloc(V);
        long cnt[16]; memset(cnt, 0, sizeof cnt);
        for (long t = 0; t < n; t++) {
            draw();
            int hp = positive_cycle(1, 1), hm = positive_cycle(1, -1), vp = positive_cycle(0, 1), vm = positive_cycle(0, -1);
            cnt[hp | (hm << 1) | (vp << 2) | (vm << 3)]++;
        }
        printf("dir n=%ld", n);
        for (int i = 0; i < 16; i++) printf(" s%d=%ld", i, cnt[i]);
        printf("\n");
        return 0;
    }
    return 2;
}
