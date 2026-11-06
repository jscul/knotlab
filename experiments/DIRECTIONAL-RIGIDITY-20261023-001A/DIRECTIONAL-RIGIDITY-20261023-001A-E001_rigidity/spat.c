/* Contradiction patterns of a twisted three-place world on the L x M triangular torus (no shear).
   For every configuration of the visible bits (a range, or a seeded random sample) the program decides, for each class in a list,
   whether the cylinder cover along that class has a hidden assignment, and prints the histogram of patterns.
   - The classes (1,0), (0,1) and (1,1) use the sliding-window transfer of TRIPLE-SHIELD-20261023-001A-E001 (tshield.c): the torus
     has an assignment iff the period relation has a fixed point, a cylinder iff it has a cycle.
   - Further classes use the same transfer with windows of up to 14 bits; a cylinder has no assignment iff the image of all
     window states under repeated periods becomes empty.
   Usage: spat R L M alpha beta mode(e|s) lo hi seed g1 g2 [g1 g2 ...]
   Output: "total <n> sat <n>", then "<pattern> <count>"; bit k of a pattern is set when class k (the three above, then the
   given ones in order) has no assignment. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int L, M, R, RB, A, B, V, F;
static int tc[64][3], tg[64][3], tli[64][3], tlj[64][3];      /* corner vertex, gauge, unreduced lattice coordinates */

typedef struct {
    int nlev, per, span, nv;                /* levels per period, vertices per level, window in levels */
    int levv[64][16];                       /* level -> vertices */
    int nstep_tri[64], step_tri[64][16];    /* triangles checked when level s is added */
    int bitpos[64][16][3];                  /* per step and triangle and corner: bit in (window ++ new level) */
    uint16_t *tab[64];                      /* per step: [xb][state] -> mask of new states */
    int nstates;
} cyl;
static cyl C[3];

static void build_triangles(void) {
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) {
        int f = 2 * (j * L + i);
        int ci[2][3] = {{i, i + 1, i + 1}, {i, i, i + 1}}, cj[2][3] = {{j, j, j + 1}, {j, j + 1, j + 1}};
        for (int t = 0; t < 2; t++) for (int k = 0; k < 3; k++) {
            int ii = ci[t][k], jj = cj[t][k], k1 = 0, k2 = 0, i2 = ii, j2 = jj;
            while (j2 >= M) { j2 -= M; k2++; }
            while (i2 >= L) { i2 -= L; k1++; }
            tc[f + t][k] = j2 * L + i2; tg[f + t][k] = (A * k1 + B * k2) & 1;
            tli[f + t][k] = ii; tlj[f + t][k] = jj;
        }
    }
}

static long phi(int c1, int c2, int i, int j) { return (long)c2 * M * i - (long)c1 * L * j; }
static long mod(long a, long m) { long r = a % m; return r < 0 ? r + m : r; }

