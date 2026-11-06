/* Exact contradiction counts of a twisted three-place world on the L x M triangular torus (no shear), with cylinder covers along
   the deck classes (1,0), (0,1) and (1,1), each by a sliding-window transfer across the levels of a linear functional that
   vanishes on the class.
   Triangles: up (i,j),(i+1,j),(i+1,j+1) and down (i,j),(i,j+1),(i+1,j+1), index 2(jL+i)+{0,1}. Visible bit 0 allows the gauged
   patterns R, bit 1 their complements; the gauge of a corner is alpha k1 + beta k2 for its deck offset (k1, k2) from the first corner.
   Usage: tshield2 R L M alpha beta LO HI
   Output: "n unsat cyl10 cyl01 cyl11 lone10 lone01 lone11 cross mism"; lone = that cylinder contradicts and the other two do not;
   cross = the torus contradicts and no cylinder does; mism = disagreements between the three torus tests. */
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

int main(int argc, char **argv) {
    if (argc < 8) return 2;
    R = atoi(argv[1]); L = atoi(argv[2]); M = atoi(argv[3]); A = atoi(argv[4]); B = atoi(argv[5]);
    unsigned long long lo = strtoull(argv[6], 0, 10), hi = strtoull(argv[7], 0, 10);
    RB = 0; for (int p = 0; p < 8; p++) if ((R >> p) & 1) RB |= 1 << (7 - p);
    V = L * M; F = 2 * V;
    if (F > 64) return 4;
    build_triangles();
    int cls[3][2] = {{1, 0}, {0, 1}, {1, 1}};
    for (int c = 0; c < 3; c++) { build_cyl(&C[c], cls[c][0], cls[c][1]); if (C[c].nstates > 16) { fprintf(stderr, "too many states\n"); return 5; } }
    unsigned long long n = 0, unsat = 0, cyl[3] = {0, 0, 0}, lone[3] = {0, 0, 0}, cross = 0, mism = 0;
    uint16_t P[16];
    for (unsigned long long x = lo; x < hi; x++) {
        n++;
        period(&C[0], x, P);
        int t0 = has_fixed(P, C[0].nstates);
        if (t0) continue;                                   /* a satisfiable torus makes every cylinder satisfiable */
        int u[3]; u[0] = !has_cycle(P, C[0].nstates);
        period(&C[1], x, P); int t1 = has_fixed(P, C[1].nstates); u[1] = !has_cycle(P, C[1].nstates);
        period(&C[2], x, P); int t2 = has_fixed(P, C[2].nstates); u[2] = !has_cycle(P, C[2].nstates);
        if (t1 || t2) mism++;
        unsat++;
        for (int c = 0; c < 3; c++) cyl[c] += u[c];
        int k = u[0] + u[1] + u[2];
        for (int c = 0; c < 3; c++) if (k == 1 && u[c]) lone[c]++;
        if (k == 0) cross++;
    }
    printf("%llu %llu %llu %llu %llu %llu %llu %llu %llu %llu\n", n, unsat, cyl[0], cyl[1], cyl[2], lone[0], lone[1], lone[2], cross, mism);
    return 0;
}
