/* Contradiction patterns on larger triangular tori, by the transfer of spat.c (LINE-DETECTOR-20261023-001A-E001) generalized to
   levels of up to six vertices and windows of up to 13 bits; every class, including (1,0), (0,1) and (1,1), uses it.
   For every configuration of the visible bits (a range, or a seeded random sample) prints the histogram of patterns: bit k is set
   when the cylinder cover along class k has no hidden assignment. Pattern 0 includes configurations with an assignment on the
   torus. A cylinder has no assignment iff the image of all window states under repeated periods becomes empty.
   Usage: spat2 R L M alpha beta mode(e|s) lo hi seed g1 g2 [g1 g2 ...]   (at most 16 classes) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int L, M, R, RB, A, B, V, F;
static int tc[64][3], tg[64][3], tli[64][3], tlj[64][3];
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

/* generalized cylinders: up to 6 vertices per level, windows of up to 13 bits, 64-bit masks of new-level values */
typedef struct { int nlev, span, nv, wbits, ns; int levv[512][8]; int nstep[512], step[512][32];
                 int bitpos[512][32][3]; uint64_t *ok[512]; } gcyl;
static int gcyl_build(gcyl *cy, int c1, int c2) {
    long P = (long)L * M; static int present[8192]; for (long r = 0; r < P; r++) present[r] = 0;
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) present[mod(phi(c1, c2, i, j), P)] = 1;
    static int lev_of[8192]; int nlev = 0;
    for (long r = 0; r < P; r++) if (present[r]) lev_of[r] = nlev++;
    cy->nlev = nlev; cy->nv = (int)(L * M / nlev);
    if (nlev > 512 || cy->nv > 6) return -1;
    int cnt[512] = {0};
    for (int j = 0; j < M; j++) for (int i = 0; i < L; i++) { int l = lev_of[mod(phi(c1, c2, i, j), P)]; cy->levv[l][cnt[l]++] = j * L + i; }
    int span = 0; static long gl[128][3];
    for (int f = 0; f < F; f++) { long mn = 1L << 60, mx = -(1L << 60);
        for (int k = 0; k < 3; k++) { long u = phi(c1, c2, tli[f][k], tlj[f][k]); long copy = (u - mod(u, P)) / P;
            gl[f][k] = copy * nlev + lev_of[mod(u, P)]; if (gl[f][k] < mn) mn = gl[f][k]; if (gl[f][k] > mx) mx = gl[f][k]; }
        if (mx - mn > span) span = (int)(mx - mn); }
    if (span < 1) span = 1; cy->span = span;
    int nv = cy->nv, wbits = span * nv; cy->wbits = wbits;
    if (wbits > 13) return -1;
    cy->ns = 1 << wbits;
    for (int s = 0; s < nlev; s++) cy->nstep[s] = 0;
    for (int f = 0; f < F; f++) {
        long mx = gl[f][0]; for (int k = 1; k < 3; k++) if (gl[f][k] > mx) mx = gl[f][k];
        int s = (int)mod(mx, nlev); int q = cy->nstep[s]++; if (q >= 32) return -1; cy->step[s][q] = f;
        for (int k = 0; k < 3; k++) {
            int back = (int)(mx - gl[f][k]); int v = tc[f][k], idx = -1, lev = (int)mod(gl[f][k], nlev);
            for (int t = 0; t < nv; t++) if (cy->levv[lev][t] == v) idx = t;
            if (idx < 0) return -1;
            int w = (back == 0) ? span : span - back;
            cy->bitpos[s][q][k] = w * nv + idx; } }
    for (int s = 0; s < nlev; s++) { int nt = cy->nstep[s]; if (nt > 12) return -1; int nx = 1 << nt;
        cy->ok[s] = calloc((size_t)nx * cy->ns, sizeof(uint64_t));
        for (int xb = 0; xb < nx; xb++) for (int st = 0; st < cy->ns; st++) { uint64_t mask = 0;
            for (int nwv = 0; nwv < (1 << nv); nwv++) { uint32_t full = (uint32_t)st | ((uint32_t)nwv << wbits); int good = 1;
                for (int q = 0; q < nt && good; q++) { int f = cy->step[s][q], p = 0;
                    for (int k = 0; k < 3; k++) p |= ((int)((full >> cy->bitpos[s][q][k]) & 1) ^ tg[f][k]) << k;
                    int rel = ((xb >> q) & 1) ? RB : R; if (!((rel >> p) & 1)) good = 0; }
                if (good) mask |= 1ULL << nwv; }
            cy->ok[s][(size_t)xb * cy->ns + st] = mask; } }
    return 0; }
