/* A fast loop and a slow loop on signed three-place not-all-equal knots (SLOW-LOOP-20261117-001A; copied for
 * EARN-BUDGET-20261117-001A and SPEC-MERGE-20261117-001A, which adds per-distinction flip counts and a pair probe). 
 *
 * Knot k binds the distinctions kv[3k..3k+2] with signs ks[3k..3k+2]. It reads the effective values x[v] ^ s and is
 * violated when all three are equal; it allows the other six joint states. Every sign 0 is the knot law of
 * WHERE-NEXT-20261116-001A, and the fast loop here then reproduces that engine run for run (gate G6): the same
 * initial state from the seed, the same random calls, the same incidence order and the same work count.
 *
 * Fast loop (fl_run): Novelty+ (algo 4) or probSAT poly (algo 2), as in WHERE-NEXT's nae_engine.c, for at most a
 * given number of flips, keeping its state between calls (one call is one epoch). It also counts, per knot, how
 * often it attended to the knot during the call: where the search dwelt.
 *
 * Slow loop (sl_probe): bounded refutation by propagation. A probe assumes a joint state of a few distinctions and
 * propagates the knots (a knot with two effective values known and equal forces its third to the other value);
 * reaching a knot with three equal effective values refutes the assumption. Refutation is sound: a refuted state
 * holds in no allowed state of the pattern, so every relation read off it holds in every allowed state.
 *   tie probe of a knot (a, b, c): assume each of its three allowed patterns up to complement ("a differs",
 *     "b differs", "c differs"); a refuted "a differs" means b and c are unequal in every allowed state: a tie.
 *   shadow-knot probe of a triple not already a knot: assume each of its four joint states up to complement; exactly one
 *     refuted pair {p, not p} is a signed three-place knot implied by the pattern (it passes K1-K3); two or three
 *     refuted pairs are ties.
 * Targets: mode 0 the knots the fast loop attended to most in the last epoch (guided), mode 1 knots drawn
 * uniformly (random), mode 2 every knot in index order (static). Each probe is charged three incidences per knot it
 * reads; the slow loop stops when its charged work reaches its budget. The tie classes, the rebuilt pattern and the
 * reconstruction of a state of the original pattern are kept in Python (slow_loop.py).
 *
 * Work is counted in incidences touched (one knot-distinction pair read), so it does not depend on the machine.
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { PROBSAT_POLY = 2, NOVELTY_PLUS = 4 };

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

static double thread_cpu(void) {
  struct timespec ts;
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

typedef struct {
  int n, m;
  int32_t *kv; uint8_t *ks;          /* knots: members and signs */
  int32_t *os, *occk; uint8_t *occs; /* incidences of each distinction: knot and sign */
  uint8_t *x, *ones;
  int32_t *vlist, *vpos;
  int nviol;
  int64_t t, *lastflip;
  int32_t *visits, *vlistk; /* attention counts this epoch, and the knots attended to, in order of first visit */
  int nvis;
  uint8_t *probed;
  int sortlog;                       /* EARN-BUDGET charge v2: the guided order's sort charged k log k, not k */
  int32_t *nflip;                    /* SPEC-MERGE: flips of each distinction since the handle was made */
  int8_t *val; int32_t *trail;       /* probe scratch */
  Rng rng, srng;
  int maxdeg;
} H;

static inline void vadd(H *S, int k) { S->vpos[k] = S->nviol; S->vlist[S->nviol++] = k; }
static inline void vdel(H *S, int k) {
  int p = S->vpos[k], last = S->vlist[--S->nviol];
  S->vlist[p] = last; S->vpos[last] = p; S->vpos[k] = -1;
}
static inline int is_v(int o) { return o == 0 || o == 3; }

/* Draw the initial state exactly as WHERE-NEXT's engine does: seed, then one bit per distinction. */
void fl_init_state(int n, uint64_t seed, uint8_t *x, uint64_t *rng_out) {
  Rng r;
  rng_seed(&r, seed);
  for (int v = 0; v < n; v++) x[v] = (uint8_t)(rng_next(&r) >> 63);
  rng_out[0] = r.s[0]; rng_out[1] = r.s[1];
}

