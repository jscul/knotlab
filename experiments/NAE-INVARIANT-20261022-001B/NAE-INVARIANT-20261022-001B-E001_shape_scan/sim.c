// Simulation core for NAE-INVARIANT-20261022-001B-E001 (compiled by run.py with gcc -O2).
//
//   sim twisted   Lh Lv s n seed [mass]   fair not-all-equal: literal graph = twisted orientation of the double cover
//   sim untwisted Lh Lv s n seed [mass]   uniform random orientation of the torus itself
//   sim box       L n seed                uniform random orientation of the L x L grid, free boundary: cyclic density
//   sim arms      L n seed                arms from the centre of an L x L box (lazy hashed orientation)
//
// Torus: vertex (x, y), x mod Lh, y mod Lv; the up-neighbour of (x, Lv-1) is ((x - s) mod Lh, 0), so the periods are
// w1 = (Lh, 0) and w2 = (s, Lv). A closed walk of class a*w1 + b*w2 has length parity a*Lh + b*(s + Lv).
// Torus modes print one line of key=value counts: samples, consistent (twisted), the strong-component test, the
// odd-cluster test, their disagreements, and the topology of the projected cyclic edges (contractible, cross, winding
// class (a, b) normalised with a >= 0).
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
static void fill_bits(uint8_t *b, int n) {
    int i = 0;
    while (i < n) { uint64_t r = rnext(); for (int k = 0; k < 64 && i < n; k++, i++) b[i] = (r >> k) & 1; }
}

static int Lh, Lv, S, V, BOX, TW;
static uint8_t *hb, *vb;
static int *rightn, *leftn, *upn, *downn;

static void build(void) {
    rightn = malloc(V * sizeof(int)); leftn = malloc(V * sizeof(int));
    upn = malloc(V * sizeof(int)); downn = malloc(V * sizeof(int));
    for (int y = 0; y < Lv; y++) for (int x = 0; x < Lh; x++) {
        int v = y * Lh + x;
        if (BOX) {
            rightn[v] = x + 1 < Lh ? v + 1 : -1; leftn[v] = x > 0 ? v - 1 : -1;
            upn[v] = y + 1 < Lv ? v + Lh : -1; downn[v] = y > 0 ? v - Lh : -1;
        } else {
            rightn[v] = y * Lh + (x + 1) % Lh; leftn[v] = y * Lh + (x + Lh - 1) % Lh;
            upn[v] = y + 1 < Lv ? v + Lh : ((x - S) % Lh + Lh) % Lh;
            downn[v] = y > 0 ? v - Lh : (Lv - 1) * Lh + (x + S) % Lh;
        }
    }
}

static inline int outs(int node, int *nb) {
    int k = 0, w;
    if (!TW) {
        int v = node;
        if ((w = rightn[v]) >= 0 && hb[v]) nb[k++] = w;
        if ((w = leftn[v]) >= 0 && !hb[w]) nb[k++] = w;
        if ((w = upn[v]) >= 0 && vb[v]) nb[k++] = w;
        if ((w = downn[v]) >= 0 && !vb[w]) nb[k++] = w;
        return k;
    }
    // node 2v + h means h_v = h; spoke 1 on {v,w}: (v,1) -> (w,0); spoke 0: (v,0) -> (w,1)
    int v = node >> 1, h = node & 1, want = h;
    if ((w = rightn[v]) >= 0 && hb[v] == want) nb[k++] = 2 * w + (1 - h);
    if ((w = leftn[v]) >= 0 && hb[w] == want) nb[k++] = 2 * w + (1 - h);
    if ((w = upn[v]) >= 0 && vb[v] == want) nb[k++] = 2 * w + (1 - h);
    if ((w = downn[v]) >= 0 && vb[w] == want) nb[k++] = 2 * w + (1 - h);
    return k;
}

static int N, *idx, *low, *comp, *stk, *cs_node, *cs_it;
static uint8_t *onst;
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
                if (idx[w] < 0) {
                    cs_it[csp - 1] = it; cs_node[csp] = w; cs_it[csp] = 0; csp++;
                    idx[w] = low[w] = counter++; stk[sp++] = w; onst[w] = 1; pushed = 1; break;
                } else if (onst[w] && idx[w] < low[v]) low[v] = idx[w];
            }
            if (pushed) continue;
            if (low[v] == idx[v]) { int w; do { w = stk[--sp]; onst[w] = 0; comp[w] = ncomp; } while (w != v); ncomp++; }
            csp--;
            if (csp) { int p = cs_node[csp - 1]; if (low[v] < low[p]) low[p] = low[v]; }
        }
    }
}