static int gcyl_contradicts(gcyl *cy, uint64_t x) {
    int ns = cy->ns, nw = (ns + 63) / 64, nv = cy->nv, wb = cy->wbits;
    static uint64_t a[128], b[128], prev[128];
    for (int i = 0; i < nw; i++) a[i] = ~0ULL; if (ns < 64) a[0] = (1ULL << ns) - 1;
    for (int it = 0; it <= ns + 1; it++) {
        for (int i = 0; i < nw; i++) prev[i] = a[i];
        for (int s = 0; s < cy->nlev; s++) { int xb = 0;
            for (int q = 0; q < cy->nstep[s]; q++) xb |= (int)((x >> cy->step[s][q]) & 1) << q;
            const uint64_t *row = cy->ok[s] + (size_t)xb * ns;
            for (int i = 0; i < nw; i++) b[i] = 0;
            for (int i = 0; i < nw; i++) { uint64_t m = a[i]; while (m) { int bb = __builtin_ctzll(m); m &= m - 1; int st = i * 64 + bb;
                uint64_t ok = row[st]; while (ok) { int nwv = __builtin_ctzll(ok); ok &= ok - 1;
                    int nxt = (int)(((uint32_t)st | ((uint32_t)nwv << wb)) >> nv); b[nxt >> 6] |= 1ULL << (nxt & 63); } } }
            for (int i = 0; i < nw; i++) a[i] = b[i]; }
        int any = 0, same = 1; for (int i = 0; i < nw; i++) { any |= a[i] != 0; same &= a[i] == prev[i]; }
        if (!any) return 1;
        if (same) return 0; }
    return 0; }
static uint64_t rng_state;
static uint64_t rnd(void) { rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17; return rng_state; }
int main(int argc, char **argv) {
    /* usage: spat2 R L M alpha beta mode(e|s) lo hi seed g1 g2 [g1 g2 ...]   (classes given explicitly, at most 16)
       prints "total <n>" then "<pattern> <count>"; bit k set when class k's cylinder has no assignment */
    if (argc < 12) return 2;
    R = atoi(argv[1]); L = atoi(argv[2]); M = atoi(argv[3]); A = atoi(argv[4]); B = atoi(argv[5]);
    char mode = argv[6][0]; unsigned long long lo = strtoull(argv[7], 0, 10), hi = strtoull(argv[8], 0, 10);
    rng_state = strtoull(argv[9], 0, 10) * 0x9E3779B97F4A7C15ULL | 1;
    int ng = (argc - 10) / 2; if (ng > 16) return 3;
    RB = 0; for (int p = 0; p < 8; p++) if ((R >> p) & 1) RB |= 1 << (7 - p);
    V = L * M; F = 2 * V; if (F > 64) return 4;
    build_triangles();
    static gcyl G[16];
    for (int g = 0; g < ng; g++) if (gcyl_build(&G[g], atoi(argv[10 + 2 * g]), atoi(argv[11 + 2 * g])) < 0) { fprintf(stderr, "class %d too wide\n", g); return 5; }
    static unsigned long long hist[1 << 16]; unsigned long long total = 0;
    uint64_t fullmask = F == 64 ? ~0ULL : ((1ULL << F) - 1);
    for (unsigned long long k = lo; k < hi; k++) {
        uint64_t x = mode == 'e' ? k : (rnd() & fullmask); total++;
        int m = 0; for (int g = 0; g < ng; g++) if (gcyl_contradicts(&G[g], x)) m |= 1 << g;
        hist[m]++; }
    printf("total %llu\n", total);
    for (int m = 0; m < (1 << ng); m++) if (hist[m]) printf("%d %llu\n", m, hist[m]);
    return 0; }
