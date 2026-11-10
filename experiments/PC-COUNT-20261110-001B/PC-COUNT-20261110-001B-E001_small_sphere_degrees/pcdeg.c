/* PC-COUNT-20261110-001B-E001: is 1 derivable at degree D over F2, by the Nullstellensatz or the polynomial calculus?

   cc -O3 -march=native -o pcdeg pcdeg.c
   ./pcdeg MODE D MEM_MIB < axioms     MODE is ns or pc; reads "n m" then m lines "t mask_1 ... mask_t" (multilinear polynomials over
                                        F2, monomials as bit masks of at most 64 variables); prints one line of JSON

   Lines are multilinear polynomials of degree at most D over F2 (x^2 = x). ns: the span of m * a over axioms a and monomials m with
   deg(m * a) <= D. pc (the standard rule): the smallest space containing the axioms of degree <= D and closed under multiplying a line
   of degree <= D - 1 by a variable. Both are kept in semi-echelon form with columns ordered by degree, highest first, so a line's
   leading column is its highest monomial, every line of degree <= D - 1 is a sum of basis rows of degree <= D - 1, and multiplying
   those rows by every variable closes the space. 1 lies in it exactly when the constant column, the last, becomes a pivot. Rows are
   dense bit vectors, allocated as the rank grows; a run that would pass MEM_MIB stops and says so, deciding nothing. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int n, D, NC, W;
static uint64_t *colmask, *hkeys;
static int *hvals, *pivot, *lead, *rend, nrows, cap, full;
static uint64_t *rows;
static size_t hsize, maxrows;

static size_t hslot(uint64_t m) {
    size_t h = (size_t)((m * 0x9E3779B97F4A7C15ULL) >> 17) & (hsize - 1);
    while (hkeys[h] != ~0ULL && hkeys[h] != m) h = (h + 1) & (hsize - 1);
    return h;
}
static int col_of(uint64_t m) { size_t h = hslot(m); return hkeys[h] == m ? hvals[h] : -1; }

static void enum_deg(int d, int start, uint64_t m, int left) {  /* all masks of popcount d, appended in order */
    if (left == 0) { colmask[NC++] = m; return; }
    for (int v = start; v <= n - left; v++) enum_deg(d, v + 1, m | (1ULL << v), left - 1);
}

static int reduce(uint64_t *v) {                     /* reduce against the pivots; the new leading column, or -1 */
    for (int w = 0; w < W; w++)
        while (v[w]) {
            int c = w * 64 + __builtin_ctzll(v[w]);
            int r = pivot[c];
            if (r < 0) return c;
            uint64_t *R = rows + (size_t)r * W;
            for (int j = w; j < rend[r]; j++) v[j] ^= R[j];
        }
    return -1;
}

static int insert(uint64_t *v) {                     /* 1 when v was new */
    int c = reduce(v);
    if (c < 0) return 0;
    int e = W;
    while (e > 0 && v[e - 1] == 0) e--;
    if (nrows == cap) {
        if ((size_t)cap >= maxrows) { full = 1; return 0; }
        size_t nc = (size_t)cap * 2 < maxrows ? (size_t)cap * 2 : maxrows;
        uint64_t *nr = realloc(rows, sizeof(uint64_t) * nc * W);
        if (!nr) { full = 1; return 0; }
        rows = nr; cap = (int)nc;
    }
    memcpy(rows + (size_t)nrows * W, v, sizeof(uint64_t) * W);
    pivot[c] = nrows; lead[nrows] = c; rend[nrows] = e; nrows++;
    return 1;
}

