/* SEP-LEFT-20261110-001B-E001: how much of a space of monomials meets the degree-D polynomial calculus over F2?

   cc -O3 -march=native -o pcsep pcsep.c
   ./pcsep D MEM_MIB < input     reads "n m", then m lines "t mask_1 ... mask_t" (the axioms: multilinear polynomials over F2, monomials
                                 as bit masks of at most 64 variables), then "s" and s probe sets, each "p" and p monomials (masks of
                                 degree at most D); prints one line of JSON

   The closure is PC-COUNT-20261110-001B-E001's (pcdeg.c, mode pc): lines are multilinear polynomials of degree at most D, a line of
   degree at most D - 1 may be multiplied by a variable (the standard rule), kept in semi-echelon form with columns ordered by degree,
   highest first. Then each probe set's monomials are inserted one at a time; "new" counts those independent of the closure and of
   the set's earlier monomials, so the set's span meets the closure in dimension p - new. The closure is restored after each set. Rows are dense bit vectors allocated as the
   rank grows; a run that would pass MEM_MIB stops and says so, deciding nothing. */
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

static void enum_deg(int start, uint64_t m, int left) {
    if (left == 0) { colmask[NC++] = m; return; }
    for (int v = start; v <= n - left; v++) enum_deg(v + 1, m | (1ULL << v), left - 1);
}

static int reduce(uint64_t *v) {
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

static int insert(uint64_t *v) {
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
    if (argc < 3) { fprintf(stderr, "usage: pcsep D MEM_MIB < input\n"); return 2; }
    D = atoi(argv[1]);
    double mem = atof(argv[2]) * 1048576.0;
    int m;
    if (scanf("%d %d", &n, &m) != 2) return 2;
    long long ncols = 0;
    { long long b = 1; for (int d = 0; d <= D; d++) { ncols += b; b = b * (n - d) / (d + 1); } }
    double fixed = (double)ncols * 40.0, rowbytes = (double)((ncols + 63) / 64) * 8.0;
    uint64_t **ax = malloc(sizeof(uint64_t *) * m); int *axt = malloc(sizeof(int) * m), *axd = malloc(sizeof(int) * m);
    for (int i = 0; i < m; i++) {
        if (scanf("%d", &axt[i]) != 1) return 2;
        ax[i] = malloc(sizeof(uint64_t) * axt[i]); axd[i] = 0;
        for (int j = 0; j < axt[i]; j++) { unsigned long long x; if (scanf("%llu", &x) != 1) return 2; ax[i][j] = x;
            if (__builtin_popcountll(x) > axd[i]) axd[i] = __builtin_popcountll(x); }
    }
    int ns; if (scanf("%d", &ns) != 1) return 2;
    int *pn = malloc(sizeof(int) * (ns ? ns : 1)); uint64_t **probe = malloc(sizeof(uint64_t *) * (ns ? ns : 1));
    for (int s = 0; s < ns; s++) {
        if (scanf("%d", &pn[s]) != 1) return 2;
        probe[s] = malloc(sizeof(uint64_t) * (pn[s] ? pn[s] : 1));
        for (int i = 0; i < pn[s]; i++) { unsigned long long x; if (scanf("%llu", &x) != 1) return 2; probe[s][i] = x; }
    }
    if (fixed + 2 * rowbytes > mem) { printf("{\"D\": %d, \"columns\": %lld, \"skipped\": \"memory cap\"}\n", D, ncols); return 0; }
    maxrows = (size_t)((mem - fixed) / rowbytes) - 1;
    if (maxrows > (size_t)ncols) maxrows = (size_t)ncols;
    colmask = malloc(sizeof(uint64_t) * ncols);
    NC = 0;
    for (int d = D; d >= 0; d--) enum_deg(0, 0, d);
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
    for (int i = 0; i < m && pivot[cst] < 0 && !full; i++) {
        if (axd[i] > D) continue;
        memset(v, 0, sizeof(uint64_t) * W);
        for (int j = 0; j < axt[i]; j++) toggle(v, ax[i][j]);
        insert(v);
    }
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
        printf("{\"D\": %d, \"columns\": %d, \"rank\": %d, \"skipped\": \"memory cap reached\", \"cpu_seconds\": %.2f}\n",
               D, NC, nrows, (double)(clock() - t0) / CLOCKS_PER_SEC);
        return 0;
    }
    int refuted = pivot[cst] >= 0, rank = nrows;
    printf("{\"D\": %d, \"columns\": %d, \"rank\": %d, \"products\": %lld, \"refuted\": %s, \"probes\": [", D, NC, rank, products,
           refuted ? "true" : "false");
    for (int s = 0; s < ns; s++) {
        long long fresh = 0;
        if (!refuted)
            for (int i = 0; i < pn[s]; i++) {
                memset(v, 0, sizeof(uint64_t) * W);
                toggle(v, probe[s][i]);
                if (reduce(v) >= 0) {                  /* new: keep it, so the set's later monomials count modulo it */
                    if (!insert(v)) { printf("]}\n{\"skipped\": \"memory cap reached in the probe\"}\n"); return 0; }
                    fresh++;
                }
            }
        for (int r = rank; r < nrows; r++) pivot[lead[r]] = -1;   /* restore the closure */
        nrows = rank;
        printf("%s[%d, %lld]", s ? ", " : "", pn[s], refuted ? 0LL : fresh);
    }
    printf("], \"cpu_seconds\": %.2f}\n", (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
