/* Per-skeleton counts for target events of twisted double covers.

   Input (stdin): as labels.c (V E K, edges "u w o_1..o_K", S, twist vectors), followed by "T" and T lines "s label".
   Usage: skel exh LO HI
   For every orientation in [LO, HI) and every target (sector s, label), if the orientation has that label in sector s, the bitmask
   of its cyclic edges (its skeleton) is tallied. Output: "K t mask=count" for every target t and skeleton met. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 160
#define MAXE 480
#define MAXK 4
#define MAXS 16
#define MAXG 512
#define LABLEN 512

static int V, E, K, S;
static int eu[MAXE], ew[MAXE], eo[MAXE][MAXK], tw[MAXS][MAXE], sa[MAXS][MAXK];
static int head[2 * MAXV], nxt[4 * MAXE], to[4 * MAXE], na;
static int idx[2 * MAXV], low[2 * MAXV], comp[2 * MAXV], onst[2 * MAXV], stk[2 * MAXV], sp, cnt, ncomp;
static int cs_v[2 * MAXV], cs_e[2 * MAXV];

static void add(int a, int b) { to[na] = b; nxt[na] = head[a]; head[a] = na++; }

static void tarjan(int n) {
    for (int i = 0; i < n; i++) { idx[i] = -1; onst[i] = 0; }
    cnt = 0; sp = 0; ncomp = 0;
    for (int r = 0; r < n; r++) {
        if (idx[r] >= 0) continue;
        int top = 0;
        cs_v[0] = r; cs_e[0] = head[r]; idx[r] = low[r] = cnt++; stk[sp++] = r; onst[r] = 1;
        while (top >= 0) {
            int v = cs_v[top], e = cs_e[top];
            if (e >= 0) {
                cs_e[top] = nxt[e];
                int w = to[e];
                if (idx[w] < 0) { top++; cs_v[top] = w; cs_e[top] = head[w]; idx[w] = low[w] = cnt++; stk[sp++] = w; onst[w] = 1; }
                else if (onst[w] && idx[w] < low[v]) low[v] = idx[w];
            } else {
                if (low[v] == idx[v]) { int w; do { w = stk[--sp]; onst[w] = 0; comp[w] = ncomp; } while (w != v); ncomp++; }
                top--;
                if (top >= 0) { int u = cs_v[top]; if (low[v] < low[u]) low[u] = low[v]; }
            }
        }
    }
}

static int par[MAXV];
static long long pot[MAXV][MAXK];
static int findp(int x, long long *acc) {
    for (int k = 0; k < K; k++) acc[k] = 0;
    while (par[x] != x) { for (int k = 0; k < K; k++) acc[k] += pot[x][k]; x = par[x]; }
    return x;
}
static int findr(int x) { while (par[x] != x) x = par[x]; return x; }
static long long gabs(long long a) { return a < 0 ? -a : a; }

/* Hermite normal form of the integer row space of m (n rows, K columns), in place; returns the rank. Rows with leading entries
   positive, entries above each pivot reduced into [0, pivot). */
static int hnf(long long m[][MAXK], int n) {
    int r = 0;
    for (int c = 0; c < K && r < n; c++) {
        /* bring a gcd into row r using the Euclidean algorithm on column c among rows r..n-1 */
        for (;;) {
            int piv = -1;
            for (int i = r; i < n; i++) if (m[i][c] != 0 && (piv < 0 || gabs(m[i][c]) < gabs(m[piv][c]))) piv = i;
            if (piv < 0) break;
            if (piv != r) for (int k = 0; k < K; k++) { long long t = m[r][k]; m[r][k] = m[piv][k]; m[piv][k] = t; }
            int done = 1;
            for (int i = r + 1; i < n; i++) {
                if (m[i][c] != 0) {
                    long long f = m[i][c] / m[r][c];
                    for (int k = 0; k < K; k++) m[i][k] -= f * m[r][k];
                    if (m[i][c] != 0) done = 0;
                }
            }
            if (done) break;
        }
        if (m[r][c] == 0) continue;
        if (m[r][c] < 0) for (int k = 0; k < K; k++) m[r][k] = -m[r][k];
        for (int i = 0; i < r; i++) {
            long long f = m[i][c] / m[r][c];
            if (m[i][c] - f * m[r][c] < 0) f--;
            for (int k = 0; k < K; k++) m[i][k] -= f * m[r][k];
        }
        r++;
    }
    return r;
}