// union-find with unwrapped displacements and homology lattices in Hermite normal form
static int *par, *dx, *dy, *csz;
typedef struct { long a, b, d; int rank; } Lat;   // rank 1: (a,b); rank 2: rows (a,b), (0,d)
static Lat *lat;
static long gcdl(long a, long b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { long t = a % b; a = b; b = t; } return a; }
static void hnf(long (*m)[2], int k, Lat *out) {
    for (int i = 1; i < k; i++)
        while (m[i][0]) {
            long q = m[0][0] / m[i][0];
            m[0][0] -= q * m[i][0]; m[0][1] -= q * m[i][1];
            long t0 = m[0][0], t1 = m[0][1]; m[0][0] = m[i][0]; m[0][1] = m[i][1]; m[i][0] = t0; m[i][1] = t1;
        }
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
static int find(int v, int *ox, int *oy) {
    int x = 0, y = 0, r = v;
    while (par[r] != r) { x += dx[r]; y += dy[r]; r = par[r]; }
    int cx = x, cy = y, u = v;
    while (par[u] != u) { int nx = cx - dx[u], ny = cy - dy[u], p = par[u]; par[u] = r; dx[u] = cx; dy[u] = cy; cx = nx; cy = ny; u = p; }
    *ox = x; *oy = y; return r;
}
static int parity(long a, long b) { return (int)((((a * Lh + b * (S + Lv)) % 2) + 2) % 2); }
static void join(int u, int v, int sx, int sy) {
    int ux, uy, vx, vy, ru = find(u, &ux, &uy), rv = find(v, &vx, &vy);
    if (ru == rv) {
        long DX = ux + sx - vx, DY = uy + sy - vy;
        if (DX || DY) { long b = DY / Lv, a = (DX - b * S) / Lh; lat_add(&lat[ru], a, b); }
        return;
    }
    par[rv] = ru; dx[rv] = ux + sx - vx; dy[rv] = uy + sy - vy;
    if (lat[rv].rank >= 1) lat_add(&lat[ru], lat[rv].a, lat[rv].b);
    if (lat[rv].rank == 2) lat_add(&lat[ru], 0, lat[rv].d);
}

static int arms(int L, long n, uint64_t seed);

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    const char *mode = argv[1];
    if (!strcmp(mode, "arms")) return arms(atoi(argv[2]), atol(argv[3]), strtoull(argv[4], 0, 10));
    long n; uint64_t seed; int MASS = 0;
    if (!strcmp(mode, "box")) { BOX = 1; Lh = Lv = atoi(argv[2]); S = 0; n = atol(argv[3]); seed = strtoull(argv[4], 0, 10); TW = 0; }
    else {
        Lh = atoi(argv[2]); Lv = atoi(argv[3]); S = atoi(argv[4]); n = atol(argv[5]); seed = strtoull(argv[6], 0, 10);
        TW = !strcmp(mode, "twisted"); MASS = argc > 7 && !strcmp(argv[7], "mass");
    }
    V = Lh * Lv; rseed(seed); build();
    hb = malloc(V); vb = malloc(V);
    N = TW ? 2 * V : V;
    idx = malloc(N * sizeof(int)); low = malloc(N * sizeof(int)); comp = malloc(N * sizeof(int));
    stk = malloc(N * sizeof(int)); cs_node = malloc(N * sizeof(int)); cs_it = malloc(N * sizeof(int)); onst = malloc(N);
    if (BOX) {
        long cyc = 0, edges = 0;
        for (long t = 0; t < n; t++) {
            fill_bits(hb, V); fill_bits(vb, V); tarjan();
            int lo = Lh / 4, hi = Lh - Lh / 4;
            for (int y = lo; y < hi; y++) for (int x = lo; x < hi; x++) {
                int v = y * Lh + x;
                if (x + 1 < hi) { edges++; cyc += comp[v] == comp[v + 1]; }
                if (y + 1 < hi) { edges++; cyc += comp[v] == comp[v + Lh]; }
            }
        }
        printf("box L=%d n=%ld central_edges=%ld central_cyclic=%ld\n", Lh, n, edges, cyc);
        return 0;
    }
    par = malloc(V * sizeof(int)); dx = malloc(V * sizeof(int)); dy = malloc(V * sizeof(int)); csz = malloc(V * sizeof(int));
    lat = malloc(V * sizeof(Lat));
    long cons = 0, inc_scc = 0, inc_topo = 0, mism = 0, contr = 0, cross = 0, wind_odd = 0, wind_even = 0;
    long wc[5][9]; memset(wc, 0, sizeof wc);
    double m1 = 0, m2 = 0, chi = 0;
    for (long t = 0; t < n; t++) {
        fill_bits(hb, V); fill_bits(vb, V); tarjan();
        int incs = 0;
        if (TW) for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { incs = 1; break; }
        for (int v = 0; v < V; v++) { par[v] = v; dx[v] = dy[v] = 0; lat[v].rank = 0; }
        for (int v = 0; v < V; v++) {
            int w = rightn[v], cyc;
            cyc = TW ? (hb[v] ? comp[2 * v + 1] == comp[2 * w] : comp[2 * v] == comp[2 * w + 1]) : comp[v] == comp[w];
            if (cyc) join(v, w, 1, 0);
            w = upn[v];
            cyc = TW ? (vb[v] ? comp[2 * v + 1] == comp[2 * w] : comp[2 * v] == comp[2 * w + 1]) : comp[v] == comp[w];
            if (cyc) join(v, w, 0, 1);
        }
        if (MASS) {
            for (int v = 0; v < V; v++) csz[v] = 0;
            for (int v = 0; v < V; v++) { int ox, oy; csz[find(v, &ox, &oy)]++; }
            int mx = 0; double s2 = 0;
            for (int v = 0; v < V; v++) { if (csz[v] > mx) mx = csz[v]; s2 += (double)csz[v] * csz[v]; }
            m1 += mx; m2 += (double)mx * mx; chi += s2 / V;
        }
        int has_cross = 0, odd = 0, wa = 0, wb = 0, haswind = 0;
        for (int v = 0; v < V; v++) {
            if (par[v] != v) continue;
            Lat *L = &lat[v];
            if (L->rank == 2) { has_cross = 1; if (parity(L->a, L->b) || parity(0, L->d)) odd = 1; }
            else if (L->rank == 1) {
                long g = gcdl(L->a, L->b), a = L->a / g, b = L->b / g;
                if (a < 0 || (a == 0 && b < 0)) { a = -a; b = -b; }
                haswind = 1; wa = (int)a; wb = (int)b;
                if (parity(L->a, L->b)) odd = 1;
            }
        }
        inc_scc += incs; inc_topo += odd; if (TW && incs != odd) mism++;
        if (TW ? !incs : !odd) cons++;
        if (has_cross) cross++;
        else if (haswind) {
            if (parity(wa, wb)) wind_odd++; else wind_even++;
            if (wa <= 4 && wb >= -4 && wb <= 4) wc[wa][wb + 4]++;
        } else contr++;
    }
    printf("%s Lh=%d Lv=%d s=%d n=%ld cons=%ld inc_scc=%ld inc_topo=%ld mismatch=%ld contr=%ld cross=%ld wind_odd=%ld wind_even=%ld",
           mode, Lh, Lv, S, n, cons, inc_scc, inc_topo, mism, contr, cross, wind_odd, wind_even);
    for (int a = 0; a <= 4; a++) for (int b = -4; b <= 4; b++) if (wc[a][b + 4]) printf(" w%d,%d=%ld", a, b, wc[a][b + 4]);
    if (MASS) printf(" m1=%.10e m2=%.10e chi=%.10e", m1, m2, chi);
    printf("\n");
    return 0;
}