/* A handle on one pattern with the fast loop's state. Charges 3m incidences (the initial count), returned in *work. */
void *fl_new(int n, int m, const int32_t *kv, const uint8_t *ks, const uint8_t *x0, const int64_t *lastflip0,
             const uint64_t *rng, uint64_t sseed, int64_t t0, const uint8_t *probed0, int64_t *work) {
  H *S = calloc(1, sizeof(H));
  S->n = n; S->m = m;
  S->kv = malloc(sizeof(int32_t) * 3 * (size_t)(m ? m : 1)); memcpy(S->kv, kv, sizeof(int32_t) * 3 * (size_t)m);
  S->ks = malloc(3 * (size_t)(m ? m : 1)); memcpy(S->ks, ks, 3 * (size_t)m);
  S->os = calloc((size_t)n + 1, sizeof(int32_t));
  for (int i = 0; i < 3 * m; i++) S->os[kv[i] + 1]++;
  for (int v = 0; v < n; v++) S->os[v + 1] += S->os[v];
  S->occk = malloc(sizeof(int32_t) * 3 * (size_t)(m ? m : 1));
  S->occs = malloc(3 * (size_t)(m ? m : 1));
  int32_t *fill = malloc(sizeof(int32_t) * ((size_t)n + 1));
  memcpy(fill, S->os, sizeof(int32_t) * ((size_t)n + 1));
  /* knots in index order within each distinction, as numpy's stable argsort gives WHERE-NEXT */
  for (int i = 0; i < 3 * m; i++) { int v = kv[i], p = fill[v]++; S->occk[p] = i / 3; S->occs[p] = ks[i]; }
  free(fill);
  S->maxdeg = 0;
  for (int v = 0; v < n; v++) if (S->os[v + 1] - S->os[v] > S->maxdeg) S->maxdeg = S->os[v + 1] - S->os[v];
  S->x = malloc((size_t)(n ? n : 1)); memcpy(S->x, x0, (size_t)n);
  S->lastflip = malloc(sizeof(int64_t) * (size_t)(n ? n : 1)); memcpy(S->lastflip, lastflip0, sizeof(int64_t) * (size_t)n);
  S->ones = malloc((size_t)(m ? m : 1));
  S->vlist = malloc(sizeof(int32_t) * (size_t)(m ? m : 1)); S->vpos = malloc(sizeof(int32_t) * (size_t)(m ? m : 1));
  S->visits = calloc((size_t)(m ? m : 1), sizeof(int32_t));
  S->vlistk = malloc(sizeof(int32_t) * (size_t)(m ? m : 1));
  S->nflip = calloc((size_t)(n ? n : 1), sizeof(int32_t));
  S->nvis = 0;
  S->probed = calloc((size_t)(m ? m : 1), 1);
  if (probed0) memcpy(S->probed, probed0, (size_t)m);
  S->val = malloc((size_t)(n ? n : 1)); memset(S->val, -1, (size_t)n);
  S->trail = malloc(sizeof(int32_t) * (size_t)(n ? n : 1));
  S->nviol = 0;
  for (int k = 0; k < m; k++) {
    S->ones[k] = (uint8_t)((S->x[kv[3 * k]] ^ ks[3 * k]) + (S->x[kv[3 * k + 1]] ^ ks[3 * k + 1]) +
                           (S->x[kv[3 * k + 2]] ^ ks[3 * k + 2]));
    S->vpos[k] = -1;
    if (is_v(S->ones[k])) vadd(S, k);
  }
  S->rng.s[0] = rng[0]; S->rng.s[1] = rng[1];
  rng_seed(&S->srng, sseed);
  S->t = t0;
  *work = 3 * (int64_t)m;
  return S;
}

void fl_free(void *h) {
  H *S = h;
  free(S->kv); free(S->ks); free(S->os); free(S->occk); free(S->occs); free(S->x); free(S->lastflip);
  free(S->ones); free(S->vlist); free(S->vpos); free(S->visits); free(S->vlistk); free(S->nflip); free(S->probed); free(S->val); free(S->trail);
  free(S);
}

