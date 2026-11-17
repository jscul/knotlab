/* Referee R1 for WHERE-NEXT-20261116-001 (copied for SCALE-MEMORY-20261116-001, with two additions: the
 * relative-age read and a CPU-time guard; the search rules are unchanged): an independent focused local-search engine for planted
 * unsigned NAE-3-SAT (the not-all-equal knot law), written from the published rule definitions.
 *
 * A knot binds three distinct distinctions; it is violated when all three are equal. Flipping any
 * member of a violated knot satisfies it.
 *   break(v) = satisfied knots containing v that a flip of v would violate
 *   make(v)  = violated knots containing v
 * so a flip of v changes the violated count by break(v) - make(v).
 *
 * Every rule attends to a uniformly drawn violated knot and flips one of its members:
 *   0 WALKSAT  (p)          zero-break member if any (uniform among them); else with prob p a uniform
 *                           member; else a uniform least-break member (Selman, Kautz, Cohen 1994)
 *   1 PROBSAT  (cb, eps)    P(v) ~ (eps + break)^-cb (Balint, Schoening 2012, poly form)
 *   2 NOVPLUS  (p, wp)      with prob wp a uniform member; else Novelty: score = break - make,
 *                           best = lowest score, ties to the least recently flipped (exact ties
 *                           uniformly); if best is the most recently flipped member, take the
 *                           second best with prob p (McAllester, Selman, Kautz 1997; Hoos 1999)
 *   3 ADAPTNOV (wp, inv_theta, phi)  Novelty+ whose noise p starts at 0 and adapts (Hoos 2002):
 *                           no improvement of the violated count for more than m/inv_theta steps
 *                           -> p += (1 - p) phi; an improvement -> p -= p phi / 2
 *   4 NOVPP    (p, dp)      Novelty++ (Li, Huang 2005): with prob dp the least recently flipped
 *                           member; else Novelty
 *
 * The engine builds its own occurrence lists, uses its own RNG (xoshiro256** seeded by splitmix64),
 * and counts one step per flip. Optional logging (task 3) records, at every step and for the three
 * members of the attended knot, the age since the member was last flipped and its flip count decayed
 * with tau = 50 steps, and the same for the attended knot's own last visit.
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { WALKSAT = 0, PROBSAT = 1, NOVPLUS = 2, ADAPTNOV = 3, NOVPP = 4 };

#define NB_AGE 2048   /* age bins: floor(64 * log2(age)), age >= 1 */
#define NB_DEC 2200   /* decayed-count bins: floor(50 * (log10(d) + 40)), d > 0 */
#define NB_REL 1000   /* relative-age bins over [0, 1): floor(1000 * a_j / max_i a_i); exactly 1 counted apart */
#define TAU 50.0

typedef struct { uint64_t s[4]; } X256;
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t xnext(X256 *r) {
  uint64_t *s = r->s;
  uint64_t res = rotl(s[1] * 5, 7) * 9, t = s[1] << 17;
  s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45);
  return res;
}
static uint64_t sm64(uint64_t *z) {
  uint64_t q = (*z += 0x9E3779B97F4A7C15ULL);
  q = (q ^ (q >> 30)) * 0xBF58476D1CE4E5B9ULL;
  q = (q ^ (q >> 27)) * 0x94D049BB133111EBULL;
  return q ^ (q >> 31);
}
static void xseed(X256 *r, uint64_t seed) {
  uint64_t z = seed ^ 0x5265666572656531ULL; /* "Referee1" */
  for (int i = 0; i < 4; i++) r->s[i] = sm64(&z);
}
static inline double xu(X256 *r) { return (double)(xnext(r) >> 11) * 0x1.0p-53; }
static inline uint32_t xb(X256 *r, uint32_t k) { return (uint32_t)(((__uint128_t)xnext(r) * k) >> 64); }