#define MAXT 4096
static int T, tsec[MAXT]; static char *tlab[MAXT]; static int need[MAXS];
typedef struct { uint64_t key; unsigned long long count; int used; } kentry;
static kentry *ktab; static size_t ksize, kused;
static uint64_t mix64(uint64_t z) { z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
static void kbump(uint64_t key) {
    if (kused * 2 >= ksize) {
        size_t nsz = ksize ? ksize * 2 : (1 << 16);
        kentry *nt = calloc(nsz, sizeof(kentry));
        for (size_t i = 0; i < ksize; i++) if (ktab[i].used) {
            size_t j = mix64(ktab[i].key) & (nsz - 1);
            while (nt[j].used) j = (j + 1) & (nsz - 1);
            nt[j] = ktab[i];
        }
        free(ktab); ktab = nt; ksize = nsz;
    }
    size_t j = mix64(key) & (ksize - 1);
    while (ktab[j].used) { if (ktab[j].key == key) { ktab[j].count++; return; } j = (j + 1) & (ksize - 1); }
    ktab[j].used = 1; ktab[j].key = key; ktab[j].count = 1; kused++;
}
static long long gens[MAXG][MAXK]; static int groot[MAXG];

static int cmpstr(const void *a, const void *b) { return strcmp(*(char * const *)a, *(char * const *)b); }

static void classify(const int *x) {
    for (int s = 0; s < S; s++) {
        if (!need[s]) continue;
        int twisted = 0;
        for (int k = 0; k < K; k++) twisted |= sa[s][k];
        na = 0;
        for (int i = 0; i < 2 * V; i++) head[i] = -1;
        for (int e = 0; e < E; e++) {
            int u = eu[e], w = ew[e], t = tw[s][e];
            if (x[e]) { add(2 * u, 2 * w + t); add(2 * w + (1 ^ t), 2 * u + 1); }
            else { add(2 * w + t, 2 * u); add(2 * u + 1, 2 * w + (1 ^ t)); }
        }
        tarjan(2 * V);
        int inv = 0;
        for (int v = 0; v < V; v++) if (comp[2 * v] == comp[2 * v + 1]) { inv = 1; break; }
        for (int v = 0; v < V; v++) { par[v] = v; for (int k = 0; k < K; k++) pot[v][k] = 0; }
        int ng = 0;
        long long pu[MAXK], pw[MAXK], d[MAXK];
        for (int e = 0; e < E; e++) {
            int u = eu[e], w = ew[e], t = tw[s][e];
            if (comp[2 * u] != comp[2 * w + t]) continue;
            int ru = findp(u, pu), rw = findp(w, pw), nz = 0;
            for (int k = 0; k < K; k++) { d[k] = pu[k] + eo[e][k] - pw[k]; if (d[k]) nz = 1; }
            if (ru == rw) {
                if (!nz) continue;
                if (ng >= MAXG) { fprintf(stderr, "too many generators\n"); exit(4); }
                for (int k = 0; k < K; k++) gens[ng][k] = d[k];
                groot[ng++] = ru;
            } else {
                par[rw] = ru;
                for (int k = 0; k < K; k++) pot[rw][k] = d[k];
            }
        }
        /* group generators by final cluster root */
        for (int g = 0; g < ng; g++) groot[g] = findr(groot[g]);
        char *parts[MAXV]; int np = 0;
        static char buf[MAXV][LABLEN];
        static long long m[MAXG][MAXK];
        int seen_root[MAXV]; int nr = 0;
        for (int g = 0; g < ng; g++) {
            int r = groot[g], already = 0;
            for (int i = 0; i < nr; i++) if (seen_root[i] == r) { already = 1; break; }
            if (already) continue;
            seen_root[nr++] = r;
            int n = 0, odd = 0;
            for (int h = g; h < ng; h++) if (groot[h] == r) {
                long long qd = 0;
                for (int k = 0; k < K; k++) { m[n][k] = gens[h][k]; qd += (long long)sa[s][k] * gens[h][k]; }
                if (gabs(qd) & 1) odd = 1;
                n++;
            }
            int rk = hnf(m, n);
            char *p = buf[np]; int len = 0;
            len += sprintf(p + len, "%c", odd ? 'o' : 'e');
            for (int i = 0; i < rk; i++) {
                len += sprintf(p + len, "[");
                for (int k = 0; k < K; k++) len += sprintf(p + len, k ? ",%lld" : "%lld", m[i][k]);
                len += sprintf(p + len, "]");
            }
            parts[np++] = p;
        }
        qsort(parts, np, sizeof(char *), cmpstr);
        static char label[LABLEN * 8];
        int L = 0;
        if (!np) L += sprintf(label, "-");
        for (int i = 0; i < np; i++) L += sprintf(label + L, i ? "|%s" : "%s", parts[i]);
        (void)inv; (void)twisted;
        for (int t = 0; t < T; t++) if (tsec[t] == s && !strcmp(tlab[t], label)) {
            uint64_t mask = 0;
            for (int e = 0; e < E; e++) if (comp[2 * eu[e]] == comp[2 * ew[e] + tw[s][e]]) mask |= 1ULL << e;
            kbump(((uint64_t)t << 40) | mask);
        }
    }
}

static uint64_t rs[4];
static uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static uint64_t next64(void) {
    uint64_t r = rotl(rs[1] * 5, 7) * 9, t = rs[1] << 17;
    rs[2] ^= rs[0]; rs[3] ^= rs[1]; rs[1] ^= rs[2]; rs[0] ^= rs[3]; rs[2] ^= t; rs[3] = rotl(rs[3], 45);
    return r;
}
static uint64_t splitmix(uint64_t *z) {
    uint64_t r = (*z += 0x9e3779b97f4a7c15ULL);
    r = (r ^ (r >> 30)) * 0xbf58476d1ce4e5b9ULL; r = (r ^ (r >> 27)) * 0x94d049bb133111ebULL;
    return r ^ (r >> 31);
}

int main(int argc, char **argv) {
    if (argc < 4) return 2;
    if (scanf("%d %d %d", &V, &E, &K) != 3 || V > MAXV || E > MAXE || K > MAXK) return 3;
    for (int e = 0; e < E; e++) {
        if (scanf("%d %d", &eu[e], &ew[e]) != 2) return 3;
        for (int k = 0; k < K; k++) if (scanf("%d", &eo[e][k]) != 1) return 3;
    }
    if (scanf("%d", &S) != 1 || S > MAXS) return 3;
    for (int s = 0; s < S; s++) for (int k = 0; k < K; k++) if (scanf("%d", &sa[s][k]) != 1) return 3;
    for (int s = 0; s < S; s++) for (int e = 0; e < E; e++) {
        long long p = 0;
        for (int k = 0; k < K; k++) p += (long long)sa[s][k] * eo[e][k];
        tw[s][e] = (int)(gabs(p) & 1);
    }
    if (scanf("%d", &T) != 1 || T > MAXT) return 3;
    for (int t = 0; t < T; t++) {
        char buf2[LABLEN * 8];
        if (scanf("%d %s", &tsec[t], buf2) != 2) return 3;
        tlab[t] = strdup(buf2); need[tsec[t]] = 1;
    }
    if (E > 40) return 5;
    static int x[MAXE];
    if (!strcmp(argv[1], "exh")) {
        if (E > 63) return 5;
        unsigned long long lo = strtoull(argv[2], 0, 10), hi = strtoull(argv[3], 0, 10);
        for (unsigned long long mm = lo; mm < hi; mm++) { for (int e = 0; e < E; e++) x[e] = (mm >> e) & 1; classify(x); }
    } else {
        uint64_t z = strtoull(argv[2], 0, 10); unsigned long long n = strtoull(argv[3], 0, 10);
        for (int i = 0; i < 4; i++) rs[i] = splitmix(&z);
        for (unsigned long long i = 0; i < n; i++) {
            for (int e = 0; e < E; e += 64) { uint64_t r = next64(); for (int b = 0; b < 64 && e + b < E; b++) x[e + b] = (r >> b) & 1; }
            classify(x);
        }
    }
    for (size_t i = 0; i < ksize; i++) if (ktab[i].used)
        printf("K %llu %llu=%llu\n", (unsigned long long)(ktab[i].key >> 40), (unsigned long long)(ktab[i].key & ((1ULL << 40) - 1)), ktab[i].count);
    return 0;
}
