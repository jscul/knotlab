/* Referee R1 for SPEC-MERGE-20261117-001: an independent Novelty+ for planted unsigned NAE-3-SAT (the not-all-equal knot
 * law), run in epochs, with per-distinction flip counts, and an independent pair probe.
 *
 * Search rule (McAllester, Selman, Kautz 1997; Hoos 1999), as in the WHERE-NEXT/SCALE-MEMORY/MEET-TRANSFER referees' engine:
 * attend to a uniformly drawn violated knot; with probability wp flip a uniform member; else Novelty on score break - make
 * (ties to the least recently flipped), taking the second best with probability p when the best is the most recently
 * flipped member. A knot is violated when its three members are equal. Own RNG (xoshiro256**, splitmix64 seeding).
 *
 * Pair probe: does assuming x_a ^ x_b = q lead to a contradiction by propagation (a knot with two members equal forces the
 * third to differ; a knot with three equal members is a contradiction)? By the complement symmetry x_a = 0 is fixed. The
 * budget counts forced assignments. Returns 1 if q was refuted within the budget, else 0.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { uint64_t s[4]; } X256;
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t xnext(X256 *r) {
  uint64_t *s = r->s, res = rotl(s[1] * 5, 7) * 9, t = s[1] << 17;
  s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45);
  return res;
}
static uint64_t sm64(uint64_t *z) {
  uint64_t r = (*z += 0x9E3779B97F4A7C15ULL);
  r = (r ^ (r >> 30)) * 0xBF58476D1CE4E5B9ULL; r = (r ^ (r >> 27)) * 0x94D049BB133111EBULL;
  return r ^ (r >> 31);
}
static inline double xu(X256 *r) { return (double)(xnext(r) >> 11) * 0x1.0p-53; }
static inline uint32_t xb(X256 *r, uint32_t k) { return (uint32_t)(((__uint128_t)xnext(r) * k) >> 64); }

typedef struct {
  int n, m;
  int32_t *kv, *ost, *occ, *vl, *vp, *nflip;
  uint8_t *x, *cnt;
  int64_t *lf;
  int nv;
  int64_t f;
  X256 r;
  /* probe scratch */
  int8_t *val;
  int32_t *stack;
} G;

static inline int viol(int c) { return c == 0 || c == 3; }
static inline void vins(G *S, int k) { S->vp[k] = S->nv; S->vl[S->nv++] = k; }
static inline void vrem(G *S, int k) { int p = S->vp[k], last = S->vl[--S->nv]; S->vl[p] = last; S->vp[last] = p; S->vp[k] = -1; }

static void flip(G *S, int v) {
  int down = S->x[v];
  S->x[v] ^= 1;
  for (int i = S->ost[v]; i < S->ost[v + 1]; i++) {
    int k = S->occ[i], o = S->cnt[k], w = down ? o - 1 : o + 1;
    S->cnt[k] = (uint8_t)w;
    if (viol(o) && !viol(w)) vrem(S, k);
    else if (!viol(o) && viol(w)) vins(S, k);
  }
  S->nflip[v]++;
  S->lf[v] = S->f;
}

static inline int score(const G *S, int v) {
  int b = 0, mk = 0, xv = S->x[v];
  for (int i = S->ost[v]; i < S->ost[v + 1]; i++) {
    int c = S->cnt[S->occ[i]];
    if (viol(c)) mk++;
    else if ((xv && c == 1) || (!xv && c == 2)) b++;
  }
  return b - mk;
}

static const int PERM[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};

void *g_new(int n, int m, const int32_t *kv, uint64_t seed) {
  G *S = calloc(1, sizeof(G));
  S->n = n; S->m = m;
  S->kv = malloc(sizeof(int32_t) * 3 * (size_t)m); memcpy(S->kv, kv, sizeof(int32_t) * 3 * (size_t)m);
  S->ost = calloc(n + 1, sizeof(int32_t)); S->occ = malloc(sizeof(int32_t) * 3 * (size_t)m);
  for (int i = 0; i < 3 * m; i++) S->ost[kv[i] + 1]++;
  for (int v = 0; v < n; v++) S->ost[v + 1] += S->ost[v];
  int32_t *fill = malloc(sizeof(int32_t) * n); memcpy(fill, S->ost, sizeof(int32_t) * n);
  for (int k = 0; k < m; k++) for (int j = 0; j < 3; j++) S->occ[fill[kv[3 * k + j]]++] = k;
  free(fill);
  S->x = malloc(n); S->cnt = malloc(m); S->vl = malloc(sizeof(int32_t) * m); S->vp = malloc(sizeof(int32_t) * m);
  S->lf = malloc(sizeof(int64_t) * n); S->nflip = calloc(n, sizeof(int32_t));
  S->val = malloc(n); S->stack = malloc(sizeof(int32_t) * n);
  uint64_t z = seed;
  for (int i = 0; i < 4; i++) S->r.s[i] = sm64(&z);
  for (int v = 0; v < n; v++) { S->x[v] = (uint8_t)(xnext(&S->r) >> 63); S->lf[v] = -1; }
  for (int k = 0; k < m; k++) {
    S->cnt[k] = (uint8_t)(S->x[kv[3 * k]] + S->x[kv[3 * k + 1]] + S->x[kv[3 * k + 2]]);
    S->vp[k] = -1;
    if (viol(S->cnt[k])) vins(S, k);
  }
  return S;
}

