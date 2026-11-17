/* Local search on not-all-equal knot patterns (the knot law of lesson 4.7).
 *
 * WHERE-NEXT-20261116-001A (copied for SCALE-MEMORY-20261116-001A and MEET-TRANSFER-20261117-001A). Every knot binds three distinct distinctions and
 * allows every joint state except 000 and 111; a state is a bit per
 * distinction. One step attends to a violated knot (all three equal) and flips
 * one of its distinctions, which always satisfies that knot.
 *
 * All arms run in this one engine, so their costs per flip are comparable:
 *   0 RW           random violated knot, random distinction
 *   1 WALKSAT      random knot; a zero-break flip if any, else noise p, else least break
 *   2 PROBSAT_POLY random knot; P(v) ~ (eps + break)^-cb
 *   3 PROBSAT_EXP  random knot; P(v) ~ cb^-break
 *   4 NOVELTY_PLUS random knot; best by break - make, age tie-break, Novelty+ rule
 *   5 GREEDY_WHERE knot = least min-break among the policy's candidates (noise q),
 *                  then PROBSAT_POLY inside it
 *   6 POLICY       learned where (flag 1) and what, with memory features (flag 2)
 *                  and a recurrent state (flag 4); flag 8 fixes what to PROBSAT_POLY
 *   7 STICKY       with probability q a knot the last flip violated, else a random
 *                  knot; then PROBSAT_POLY (the hand-written "follow what you broke")
 *   8 FMS          focused Metropolis: random knot, random distinction, accepted
 *                  when it violates no more knots than it repairs, else with
 *                  probability eta^(break - make); a rejected try counts as a step
 *
 * SCALE-MEMORY-20261116-001A adds flag 16 (with flag 2): the long-horizon memory
 * reads count no steps. A distinction's clipped log age is replaced by its age over
 * the oldest of the attended knot's three, and a candidate knot's by its visit age
 * over the oldest candidate's (never flipped or visited: age t + 1). Ranks, the
 * last-flipped flag and the 50-step recent counts (a constant horizon) are kept.
 * The recurrent input reads the flipped distinction's relative age and the violated
 * fraction (10 * violated / knots, clipped at 1) in place of the log count ratio.
 *
 * SIGNED-NAV-20261117-001 (this copy) adds signed knots: knot (a, b, c) with signs (sa, sb, sc) allows every joint
 * state except the two in which x_a ^ sa, x_b ^ sb and x_c ^ sc are all equal; ones[k] counts the knot's literals
 * that are 1. nae_run_signed takes the signs (3m, or NULL for unsigned, which reproduces the earlier engines run for
 * run), the signs per occurrence (aligned with occ), and an optional initial state (NULL: drawn as before).
 *
 * MEET-TRANSFER-20261117-001A adds flag 32: break and make are read as fractions of
 * the distinction's own knots (break / degree, make / degree), for the attended
 * knot's distinctions, the where-candidates and the recurrent input, and the 50-step
 * recent counts are not read (they fall to about 0 as patterns grow).
 *
 * Work is counted in incidences touched (one knot-distinction pair read), so it
 * does not depend on the machine.
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { RW = 0, WALKSAT = 1, PROBSAT_POLY = 2, PROBSAT_EXP = 3, NOVELTY_PLUS = 4,
       GREEDY_WHERE = 5, POLICY = 6, STICKY = 7, FMS = 8 };
enum { LEARN_WHERE = 1, MEM_AGE = 2, MEM_RNN = 4, WHAT_PROBSAT = 8, MEM_SF = 16, DEGNORM = 32 };

#define NEWMAX 3     /* newly violated knots kept as where-candidates */
#define RANDC 3      /* uniformly drawn violated knots added as candidates */
#define NCAND (NEWMAX + RANDC)
#define HID 8        /* hidden units of each scorer */
#define HR 6         /* recurrent state size */
#define DW 7         /* what features */
#define DK 8         /* where features */
#define DS 6         /* recurrent input */
#define TAU 50.0     /* decay (steps) of the recent-flip and recent-visit counts */
#define AGE_CLIP 6.90875477931522 /* log1p(1000): ages beyond 1000 steps read as "long ago" */

