/* Exhaustive listing of side tables (THIRD-HOLDER-20261123-001B-E001, census).
   A side: observer distinctions x1 x2 x3 (each 1..OBSMAX old holders: OBSMAX = 1 is class L, 2 is class S), CUT shared
   distinctions (exactly one holder on this side), I internal distinctions (each 1..HMAX holders), I = 0..IMAX, and 1..KMAX
   knots of 3 or 4 places with law even, odd or not-all-equal, on distinct (members, law) pairs.  Every labelled structure
   is visited (depth-first over increasing knot indices); its side table T[x, s] (the number of completions of the
   internal distinctions) is computed from the bitset of allowed words and inserted into a hash set (exact tables).
   For each table the structure kept is the first with the fewest knots, then fewest extra holders (holders beyond two).

   usage: sides_enum CUT KMAX IMAX OBSMAX HMAX OUTFILE [PART NPARTS]
   (with PART NPARTS only structures whose first knot index is PART modulo NPARTS are visited; the parts are merged by sides.py)
   output (binary, little-endian): int32 N, int32 K, uint8 tables[N][8][K], then per table: int32 I, int32 nk, int32 extra,
   then nk x (int32 arity, int32 law, int32 members[4]); law 0 even, 1 odd, 2 nae; members are distinction indices
   0..2 = x1..x3, 3..3+CUT-1 = s1.., then h1..  Statistics are printed to stdout as JSON lines. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 12
#define MAXW 64   /* 64-bit words: 2^12 bits */
#define MAXK 6

static int CUT, KMAX, IMAX, OBSMAX, HMAX, K, PART = 0, NPARTS = 1;
static int n, I, NB, NWORDS, nq;
static int q_ar[4096], q_law[4096], q_mem[4096][4];
static uint64_t q_bits[4096][MAXW];
static int8_t cap[MAXN];
static int8_t q_inc[4096][MAXN];

/* hash set of tables */
static int TB;                     /* bytes per table = 8*K */
static uint8_t *tabs = NULL; static long ntab = 0, captab = 0;
static int32_t *t_I, *t_nk, *t_extra; static int32_t (*t_knots)[MAXK][6];
static long *hidx = NULL; static long hsize = 0;
static long long nstruct[MAXN + 1][MAXK + 1], newtab[MAXN + 1][MAXK + 1];

static uint64_t hash_bytes(const uint8_t *p, int len) {
    uint64_t h = 1469598103934665603ULL;
    for (int i = 0; i < len; i++) { h ^= p[i]; h *= 1099511628211ULL; }
    h ^= h >> 29; h *= 0xbf58476d1ce4e5b9ULL; h ^= h >> 32;
    return h;
}
static void grow_hash(void) {
    long ns = hsize ? hsize * 2 : (1L << 20);
    long *nh = malloc(sizeof(long) * ns); for (long i = 0; i < ns; i++) nh[i] = -1;
    for (long t = 0; t < ntab; t++) {
        uint64_t h = hash_bytes(tabs + t * TB, TB); long pos = h & (ns - 1);
        while (nh[pos] >= 0) pos = (pos + 1) & (ns - 1);
        nh[pos] = t;
    }
    free(hidx); hidx = nh; hsize = ns;
}
static void grow_tabs(void) {
    long nc = captab ? captab * 2 : (1L << 16);
    tabs = realloc(tabs, nc * TB); t_I = realloc(t_I, nc * 4); t_nk = realloc(t_nk, nc * 4); t_extra = realloc(t_extra, nc * 4);
    t_knots = realloc(t_knots, nc * sizeof(*t_knots)); captab = nc;
}

static int stack_q[MAXK];
static int8_t cnt_stack[MAXK + 1][MAXN];
static uint64_t allow_stack[MAXK + 1][MAXW];

static void record(int depth) {
    /* table from allow_stack[depth] */
    uint8_t T[32];
    const uint64_t *al = allow_stack[depth];
    int seg = 1 << I;                       /* bits per cell */
    for (int cell = 0; cell < 8 * K; cell++) {
        long b0 = (long)cell * seg;
        int c;
        if (seg >= 64) { c = 0; for (int w = 0; w < seg / 64; w++) c += __builtin_popcountll(al[b0 / 64 + w]); }
        else {
            uint64_t m = (seg == 64) ? ~0ULL : ((1ULL << seg) - 1);
            c = __builtin_popcountll((al[b0 / 64] >> (b0 % 64)) & m);
        }
        T[cell] = (uint8_t)c;
    }
    int extra = 0;
    for (int j = 3 + CUT; j < n; j++) if (cnt_stack[depth][j] > 2) extra += cnt_stack[depth][j] - 2;
    if ((ntab + 1) * 2 > hsize) grow_hash();
    uint64_t h = hash_bytes(T, TB); long pos = h & (hsize - 1);
    while (hidx[pos] >= 0) {
        long t = hidx[pos];
        if (memcmp(tabs + t * TB, T, TB) == 0) {
            if (depth < t_nk[t] || (depth == t_nk[t] && extra < t_extra[t])) {
                t_I[t] = I; t_nk[t] = depth; t_extra[t] = extra;
                for (int k = 0; k < depth; k++) { int q = stack_q[k]; t_knots[t][k][0] = q_ar[q]; t_knots[t][k][1] = q_law[q];
                    for (int u = 0; u < 4; u++) t_knots[t][k][2 + u] = u < q_ar[q] ? q_mem[q][u] : -1; }
            }
            return;
        }
        pos = (pos + 1) & (hsize - 1);
    }
    if (ntab >= captab) grow_tabs();
    memcpy(tabs + ntab * TB, T, TB);
    t_I[ntab] = I; t_nk[ntab] = depth; t_extra[ntab] = extra;
    for (int k = 0; k < depth; k++) { int q = stack_q[k]; t_knots[ntab][k][0] = q_ar[q]; t_knots[ntab][k][1] = q_law[q];
        for (int u = 0; u < 4; u++) t_knots[ntab][k][2 + u] = u < q_ar[q] ? q_mem[q][u] : -1; }
    hidx[pos] = ntab; ntab++;
    newtab[I][depth]++;
}