void fl_get(void *h, uint8_t *x, int64_t *lastflip, uint64_t *rng, int64_t *t, int32_t *visits, uint8_t *probed) {
  H *S = h;
  if (x) memcpy(x, S->x, (size_t)S->n);
  if (lastflip) memcpy(lastflip, S->lastflip, sizeof(int64_t) * (size_t)S->n);
  if (rng) { rng[0] = S->rng.s[0]; rng[1] = S->rng.s[1]; }
  if (t) *t = S->t;
  if (visits) memcpy(visits, S->visits, sizeof(int32_t) * (size_t)S->m);
  if (probed) memcpy(probed, S->probed, (size_t)S->m);
}

int fl_nviol(void *h) { return ((H *)h)->nviol; }
void fl_set_sortlog(void *h, int on) { ((H *)h)->sortlog = on; }
void fl_get_flips(void *h, int32_t *out) { H *S = h; memcpy(out, S->nflip, sizeof(int32_t) * (size_t)S->n); }

static void flip(H *S, int v, int64_t *work) {
  int xv = S->x[v];
  S->x[v] ^= 1;
  S->nflip[v]++;
  for (int i = S->os[v]; i < S->os[v + 1]; i++) {
    int k = S->occk[i], o = S->ones[k], up = (xv ^ S->occs[i]) == 0, nw = up ? o + 1 : o - 1;
    S->ones[k] = (uint8_t)nw;
    int wv = is_v(o), nv = is_v(nw);
    if (wv && !nv) vdel(S, k);
    else if (!wv && nv) vadd(S, k);
  }
  *work += S->os[v + 1] - S->os[v];
}

/* break: satisfied knots of v that a flip of v would violate; make: violated knots of v */
static inline void bm(H *S, int v, int *b, int *mk, int64_t *work) {
  int bb = 0, mm = 0, xv = S->x[v];
  for (int i = S->os[v]; i < S->os[v + 1]; i++) {
    int o = S->ones[S->occk[i]];
    if (is_v(o)) mm++;
    else if ((xv ^ S->occs[i]) ? (o == 1) : (o == 2)) bb++;
  }
  *work += S->os[v + 1] - S->os[v];
  *b = bb; *mk = mm;
}

static inline int pick3(Rng *r, const double *w) {
  double s = w[0] + w[1] + w[2], u = rng_unif(r) * s;
  if (u < w[0]) return 0;
  if (u < w[0] + w[1]) return 1;
  return 2;
}

/* One epoch: at most max_flips flips, or until no knot is violated. The visit counts restart at each call.
 * out: [0] flips, [1] solved, [2] least violated count seen, [3] work, [4] thread CPU seconds */
int fl_run(void *h, int algo, const double *params, int64_t max_flips, double *out) {
  H *S = h;
  double c0 = thread_cpu();
  int64_t work = 0, f = 0;
  int minviol = S->nviol;
  for (int i = 0; i < S->nvis; i++) S->visits[S->vlistk[i]] = 0;
  S->nvis = 0;
  double *tab = NULL;
  if (algo == PROBSAT_POLY) {
    tab = malloc(sizeof(double) * ((size_t)S->maxdeg + 2));
    for (int b = 0; b <= S->maxdeg + 1; b++) tab[b] = pow(params[1] + b, -params[0]);
  }
  while (S->nviol > 0 && f < max_flips) {
    int k = S->vlist[rng_below(&S->rng, S->nviol)];
    if (S->visits[k]++ == 0) S->vlistk[S->nvis++] = k;
    const int32_t *vs = S->kv + 3 * k;
    int b[3] = {0, 0, 0}, mk[3] = {0, 0, 0}, pick = 0;
    if (algo == NOVELTY_PLUS) {
      if (rng_unif(&S->rng) < params[1]) {
        pick = (int)rng_below(&S->rng, 3);
      } else {
        int sc[3], best = -1, second = -1, youngest = 0;
        for (int j = 0; j < 3; j++) { bm(S, vs[j], &b[j], &mk[j], &work); sc[j] = b[j] - mk[j]; }
        for (int j = 1; j < 3; j++) if (S->lastflip[vs[j]] > S->lastflip[vs[youngest]]) youngest = j;
        for (int j = 0; j < 3; j++) {
          if (best < 0 || sc[j] < sc[best] ||
              (sc[j] == sc[best] && S->lastflip[vs[j]] < S->lastflip[vs[best]])) {
            second = best; best = j;
          } else if (second < 0 || sc[j] < sc[second] ||
                     (sc[j] == sc[second] && S->lastflip[vs[j]] < S->lastflip[vs[second]])) {
            second = j;
          }
        }
        if (best == youngest && S->lastflip[vs[best]] >= 0 && rng_unif(&S->rng) < params[0]) pick = second;
        else pick = best;
      }
    } else {
      double w[3];
      for (int j = 0; j < 3; j++) { bm(S, vs[j], &b[j], &mk[j], &work); w[j] = tab[b[j]]; }
      pick = pick3(&S->rng, w);
    }
    int v = vs[pick];
    f++;
    flip(S, v, &work);
    S->lastflip[v] = S->t;
    S->t++;
    if (S->nviol < minviol) minviol = S->nviol;
  }
  free(tab);
  out[0] = (double)f; out[1] = S->nviol == 0; out[2] = minviol; out[3] = (double)work; out[4] = thread_cpu() - c0;
  return S->nviol == 0;
}