static void build_cyl(cyl *cy, int c1, int c2) {
    long P = (long)L * M;                                   /* phi(Lambda) = L M Z for primitive c */
    /* residues present */
    int present[1024] = {0};
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) present[mod(phi(c1, c2, i, j), P)] = 1;
    int lev_of[1024], nlev = 0;
    for (long r = 0; r < P; r++) if (present[r]) lev_of[r] = nlev++;
    cy->nlev = nlev; cy->nv = (int)(L * M / nlev);
    int cnt[64] = {0};
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) { int l = lev_of[mod(phi(c1, c2, i, j), P)]; cy->levv[l][cnt[l]++] = j * L + i; }
    /* global level of a lifted point: copy * nlev + level */
    int span = 0;
    long gl[64][3];
    for (int f = 0; f < F; f++) {
        long mn = 1L << 60, mx = -(1L << 60);
        for (int k = 0; k < 3; k++) {
            long u = phi(c1, c2, tli[f][k], tlj[f][k]);
            long copy = (u - mod(u, P)) / P;
            gl[f][k] = copy * nlev + lev_of[mod(u, P)];
            if (gl[f][k] < mn) mn = gl[f][k];
            if (gl[f][k] > mx) mx = gl[f][k];
        }
        if (mx - mn > span) span = (int)(mx - mn);
    }
    if (span < 1) span = 1;
    cy->span = span;
    int nv = cy->nv, wbits = span * nv;                     /* window = the last span levels */
    if (wbits > 16) { fprintf(stderr, "window too large\n"); exit(5); }
    cy->nstates = 1 << wbits;
    for (int s = 0; s < nlev; s++) cy->nstep_tri[s] = 0;
    for (int f = 0; f < F; f++) {
        long mx = gl[f][0]; for (int k = 1; k < 3; k++) if (gl[f][k] > mx) mx = gl[f][k];
        int s = (int)mod(mx, nlev);
        int q = cy->nstep_tri[s]++;
        cy->step_tri[s][q] = f;
        for (int k = 0; k < 3; k++) {
            int back = (int)(mx - gl[f][k]);                /* 0 = the new level, 1..span = window levels counted back */
            int v = tc[f][k], idx = -1, lev = (int)mod(gl[f][k], nlev);
            for (int t = 0; t < nv; t++) if (cy->levv[lev][t] == v) idx = t;
            if (idx < 0) { fprintf(stderr, "vertex not on its level\n"); exit(6); }
            /* window bit layout: level (current - span + 1 + w) occupies bits [w*nv, (w+1)*nv), w = 0..span-1; the new level is
               appended as bits [span*nv, (span+1)*nv) before shifting */
            int w = (back == 0) ? span : span - back;
            cy->bitpos[s][q][k] = w * nv + idx;
        }
    }
    for (int s = 0; s < nlev; s++) {
        int nt = cy->nstep_tri[s], nx = 1 << nt;
        cy->tab[s] = calloc((size_t)nx * cy->nstates, sizeof(uint16_t));
        for (int xb = 0; xb < nx; xb++) for (int st = 0; st < cy->nstates; st++) {
            uint16_t mask = 0;
            for (int nwv = 0; nwv < (1 << nv); nwv++) {
                uint32_t full = (uint32_t)st | ((uint32_t)nwv << wbits);
                int ok = 1;
                for (int q = 0; q < nt && ok; q++) {
                    int f = cy->step_tri[s][q], p = 0;
                    for (int k = 0; k < 3; k++) p |= ((int)((full >> cy->bitpos[s][q][k]) & 1) ^ tg[f][k]) << k;
                    int rel = ((xb >> q) & 1) ? RB : R;
                    if (!((rel >> p) & 1)) ok = 0;
                }
                if (ok) mask |= (uint16_t)(1u << (int)(full >> nv));   /* drop the oldest level */
            }
            cy->tab[s][xb * cy->nstates + st] = mask;
        }
    }
}

static void period(cyl *cy, uint64_t x, uint16_t *P) {
    int ns = cy->nstates;
    static uint16_t a[1 << 16], b[1 << 16];
    for (int s0 = 0; s0 < ns; s0++) a[s0] = (uint16_t)(1u << s0);
    for (int s = 0; s < cy->nlev; s++) {
        int xb = 0;
        for (int q = 0; q < cy->nstep_tri[s]; q++) xb |= (int)((x >> cy->step_tri[s][q]) & 1) << q;
        const uint16_t *row = cy->tab[s] + (size_t)xb * ns;
        for (int s0 = 0; s0 < ns; s0++) { uint16_t m = a[s0], o = 0; while (m) { int bb = __builtin_ctz(m); m &= m - 1; o |= row[bb]; } b[s0] = o; }
        for (int s0 = 0; s0 < ns; s0++) a[s0] = b[s0];
    }
    for (int s0 = 0; s0 < ns; s0++) P[s0] = a[s0];
}

static int has_fixed(const uint16_t *P, int ns) { for (int s = 0; s < ns; s++) if ((P[s] >> s) & 1) return 1; return 0; }
static int has_cycle(const uint16_t *P, int ns) {
    uint16_t Q[16], T[16];
    for (int s = 0; s < ns; s++) Q[s] = P[s];
    for (int k = 1; k <= ns; k++) {
        if (has_fixed(Q, ns)) return 1;
        int any = 0;
        for (int s = 0; s < ns; s++) { uint16_t m = Q[s], o = 0; while (m) { int bb = __builtin_ctz(m); m &= m - 1; o |= P[bb]; } T[s] = o; any |= o; }
        for (int s = 0; s < ns; s++) Q[s] = T[s];
        if (!any) return 0;
    }
    return 0;
}