/* theta layout */
#define W_W1 0
#define W_B1 (W_W1 + HID * (DW + HR))
#define W_W2 (W_B1 + HID)
#define K_W1 (W_W2 + HID)
#define K_B1 (K_W1 + HID * (DK + HR))
#define K_W2 (K_B1 + HID)
#define R_WH (K_W2 + HID)
#define R_WS (R_WH + HR * HR)
#define R_B (R_WS + HR * DS)
#define NTHETA (R_B + HR)

int nae_ntheta(void) { return NTHETA; }
void nae_layout(int *o) {
  int v[] = {W_W1, W_B1, W_W2, K_W1, K_B1, K_W2, R_WH, R_WS, R_B, NTHETA, HID, HR, DW, DK, DS};
  memcpy(o, v, sizeof v);
}

typedef struct { uint64_t s[2]; } Rng;

static uint64_t splitmix(uint64_t *z) {
  uint64_t r = (*z += 0x9E3779B97F4A7C15ULL);
  r = (r ^ (r >> 30)) * 0xBF58476D1CE4E5B9ULL;
  r = (r ^ (r >> 27)) * 0x94D049BB133111EBULL;
  return r ^ (r >> 31);
}
static void rng_seed(Rng *r, uint64_t seed) {
  uint64_t z = seed;
  r->s[0] = splitmix(&z);
  r->s[1] = splitmix(&z);
  if (!r->s[0] && !r->s[1]) r->s[1] = 1;
}
static inline uint64_t rng_next(Rng *r) {
  uint64_t s1 = r->s[0];
  const uint64_t s0 = r->s[1];
  r->s[0] = s0;
  s1 ^= s1 << 23;
  r->s[1] = s1 ^ s0 ^ (s1 >> 17) ^ (s0 >> 26);
  return r->s[1] + s0;
}
static inline double rng_unif(Rng *r) { return (rng_next(r) >> 11) * (1.0 / 9007199254740992.0); }
static inline uint32_t rng_below(Rng *r, uint32_t k) {
  return (uint32_t)(((rng_next(r) >> 32) * (uint64_t)k) >> 32);
}

/* tanh by a Pade approximant, exact in sign and saturation; used in training and test alike */
static inline double ftanh(double x) {
  if (x > 3.0) return 1.0;
  if (x < -3.0) return -1.0;
  double x2 = x * x;
  return x * (27.0 + x2) / (27.0 + 9.0 * x2);
}

typedef struct {
  int n, m;
  const int32_t *kv, *os, *occ;
  const uint8_t *ks, *ocs; /* signs per knot position and per occurrence; NULL: unsigned */
  uint8_t *x, *ones;
  int32_t *vlist, *vpos;
  int nviol;
  int32_t newk[NEWMAX];
  int nnew;
  int64_t t, work;
  /* memory */
  int64_t *lastflip, *fcnt_t, *lastvisit, *vcnt_t;
  double *fcnt, *vcnt;
  int last_var;
  Rng rng;
} St;

static inline void vadd(St *S, int k) {
  S->vpos[k] = S->nviol;
  S->vlist[S->nviol++] = k;
}
static inline void vdel(St *S, int k) {
  int p = S->vpos[k], last = S->vlist[--S->nviol];
  S->vlist[p] = last;
  S->vpos[last] = p;
  S->vpos[k] = -1;
}
static inline int is_v(int o) { return o == 0 || o == 3; }

static void flip(St *S, int v) {
  int xv = S->x[v];
  S->x[v] ^= 1;
  S->nnew = 0;
  for (int i = S->os[v]; i < S->os[v + 1]; i++) {
    int lit = S->ocs ? (xv ^ S->ocs[i]) : xv; /* the literal before the flip */
    int k = S->occ[i], o = S->ones[k], nw = lit ? o - 1 : o + 1;
    S->ones[k] = (uint8_t)nw;
    int wv = is_v(o), nv = is_v(nw);
    if (wv && !nv) vdel(S, k);
    else if (!wv && nv) {
      vadd(S, k);
      if (S->nnew < NEWMAX) S->newk[S->nnew++] = k;
    }
  }
  S->work += S->os[v + 1] - S->os[v];
}

/* break: satisfied knots of v that a flip of v would violate; make: violated knots of v */
static inline void bm(St *S, int v, int *b, int *mk) {
  int bb = 0, mm = 0, xv = S->x[v];
  for (int i = S->os[v]; i < S->os[v + 1]; i++) {
    int o = S->ones[S->occ[i]], lit = S->ocs ? (xv ^ S->ocs[i]) : xv;
    if (is_v(o)) mm++;
    else if (lit ? (o == 1) : (o == 2)) bb++;
  }
  S->work += S->os[v + 1] - S->os[v];
  *b = bb;
  *mk = mm;
}