/* ---- slow loop ---- */

/* Propagate from the assumed values; returns 1 on a refutation, 0 otherwise (also when the budget runs out). */
static int propagate(H *S, int ns, const int32_t *sv, const uint8_t *sx, int64_t budget, int64_t *work) {
  int nt = 0, head = 0, refuted = 0;
  int64_t used = 0;
  for (int i = 0; i < ns; i++) {
    if (S->val[sv[i]] >= 0) { if (S->val[sv[i]] != sx[i]) { refuted = 1; goto done; } continue; }
    S->val[sv[i]] = (int8_t)sx[i];
    S->trail[nt++] = sv[i];
  }
  while (head < nt) {
    int v = S->trail[head++];
    for (int i = S->os[v]; i < S->os[v + 1]; i++) {
      if (used >= budget) goto done;
      int k = S->occk[i];
      used += 3;
      int e[3], u = -1, nk = 0;
      for (int j = 0; j < 3; j++) {
        int w = S->kv[3 * k + j], a = S->val[w];
        if (a < 0) { e[j] = -1; u = j; } else { e[j] = a ^ S->ks[3 * k + j]; nk++; }
      }
      if (nk == 3) {
        if (e[0] == e[1] && e[1] == e[2]) { refuted = 1; goto done; }
      } else if (nk == 2) {
        int p = (u + 1) % 3, q = (u + 2) % 3;
        if (e[p] == e[q]) {
          int w = S->kv[3 * k + u];
          S->val[w] = (int8_t)((e[p] ^ 1) ^ S->ks[3 * k + u]);
          S->trail[nt++] = w;
        }
      }
    }
  }
done:
  for (int i = 0; i < nt; i++) S->val[S->trail[i]] = -1;
  *work += used + ns;
  return refuted;
}

static int is_knot(H *S, int a, int b, int c, int64_t *work) {
  for (int i = S->os[a]; i < S->os[a + 1]; i++) {
    const int32_t *t = S->kv + 3 * S->occk[i];
    int hb = t[0] == b || t[1] == b || t[2] == b, hc = t[0] == c || t[1] == c || t[2] == c;
    if (hb && hc) { *work += i - S->os[a] + 1; return 1; }
  }
  *work += S->os[a + 1] - S->os[a];
  return 0;
}

/* Ties are written as (p, q, parity): x_p = x_q ^ parity in every allowed state. Shadow knots as (a, b, c, sa, sb, sc). */
typedef struct { int32_t *ties; int nt, capt; int32_t *br; int nb, capb; } Out;

static void put_tie(Out *O, int p, int q, int par) {
  if (O->nt < O->capt) { O->ties[3 * O->nt] = p; O->ties[3 * O->nt + 1] = q; O->ties[3 * O->nt + 2] = par; O->nt++; }
}

static int tie_probe(H *S, int k, int64_t pb, int64_t *work, Out *O) {
  const int32_t *t = S->kv + 3 * k;
  const uint8_t *s = S->ks + 3 * k;
  int found = 0, nref = 0;
  for (int d = 0; d < 3; d++) {
    uint8_t xs[3];
    for (int j = 0; j < 3; j++) xs[j] = (uint8_t)((j == d) ^ s[j]);
    if (propagate(S, 3, t, xs, pb, work)) {
      nref++;
      int p = (d + 1) % 3, q = (d + 2) % 3;
      put_tie(O, t[p], t[q], 1 ^ s[p] ^ s[q]);
      found++;
    }
  }
  return nref == 3 ? -1 : found;
}

