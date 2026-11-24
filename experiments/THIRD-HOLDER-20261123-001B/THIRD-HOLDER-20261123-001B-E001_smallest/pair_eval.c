/* Evaluation of many pairs of side tables (THIRD-HOLDER-20261123-001B-E001), called by pairs.py.
   For every compatible pair of classes (gA, gB) in [Q0, Q1) and every Alice table a of group gA and Bob table b of group gB:
   M = T_A[a] T_B[b]^T (exact integers); pairs with no allowed old word are counted; M is divided by the gcd of its entries;
   hiding is tested exactly in integers (M W0 || M W1 and M^T W0 || M^T W1); a hidden M is brought to the lexicographically
   smallest of its 32 images under the symmetries of the evaluation (swap x2<->x3 and flip all three old values, on each
   side, and exchange of the observers), deduplicated by a 128-bit hash of that form, and every new one is scored with the
   same float arithmetic as chsh_kernel.c (best four-correlation value over the 15^4 parity outcome choices and the four
   sign patterns); an old table whose four largest |correlations| sum to less than 2 - 1e-9 is counted as below 2 without the
   full maximisation (the score is at most that sum).  Old tables scoring at least 2 - 1e-9 are written out (with the smallest pair, by knots then extra
   holders, among the pairs giving them) for exact checking in Python.

   usage: pair_eval INFILE OUTPREFIX Q0 Q1
   INFILE (int32 little-endian): K, NA, NB, NG_A, NG_B, NQ, then TA[NA][8][K], TB[NB][8][K], kA[NA], eA[NA], kB[NB], eB[NB],
   offA[NG_A+1], memA[offA[NG_A]], offB[NG_B+1], memB[offB[NG_B]], qA[NQ], qB[NQ]; then doubles C[2][15][8], W[2][8].
   Output: OUTPREFIX.json (counts) and OUTPREFIX.near (int32 records: 64 entries of M, a, b, knots, extra, pairs). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int K, NA, NB, NGA, NGB, NQ;
static int32_t *TA, *TB, *kA, *eA, *kB, *eB, *offA, *memA, *offB, *memB, *qA, *qB;
static double Cc[2][15][8], Wd[2][8];
static int64_t Wi[2][8];
static int perm_row[4][8];

typedef struct { uint64_t h1, h2; int32_t near; } Entry;
static Entry *tab = NULL; static long tsize = 0, tcount = 0;

typedef struct { int32_t M[64]; int32_t a, b, kn, ex; int64_t pairs; double score; } Near;
static Near *nearv = NULL; static long nnear = 0, cnear = 0;

static uint64_t mix(uint64_t h) { h ^= h >> 33; h *= 0xff51afd7ed558ccdULL; h ^= h >> 33; h *= 0xc4ceb9fe1a85ec53ULL; h ^= h >> 33; return h; }

static void grow(void) {
    long ns = tsize ? tsize * 2 : (1L << 22);
    Entry *nt = calloc(ns, sizeof(Entry));
    for (long i = 0; i < tsize; i++) if (tab[i].h1 | tab[i].h2) {
        long p = tab[i].h1 & (ns - 1);
        while (nt[p].h1 | nt[p].h2) p = (p + 1) & (ns - 1);
        nt[p] = tab[i];
    }
    free(tab); tab = nt; tsize = ns;
}

static long long n_screened = 0;
static double best_score(const int64_t *M, int *screened) {
    double E[4][15][15];
    *screened = 0;
    for (int a = 0; a < 2; a++) for (int b = 0; b < 2; b++) {
        double den = 0.0;
        for (int x = 0; x < 8; x++) for (int y = 0; y < 8; y++) den += Wd[a][x] * (double)M[8 * x + y] * Wd[b][y];
        for (int k = 0; k < 15; k++) {
            double tmp[8];
            for (int y = 0; y < 8; y++) { double s = 0.0; for (int x = 0; x < 8; x++) s += Cc[a][k][x] * (double)M[8 * x + y]; tmp[y] = s; }
            for (int l = 0; l < 15; l++) { double s = 0.0; for (int y = 0; y < 8; y++) s += tmp[y] * Cc[b][l][y]; E[2 * a + b][k][l] = s / den; }
        }
    }
    /* screen: the score is at most the sum over the four settings of the largest |correlation| */
    double bound = 0.0;
    for (int t = 0; t < 4; t++) { double m = 0.0; for (int k = 0; k < 15; k++) for (int l = 0; l < 15; l++) { double v = E[t][k][l] < 0 ? -E[t][k][l] : E[t][k][l]; if (v > m) m = v; } bound += m; }
    if (bound < 2.0 - 1e-9) { *screened = 1; return bound; }
    double best = 0.0;
    for (int p = 0; p < 4; p++) {
        double s[4] = {1.0, 1.0, 1.0, 1.0}; s[p] = -1.0;
        for (int k0 = 0; k0 < 15; k0++) for (int k1 = 0; k1 < 15; k1++) {
            double umax = -1e300, umin = 1e300, vmax = -1e300, vmin = 1e300;
            for (int l = 0; l < 15; l++) {
                double u = s[0] * E[0][k0][l] + s[2] * E[2][k1][l];
                double v = s[1] * E[1][k0][l] + s[3] * E[3][k1][l];
                if (u > umax) umax = u; if (u < umin) umin = u;
                if (v > vmax) vmax = v; if (v < vmin) vmin = v;
            }
            double c1 = umax + vmax, c2 = -(umin + vmin);
            if (c1 > best) best = c1; if (c2 > best) best = c2;
        }
    }
    return best;
}

