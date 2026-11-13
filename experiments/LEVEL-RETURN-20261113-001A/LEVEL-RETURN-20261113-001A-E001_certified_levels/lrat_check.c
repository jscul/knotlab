/* LRAT checker written by the thread for LEVEL-RETURN-20261113-001A (RUP steps only; a RAT step, a bad hint or a missing
   empty clause is a failure). Usage: lrat_check formula.cnf proof.lrat ; prints "VERIFIED" and exits 0, else "FAILED: why", 1.
   Proof in text LRAT: "<id> <lits> 0 <hints> 0" adds a clause; "<id> d <ids> 0" deletes clauses. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef long long ll;
static int *pool; static ll pool_n = 0, pool_cap = 0;
static ll *off; static int *len; static ll ids_cap = 0;
static signed char *val; static int nvars = 0; static int *trail; static int tn = 0;
static void fail(const char *w, ll id) { printf("FAILED: %s (clause %lld)\n", w, id); exit(1); }
static void ensure_id(ll id) {
  if (id < ids_cap) return;
  ll nc = ids_cap ? ids_cap : 1024; while (nc <= id) nc *= 2;
  off = realloc(off, nc * sizeof(ll)); len = realloc(len, nc * sizeof(int));
  for (ll i = ids_cap; i < nc; i++) { off[i] = -1; len[i] = 0; }
  ids_cap = nc;
}
static ll push_clause(int *lits, int n) {
  if (pool_n + n > pool_cap) { pool_cap = (pool_cap + n) * 2 + 1024; pool = realloc(pool, pool_cap * sizeof(int)); }
  memcpy(pool + pool_n, lits, n * sizeof(int)); ll o = pool_n; pool_n += n; return o;
}
static int litval(int l) { int v = val[abs(l)]; return l > 0 ? v : -v; } /* 1 true, -1 false, 0 unassigned */
static void setlit(int l, int truth) { int v = abs(l); val[v] = (l > 0) == (truth > 0) ? 1 : -1; trail[tn++] = v; }
static void undo(void) { while (tn) val[trail[--tn]] = 0; }
static int readint(FILE *f, ll *x) { return fscanf(f, "%lld", x) == 1; }
int main(int argc, char **argv) {
  if (argc != 3) { fprintf(stderr, "usage\n"); return 2; }
  FILE *f = fopen(argv[1], "r"); if (!f) fail("cannot open formula", 0);
  char buf[256]; ll nc = 0, id = 0; int c;
  while ((c = fgetc(f)) == 'c') { if (!fgets(buf, sizeof buf, f)) break; }
  ungetc(c, f);
  if (fscanf(f, " p cnf %d %lld", &nvars, &nc) != 2) fail("bad header", 0);
  val = calloc(nvars + 2, 1); trail = malloc((nvars + 2) * sizeof(int));
  int *tmp = malloc(sizeof(int) * (nvars + 2) * 2 + 64); int tl = 0; ll x;
  while (readint(f, &x)) {
    if (x == 0) { id++; ensure_id(id); off[id] = push_clause(tmp, tl); len[id] = tl; tl = 0; }
    else { if (llabs(x) > nvars) fail("literal out of range", id + 1); tmp[tl++] = (int)x; }
  }
  fclose(f);
  if (id != nc) fail("clause count differs from header", id);
  FILE *p = fopen(argv[2], "r"); if (!p) fail("cannot open proof", 0);
  ll cid; int empty_ok = 0; ll steps = 0;
  while (readint(p, &cid)) {
    int ch; do ch = fgetc(p); while (ch == ' ');
    if (ch == 'd') { while (readint(p, &x) && x != 0) { if (x < ids_cap && off[x] >= 0) off[x] = -2; } continue; }
    ungetc(ch, p);
    tl = 0; while (readint(p, &x) && x != 0) { if (llabs(x) > nvars) fail("literal out of range", cid); tmp[tl++] = (int)x; }
    if (cid < ids_cap && off[cid] != -1) fail("clause id reused", cid);
    int taut = 0;
    for (int i = 0; i < tl; i++) { int lv = litval(tmp[i]); if (lv == 1) taut = 1; else if (lv == 0) setlit(tmp[i], -1); }
    int conflict = taut;
    while (readint(p, &x) && x != 0) {
      if (conflict) continue;
      if (x < 0) fail("RAT hint not supported", cid);
      if (x >= ids_cap || off[x] < 0) fail("hint to a missing clause", cid);
      int unassigned = 0, ul = 0, sat = 0;
      for (int i = 0; i < len[x]; i++) { int l = pool[off[x] + i], lv = litval(l); if (lv == 1) { sat = 1; break; } if (lv == 0) { unassigned++; ul = l; } }
      if (sat) fail("hint clause satisfied", cid);
      if (unassigned == 0) conflict = 1; else if (unassigned == 1) setlit(ul, 1); else fail("hint clause not unit", cid);
    }
    undo();
    if (!conflict) fail("no conflict after hints", cid);
    ensure_id(cid); off[cid] = push_clause(tmp, tl); len[cid] = tl; steps++;
    if (tl == 0) { empty_ok = 1; break; }
  }
  fclose(p);
  if (!empty_ok) fail("no empty clause derived", 0);
  printf("VERIFIED %lld steps\n", steps); return 0;
}