typedef struct {
  int n, m;
  const int32_t *kv;
  int32_t *ost, *occ;
  uint8_t *x, *cnt;
  int32_t *vl, *vp;
  int nv;
  int64_t *lf, *fct, *lv, *vct;
  double *fc, *vc;
  X256 r;
} St;

static inline int viol(int c) { return c == 0 || c == 3; }
static inline void vins(St *S, int k) { S->vp[k] = S->nv; S->vl[S->nv++] = k; }
static inline void vrem(St *S, int k) {
  int p = S->vp[k], last = S->vl[--S->nv];
  S->vl[p] = last; S->vp[last] = p; S->vp[k] = -1;
}

static void do_flip(St *S, int v) {
  int down = S->x[v];
  S->x[v] ^= 1;
  for (int i = S->ost[v]; i < S->ost[v + 1]; i++) {
    int k = S->occ[i], o = S->cnt[k], w = down ? o - 1 : o + 1;
    S->cnt[k] = (uint8_t)w;
    if (viol(o) && !viol(w)) vrem(S, k);
    else if (!viol(o) && viol(w)) vins(S, k);
  }
}

static inline void brk_mk(const St *S, int v, int *b, int *mk) {
  int bb = 0, mm = 0, xv = S->x[v];
  for (int i = S->ost[v]; i < S->ost[v + 1]; i++) {
    int c = S->cnt[S->occ[i]];
    if (viol(c)) mm++;
    else if ((xv && c == 1) || (!xv && c == 2)) bb++;
  }
  *b = bb; *mk = mm;
}

static const int PERM[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};

/* Novelty on the three members vs: returns the index picked. */
static int novelty(St *S, const int32_t *vs, double p) {
  int sc[3];
  for (int j = 0; j < 3; j++) { int b, mk; brk_mk(S, vs[j], &b, &mk); sc[j] = b - mk; }
  const int *o = PERM[xb(&S->r, 6)];
  int best = o[0], second = -1;
  for (int t = 1; t < 3; t++) {
    int j = o[t];
    int better_best = sc[j] < sc[best] || (sc[j] == sc[best] && S->lf[vs[j]] < S->lf[vs[best]]);
    if (better_best) { second = best; best = j; }
    else if (second < 0 || sc[j] < sc[second] || (sc[j] == sc[second] && S->lf[vs[j]] < S->lf[vs[second]]))
      second = j;
  }
  int young = 0;
  for (int j = 1; j < 3; j++) if (S->lf[vs[j]] > S->lf[vs[young]]) young = j;
  if (S->lf[vs[young]] < 0) young = -1; /* no member flipped yet */
  if (best == young && xu(&S->r) < p) return second;
  return best;
}

