/* Maximal unheld groups of an end, the search used by rlaw.Groups (same algorithm as its Python fallback).

   Nodes are classes of interchangeable knots that lie in two or more witnessed sets.  adj: m rows of W words (bit set
   of adjacent classes).  bmask: B rows of W words (the classes in each witnessed set).  keys: for class j, its witnessed
   sets are keys[koff[j] .. koff[j+1]-1].  size[j]: knots in class j.  A Bron-Kerbosch search with pivot (the pivot is
   a class of P|X with the most neighbours in P), pruned when R|P has fewer than three knots or lies inside one
   witnessed set; every maximal R with P and X empty is written to out as (length, classes...).
   Returns the number of ints written, -1 when cap is too small, or -3 when more than `limit` groups exist (limit >= 0).
   Build: gcc -O2 -shared -fPIC -o bk.so bk.c */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef uint64_t u64;

static int m_, W_;
static const u64 *adj_, *bmask_;
static const int *keys_, *koff_, *size_;
static int *out_;
static long cap_, used_, limit_, found_;
static int overflow_, exceeded_;
static u64 *stack_;  /* per depth: R, P, X */
static int *rlist_;

static int weight3(const u64 *rp) {
    int w = 0;
    for (int i = 0; i < W_; i++) {
        u64 x = rp[i];
        while (x) {
            int b = __builtin_ctzll(x);
            w += size_[i * 64 + b];
            if (w >= 3) return 1;
            x &= x - 1;
        }
    }
    return 0;
}

static int held(const u64 *rp) {
    int j = -1;
    for (int i = 0; i < W_; i++) if (rp[i]) { j = i * 64 + __builtin_ctzll(rp[i]); break; }
    if (j < 0) return 0;
    for (int t = koff_[j]; t < koff_[j + 1]; t++) {
        const u64 *bm = bmask_ + (long)keys_[t] * W_;
        int inside = 1;
        for (int i = 0; i < W_; i++) if (rp[i] & ~bm[i]) { inside = 0; break; }
        if (inside) return 1;
    }
    return 0;
}

static void bk(int depth, int rlen) {
    u64 *R = stack_ + (long)depth * 3 * W_, *P = R + W_, *X = P + W_;
    u64 *rp = stack_ + (long)(m_ + 2) * 3 * W_;  /* scratch */
    int anyp = 0, anyx = 0, anyrp = 0;
    for (int i = 0; i < W_; i++) {
        rp[i] = R[i] | P[i];
        if (P[i]) anyp = 1;
        if (X[i]) anyx = 1;
        if (rp[i]) anyrp = 1;
    }
    if (!anyrp || !weight3(rp) || held(rp)) return;
    if (!anyp) {
        if (!anyx) {
            if (limit_ >= 0 && ++found_ > limit_) { exceeded_ = 1; return; }
            if (used_ + rlen + 1 > cap_) { overflow_ = 1; return; }
            out_[used_++] = rlen;
            for (int k = 0; k < rlen; k++) out_[used_++] = rlist_[k];
        }
        return;
    }
    int best = -1, pivot = -1;
    for (int i = 0; i < W_; i++) {
        u64 x = P[i] | X[i];
        while (x) {
            int u = i * 64 + __builtin_ctzll(x);
            x &= x - 1;
            const u64 *a = adj_ + (long)u * W_;
            int c = 0;
            for (int k = 0; k < W_; k++) c += __builtin_popcountll(P[k] & a[k]);
            if (c > best) { best = c; pivot = u; }
        }
    }
    const u64 *ap = adj_ + (long)pivot * W_;
    u64 *R2 = stack_ + (long)(depth + 1) * 3 * W_, *P2 = R2 + W_, *X2 = P2 + W_;
    for (int i = 0; i < W_; i++) {
        u64 cand = P[i] & ~ap[i];
        while (cand) {
            int v = i * 64 + __builtin_ctzll(cand);
            cand &= cand - 1;
            u64 bit = 1ULL << (v & 63);
            const u64 *av = adj_ + (long)v * W_;
            for (int k = 0; k < W_; k++) {
                R2[k] = R[k];
                P2[k] = P[k] & av[k];
                X2[k] = X[k] & av[k];
            }
            R2[v >> 6] |= bit;
            rlist_[rlen] = v;
            bk(depth + 1, rlen + 1);
            if (overflow_ || exceeded_) return;
            P[v >> 6] &= ~bit;
            X[v >> 6] |= bit;
        }
    }
}

long maximal_groups(int m, int W, const u64 *adj, const u64 *bmask, const int *keys, const int *koff,
                    const int *size, int *out, long cap, long limit) {
    m_ = m; W_ = W; adj_ = adj; bmask_ = bmask; keys_ = keys; koff_ = koff; size_ = size;
    out_ = out; cap_ = cap; used_ = 0; overflow_ = 0; limit_ = limit; found_ = 0; exceeded_ = 0;
    stack_ = calloc((size_t)(m + 3) * 3 * W, sizeof(u64));
    rlist_ = calloc((size_t)m + 1, sizeof(int));
    if (!stack_ || !rlist_) { free(stack_); free(rlist_); return -2; }
    u64 *P = stack_ + W;
    for (int v = 0; v < m; v++) P[v >> 6] |= 1ULL << (v & 63);
    bk(0, 0);
    free(stack_);
    free(rlist_);
    return exceeded_ ? -3 : (overflow_ ? -1 : used_);
}
