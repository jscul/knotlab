/* Referee BASES-WITHIN-R1: does O[I] with shifted stitches live? Exhaustive over the free shifts, or over a given list.
 *
 * stdin:  P nW / nW words (bit i = the word's value at place i) / nreps rep indices (first row, up to a global shift and mirror)
 *         n e / e knots a b c / nfree, then nfree pairs (knot, position) / mode: 0 = every assignment of the free shifts
 *         (the others 0), 1 = a list: count, then for each assignment 3e shifts.
 * stdout: mode 0: "total dead" and up to 5 dead assignments; mode 1: one 0/1 per assignment (1 = lives).
 * Rows are words of W; knot k with shifts (sa, sb, sc) holds when NAE(w_a(i+sa), w_b(i+sb), w_c(i+sc)) at every place i. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 mask_t;
static int P, nW, nreps, n, e, nfree;
static int W[256], reps[256], knot[16][3], freek[64], freep[64];
static int sh[16][256];
static mask_t *Tm;               /* Tm[(t * nW + u) * nW + v] = {w : shift_t(w) is NAE with u and v at every place} */
static int sft[16][3];
static int lastof[16], other1[16], other2[16], posz[16], posx[16], posy[16];
static int byj[16][16], nbyj[16];
static int row[16];
static mask_t full;

static int rot(int w, int s) { /* (shift_s w)(i) = w(i+s) */
    int m = (1 << P) - 1;
    s %= P;
    return s == 0 ? w : (((w >> s) | (w << (P - s))) & m);
}

static int go(int j) {
    if (j == n) return 1;
    mask_t c = full;
    if (j == 0) {
        c = 0;
        for (int r = 0; r < nreps; r++) c |= ((mask_t)1) << reps[r];
    }
    for (int q = 0; q < nbyj[j]; q++) {
        int k = byj[j][q];
        int ux = sh[sft[k][posx[k]]][row[other1[k]]];
        int uy = sh[sft[k][posy[k]]][row[other2[k]]];
        c &= Tm[((size_t)sft[k][posz[k]] * nW + ux) * nW + uy];
        if (!c) return 0;
    }
    while (c) {
        uint64_t lo = (uint64_t)c;
        int b = lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((uint64_t)(c >> 64));
        c &= c - 1;
        row[j] = b;
        if (go(j + 1)) return 1;
    }
    return 0;
}

int main(void) {
    if (scanf("%d %d", &P, &nW) != 2) return 1;
    for (int i = 0; i < nW; i++) scanf("%d", &W[i]);
    scanf("%d", &nreps);
    for (int i = 0; i < nreps; i++) scanf("%d", &reps[i]);
    scanf("%d %d", &n, &e);
    for (int k = 0; k < e; k++) scanf("%d %d %d", &knot[k][0], &knot[k][1], &knot[k][2]);
    scanf("%d", &nfree);
    for (int i = 0; i < nfree; i++) scanf("%d %d", &freek[i], &freep[i]);
    int mode;
    scanf("%d", &mode);
    full = 0;
    for (int i = 0; i < nW; i++) full |= ((mask_t)1) << i;
    /* shift table */
    for (int s = 0; s < P; s++)
        for (int i = 0; i < nW; i++) {
            int r = rot(W[i], s), f = -1;
            for (int j = 0; j < nW; j++) if (W[j] == r) f = j;
            if (f < 0) { fprintf(stderr, "W not closed under shifts\n"); return 1; }
            sh[s][i] = f;
        }
    int pm = (1 << P) - 1;
    Tm = calloc((size_t)P * nW * nW, sizeof(mask_t));
    for (int t = 0; t < P; t++)
        for (int u = 0; u < nW; u++)
            for (int v = 0; v < nW; v++) {
                mask_t m = 0;
                int eq = ~(W[u] ^ W[v]) & pm;       /* places where u == v: there z must differ from u */
                for (int z = 0; z < nW; z++) {
                    int zz = rot(W[z], t);
                    if (((zz ^ W[u]) & eq) == eq) m |= ((mask_t)1) << z;
                }
                Tm[((size_t)t * nW + u) * nW + v] = m;
            }
    /* each knot is checked when its last distinction is placed */
    memset(nbyj, 0, sizeof nbyj);
    for (int k = 0; k < e; k++) {
        int z = 0;
        for (int p = 1; p < 3; p++) if (knot[k][p] > knot[k][z]) z = p;
        int x = (z + 1) % 3, y = (z + 2) % 3;
        posz[k] = z; posx[k] = x; posy[k] = y;
        lastof[k] = knot[k][z]; other1[k] = knot[k][x]; other2[k] = knot[k][y];
        byj[lastof[k]][nbyj[lastof[k]]++] = k;
    }
    if (mode == 0) {
        long long total = 1, dead = 0;
        for (int i = 0; i < nfree; i++) total *= P;
        int shown = 0;
        int val[64];
        for (long long a = 0; a < total; a++) {
            long long r = a;
            memset(sft, 0, sizeof sft);
            for (int i = 0; i < nfree; i++) { val[i] = r % P; r /= P; sft[freek[i]][freep[i]] = val[i]; }
            if (!go(0)) {
                dead++;
                if (shown < 5) {
                    shown++;
                    printf("dead");
                    for (int k = 0; k < e; k++) printf(" %d,%d,%d", sft[k][0], sft[k][1], sft[k][2]);
                    printf("\n");
                }
            }
        }
        printf("total %lld dead %lld\n", total, dead);
    } else {
        int cnt;
        scanf("%d", &cnt);
        for (int q = 0; q < cnt; q++) {
            for (int k = 0; k < e; k++) for (int p = 0; p < 3; p++) scanf("%d", &sft[k][p]);
            printf("%d\n", go(0));
        }
    }
    return 0;
}