static double tcpu(void) {
  struct timespec ts;
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

static inline int age_bin(int64_t a) {
  int b = (int)floor(64.0 * log2((double)a));
  return b < 0 ? 0 : (b >= NB_AGE ? NB_AGE - 1 : b);
}
static inline int dec_bin(double d) {
  if (!(d > 0.0)) return 0;
  int b = (int)floor(50.0 * (log10(d) + 40.0));
  return b < 0 ? 0 : (b >= NB_DEC ? NB_DEC - 1 : b);
}

/* hist layout (int64), when non-NULL:
 *   [0] member observations  [1] never flipped  [2] age > 1000  [3] decayed count exactly 0 (never)
 *   [4] knot observations    [5] knot never visited  [6] knot age > 1000  [7] knot decayed 0
 *   [8 .. 8+NB_AGE)                       member age histogram
 *   [8+NB_AGE .. 8+NB_AGE+NB_DEC)         member decayed-count histogram
 *   [.. +NB_AGE)                          knot visit-age histogram
 *   [.. +NB_DEC)                          knot decayed visit-count histogram
 */
/*   then [REL0] relative-age reads  [REL0+1] reads exactly 1  [REL0+2] steps with >= 2 members at the max
 *   [REL0+3 .. REL0+3+NB_REL)  relative-age histogram (reads below 1)
 * relative age of member j = a_j / max(a_1, a_2, a_3), a = steps since last flip, never flipped = t + 1 */
#define REL0 (8 + 2 * (NB_AGE + NB_DEC))
int ref_hist_size(void) { return REL0 + 3 + NB_REL; }

/* out: [0] flips, [1] solved, [2] least violated count, [3] cpu s, [4] final noise (ADAPTNOV),
 *      [5] mean noise over steps (ADAPTNOV), [6] stopped by the CPU-time guard (prm[3] seconds; 0 = none) */
int ref_run(int n, int m, const int32_t *kv, int algo, const double *prm, uint64_t seed, int64_t cap,
            double *out, int64_t *hist, uint8_t *xout) {
  double c0 = tcpu();
  St S;
  memset(&S, 0, sizeof S);
  S.n = n; S.m = m; S.kv = kv;
  S.ost = calloc(n + 1, sizeof(int32_t));
  S.occ = malloc(sizeof(int32_t) * 3 * (size_t)m);
  for (int i = 0; i < 3 * m; i++) S.ost[kv[i] + 1]++;
  for (int v = 0; v < n; v++) S.ost[v + 1] += S.ost[v];
  int32_t *fill = malloc(sizeof(int32_t) * n);
  memcpy(fill, S.ost, sizeof(int32_t) * n);
  for (int k = 0; k < m; k++) for (int j = 0; j < 3; j++) S.occ[fill[kv[3 * k + j]]++] = k;
  free(fill);
  S.x = malloc(n); S.cnt = malloc(m);
  S.vl = malloc(sizeof(int32_t) * m); S.vp = malloc(sizeof(int32_t) * m);
  S.lf = malloc(sizeof(int64_t) * n); S.fct = malloc(sizeof(int64_t) * n); S.fc = calloc(n, sizeof(double));
  S.lv = malloc(sizeof(int64_t) * m); S.vct = malloc(sizeof(int64_t) * m); S.vc = calloc(m, sizeof(double));
  xseed(&S.r, seed);
  for (int v = 0; v < n; v++) { S.x[v] = (uint8_t)(xnext(&S.r) >> 63); S.lf[v] = -1; S.fct[v] = -1; }
  S.nv = 0;
  for (int k = 0; k < m; k++) {
    S.cnt[k] = (uint8_t)(S.x[kv[3 * k]] + S.x[kv[3 * k + 1]] + S.x[kv[3 * k + 2]]);
    S.vp[k] = -1; S.lv[k] = -1; S.vct[k] = -1;
    if (viol(S.cnt[k])) vins(&S, k);
  }
  int maxdeg = 0;
  for (int v = 0; v < n; v++) if (S.ost[v + 1] - S.ost[v] > maxdeg) maxdeg = S.ost[v + 1] - S.ost[v];
  double *tab = malloc(sizeof(double) * (maxdeg + 2));
  if (algo == PROBSAT) for (int b = 0; b <= maxdeg + 1; b++) tab[b] = pow(prm[1] + b, -prm[0]);

  int64_t *H = hist, *Hage = hist ? hist + 8 : NULL, *Hdec = hist ? hist + 8 + NB_AGE : NULL;
  int64_t *Hkage = hist ? hist + 8 + NB_AGE + NB_DEC : NULL, *Hkdec = hist ? hist + 8 + 2 * NB_AGE + NB_DEC : NULL;

  double noise = (algo == ADAPTNOV) ? 0.0 : prm[0], noise_sum = 0.0;
  int64_t last_adapt = 0;
  int last_nf = S.nv, minv = S.nv;
  int64_t win = (algo == ADAPTNOV) ? (int64_t)(m / prm[1]) : 0;
  int64_t f = 0;
  int timed_out = 0;
  double tlim = prm[3];
  while (S.nv > 0 && f < cap) {
    if (tlim > 0 && (f & 0xFFFFF) == 0 && f > 0 && tcpu() - c0 > tlim) { timed_out = 1; break; }
    int k = S.vl[xb(&S.r, S.nv)];
    const int32_t *vs = kv + 3 * k;
    if (H) {
      for (int j = 0; j < 3; j++) {
        int v = vs[j];
        H[0]++;
        if (S.lf[v] < 0) H[1]++;
        else { int64_t a = f - S.lf[v]; Hage[age_bin(a)]++; if (a > 1000) H[2]++; }
        if (S.fct[v] < 0) H[3]++;
        else Hdec[dec_bin(S.fc[v] * exp(-(double)(f - S.fct[v]) / TAU))]++;
      }
      {
        int64_t a[3], mx = 0;
        int nmax = 0;
        for (int j = 0; j < 3; j++) { a[j] = f - S.lf[vs[j]]; if (a[j] > mx) mx = a[j]; } /* lf = -1: t + 1 */
        for (int j = 0; j < 3; j++) {
          H[REL0]++;
          if (a[j] == mx) { H[REL0 + 1]++; nmax++; }
          else { int b = (int)((double)a[j] / (double)mx * NB_REL); H[REL0 + 3 + (b >= NB_REL ? NB_REL - 1 : b)]++; }
        }
        if (nmax >= 2) H[REL0 + 2]++;
      }
      H[4]++;
      if (S.lv[k] < 0) H[5]++;
      else { int64_t a = f - S.lv[k]; Hkage[age_bin(a)]++; if (a > 1000) H[6]++; }
      if (S.vct[k] < 0) H[7]++;
      else Hkdec[dec_bin(S.vc[k] * exp(-(double)(f - S.vct[k]) / TAU))]++;
      S.vc[k] = (S.vct[k] < 0 ? 0.0 : S.vc[k] * exp(-(double)(f - S.vct[k]) / TAU)) + 1.0;
      S.vct[k] = f; S.lv[k] = f;
    }
    int pick = 0;
    switch (algo) {
      case WALKSAT: {
        int b[3], mk, z[3], nz = 0, mb = 1 << 30;
        for (int j = 0; j < 3; j++) { brk_mk(&S, vs[j], &b[j], &mk); if (b[j] == 0) z[nz++] = j; if (b[j] < mb) mb = b[j]; }
        if (nz > 0) pick = z[xb(&S.r, nz)];
        else if (xu(&S.r) < prm[0]) pick = (int)xb(&S.r, 3);
        else { int c = 0, l[3]; for (int j = 0; j < 3; j++) if (b[j] == mb) l[c++] = j; pick = l[xb(&S.r, c)]; }
        break;
      }
      case PROBSAT: {
        double w[3], tot = 0.0;
        for (int j = 0; j < 3; j++) { int b, mk; brk_mk(&S, vs[j], &b, &mk); w[j] = tab[b]; tot += w[j]; }
        double u = xu(&S.r) * tot;
        pick = u < w[0] ? 0 : (u < w[0] + w[1] ? 1 : 2);
        break;
      }
      case NOVPLUS:
        if (xu(&S.r) < prm[1]) pick = (int)xb(&S.r, 3);
        else pick = novelty(&S, vs, prm[0]);
        break;
      case ADAPTNOV:
        noise_sum += noise;
        if (xu(&S.r) < prm[0]) pick = (int)xb(&S.r, 3);
        else pick = novelty(&S, vs, noise);
        break;
      case NOVPP:
        if (xu(&S.r) < prm[1]) {
          const int *o = PERM[xb(&S.r, 6)];
          pick = o[0];
          for (int t = 1; t < 3; t++) if (S.lf[vs[o[t]]] < S.lf[vs[pick]]) pick = o[t];
        } else pick = novelty(&S, vs, prm[0]);
        break;
    }
    int v = vs[pick];
    do_flip(&S, v);
    S.fc[v] = (S.fct[v] < 0 ? 0.0 : S.fc[v] * exp(-(double)(f - S.fct[v]) / TAU)) + 1.0;
    S.fct[v] = f;
    S.lf[v] = f;
    f++;
    if (S.nv < minv) minv = S.nv;
    if (algo == ADAPTNOV) {
      if (f - last_adapt > win) { noise += (1.0 - noise) * prm[2]; last_adapt = f; last_nf = S.nv; }
      else if (S.nv < last_nf) { noise -= noise * prm[2] / 2.0; last_adapt = f; last_nf = S.nv; }
    }
  }
  out[0] = (double)f; out[1] = S.nv == 0; out[2] = minv; out[4] = noise;
  out[5] = f > 0 ? noise_sum / (double)f : 0.0;
  out[6] = timed_out;
  if (xout) memcpy(xout, S.x, n);
  free(tab); free(S.ost); free(S.occ); free(S.x); free(S.cnt); free(S.vl); free(S.vp);
  free(S.lf); free(S.fct); free(S.fc); free(S.lv); free(S.vct); free(S.vc);
  out[3] = tcpu() - c0;
  return 0;
}

/* Self-test: random flips; after each, the violated list and the break/make counts must equal a
 * recomputation from the state. Returns the number of mismatches. */
int ref_selftest(int n, int m, const int32_t *kv, uint64_t seed, int64_t nflips) {
  double out[6];
  (void)out;
  St S;
  memset(&S, 0, sizeof S);
  S.n = n; S.m = m; S.kv = kv;
  S.ost = calloc(n + 1, sizeof(int32_t));
  S.occ = malloc(sizeof(int32_t) * 3 * (size_t)m);
  for (int i = 0; i < 3 * m; i++) S.ost[kv[i] + 1]++;
  for (int v = 0; v < n; v++) S.ost[v + 1] += S.ost[v];
  int32_t *fill = malloc(sizeof(int32_t) * n);
  memcpy(fill, S.ost, sizeof(int32_t) * n);
  for (int k = 0; k < m; k++) for (int j = 0; j < 3; j++) S.occ[fill[kv[3 * k + j]]++] = k;
  free(fill);
  S.x = malloc(n); S.cnt = malloc(m);
  S.vl = malloc(sizeof(int32_t) * m); S.vp = malloc(sizeof(int32_t) * m);
  xseed(&S.r, seed);
  for (int v = 0; v < n; v++) S.x[v] = (uint8_t)(xnext(&S.r) >> 63);
  for (int k = 0; k < m; k++) {
    S.cnt[k] = (uint8_t)(S.x[kv[3 * k]] + S.x[kv[3 * k + 1]] + S.x[kv[3 * k + 2]]);
    S.vp[k] = -1;
    if (viol(S.cnt[k])) vins(&S, k);
  }
  int bad = 0;
  int *before = malloc(sizeof(int) * m);
  for (int64_t f = 0; f < nflips; f++) {
    int v = (int)xb(&S.r, n), b, mk;
    brk_mk(&S, v, &b, &mk);
    int nv0 = S.nv;
    do_flip(&S, v);
    if (S.nv - nv0 != b - mk) bad++;
    int nvv = 0;
    for (int k = 0; k < m; k++) {
      int s = S.x[kv[3 * k]] + S.x[kv[3 * k + 1]] + S.x[kv[3 * k + 2]];
      if (s != S.cnt[k]) bad++;
      if (viol(s)) { nvv++; if (S.vp[k] < 0 || S.vl[S.vp[k]] != k) bad++; }
      else if (S.vp[k] >= 0) bad++;
    }
    if (nvv != S.nv) bad++;
  }
  free(before);
  free(S.ost); free(S.occ); free(S.x); free(S.cnt); free(S.vl); free(S.vp);
  return bad;
}