// ---- arms: out-reach, in-reach and strong component of the centre of an L x L box, lazily hashed orientation
static int AL; static uint64_t akey;
static inline int obit(int v, int vert) { return (int)(mix(akey ^ ((uint64_t)(2 * v + vert) * 0xd1342543de82ef95ULL)) & 1); }
static int *aq;
static int bfs(int c, int forward, int *mark, int mv, int *len) {
    int h = 0, t = 0, R = 0, cx = c % AL, cy = c / AL;
    aq[t++] = c; mark[c] = mv;
    while (h < t) {
        int v = aq[h++], x = v % AL, y = v / AL, ddx = abs(x - cx), ddy = abs(y - cy), r = ddx > ddy ? ddx : ddy, nb[4], k = 0;
        if (r > R) R = r;
        if (x + 1 < AL && obit(v, 0) == forward) nb[k++] = v + 1;
        if (x > 0 && obit(v - 1, 0) != forward) nb[k++] = v - 1;
        if (y + 1 < AL && obit(v, 1) == forward) nb[k++] = v + AL;
        if (y > 0 && obit(v - AL, 1) != forward) nb[k++] = v - AL;
        for (int i = 0; i < k; i++) if (mark[nb[i]] != mv) { mark[nb[i]] = mv; aq[t++] = nb[i]; }
    }
    *len = t;
    return R;
}
static int arms(int L, long n, uint64_t seed) {
    AL = L;
    int VV = L * L, c = (L / 2) * L + L / 2, Rmax = L / 2 + 1;
    aq = malloc(VV * sizeof(int));
    int *mF = calloc(VV, sizeof(int)), *mB = calloc(VV, sizeof(int));
    long *hF = calloc(Rmax + 1, sizeof(long)), *hB = calloc(Rmax + 1, sizeof(long)), *hM = calloc(Rmax + 1, sizeof(long)), *hS = calloc(Rmax + 1, sizeof(long));
    for (long s = 1; s <= n; s++) {
        akey = mix(seed * 1000003ULL + (uint64_t)s);
        int lenF, lenB;
        int rF = bfs(c, 1, mF, (int)s, &lenF);
        int rB = bfs(c, 0, mB, (int)s, &lenB);
        int rS = 0, cx = L / 2, cy = L / 2;
        for (int i = 0; i < lenB; i++) {
            int v = aq[i];
            if (mF[v] == (int)s) { int ddx = abs(v % L - cx), ddy = abs(v / L - cy), r = ddx > ddy ? ddx : ddy; if (r > rS) rS = r; }
        }
        hF[rF]++; hB[rB]++; hM[rF < rB ? rF : rB]++; hS[rS]++;
    }
    printf("arms L=%d n=%ld\n", L, n);
    for (int r = 0; r <= Rmax; r++) if (hF[r] || hB[r] || hM[r] || hS[r]) printf("%d %ld %ld %ld %ld\n", r, hF[r], hB[r], hM[r], hS[r]);
    return 0;
}