static void dfs(int depth, int start) {
    /* depth = number of knots already chosen */
    for (int q = start; q < nq; q++) {
        if (depth == 0 && (q % NPARTS) != PART) continue;
        int ok = 1;
        for (int j = 0; j < n; j++) { int v = cnt_stack[depth][j] + q_inc[q][j]; if (v > cap[j]) { ok = 0; break; } cnt_stack[depth + 1][j] = v; }
        if (!ok) continue;
        for (int w = 0; w < NWORDS; w++) allow_stack[depth + 1][w] = allow_stack[depth][w] & q_bits[q][w];
        stack_q[depth] = q;
        int unc = 0;
        for (int j = 0; j < n; j++) if (cnt_stack[depth + 1][j] == 0) unc++;
        if (unc == 0) { nstruct[I][depth + 1]++; record(depth + 1); }
        if (depth + 1 < KMAX && unc <= 4 * (KMAX - depth - 1)) dfs(depth + 1, q + 1);
    }
}

static int bitpos(int j) {             /* bit of the word index that holds distinction j */
    if (j < 3) return CUT + I + 2 - j;
    if (j < 3 + CUT) return I + (CUT - 1 - (j - 3));
    return I - 1 - (j - 3 - CUT);
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 1; }
    CUT = atoi(argv[1]); KMAX = atoi(argv[2]); IMAX = atoi(argv[3]); OBSMAX = atoi(argv[4]); HMAX = atoi(argv[5]);
    const char *out = argv[6];
    if (argc >= 9) { PART = atoi(argv[7]); NPARTS = atoi(argv[8]); }
    K = 1 << CUT; TB = 8 * K;
    memset(nstruct, 0, sizeof nstruct); memset(newtab, 0, sizeof newtab);
    clock_t t0 = clock();
    for (I = 0; I <= IMAX; I++) {
        n = 3 + CUT + I; NB = 1 << n; NWORDS = NB >= 64 ? NB / 64 : 1;
        for (int j = 0; j < n; j++) cap[j] = j < 3 ? OBSMAX : (j < 3 + CUT ? 1 : HMAX);
        nq = 0;
        for (int ar = 3; ar <= 4; ar++) {
            int idx[4];
            for (idx[0] = 0; idx[0] < n; idx[0]++) for (idx[1] = idx[0] + 1; idx[1] < n; idx[1]++) for (idx[2] = idx[1] + 1; idx[2] < n; idx[2]++)
            for (idx[3] = (ar == 4 ? idx[2] + 1 : n); idx[3] < (ar == 4 ? n : n + 1); idx[3]++) {
                for (int law = 0; law < 3; law++) {
                    q_ar[nq] = ar; q_law[nq] = law;
                    memset(q_inc[nq], 0, MAXN);
                    for (int u = 0; u < ar; u++) { q_mem[nq][u] = idx[u]; q_inc[nq][idx[u]] = 1; }
                    memset(q_bits[nq], 0, sizeof(q_bits[nq]));
                    for (int w = 0; w < NB; w++) {
                        int s = 0;
                        for (int u = 0; u < ar; u++) s += (w >> bitpos(idx[u])) & 1;
                        int good = law == 2 ? (s != 0 && s != ar) : (law == 0 ? (s % 2 == 0) : (s % 2 == 1));
                        if (good) q_bits[nq][w / 64] |= 1ULL << (w % 64);
                    }
                    nq++;
                }
            }
        }
        for (int j = 0; j < n; j++) cnt_stack[0][j] = 0;
        for (int w = 0; w < NWORDS; w++) allow_stack[0][w] = (NB >= 64) ? ~0ULL : ((1ULL << NB) - 1);
        dfs(0, 0);
        for (int d = 1; d <= KMAX; d++)
            printf("{\"cut\": %d, \"internal\": %d, \"knots\": %d, \"structures\": %lld, \"new_tables\": %lld, \"knot_types\": %d, \"cpu_seconds\": %.1f}\n",
                   CUT, I, d, nstruct[I][d], newtab[I][d], nq, (double)(clock() - t0) / CLOCKS_PER_SEC);
        fflush(stdout);
    }
    FILE *f = fopen(out, "wb");
    int32_t N32 = (int32_t)ntab, K32 = K; fwrite(&N32, 4, 1, f); fwrite(&K32, 4, 1, f);
    fwrite(tabs, TB, ntab, f);
    for (long t = 0; t < ntab; t++) {
        fwrite(&t_I[t], 4, 1, f); fwrite(&t_nk[t], 4, 1, f); fwrite(&t_extra[t], 4, 1, f);
        for (int k = 0; k < t_nk[t]; k++) fwrite(t_knots[t][k], 4, 6, f);
    }
    fclose(f);
    long long tot = 0; for (int i = 0; i <= IMAX; i++) for (int d = 1; d <= KMAX; d++) tot += nstruct[i][d];
    printf("{\"done\": true, \"tables\": %ld, \"structures\": %lld, \"cpu_seconds\": %.1f}\n", ntab, tot, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