static inline int pick3(Rng *r, const double *w) {
  double s = w[0] + w[1] + w[2], u = rng_unif(r) * s;
  if (u < w[0]) return 0;
  if (u < w[0] + w[1]) return 1;
  return 2;
}

/* log1p(age) clipped at 1000 steps, scaled to [0, 1]; never = 1 */
static inline double agefeat(int64_t t, int64_t last) {
  if (last < 0) return 1.0;
  double a = log1p((double)(t - last)) / AGE_CLIP;
  return a > 1.0 ? 1.0 : a;
}
static inline double decayed(double c, int64_t ct, int64_t t) {
  return ct < 0 ? 0.0 : c * exp(-(double)(t - ct) / TAU);
}
/* rank of a[i] among a[0..c-1], ties averaged, scaled to [0, 1] */
static inline double rankof(const double *a, int c, int i) {
  if (c < 2) return 0.5;
  double r = 0.0;
  for (int j = 0; j < c; j++) {
    if (a[j] < a[i]) r += 1.0;
    else if (a[j] == a[i] && j != i) r += 0.5;
  }
  return r / (c - 1);
}

static double mlp(const double *th, int w1, int b1, int w2, int din, const double *xin) {
  double s = 0.0;
  for (int j = 0; j < HID; j++) {
    double a = th[b1 + j];
    const double *row = th + w1 + j * din;
    for (int i = 0; i < din; i++) a += row[i] * xin[i];
    s += th[w2 + j] * ftanh(a);
  }
  return s;
}

static int softmax_pick(Rng *r, const double *sc, int c) {
  double mx = sc[0], w[NCAND], tot = 0.0;
  for (int i = 1; i < c; i++) if (sc[i] > mx) mx = sc[i];
  for (int i = 0; i < c; i++) { w[i] = exp(sc[i] - mx); tot += w[i]; }
  double u = rng_unif(r) * tot;
  for (int i = 0; i < c; i++) { u -= w[i]; if (u <= 0.0) return i; }
  return c - 1;
}