/* ---------------- generalized cylinders for any primitive class (window up to 14 bits) ---------------- */
typedef struct { int nlev, span, nv, wbits, ns; int levv[256][16]; int nstep[256], step[256][64];
                 int bitpos[256][64][3]; uint16_t *ok[256]; } gcyl;
static int gcyl_build(gcyl *cy, int c1, int c2) {
    long P = (long)L * M; static int present[4096]; for (long r = 0; r < P; r++) present[r] = 0;
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) present[mod(phi(c1, c2, i, j), P)] = 1;
    static int lev_of[4096]; int nlev = 0;
    for (long r = 0; r < P; r++) if (present[r]) lev_of[r] = nlev++;
    cy->nlev = nlev; cy->nv = (int)(L * M / nlev);
    if (nlev > 256 || cy->nv > 16) return -1;
    int cnt[256] = {0};
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) { int l = lev_of[mod(phi(c1, c2, i, j), P)]; cy->levv[l][cnt[l]++] = j * L + i; }
    int span = 0; static long gl[128][3];
    for (int f = 0; f < F; f++) { long mn = 1L << 60, mx = -(1L << 60);
        for (int k = 0; k < 3; k++) { long u = phi(c1, c2, tli[f][k], tlj[f][k]); long copy = (u - mod(u, P)) / P;
            gl[f][k] = copy * nlev + lev_of[mod(u, P)]; if (gl[f][k] < mn) mn = gl[f][k]; if (gl[f][k] > mx) mx = gl[f][k]; }
        if (mx - mn > span) span = (int)(mx - mn); }
    if (span < 1) span = 1; cy->span = span;
    int nv = cy->nv, wbits = span * nv; cy->wbits = wbits;
    if (wbits > 14 || nv > 4) return -1;
    cy->ns = 1 << wbits;
    for (int s = 0; s < nlev; s++) cy->nstep[s] = 0;
    for (int f = 0; f < F; f++) {
        long mx = gl[f][0]; for (int k = 1; k < 3; k++) if (gl[f][k] > mx) mx = gl[f][k];
        int s = (int)mod(mx, nlev); int q = cy->nstep[s]++; if (q >= 64) return -1; cy->step[s][q] = f;
        for (int k = 0; k < 3; k++) {
            int back = (int)(mx - gl[f][k]); int v = tc[f][k], idx = -1, lev = (int)mod(gl[f][k], nlev);
            for (int t = 0; t < nv; t++) if (cy->levv[lev][t] == v) idx = t;
            if (idx < 0) return -1;
            int w = (back == 0) ? span : span - back;
            cy->bitpos[s][q][k] = w * nv + idx; } }
    for (int s = 0; s < nlev; s++) { int nt = cy->nstep[s]; if (nt > 12) return -1; int nx = 1 << nt;
        cy->ok[s] = calloc((size_t)nx * cy->ns, sizeof(uint16_t));
        for (int xb = 0; xb < nx; xb++) for (int st = 0; st < cy->ns; st++) { uint16_t mask = 0;
            for (int nwv = 0; nwv < (1 << nv); nwv++) { uint32_t full = (uint32_t)st | ((uint32_t)nwv << wbits); int good = 1;
                for (int q = 0; q < nt && good; q++) { int f = cy->step[s][q], p = 0;
                    for (int k = 0; k < 3; k++) p |= ((int)((full >> cy->bitpos[s][q][k]) & 1) ^ tg[f][k]) << k;
                    int rel = ((xb >> q) & 1) ? RB : R; if (!((rel >> p) & 1)) good = 0; }
                if (good) mask |= (uint16_t)(1u << nwv); }
            cy->ok[s][(size_t)xb * cy->ns + st] = mask; } }
    return 0; }