static int shadow_triple(H *S, int a, int b, int c, int64_t pb, int64_t *work, Out *O) {
  static const uint8_t reps[4][3] = {{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
  int32_t tv[3] = {a, b, c};
  int ref[4], nref = 0;
  for (int r = 0; r < 4; r++) { ref[r] = propagate(S, 3, tv, reps[r], pb, work); nref += ref[r]; }
  if (nref == 0) return 0;
  if (nref == 4) return -1;
  if (nref == 1) {
    for (int r = 0; r < 4; r++)
      if (ref[r] && O->nb < O->capb) {
        int32_t *w = O->br + 6 * O->nb++;
        w[0] = a; w[1] = b; w[2] = c; w[3] = reps[r][0]; w[4] = reps[r][1]; w[5] = reps[r][2];
      }
    return 1;
  }
  /* two or three refuted: the surviving representatives agree on the parity of some pair, which is a tie */
  int surv[4], ns = 0;
  for (int r = 0; r < 4; r++) if (!ref[r]) surv[ns++] = r;
  static const int pairs[3][2] = {{0, 1}, {0, 2}, {1, 2}};
  int got = 0;
  for (int pi = 0; pi < 3; pi++) {
    int i = pairs[pi][0], j = pairs[pi][1], par = reps[surv[0]][i] ^ reps[surv[0]][j], same = 1;
    for (int z = 1; z < ns; z++) if ((reps[surv[z]][i] ^ reps[surv[z]][j]) != par) same = 0;
    if (same) { put_tie(O, tv[i], tv[j], par); got++; }
  }
  return got;
}

static const int32_t *g_vis;
static int cmp_vis(const void *a, const void *b) {
  int ka = *(const int32_t *)a, kb = *(const int32_t *)b;
  if (g_vis[ka] != g_vis[kb]) return g_vis[kb] - g_vis[ka];
  return ka - kb;
}

/* One slow-loop pass. mode 0 guided, 1 random, 2 static (every knot in order). budget: charged incidences
 * (<= 0: no limit). pb: budget of one probe. beta: share of targets followed by shadow-knot probes (each target is
 * followed by them with probability beta). J: overlapping knots read per such target. abort_after (> 0): stop once that
 * many targets have been probed without a find.
 * out: [0] targets probed, [1] ties written, [2] shadow knots written, [3] work, [4] thread CPU, [5] refuted all patterns
 * of something (a contradiction; never expected on a planted pattern) */
int sl_probe(void *h, int mode, int64_t budget, int64_t pb, double beta, int J, int abort_after, int32_t *ties,
             int capt, int32_t *br, int capb, double *out) {
  H *S = h;
  double c0 = thread_cpu();
  int64_t work = 0;
  Out O = {ties, 0, capt, br, 0, capb};
  int ntarg = 0, contra = 0;
  int32_t *order = NULL;
  int nord = 0;
  if (mode == 0) {
    order = malloc(sizeof(int32_t) * (size_t)(S->nvis ? S->nvis : 1));
    for (int i = 0; i < S->nvis; i++) if (!S->probed[S->vlistk[i]]) order[nord++] = S->vlistk[i];
    g_vis = S->visits;
    qsort(order, (size_t)nord, sizeof(int32_t), cmp_vis);
    work += S->nvis + (S->sortlog ? (int64_t)(nord * ceil(log2(nord + 1.0))) : nord);
  } else if (mode == 2) {
    nord = S->m;
  } else {
    nord = S->m; /* random draws, at most m tries per target */
  }
  for (int idx = 0; idx < nord; idx++) {
    if (budget > 0 && work >= budget) break;
    if (abort_after > 0 && ntarg >= abort_after && O.nt + O.nb == 0) break; /* a pass that finds nothing early stops */
    int k;
    if (mode == 0) k = order[idx];
    else if (mode == 2) { k = idx; if (S->probed[k]) continue; }
    else {
      int tries = 0;
      do { k = (int)rng_below(&S->srng, (uint32_t)S->m); work += 1; } while (S->probed[k] && ++tries < 64);
      if (S->probed[k]) break;
    }
    S->probed[k] = 1;
    ntarg++;
    if (tie_probe(S, k, pb, &work, &O) < 0) contra = 1;
    if (beta > 0 && rng_unif(&S->srng) < beta) {
      const int32_t *t = S->kv + 3 * k;
      for (int jj = 0; jj < J; jj++) {
        int cpos = (int)rng_below(&S->srng, 3), c = t[cpos];
        int deg = S->os[c + 1] - S->os[c];
        if (deg < 2) continue;
        int k2 = S->occk[S->os[c] + (int)rng_below(&S->srng, (uint32_t)deg)];
        if (k2 == k) continue;
        const int32_t *t2 = S->kv + 3 * k2;
        int a = t[(cpos + 1) % 3], b = t[(cpos + 2) % 3], u = -1, w = -1, shared = 0;
        for (int j = 0; j < 3; j++) {
          if (t2[j] == c) continue;
          if (t2[j] == a || t2[j] == b) { shared = 1; break; }
          if (u < 0) u = t2[j]; else w = t2[j];
        }
        if (shared || u < 0 || w < 0) continue;
        int tri[4][3] = {{a, b, u}, {a, b, w}, {a, u, w}, {b, u, w}};
        for (int q = 0; q < 4; q++) {
          if (is_knot(S, tri[q][0], tri[q][1], tri[q][2], &work)) continue;
          if (shadow_triple(S, tri[q][0], tri[q][1], tri[q][2], pb, &work, &O) < 0) contra = 1;
        }
        work += 6;
      }
    }
  }
  free(order);
  out[0] = ntarg; out[1] = O.nt; out[2] = O.nb; out[3] = (double)work; out[4] = thread_cpu() - c0; out[5] = contra;
  return O.nt + O.nb;
}

/* ---- tie classes ---- */

static int uf_find(int32_t *parent, uint8_t *par, int v, int *pv) {
  int p = 0, r = v;
  while (parent[r] != r) { p ^= par[r]; r = parent[r]; }
  /* compress: every node on the path points at the root with its own parity */
  int acc = p, u = v;
  while (parent[u] != u) {
    int nx = parent[u], pu = par[u];
    parent[u] = r; par[u] = (uint8_t)acc;
    acc ^= pu; u = nx;
  }
  *pv = p;
  return r;
}

/* Apply ties (a, b, parity: x_a = x_b ^ parity) and the ties that merging forces, over every knot of the pattern
 * (original and derived, in original distinction ids). A knot whose members fall in two classes with equal effective
 * signs at the shared class forces its third member to differ: a new tie. Returns the root and parity of every
 * distinction. out: [0] contradiction, [1] work (incidences read). parent/par/size are the tie classes, kept
 * between calls. */
void sl_reduce(int n0, int m, const int32_t *kv, const uint8_t *ks, int32_t *parent, uint8_t *par, int32_t *size,
               int ntie, const int32_t *ties, int32_t *root_out, uint8_t *par_out, int32_t *kv_out, uint8_t *ks_out,
               uint8_t *keep_out, double *out) {
  int64_t work = 0;
  int contra = 0;
  if (m < 0) m = 0;
  /* incidence lists per class, as linked lists that are joined on a merge */
  int32_t *head = malloc(sizeof(int32_t) * (size_t)n0), *tail = malloc(sizeof(int32_t) * (size_t)n0);
  int32_t *nxt = malloc(sizeof(int32_t) * 3 * (size_t)(m ? m : 1));
  for (int v = 0; v < n0; v++) head[v] = tail[v] = -1;
  for (int i = 0; i < 3 * m; i++) {
    int pv, r = uf_find(parent, par, kv[i], &pv);
    nxt[i] = -1;
    if (head[r] < 0) head[r] = tail[r] = i; else { nxt[tail[r]] = i; tail[r] = i; }
  }
  work += 3 * (int64_t)m;
  int32_t *wl = malloc(sizeof(int32_t) * (size_t)(m ? m : 1) * 4 + 64);
  uint8_t *inwl = calloc((size_t)(m ? m : 1), 1);
  int64_t cap = (int64_t)(m ? m : 1) * 4 + 16, wn = 0;
  for (int k = 0; k < m; k++) { wl[wn++] = k; inwl[k] = 1; }
  int ti = 0;
  for (;;) {
    int a, b, parity;
    if (ti < ntie) {
      a = ties[3 * ti]; b = ties[3 * ti + 1]; parity = ties[3 * ti + 2]; ti++;
    } else {
      if (wn == 0) break;
      int k = wl[--wn];
      inwl[k] = 0;
      int r[3], s[3];
      for (int j = 0; j < 3; j++) { int pv; r[j] = uf_find(parent, par, kv[3 * k + j], &pv); s[j] = ks[3 * k + j] ^ pv; }
      work += 3;
      int e01 = r[0] == r[1], e02 = r[0] == r[2], e12 = r[1] == r[2];
      if (e01 && e02) { if (s[0] == s[1] && s[1] == s[2]) contra = 1; continue; }
      int p, q, u;
      if (e01) { p = 0; q = 1; u = 2; } else if (e02) { p = 0; q = 2; u = 1; } else if (e12) { p = 1; q = 2; u = 0; }
      else continue;
      if (s[p] != s[q]) continue;      /* always satisfied */
      a = r[u]; b = r[p]; parity = s[u] ^ s[p] ^ 1;
    }
    int pa, pb, ra = uf_find(parent, par, a, &pa), rb = uf_find(parent, par, b, &pb);
    if (ra == rb) { if ((pa ^ pb) != parity) contra = 1; continue; }
    int d = pa ^ pb ^ parity;          /* x_ra = x_rb ^ d */
    if (size[ra] > size[rb]) { int tt = ra; ra = rb; rb = tt; }
    parent[ra] = rb; par[ra] = (uint8_t)d; size[rb] += size[ra];
    /* re-read every knot of the smaller class, then join its list to the larger's */
    for (int i = head[ra]; i >= 0; i = nxt[i]) {
      int k = i / 3;
      work += 1;
      if (!inwl[k]) {
        if (wn >= cap) { cap *= 2; wl = realloc(wl, sizeof(int32_t) * (size_t)cap); }
        wl[wn++] = k; inwl[k] = 1;
      }
    }
    if (head[ra] >= 0) {
      if (head[rb] < 0) { head[rb] = head[ra]; tail[rb] = tail[ra]; }
      else { nxt[tail[rb]] = head[ra]; tail[rb] = tail[ra]; }
      head[ra] = tail[ra] = -1;
    }
  }
  for (int v = 0; v < n0; v++) { int pv; root_out[v] = uf_find(parent, par, v, &pv); par_out[v] = (uint8_t)pv; }
  work += n0;
  /* every knot through the classes: members sorted, first sign 0 (complement symmetry), kept when its three
   * members fall in three classes */
  for (int k = 0; k < m; k++) {
    int r[3], s[3];
    for (int j = 0; j < 3; j++) { r[j] = root_out[kv[3 * k + j]]; s[j] = ks[3 * k + j] ^ par_out[kv[3 * k + j]]; }
    for (int a = 0; a < 2; a++)
      for (int b = 0; b < 2 - a; b++)
        if (r[b] > r[b + 1]) { int t1 = r[b]; r[b] = r[b + 1]; r[b + 1] = t1; t1 = s[b]; s[b] = s[b + 1]; s[b + 1] = t1; }
    keep_out[k] = r[0] != r[1] && r[1] != r[2];
    for (int j = 0; j < 3; j++) { kv_out[3 * k + j] = r[j]; ks_out[3 * k + j] = (uint8_t)(s[j] ^ s[0]); }
  }
  work += 3 * (int64_t)m;
  free(head); free(tail); free(nxt); free(wl); free(inwl);
  out[0] = contra; out[1] = (double)work;
}

/* SPEC-MERGE: is the pair (a, b) tied by a refutation? Assumes x_a = x_b and then x_a != x_b, propagating each; bit 0 of
 * the result: "equal" refuted (so a and b are unequal in every allowed state); bit 1: "unequal" refuted. out[0] = work. */
int sl_pair_probe(void *h, int a, int b, int64_t pb, double *out) {
  H *S = h;
  int64_t work = 0;
  int32_t sv[2] = {a, b};
  uint8_t eq[2] = {0, 0}, ne[2] = {0, 1};
  int r = 0;
  if (propagate(S, 2, sv, eq, pb, &work)) r |= 1;
  if (propagate(S, 2, sv, ne, pb, &work)) r |= 2;
  out[0] = (double)work;
  return r;
}
