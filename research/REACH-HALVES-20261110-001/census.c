/* Full-reach census on the cut-open n x n torus (doubled box [0,2n-2]^2, contacts X+Y odd).
   Row c of A^k is kept as a bitset over grid points; row_{k+1}[c] = XOR of row_k[c'] over the contacts c' that c reads.
   OR[c] accumulates supports. Mode "early": stop when every contact has met every ring (prints FULL) or at maxsteps.
   Mode "exact": run exactly P steps (P a multiple of the period of A, so the OR is the exact reach set) and report. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint64_t u64;
int n, N, Wd, NB, NW, NC;
int *cx, *cy, *rd1, *rd2;      /* contact coordinates and the two read targets (-1 if dead) */
int *gidx;                     /* grid index -> contact index */
static inline int G(int X, int Y) { return X * Wd + Y; }
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: census n early|exact steps\n"); return 1; }
    n = atoi(argv[1]); int exact = strcmp(argv[2], "exact") == 0; long steps = atol(argv[3]);
    N = 2 * n - 2; Wd = N + 1; NB = Wd * Wd; NW = (NB + 63) / 64;
    gidx = malloc(sizeof(int) * NB); for (int i = 0; i < NB; i++) gidx[i] = -1;
    NC = 0; for (int X = 0; X <= N; X++) for (int Y = 0; Y <= N; Y++) if ((X + Y) & 1) gidx[G(X, Y)] = NC++;
    cx = malloc(sizeof(int) * NC); cy = malloc(sizeof(int) * NC); rd1 = malloc(sizeof(int) * NC); rd2 = malloc(sizeof(int) * NC);
    for (int X = 0; X <= N; X++) for (int Y = 0; Y <= N; Y++) if ((X + Y) & 1) {
        int c = gidx[G(X, Y)]; cx[c] = X; cy[c] = Y;
        int a1, b1, a2, b2;
        if (X & 1) { a1 = X - 1; b1 = Y - 1; a2 = X + 1; b2 = Y + 1; } else { a1 = X + 1; b1 = Y - 1; a2 = X - 1; b2 = Y + 1; }
        rd1[c] = (a1 >= 0 && a1 <= N && b1 >= 0 && b1 <= N) ? gidx[G(a1, b1)] : -1;
        rd2[c] = (a2 >= 0 && a2 <= N && b2 >= 0 && b2 <= N) ? gidx[G(a2, b2)] : -1;
    }
    /* rings (i,j), i,j in [0,n-1]: contacts (2i+-1,2j), (2i,2j+-1) inside the box */
    int NR = n * n; int *rpos = malloc(sizeof(int) * NR * 4), *rcnt = calloc(NR, sizeof(int));
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
        int cand[4][2] = {{2*i+1, 2*j}, {2*i-1, 2*j}, {2*i, 2*j+1}, {2*i, 2*j-1}};
        for (int t = 0; t < 4; t++) { int X = cand[t][0], Y = cand[t][1];
            if (X >= 0 && X <= N && Y >= 0 && Y <= N) { int r = i*n+j; rpos[r*4 + rcnt[r]++] = G(X, Y); } }
    }
    size_t SZ = (size_t)NC * NW;
    u64 *cur = calloc(SZ, sizeof(u64)), *nxt = calloc(SZ, sizeof(u64)), *orr = calloc(SZ, sizeof(u64));
    if (!cur || !nxt || !orr) { fprintf(stderr, "alloc failed\n"); return 2; }
    for (int c = 0; c < NC; c++) { int g = G(cx[c], cy[c]); cur[(size_t)c*NW + g/64] |= 1ULL << (g%64); orr[(size_t)c*NW + g/64] |= 1ULL << (g%64); }
    /* unmet[c] = number of rings c has not met yet; checked periodically */
    char *met = calloc((size_t)NC * NR, 1); long unmet = (long)NC * NR; int checkevery = 32;
    int *done = calloc(NC, sizeof(int)); int *left = malloc(sizeof(int) * NC); for (int c = 0; c < NC; c++) left[c] = NR;
    long k;
    for (k = 1; k <= steps; k++) {
        for (int c = 0; c < NC; c++) {
            u64 *d = nxt + (size_t)c*NW, *o = orr + (size_t)c*NW;
            int r1 = rd1[c], r2 = rd2[c];
            if (r1 >= 0 && r2 >= 0) { u64 *s1 = cur + (size_t)r1*NW, *s2 = cur + (size_t)r2*NW; for (int w = 0; w < NW; w++) { d[w] = s1[w] ^ s2[w]; o[w] |= d[w]; } }
            else if (r1 >= 0) { u64 *s1 = cur + (size_t)r1*NW; for (int w = 0; w < NW; w++) { d[w] = s1[w]; o[w] |= d[w]; } }
            else if (r2 >= 0) { u64 *s2 = cur + (size_t)r2*NW; for (int w = 0; w < NW; w++) { d[w] = s2[w]; o[w] |= d[w]; } }
            else memset(d, 0, NW * sizeof(u64));
        }
        u64 *t = cur; cur = nxt; nxt = t;
        if (!exact && (k % checkevery == 0)) {
            for (int c = 0; c < NC; c++) if (!done[c]) {
                u64 *o = orr + (size_t)c*NW;
                for (int r = 0; r < NR; r++) if (!met[(size_t)c*NR + r]) {
                    int hit = 0;
                    for (int t = 0; t < rcnt[r]; t++) { int g = rpos[r*4+t]; if ((o[g/64] >> (g%64)) & 1) { hit = 1; break; } }
                    if (hit) { met[(size_t)c*NR + r] = 1; unmet--; if (--left[c] == 0) done[c] = 1; }
                }
            }
            if (unmet == 0) { printf("n %d FULL REACH certified at step %ld (contacts %d)\n", n, k, NC); fflush(stdout); return 0; }
        }
    }
    /* in exact mode, verify A^steps = I so that the OR over [0, steps] is the exact reach set */
    if (exact) {
        int ok = 1;
        for (int c = 0; c < NC && ok; c++) { int g = G(cx[c], cy[c]); u64 *r = cur + (size_t)c*NW;
            for (int w = 0; w < NW; w++) { u64 want = (w == g/64) ? (1ULL << (g%64)) : 0; if (r[w] != want) { ok = 0; break; } } }
        printf("n %d period check: A^%ld %s the identity\n", n, steps, ok ? "IS" : "is NOT");
    }
    /* final report */
    int missring = 0, misscontact = 0;
    for (int c = 0; c < NC; c++) {
        u64 *o = orr + (size_t)c*NW; int mr = 0; char buf[4096]; buf[0] = 0;
        for (int r = 0; r < NR; r++) { int hit = 0; int empty = rcnt[r] == 0;
            for (int t = 0; t < rcnt[r]; t++) { int g = rpos[r*4+t]; if ((o[g/64] >> (g%64)) & 1) { hit = 1; break; } }
            if (!hit && !empty) { mr++; if (strlen(buf) < 4000) sprintf(buf + strlen(buf), " (%d,%d)", r / n, r % n); } }
        int mc = 0; for (int c2 = 0; c2 < NC; c2++) { int g = G(cx[c2], cy[c2]); if (!((o[g/64] >> (g%64)) & 1)) { mc = 1; break; } }
        if (mr) { missring++; if (exact) printf("  contact (%d,%d) misses %d rings:%s\n", cx[c], cy[c], mr, buf); }
        if (mc) misscontact++;
    }
    printf("n %d %s after %ld steps: contacts %d, missing a ring %d, missing some contact %d, unmet pairs %ld\n",
           n, exact ? "EXACT" : "EARLY-STOP-NOT-REACHED", k - 1, NC, missring, misscontact, exact ? -1L : unmet);
    return 0;
}