/* 1 if the cylinder has no assignment: the image of all window states under repeated periods becomes empty */
static int gcyl_contradicts(gcyl *cy, uint64_t x) {
    int ns = cy->ns, nw = (ns + 63) / 64, nv = cy->nv, wb = cy->wbits;
    static uint64_t a[256], b[256], prev[256];
    for (int i = 0; i < nw; i++) a[i] = ~0ULL; if (ns < 64) a[0] = (1ULL << ns) - 1;
    for (int it = 0; it <= ns + 1; it++) {
        for (int i = 0; i < nw; i++) prev[i] = a[i];
        for (int s = 0; s < cy->nlev; s++) { int xb = 0;
            for (int q = 0; q < cy->nstep[s]; q++) xb |= (int)((x >> cy->step[s][q]) & 1) << q;
            const uint16_t *row = cy->ok[s] + (size_t)xb * ns;
            for (int i = 0; i < nw; i++) b[i] = 0;
            for (int i = 0; i < nw; i++) { uint64_t m = a[i]; while (m) { int bb = __builtin_ctzll(m); m &= m - 1; int st = i * 64 + bb;
                uint16_t ok = row[st]; while (ok) { int nwv = __builtin_ctz(ok); ok &= ok - 1;
                    int nxt = (int)(((uint32_t)st | ((uint32_t)nwv << wb)) >> nv); b[nxt >> 6] |= 1ULL << (nxt & 63); } } }
            for (int i = 0; i < nw; i++) a[i] = b[i]; }
        int any = 0, same = 1; for (int i = 0; i < nw; i++) { any |= a[i] != 0; same &= a[i] == prev[i]; }
        if (!any) return 1;
        if (same) return 0; }
    return 0; }

static uint64_t rng_state;
static uint64_t rnd(void) { rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17; return rng_state; }
int main(int argc, char **argv) {
    /* usage: spat R L M alpha beta mode(e|s) lo hi seed g1 g2 [g1 g2 ...]
       Classes are (1,0), (0,1), (1,1) followed by the extra ones given. For every configuration (a range, or hi - lo
       random ones) prints the histogram of contradiction patterns: bit k set when the cylinder along class k has no
       assignment; pattern -1 means the torus itself has an assignment. */
    if (argc < 10) return 2;
    R = atoi(argv[1]); L = atoi(argv[2]); M = atoi(argv[3]); A = atoi(argv[4]); B = atoi(argv[5]);
    char mode = argv[6][0]; unsigned long long lo = strtoull(argv[7], 0, 10), hi = strtoull(argv[8], 0, 10);
    rng_state = strtoull(argv[9], 0, 10) * 0x9E3779B97F4A7C15ULL | 1;
    int ng = (argc - 10) / 2; if (ng > 13) return 3;
    RB = 0; for (int p = 0; p < 8; p++) if ((R >> p) & 1) RB |= 1 << (7 - p);
    V = L * M; F = 2 * V; if (F > 64) return 4;
    build_triangles();
    int cls[3][2] = {{1, 0}, {0, 1}, {1, 1}};
    for (int c = 0; c < 3; c++) build_cyl(&C[c], cls[c][0], cls[c][1]);
    static gcyl G[13];
    for (int g = 0; g < ng; g++) if (gcyl_build(&G[g], atoi(argv[10 + 2 * g]), atoi(argv[11 + 2 * g])) < 0) { fprintf(stderr, "class %d too wide\n", g); return 5; }
    static unsigned long long hist[1 << 16]; unsigned long long satn = 0, total = 0; uint16_t P[16];
    uint64_t fullmask = F == 64 ? ~0ULL : ((1ULL << F) - 1);
    for (unsigned long long k = lo; k < hi; k++) {
        uint64_t x = mode == 'e' ? k : (rnd() & fullmask); total++;
        period(&C[0], x, P); if (has_fixed(P, C[0].nstates)) { satn++; continue; }
        int m = 0; if (!has_cycle(P, C[0].nstates)) m |= 1;
        period(&C[1], x, P); if (!has_cycle(P, C[1].nstates)) m |= 2;
        period(&C[2], x, P); if (!has_cycle(P, C[2].nstates)) m |= 4;
        for (int g = 0; g < ng; g++) if (gcyl_contradicts(&G[g], x)) m |= 8 << g;
        hist[m]++; }
    printf("total %llu sat %llu\n", total, satn);
    for (int m = 0; m < (1 << (3 + ng)); m++) if (hist[m]) printf("%d %llu\n", m, hist[m]);
    return 0; }