static void toggle(uint64_t *v, uint64_t m) { int c = col_of(m); v[c >> 6] ^= 1ULL << (c & 63); }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: pcdeg ns|pc D MEM_MIB < axioms\n"); return 2; }
    int pc = strcmp(argv[1], "pc") == 0;
    D = atoi(argv[2]);
    double mem = atof(argv[3]) * 1048576.0;
    int m;
    if (scanf("%d %d", &n, &m) != 2) return 2;
    long long ncols = 0;                              /* sum of binomials C(n, d), d <= D */
    { long long b = 1; for (int d = 0; d <= D; d++) { ncols += b; b = b * (n - d) / (d + 1); } }
    double fixed = (double)ncols * 40.0;               /* masks, hash table, pivot and row tables */
    double rowbytes = (double)((ncols + 63) / 64) * 8.0;
    if (fixed + 2 * rowbytes > mem) { printf("{\"mode\": \"%s\", \"D\": %d, \"columns\": %lld, \"skipped\": \"memory cap\"}\n", argv[1], D, ncols); return 0; }
    maxrows = (size_t)((mem - fixed) / rowbytes) - 1;
    if (maxrows > (size_t)ncols) maxrows = (size_t)ncols;
    colmask = malloc(sizeof(uint64_t) * ncols);
    NC = 0;
    for (int d = D; d >= 0; d--) enum_deg(d, 0, 0, d);
    W = (NC + 63) / 64;
    hsize = 1; while (hsize < 2 * (size_t)NC) hsize <<= 1;
    hkeys = malloc(sizeof(uint64_t) * hsize); hvals = malloc(sizeof(int) * hsize);
    memset(hkeys, 0xff, sizeof(uint64_t) * hsize);
    for (int c = 0; c < NC; c++) { size_t h = hslot(colmask[c]); hkeys[h] = colmask[c]; hvals[h] = c; }
    cap = maxrows < 1024 ? (int)maxrows : 1024; full = 0;
    rows = malloc(sizeof(uint64_t) * (size_t)cap * W);
    pivot = malloc(sizeof(int) * NC); lead = malloc(sizeof(int) * NC); rend = malloc(sizeof(int) * NC);
    for (int c = 0; c < NC; c++) pivot[c] = -1;
    nrows = 0;
    uint64_t *v = malloc(sizeof(uint64_t) * W);
    clock_t t0 = clock();
    long long products = 0;
    int cst = col_of(0);
    for (int i = 0; i < m; i++) {
        int t; if (scanf("%d", &t) != 1) return 2;
        uint64_t *ax = malloc(sizeof(uint64_t) * t), sup = 0; int deg = 0;
        for (int j = 0; j < t; j++) { unsigned long long x; if (scanf("%llu", &x) != 1) return 2; ax[j] = x; sup |= x;
            if (__builtin_popcountll(x) > deg) deg = __builtin_popcountll(x); }
        if (deg > D) { free(ax); continue; }
        if (!pc) {                                     /* every m * a with m outside a's variables and deg(m * a) <= D */
            int free_vars[64], nf = 0;
            for (int x = 0; x < n; x++) if (!((sup >> x) & 1)) free_vars[nf++] = x;
            int room = D - deg;
            /* enumerate subsets of free_vars of size <= room */
            int idx[64], k;
            for (int s = 0; s <= room; s++) {
                for (k = 0; k < s; k++) idx[k] = k;
                if (s > nf) break;
                while (1) {
                    uint64_t mm = 0; for (k = 0; k < s; k++) mm |= 1ULL << free_vars[idx[k]];
                    memset(v, 0, sizeof(uint64_t) * W);
                    for (int j = 0; j < t; j++) toggle(v, ax[j] | mm);
                    insert(v); products++;
                    for (k = s - 1; k >= 0 && idx[k] == nf - s + k; k--);
                    if (k < 0) break;
                    idx[k]++; for (int q = k + 1; q < s; q++) idx[q] = idx[q - 1] + 1;
                }
            }
        } else {
            memset(v, 0, sizeof(uint64_t) * W);
            for (int j = 0; j < t; j++) toggle(v, ax[j]);
            insert(v);
        }
        free(ax);
        if (pivot[cst] >= 0 || full) break;
    }
    if (pc)
        for (int q = 0; q < nrows && pivot[cst] < 0 && !full; q++) {
            if (__builtin_popcountll(colmask[lead[q]]) > D - 1) continue;
            for (int x = 0; x < n && pivot[cst] < 0 && !full; x++) {
                memset(v, 0, sizeof(uint64_t) * W);
                uint64_t *R = rows + (size_t)q * W;
                for (int w = lead[q] >> 6; w < rend[q]; w++) {
                    uint64_t b = R[w];
                    while (b) { int c = w * 64 + __builtin_ctzll(b); b &= b - 1; toggle(v, colmask[c] | (1ULL << x)); }
                }
                insert(v); products++;
            }
        }
    if (full && pivot[cst] < 0) {
        printf("{\"mode\": \"%s\", \"D\": %d, \"columns\": %d, \"rank\": %d, \"products\": %lld, \"skipped\": \"memory cap reached\", \"cpu_seconds\": %.2f}\n",
               argv[1], D, NC, nrows, products, (double)(clock() - t0) / CLOCKS_PER_SEC);
        return 0;
    }
    printf("{\"mode\": \"%s\", \"D\": %d, \"columns\": %d, \"rank\": %d, \"products\": %lld, \"refuted\": %s, \"cpu_seconds\": %.2f}\n",
           argv[1], D, NC, nrows, products, pivot[cst] >= 0 ? "true" : "false", (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
