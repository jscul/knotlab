/* LRAT checker written by the thread for LEVEL-RETURN-20261113-001A (RUP steps only; a RAT step, a bad hint or a missing
   empty clause is a failure). Usage: lrat_check formula.cnf proof.lrat ; prints "VERIFIED" and exits 0, else "FAILED: why", 1.
   Proof in text LRAT: "<id> <lits> 0 <hints> 0" adds a clause; "<id> d <ids> 0" deletes clauses. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef long long ll;
static int **cl; static int *len; static ll ids_cap = 0; static signed char *state; /* 0 never, 1 live, 2 deleted */
static signed char *val; static int nvars = 0; static int *trail; static int tn = 0;
static void fail(const char *w, ll id) { printf("FAILED: %s (clause %lld)\n", w, id); exit(1); }
static void ensure_id(ll id) {
  if (id < ids_cap) return;
  ll nc = ids_cap ? ids_cap : 1024; while (nc <= id) nc *= 2;
  cl = realloc(cl, nc * sizeof(int *)); len = realloc(len, nc * sizeof(int)); state = realloc(state, nc);
  for (ll i = ids_cap; i < nc; i++) { cl[i] = NULL; len[i] = 0; state[i] = 0; }
  ids_cap = nc;
}
static void store(ll id, int *lits, int n) {
  ensure_id(id); cl[id] = malloc((n ? n : 1) * sizeof(int)); memcpy(cl[id], lits, n * sizeof(int)); len[id] = n; state[id] = 1;
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
    if (x == 0) { id++; store(id, tmp, tl); tl = 0; }
    else { if (llabs(x) > nvars) fail("literal out of range", id + 1); tmp[tl++] = (int)x; }
  }
  fclose(f);
  if (id != nc) fail("clause count differs from header", id);
  FILE *p = fopen(argv[2], "r"); if (!p) fail("cannot open proof", 0);
  ll cid; int empty_ok = 0; ll steps = 0;
  while (readint(p, &cid)) {
    int ch; do ch = fgetc(p); while (ch == ' ');
    if (ch == 'd') { while (readint(p, &x) && x != 0) { if (x > 0 && x < ids_cap && state[x] == 1) { free(cl[x]); cl[x] = NULL; state[x] = 2; } } continue; }
    ungetc(ch, p);
    tl = 0; while (readint(p, &x) && x != 0) { if (llabs(x) > nvars) fail("literal out of range", cid); tmp[tl++] = (int)x; }
    if (cid < ids_cap && state[cid] != 0) fail("clause id reused", cid);
    int taut = 0;
    for (int i = 0; i < tl; i++) { int lv = litval(tmp[i]); if (lv == 1) taut = 1; else if (lv == 0) setlit(tmp[i], -1); }
    int conflict = taut;
    while (readint(p, &x) && x != 0) {
      if (conflict) continue;
      if (x < 0) fail("RAT hint not supported", cid);
      if (x >= ids_cap || state[x] != 1) fail("hint to a missing clause", cid);
      int unassigned = 0, ul = 0, sat = 0;
      for (int i = 0; i < len[x]; i++) { int l = cl[x][i], lv = litval(l); if (lv == 1) { sat = 1; break; } if (lv == 0) { unassigned++; ul = l; } }
      if (sat) fail("hint clause satisfied", cid);
      if (unassigned == 0) conflict = 1; else if (unassigned == 1) setlit(ul, 1); else fail("hint clause not unit", cid);
    }
    undo();
    if (!conflict) fail("no conflict after hints", cid);
    store(cid, tmp, tl); steps++;
    if (tl == 0) { empty_ok = 1; break; }
  }
  fclose(p);
  if (!empty_ok) fail("no empty clause derived", 0);
  printf("VERIFIED %lld steps\n", steps); return 0;
}