static double thread_cpu(void) {
  struct timespec ts;
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

/* out: [0] steps (flips; FMS counts rejected tries too), [1] solved, [2] least violated count seen,
 *      [3] work, [4] cpu seconds, [5] where-steps that chose a newly violated knot,
 *      [6] where-steps with one available, [7] distinct candidates summed over where-steps,
 *      [8] where-steps, [9] accepted flips */
int nae_run_signed(int n, int m, const int32_t *kv, const int32_t *os, const int32_t *occ, const uint8_t *ks,
                   const uint8_t *ocs, const uint8_t *x0, int algo, const double *params, const double *theta, int flags,
                   uint64_t seed, int64_t max_flips, double *out, uint8_t *xout) {
  double c0 = thread_cpu();
  St S;
  memset(&S, 0, sizeof S);
  S.n = n; S.m = m; S.kv = kv; S.os = os; S.occ = occ; S.ks = ks; S.ocs = ocs;
  rng_seed(&S.rng, seed);
  S.x = malloc(n); S.ones = malloc(m);
  S.vlist = malloc(sizeof(int32_t) * m); S.vpos = malloc(sizeof(int32_t) * m);
  S.lastflip = malloc(sizeof(int64_t) * n); S.fcnt_t = malloc(sizeof(int64_t) * n);
  S.fcnt = malloc(sizeof(double) * n);
  S.lastvisit = malloc(sizeof(int64_t) * m); S.vcnt_t = malloc(sizeof(int64_t) * m);
  S.vcnt = malloc(sizeof(double) * m);
  for (int v = 0; v < n; v++) {
    S.x[v] = x0 ? x0[v] : (uint8_t)(rng_next(&S.rng) >> 63);
    S.lastflip[v] = -1; S.fcnt_t[v] = -1; S.fcnt[v] = 0.0;
  }
  S.nviol = 0;
  for (int k = 0; k < m; k++) {
    if (ks)
      S.ones[k] = (uint8_t)((S.x[kv[3 * k]] ^ ks[3 * k]) + (S.x[kv[3 * k + 1]] ^ ks[3 * k + 1]) + (S.x[kv[3 * k + 2]] ^ ks[3 * k + 2]));
    else
      S.ones[k] = (uint8_t)(S.x[kv[3 * k]] + S.x[kv[3 * k + 1]] + S.x[kv[3 * k + 2]]);
    S.vpos[k] = -1;
    S.lastvisit[k] = -1; S.vcnt_t[k] = -1; S.vcnt[k] = 0.0;
    if (is_v(S.ones[k])) vadd(&S, k);
  }
  S.work = 3 * (int64_t)m;
  S.last_var = -1;
  int minviol = S.nviol;

  int maxdeg = 0;
  for (int v = 0; v < n; v++) if (os[v + 1] - os[v] > maxdeg) maxdeg = os[v + 1] - os[v];
  double *tab = malloc(sizeof(double) * (maxdeg + 2));
  int poly_what = algo == PROBSAT_POLY || algo == GREEDY_WHERE || algo == STICKY ||
                  (algo == POLICY && (flags & WHAT_PROBSAT));
  if (poly_what) {
    double cb = params[0], eps = params[1];
    for (int b = 0; b <= maxdeg + 1; b++) tab[b] = pow(eps + b, -cb);
  } else if (algo == PROBSAT_EXP) {
    for (int b = 0; b <= maxdeg + 1; b++) tab[b] = pow(params[0], -(double)b);
  }

  double h[HR] = {0}, hn[HR];
  double newchosen = 0, newavail = 0, distinct_sum = 0, wsteps = 0, accepted = 0;
  int64_t f = 0;
  while (S.nviol > 0 && f < max_flips) {
    int k, cand[NCAND], isnew[NCAND], nc = 0;
    /* where */
    if (algo == GREEDY_WHERE || (algo == POLICY && (flags & LEARN_WHERE) && S.t > 0)) {
      for (int i = 0; i < S.nnew; i++) {
        int u = S.newk[i];
        if (S.vpos[u] >= 0) { cand[nc] = u; isnew[nc++] = 1; }
      }
      int nn = nc;
      for (int i = 0; i < RANDC; i++) { cand[nc] = S.vlist[rng_below(&S.rng, S.nviol)]; isnew[nc++] = 0; }
      int distinct = 0;
      for (int c = 0; c < nc; c++) {
        int dup = 0;
        for (int e = 0; e < c; e++) if (cand[e] == cand[c]) dup = 1;
        distinct += !dup;
      }
      distinct_sum += distinct;
      wsteps += 1;
      double sc[NCAND];
      int choice;
      if (algo == GREEDY_WHERE && rng_unif(&S.rng) < params[2]) {
        choice = (int)rng_below(&S.rng, nc);
      } else {
        double vage[NCAND];
        for (int c = 0; c < nc; c++) vage[c] = (double)(S.lastvisit[cand[c]] < 0 ? -1e18 : S.lastvisit[cand[c]]);
        for (int c = 0; c < nc; c++) {
          int u = cand[c], minb = 1 << 30, sumb = 0, nz = 0;
          double minbf = 1e9, sumbf = 0.0;
          for (int j = 0; j < 3; j++) {
            int b, mk, vj = S.kv[3 * u + j];
            bm(&S, vj, &b, &mk);
            if (b < minb) minb = b;
            sumb += b;
            nz += b == 0;
            double bf = (double)b / (double)(S.os[vj + 1] - S.os[vj]);
            if (bf < minbf) minbf = bf;
            sumbf += bf;
          }
          if (algo == GREEDY_WHERE) {
            sc[c] = -(double)minb + 1e-3 * rng_unif(&S.rng);
          } else {
            int ov = isnew[c];
            if (!ov && S.last_var >= 0) {
              for (int j = 0; j < 3; j++) if (S.kv[3 * u + j] == S.last_var) ov = 1;
            }
            double xin[DK + HR];
            xin[0] = isnew[c];
            xin[1] = minb / 4.0;
            xin[2] = sumb / 12.0;
            xin[3] = nz / 3.0;
            xin[4] = (flags & MEM_AGE) ? agefeat(S.t, S.lastvisit[u]) : 0.0;
            /* rank by last visit: 1 = visited longest ago (or never) */
            xin[5] = (flags & MEM_AGE) ? 1.0 - rankof(vage, nc, c) : 0.0;
            xin[6] = (flags & MEM_AGE) ? decayed(S.vcnt[u], S.vcnt_t[u], S.t) / 4.0 : 0.0;
            if (flags & MEM_SF) {
              /* visit age over the oldest candidate's */
              double amax = 0.0;
              for (int e = 0; e < nc; e++) {
                double a = (double)(S.lastvisit[cand[e]] < 0 ? S.t + 1 : S.t - S.lastvisit[cand[e]]);
                if (a > amax) amax = a;
              }
              double au = (double)(S.lastvisit[u] < 0 ? S.t + 1 : S.t - S.lastvisit[u]);
              xin[4] = amax > 0 ? au / amax : 1.0;
            }
            xin[7] = ov;
            if (flags & DEGNORM) { xin[1] = minbf; xin[2] = sumbf / 3.0; xin[6] = 0.0; }
            for (int j = 0; j < HR; j++) xin[DK + j] = (flags & MEM_RNN) ? h[j] : 0.0;
            sc[c] = mlp(theta, K_W1, K_B1, K_W2, DK + HR, xin);
          }
        }
        if (algo == GREEDY_WHERE) {
          choice = 0;
          for (int c = 1; c < nc; c++) if (sc[c] > sc[choice]) choice = c;
        } else {
          choice = softmax_pick(&S.rng, sc, nc);
        }
      }
      if (nn > 0) { newavail += 1; newchosen += isnew[choice]; }
      k = cand[choice];
    } else if (algo == STICKY && S.t > 0) {
      int live[NEWMAX], nl = 0;
      for (int i = 0; i < S.nnew; i++) if (S.vpos[S.newk[i]] >= 0) live[nl++] = S.newk[i];
      if (nl > 0) newavail += 1;
      if (nl > 0 && rng_unif(&S.rng) < params[2]) { k = live[rng_below(&S.rng, nl)]; newchosen += 1; }
      else k = S.vlist[rng_below(&S.rng, S.nviol)];
    } else {
      k = S.vlist[rng_below(&S.rng, S.nviol)];
    }
    int was_new = 0;
    for (int i = 0; i < S.nnew; i++) if (S.newk[i] == k) was_new = 1;
    /* visit memory */
    S.vcnt[k] = decayed(S.vcnt[k], S.vcnt_t[k], S.t) + 1.0;
    S.vcnt_t[k] = S.t;
    S.lastvisit[k] = S.t;

    /* what */
    const int32_t *vs = S.kv + 3 * k;
    int b[3] = {0, 0, 0}, mk[3] = {0, 0, 0}, pick = 0, do_flip = 1;
    double w[3];
    switch (algo) {
      case RW:
        pick = (int)rng_below(&S.rng, 3);
        break;
      case WALKSAT: {
        for (int j = 0; j < 3; j++) bm(&S, vs[j], &b[j], &mk[j]);
        int mb = b[0];
        for (int j = 1; j < 3; j++) if (b[j] < mb) mb = b[j];
        if (mb > 0 && rng_unif(&S.rng) < params[0]) {
          pick = (int)rng_below(&S.rng, 3);
        } else {
          int c = 0, idx[3];
          for (int j = 0; j < 3; j++) if (b[j] == mb) idx[c++] = j;
          pick = idx[rng_below(&S.rng, c)];
        }
        break;
      }
      case NOVELTY_PLUS: {
        if (rng_unif(&S.rng) < params[1]) { pick = (int)rng_below(&S.rng, 3); break; }
        int sc[3], best = -1, second = -1, youngest = 0;
        for (int j = 0; j < 3; j++) { bm(&S, vs[j], &b[j], &mk[j]); sc[j] = b[j] - mk[j]; }
        for (int j = 1; j < 3; j++) if (S.lastflip[vs[j]] > S.lastflip[vs[youngest]]) youngest = j;
        for (int j = 0; j < 3; j++) {
          /* better = lower score, then older (smaller lastflip) */
          if (best < 0 || sc[j] < sc[best] ||
              (sc[j] == sc[best] && S.lastflip[vs[j]] < S.lastflip[vs[best]])) {
            second = best; best = j;
          } else if (second < 0 || sc[j] < sc[second] ||
                     (sc[j] == sc[second] && S.lastflip[vs[j]] < S.lastflip[vs[second]])) {
            second = j;
          }
        }
        if (best == youngest && S.lastflip[vs[best]] >= 0 && rng_unif(&S.rng) < params[0]) pick = second;
        else pick = best;
        break;
      }
      case FMS: {
        pick = (int)rng_below(&S.rng, 3);
        bm(&S, vs[pick], &b[pick], &mk[pick]);
        int d = b[pick] - mk[pick];
        if (d > 0 && rng_unif(&S.rng) >= pow(params[0], (double)d)) do_flip = 0;
        break;
      }
      case POLICY:
        if (!(flags & WHAT_PROBSAT)) {
          double sc[3], fage[3], rage[3] = {1.0, 1.0, 1.0};
          for (int j = 0; j < 3; j++) fage[j] = (double)(S.lastflip[vs[j]] < 0 ? -1e18 : S.lastflip[vs[j]]);
          if (flags & MEM_SF) {
            /* age over the knot's oldest */
            double a[3], amax = 0.0;
            for (int j = 0; j < 3; j++) {
              a[j] = (double)(S.lastflip[vs[j]] < 0 ? S.t + 1 : S.t - S.lastflip[vs[j]]);
              if (a[j] > amax) amax = a[j];
            }
            for (int j = 0; j < 3; j++) rage[j] = amax > 0 ? a[j] / amax : 1.0;
          }
          for (int j = 0; j < 3; j++) {
            int v = vs[j];
            bm(&S, v, &b[j], &mk[j]);
            double xin[DW + HR];
            xin[0] = b[j] / 4.0;
            xin[1] = mk[j] / 4.0;
            xin[2] = b[j] == 0;
            xin[3] = (flags & MEM_AGE) ? agefeat(S.t, S.lastflip[v]) : 0.0;
            xin[4] = (flags & MEM_AGE) ? 1.0 - rankof(fage, 3, j) : 0.0; /* 1 = flipped longest ago */
            xin[5] = (flags & MEM_AGE) ? (double)(v == S.last_var) : 0.0;
            xin[6] = (flags & MEM_AGE) ? decayed(S.fcnt[v], S.fcnt_t[v], S.t) / 4.0 : 0.0;
            if (flags & MEM_SF) xin[3] = rage[j];
            if (flags & DEGNORM) {
              double dg = (double)(S.os[v + 1] - S.os[v]);
              xin[0] = b[j] / dg; xin[1] = mk[j] / dg; xin[6] = 0.0;
            }
            for (int i = 0; i < HR; i++) xin[DW + i] = (flags & MEM_RNN) ? h[i] : 0.0;
            sc[j] = mlp(theta, W_W1, W_B1, W_W2, DW + HR, xin);
          }
          pick = softmax_pick(&S.rng, sc, 3);
          break;
        }
        /* flag 8: the fixed probSAT what below */
        __attribute__((fallthrough));
      case PROBSAT_POLY:
      case PROBSAT_EXP:
      case GREEDY_WHERE:
      case STICKY:
        for (int j = 0; j < 3; j++) { bm(&S, vs[j], &b[j], &mk[j]); w[j] = tab[b[j]]; }
        pick = pick3(&S.rng, w);
        break;
    }
    int v = vs[pick];
    double af = agefeat(S.t, S.lastflip[v]);
    if (flags & MEM_SF) {
      double amax = 0.0, a[3];
      for (int j = 0; j < 3; j++) {
        a[j] = (double)(S.lastflip[vs[j]] < 0 ? S.t + 1 : S.t - S.lastflip[vs[j]]);
        if (a[j] > amax) amax = a[j];
      }
      af = amax > 0 ? a[pick] / amax : 1.0;
    }
    int before = S.nviol;
    f++;
    if (do_flip) {
      flip(&S, v);
      accepted += 1;
      S.fcnt[v] = decayed(S.fcnt[v], S.fcnt_t[v], S.t) + 1.0;
      S.fcnt_t[v] = S.t;
      S.lastflip[v] = S.t;
      S.last_var = v;
    } else {
      S.nnew = 0;
    }
    S.t++;
    if (S.nviol < minviol) minviol = S.nviol;
    if (algo == POLICY && (flags & MEM_RNN)) {
      double s[DS];
      s[0] = b[pick] / 4.0;
      s[1] = mk[pick] / 4.0;
      if (flags & DEGNORM) {
        double dg = (double)(S.os[v + 1] - S.os[v]);
        s[0] = b[pick] / dg; s[1] = mk[pick] / dg;
      }
      s[2] = (S.nviol - before) / 2.0;
      s[3] = was_new;
      s[4] = (flags & MEM_SF) ? fmin(1.0, 10.0 * S.nviol / (double)m) : log1p((double)S.nviol) / log1p((double)m);
      s[5] = af;
      for (int i = 0; i < HR; i++) {
        double a = theta[R_B + i];
        for (int j = 0; j < HR; j++) a += theta[R_WH + i * HR + j] * h[j];
        for (int j = 0; j < DS; j++) a += theta[R_WS + i * DS + j] * s[j];
        hn[i] = ftanh(a);
      }
      memcpy(h, hn, sizeof h);
    }
  }
  out[0] = (double)f;
  out[1] = S.nviol == 0;
  out[2] = minviol;
  out[3] = (double)S.work;
  out[5] = newchosen;
  out[6] = newavail;
  out[7] = distinct_sum;
  out[8] = wsteps;
  out[9] = accepted;
  if (xout) memcpy(xout, S.x, n);
  free(tab);
  free(S.x); free(S.ones); free(S.vlist); free(S.vpos);
  free(S.lastflip); free(S.fcnt_t); free(S.fcnt);
  free(S.lastvisit); free(S.vcnt_t); free(S.vcnt);
  out[4] = thread_cpu() - c0;
  return 0;
}

int nae_run(int n, int m, const int32_t *kv, const int32_t *os, const int32_t *occ, int algo,
            const double *params, const double *theta, int flags, uint64_t seed,
            int64_t max_flips, double *out, uint8_t *xout) {
  return nae_run_signed(n, m, kv, os, occ, NULL, NULL, NULL, algo, params, theta, flags, seed, max_flips, out, xout);
}

/* Gate check: random flips; after each, the incremental counts and violated list must equal a
 * recomputation from the state. Returns the number of mismatches found. */
int nae_selftest_signed(int n, int m, const int32_t *kv, const int32_t *os, const int32_t *occ, const uint8_t *ks,
                        const uint8_t *ocs, uint64_t seed, int64_t nflips) {
  St S;
  memset(&S, 0, sizeof S);
  S.n = n; S.m = m; S.kv = kv; S.os = os; S.occ = occ; S.ks = ks; S.ocs = ocs;
  rng_seed(&S.rng, seed);
  S.x = malloc(n); S.ones = malloc(m);
  S.vlist = malloc(sizeof(int32_t) * m); S.vpos = malloc(sizeof(int32_t) * m);
#define LITS(k) ((S.x[kv[3 * (k)]] ^ (ks ? ks[3 * (k)] : 0)) + (S.x[kv[3 * (k) + 1]] ^ (ks ? ks[3 * (k) + 1] : 0)) + \
                 (S.x[kv[3 * (k) + 2]] ^ (ks ? ks[3 * (k) + 2] : 0)))
  for (int v = 0; v < n; v++) S.x[v] = (uint8_t)(rng_next(&S.rng) >> 63);
  for (int k = 0; k < m; k++) {
    S.ones[k] = (uint8_t)LITS(k);
    S.vpos[k] = -1;
    if (is_v(S.ones[k])) vadd(&S, k);
  }
  int bad = 0;
  for (int64_t f = 0; f < nflips; f++) {
    int v = (int)rng_below(&S.rng, n), b, mk, b2 = 0, mk2 = 0;
    bm(&S, v, &b, &mk);
    for (int i = os[v]; i < os[v + 1]; i++) {
      int k = occ[i];
      int s0 = LITS(k);
      int lit = S.x[v] ^ (ocs ? ocs[i] : 0);
      int s1 = s0 + (lit ? -1 : 1);
      if (is_v(s0)) mk2++;
      else if (is_v(s1)) b2++;
    }
    if (b != b2 || mk != mk2) bad++;
    flip(&S, v);
    int nv = 0;
    for (int k = 0; k < m; k++) {
      int s = LITS(k);
      if (s != S.ones[k]) bad++;
      if (is_v(s)) { nv++; if (S.vpos[k] < 0 || S.vlist[S.vpos[k]] != k) bad++; }
      else if (S.vpos[k] >= 0) bad++;
    }
    if (nv != S.nviol) bad++;
  }
  free(S.x); free(S.ones); free(S.vlist); free(S.vpos);
  return bad;
#undef LITS
}

int nae_selftest(int n, int m, const int32_t *kv, const int32_t *os, const int32_t *occ, uint64_t seed, int64_t nflips) {
  return nae_selftest_signed(n, m, kv, os, occ, NULL, NULL, seed, nflips);
}