/* out: [0] flips this call, [1] solved, [2] violated count at the end */
void g_run(void *h, double p, double wp, int64_t nflips, double *out) {
  G *S = h;
  int64_t f0 = S->f;
  while (S->nv > 0 && S->f - f0 < nflips) {
    int k = S->vl[xb(&S->r, S->nv)];
    const int32_t *vs = S->kv + 3 * k;
    int pick;
    if (xu(&S->r) < wp) pick = (int)xb(&S->r, 3);
    else {
      int sc[3];
      for (int j = 0; j < 3; j++) sc[j] = score(S, vs[j]);
      const int *o = PERM[xb(&S->r, 6)];
      int best = o[0], second = -1;
      for (int t = 1; t < 3; t++) {
        int j = o[t];
        if (sc[j] < sc[best] || (sc[j] == sc[best] && S->lf[vs[j]] < S->lf[vs[best]])) { second = best; best = j; }
        else if (second < 0 || sc[j] < sc[second] || (sc[j] == sc[second] && S->lf[vs[j]] < S->lf[vs[second]])) second = j;
      }
      int young = 0;
      for (int j = 1; j < 3; j++) if (S->lf[vs[j]] > S->lf[vs[young]]) young = j;
      if (S->lf[vs[young]] < 0) young = -1;
      pick = (best == young && xu(&S->r) < p) ? second : best;
    }
    flip(S, vs[pick]);
    S->f++;
  }
  out[0] = (double)(S->f - f0); out[1] = S->nv == 0; out[2] = S->nv;
}

void g_state(void *h, uint8_t *x, int32_t *nflip) {
  G *S = h;
  memcpy(x, S->x, S->n);
  memcpy(nflip, S->nflip, sizeof(int32_t) * S->n);
}

/* propagate from the assignments on the stack [0, top); returns 1 on contradiction, 0 otherwise or out of budget (*spent) */
static int propagate(G *S, int top, int budget, int *spent, int *topo) {
  int head = 0;
  while (head < top) {
    int v = S->stack[head++];
    for (int i = S->ost[v]; i < S->ost[v + 1]; i++) {
      const int32_t *ks = S->kv + 3 * S->occ[i];
      int a = S->val[ks[0]], b = S->val[ks[1]], c = S->val[ks[2]];
      int na = (a >= 0) + (b >= 0) + (c >= 0);
      if (na == 3) { if (a == b && b == c) { *topo = top; return 1; } continue; }
      if (na == 2) {
        int u, w, free_;
        if (a < 0) { free_ = ks[0]; u = b; w = c; } else if (b < 0) { free_ = ks[1]; u = a; w = c; } else { free_ = ks[2]; u = a; w = b; }
        if (u == w) {
          if (++(*spent) > budget) { *topo = top; return 0; }
          S->val[free_] = (int8_t)(1 - u);
          S->stack[top++] = free_;
        }
      }
    }
  }
  *topo = top;
  return 0;
}

int g_pair_probe(void *h, int a, int b, int q, int budget) {
  G *S = h;
  if (a == b) return q == 1;
  memset(S->val, -1, S->n);
  S->val[a] = 0; S->val[b] = (int8_t)q;
  S->stack[0] = a; S->stack[1] = b;
  int spent = 0, top = 0;
  int res = propagate(S, 2, budget, &spent, &top);
  return res;
}

void g_free(void *h) {
  G *S = h;
  free(S->kv); free(S->ost); free(S->occ); free(S->x); free(S->cnt); free(S->vl); free(S->vp); free(S->lf); free(S->nflip);
  free(S->val); free(S->stack); free(S);
}