static int64_t gcd64(int64_t a, int64_t b) { while (b) { int64_t t = a % b; a = b; b = t; } return a < 0 ? -a : a; }

static int parallel(const int64_t *u, const int64_t *v, int n) {
    int64_t su = 0, sv = 0;
    for (int i = 0; i < n; i++) { su += u[i]; sv += v[i]; }
    for (int i = 0; i < n; i++) if ((__int128)u[i] * sv != (__int128)v[i] * su) return 0;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 1; }
    FILE *f = fopen(argv[1], "rb");
    int32_t hdr[6]; if (fread(hdr, 4, 6, f) != 6) return 2;
    K = hdr[0]; NA = hdr[1]; NB = hdr[2]; NGA = hdr[3]; NGB = hdr[4]; NQ = hdr[5];
#define RD(ptr, n) do { ptr = malloc(sizeof(int32_t) * ((n) > 0 ? (n) : 1)); if ((long)fread(ptr, 4, (n), f) != (long)(n)) return 3; } while (0)
    RD(TA, (long)NA * 8 * K); RD(TB, (long)NB * 8 * K); RD(kA, NA); RD(eA, NA); RD(kB, NB); RD(eB, NB);
    RD(offA, NGA + 1); RD(memA, offA[NGA]); RD(offB, NGB + 1); RD(memB, offB[NGB]); RD(qA, NQ); RD(qB, NQ);
    if (fread(Cc, 8, 240, f) != 240) return 4; if (fread(Wd, 8, 16, f) != 16) return 5;
    fclose(f);
    for (int a = 0; a < 2; a++) for (int x = 0; x < 8; x++) Wi[a][x] = (int64_t)Wd[a][x];
    for (int x = 0; x < 8; x++) {
        int sw = ((x >> 2) & 1) * 4 + (x & 1) * 2 + ((x >> 1) & 1);
        perm_row[0][x] = x; perm_row[1][x] = sw; perm_row[2][x] = 7 - x; perm_row[3][x] = ((7 - x) >> 2 & 1) * 4 + ((7 - x) & 1) * 2 + (((7 - x) >> 1) & 1);
    }
    long Q0 = atol(argv[3]), Q1 = atol(argv[4]); if (Q1 > NQ) Q1 = NQ;
    long long n_pairs = 0, n_zero = 0, n_hidden = 0, n_hidA_only = 0, n_unique = 0, n_ge2 = 0, n_gt2f = 0;
    double max_score = 0.0;
    long long hist[401]; memset(hist, 0, sizeof hist);
    clock_t t0 = clock();
    grow();
    int64_t M[64], Mc[64], img[64];
    for (long q = Q0; q < Q1; q++) {
        int ga = qA[q], gb = qB[q];
        for (int ia = offA[ga]; ia < offA[ga + 1]; ia++) {
            int a = memA[ia]; const int32_t *A = TA + (long)a * 8 * K;
            for (int ib = offB[gb]; ib < offB[gb + 1]; ib++) {
                int b = memB[ib]; const int32_t *B = TB + (long)b * 8 * K;
                n_pairs++;
                int64_t g = 0;
                for (int x = 0; x < 8; x++) for (int y = 0; y < 8; y++) {
                    int64_t s = 0; for (int k = 0; k < K; k++) s += (int64_t)A[x * K + k] * B[y * K + k];
                    M[8 * x + y] = s; g = gcd64(g, s);
                }
                if (g == 0) { n_zero++; continue; }
                if (g > 1) for (int i = 0; i < 64; i++) M[i] /= g;
                int64_t u0[8], u1[8], v0[8], v1[8];
                for (int x = 0; x < 8; x++) { u0[x] = u1[x] = 0; for (int y = 0; y < 8; y++) { u0[x] += M[8 * x + y] * Wi[0][y]; u1[x] += M[8 * x + y] * Wi[1][y]; } }
                for (int y = 0; y < 8; y++) { v0[y] = v1[y] = 0; for (int x = 0; x < 8; x++) { v0[y] += M[8 * x + y] * Wi[0][x]; v1[y] += M[8 * x + y] * Wi[1][x]; } }
                int hA = parallel(u0, u1, 8), hB = parallel(v0, v1, 8);
                if (!(hA && hB)) { if (hA) n_hidA_only++; continue; }
                n_hidden++;
                /* lexicographically smallest image */
                int have = 0;
                for (int t = 0; t < 2; t++) for (int pa = 0; pa < 4; pa++) for (int pb = 0; pb < 4; pb++) {
                    for (int x = 0; x < 8; x++) for (int y = 0; y < 8; y++)
                        img[8 * x + y] = t == 0 ? M[8 * perm_row[pa][x] + perm_row[pb][y]] : M[8 * perm_row[pb][y] + perm_row[pa][x]];
                    if (!have) { memcpy(Mc, img, sizeof Mc); have = 1; continue; }
                    for (int i = 0; i < 64; i++) { if (img[i] < Mc[i]) { memcpy(Mc, img, sizeof Mc); break; } if (img[i] > Mc[i]) break; }
                }
                uint64_t h1 = 0x9e3779b97f4a7c15ULL, h2 = 0x6a09e667f3bcc909ULL;
                for (int i = 0; i < 64; i++) { h1 = mix(h1 ^ (uint64_t)Mc[i] ^ ((uint64_t)i << 40)); h2 = mix(h2 + (uint64_t)Mc[i] * 0x100000001b3ULL + i); }
                if (h1 == 0 && h2 == 0) h1 = 1;
                if ((tcount + 1) * 2 > tsize) grow();
                long p = h1 & (tsize - 1);
                while ((tab[p].h1 | tab[p].h2) && !(tab[p].h1 == h1 && tab[p].h2 == h2)) p = (p + 1) & (tsize - 1);
                int kn = kA[a] + kB[b], ex = eA[a] + eB[b];
                if (tab[p].h1 | tab[p].h2) {
                    int ni = tab[p].near;
                    if (ni >= 0) {
                        Near *nv = &nearv[ni]; nv->pairs++;
                        if (kn < nv->kn || (kn == nv->kn && ex < nv->ex)) { nv->kn = kn; nv->ex = ex; nv->a = a; nv->b = b; }
                    }
                    continue;
                }
                tab[p].h1 = h1; tab[p].h2 = h2; tab[p].near = -1; tcount++; n_unique++;
                int scr; double sc = best_score(Mc, &scr);
                if (scr) { n_screened++; continue; }
                if (sc > max_score) max_score = sc;
                int hb = (int)(sc * 100.0 + 1e-9); if (hb > 400) hb = 400; if (hb < 0) hb = 0; hist[hb]++;
                if (sc >= 2.0 - 1e-9) {
                    n_ge2++; if (sc > 2.0 + 1e-9) n_gt2f++;
                    if (nnear >= cnear) { cnear = cnear ? cnear * 2 : 4096; nearv = realloc(nearv, cnear * sizeof(Near)); }
                    Near *nv = &nearv[nnear];
                    for (int i = 0; i < 64; i++) nv->M[i] = (int32_t)Mc[i];
                    nv->a = a; nv->b = b; nv->kn = kn; nv->ex = ex; nv->pairs = 1; nv->score = sc;
                    tab[p].near = (int32_t)nnear; nnear++;
                }
            }
        }
    }
    char fn[4096];
    snprintf(fn, sizeof fn, "%s.near", argv[2]);
    FILE *g = fopen(fn, "wb");
    for (long i = 0; i < nnear; i++) {
        int32_t rec[70]; memcpy(rec, nearv[i].M, 256); rec[64] = nearv[i].a; rec[65] = nearv[i].b; rec[66] = nearv[i].kn; rec[67] = nearv[i].ex;
        int64_t pr = nearv[i].pairs; memcpy(rec + 68, &pr, 8);
        fwrite(rec, 4, 70, g);
    }
    fclose(g);
    snprintf(fn, sizeof fn, "%s.json", argv[2]);
    g = fopen(fn, "w");
    fprintf(g, "{\"class_pairs\": [%ld, %ld], \"pairs\": %lld, \"pairs_no_word\": %lld, \"pairs_hidden\": %lld, \"pairs_alice_hidden_only\": %lld, "
               "\"unique_hidden_M\": %lld, \"unique_screened_below2\": %lld, \"unique_ge2_float\": %lld, \"unique_gt2_float\": %lld, \"max_score_float\": %.17g, \"cpu_seconds\": %.1f, \"hist_score_x100\": [",
            Q0, Q1, n_pairs, n_zero, n_hidden, n_hidA_only, n_unique, n_screened, n_ge2, n_gt2f, max_score, (double)(clock() - t0) / CLOCKS_PER_SEC);
    for (int i = 0; i <= 400; i++) fprintf(g, "%s%lld", i ? ", " : "", hist[i]);
    fprintf(g, "]}\n");
    fclose(g);
    return 0;
}
