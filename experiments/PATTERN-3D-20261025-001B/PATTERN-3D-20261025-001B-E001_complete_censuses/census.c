/* Census for PATTERN-3D-20261025-001B-E001: pure counting laws on ordered triangulations under the ordered 2-3 and 1-4 identities.
   A triangle a<b<c reads (x_ab, x_bc, x_ac); a tetrahedron is allowed when its four faces are in the rule R.
   1-4: every allowed tetrahedron extends in exactly mu ways at each of the five positions of a new vertex.
   2-3: for every labelling of the nine boundary edges with the six boundary triangles in R, the number of labels on the new edge
        putting the three interior triangles in R equals lam * [shared triangle in R].
   A law survives when both hold with lam, mu >= 1.
   usage: census rel n start end   -- relations R on n <= 3 labels, R as a bitmask over index (x_ab*n + x_bc)*n + x_ac
          census tab n start end   -- total tables on n <= 4 labels, table index in base n, row-major op[a][b]
   output: one line "SURV <index> <lam> <mu>" per surviving law, then "STATS empty=.. mu0=.. fail14=.. fail23=.. surv=..". */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int n, n3, n4, n6, n9;
static int eid[5][5], E5[10][2];
static const int P4[6][2] = {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
static long nempty, nmu0, nf14, nf23, ns;

/* ------------------------------------------------------------------ relations (n <= 3, R fits in 32 bits) */
static uint32_t *tmask, *emask, *bmask, *shmask, *imask;
static inline uint32_t bit(int a, int b, int c) { return 1u << ((a * n + b) * n + c); }
static uint32_t trimask(const int *x, int a, int b, int c) { return bit(x[eid[a][b]], x[eid[b][c]], x[eid[a][c]]); }

static void rel_setup(void) {
  int x[10];
  tmask = malloc(sizeof(uint32_t) * n6);
  for (int i = 0; i < n6; i++) { int t = i;
    for (int e = 0; e < 6; e++) { x[eid[P4[e][0]][P4[e][1]]] = t % n; t /= n; }
    tmask[i] = trimask(x, 0, 1, 2) | trimask(x, 0, 1, 3) | trimask(x, 0, 2, 3) | trimask(x, 1, 2, 3); }
  emask = malloc(sizeof(uint32_t) * 5 * n6 * n4);
  for (int r = 0; r < 5; r++) { int old[4], m = 0; for (int v = 0; v < 5; v++) if (v != r) old[m++] = v;
    int newe[4], q = 0; for (int v = 0; v < 5; v++) if (v != r) newe[q++] = (v < r) ? eid[v][r] : eid[r][v];
    for (int i = 0; i < n6; i++) { int t = i;
      for (int e = 0; e < 6; e++) { x[eid[old[P4[e][0]]][old[P4[e][1]]]] = t % n; t /= n; }
      for (int j = 0; j < n4; j++) { int u = j; for (int e = 0; e < 4; e++) { x[newe[e]] = u % n; u /= n; }
        uint32_t msk = 0;
        for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) for (int c = b + 1; c < 5; c++)
          if (a == r || b == r || c == r) msk |= trimask(x, a, b, c);
        emask[((long)r * n6 + i) * n4 + j] = msk; } } }
  bmask = malloc(sizeof(uint32_t) * 10 * n9); shmask = malloc(sizeof(uint32_t) * 10 * n9);
  imask = malloc(sizeof(uint32_t) * 10 * n9 * n);
  int kk = 0;
  for (int p = 0; p < 5; p++) for (int q = p + 1; q < 5; q++, kk++) {
    int others[3], m = 0; for (int v = 0; v < 5; v++) if (v != p && v != q) others[m++] = v;
    int bedges[9], mm = 0; for (int e = 0; e < 10; e++) if (!(E5[e][0] == p && E5[e][1] == q)) bedges[mm++] = e;
    for (long L = 0; L < n9; L++) { long t = L; for (int i = 0; i < 9; i++) { x[bedges[i]] = t % n; t /= n; }
      uint32_t bm = 0;
      for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) for (int c = b + 1; c < 5; c++) {
        int hp = (a == p || b == p || c == p), hq = (a == q || b == q || c == q);
        if (hp && hq) continue;
        if (a == others[0] && b == others[1] && c == others[2]) continue;
        bm |= trimask(x, a, b, c); }
      bmask[(long)kk * n9 + L] = bm; shmask[(long)kk * n9 + L] = trimask(x, others[0], others[1], others[2]);
      for (int e = 0; e < n; e++) { x[eid[p][q]] = e; uint32_t im = 0;
        for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) for (int c = b + 1; c < 5; c++) {
          int hp = (a == p || b == p || c == p), hq = (a == q || b == q || c == q); if (hp && hq) im |= trimask(x, a, b, c); }
        imask[((long)kk * n9 + L) * n + e] = im; } } }
}

static void rel_run(long start, long end) {
  int *cons = malloc(sizeof(int) * n6);
  for (long Rl = start; Rl < end; Rl++) { uint32_t R = (uint32_t)Rl; int nc = 0;
    for (int i = 0; i < n6; i++) if ((R & tmask[i]) == tmask[i]) cons[nc++] = i;
    if (!nc) { nempty++; continue; }
    int mu = -1, bad = 0;
    for (int ci = 0; ci < nc && !bad; ci++) for (int r = 0; r < 5 && !bad; r++) {
      const uint32_t *em = emask + ((long)r * n6 + cons[ci]) * n4; int cnt = 0;
      for (int j = 0; j < n4; j++) if ((R & em[j]) == em[j]) cnt++;
      if (mu < 0) mu = cnt; else if (cnt != mu) bad = 1; }
    if (bad) { nf14++; continue; }
    if (mu == 0) { nmu0++; continue; }
    int lam = -1; bad = 0;
    for (int kq = 0; kq < 10 && !bad; kq++) for (long L = 0; L < n9 && !bad; L++) { long id = (long)kq * n9 + L;
      if ((R & bmask[id]) != bmask[id]) continue;
      int sh = (R & shmask[id]) != 0, cnt = 0;
      for (int e = 0; e < n; e++) { uint32_t im = imask[id * n + e]; if ((R & im) == im) cnt++; }
      if (sh) { if (lam < 0) lam = cnt; else if (cnt != lam) bad = 1; } else if (cnt) bad = 1; }
    if (bad || lam < 1) { nf23++; continue; }
    ns++; printf("SURV %ld %d %d\n", Rl, lam, mu); }
  free(cons);
}

/* ------------------------------------------------------------------ total tables (n <= 4) */
static int op[4][4];
static int assoc(int a, int b, int c) { return op[op[a][b]][c] == op[a][op[b][c]]; }
static int tri_ok(const int *x, int a, int b, int c) { return x[eid[a][c]] == op[x[eid[a][b]]][x[eid[b][c]]]; }
static int tab_check23(void) {
  int lam = -1, x[10];
  for (int p = 0; p < 5; p++) for (int q = p + 1; q < 5; q++) {
    int others[3], k = 0; for (int v = 0; v < 5; v++) if (v != p && v != q) others[k++] = v;
    int bt[6][3], nb = 0, it[3][3], ni = 0;
    for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) for (int c = b + 1; c < 5; c++) {
      int hp = (a == p || b == p || c == p), hq = (a == q || b == q || c == q);
      if (hp && hq) { it[ni][0] = a; it[ni][1] = b; it[ni][2] = c; ni++; }
      else if (!(a == others[0] && b == others[1] && c == others[2])) { bt[nb][0] = a; bt[nb][1] = b; bt[nb][2] = c; nb++; } }
    int bedges[9], m = 0; for (int e = 0; e < 10; e++) if (!(E5[e][0] == p && E5[e][1] == q)) bedges[m++] = e;
    for (long L = 0; L < n9; L++) { long t = L; for (int i = 0; i < 9; i++) { x[bedges[i]] = t % n; t /= n; }
      int ok = 1; for (int i = 0; i < 6 && ok; i++) ok = tri_ok(x, bt[i][0], bt[i][1], bt[i][2]);
      if (!ok) continue;
      int sh = tri_ok(x, others[0], others[1], others[2]), cnt = 0;
      for (int e = 0; e < n; e++) { x[eid[p][q]] = e; int g = 1; for (int i = 0; i < 3 && g; i++) g = tri_ok(x, it[i][0], it[i][1], it[i][2]); cnt += g; }
      if (sh) { if (lam < 0) lam = cnt; else if (cnt != lam) return -1; } else if (cnt) return -1; } }
  return lam < 0 ? 0 : lam;
}
static void tab_run(long start, long end) {
  static int N[5][64];
  for (long T = start; T < end; T++) {
    long t = T; for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) { op[a][b] = t % n; t /= n; }
    int any = 0; for (int a = 0; a < n && !any; a++) for (int b = 0; b < n && !any; b++) for (int c = 0; c < n && !any; c++) any = assoc(a, b, c);
    if (!any) { nempty++; continue; }
    memset(N, 0, sizeof(N));
    for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) for (int c = 0; c < n; c++) for (int d = 0; d < n; d++) {
      int ab = op[a][b], bc = op[b][c], cd = op[c][d];
      if (!assoc(a, b, c) || !assoc(b, c, d) || !assoc(ab, c, d) || !assoc(a, b, cd) || !assoc(a, bc, d)) continue;
      N[4][(a * n + b) * n + c]++; N[0][(b * n + c) * n + d]++; N[1][(ab * n + c) * n + d]++;
      N[2][(a * n + bc) * n + d]++; N[3][(a * n + b) * n + cd]++; }
    int mu = -1, bad = 0;
    for (int i = 0; i < n3 && !bad; i++) { int a = i / (n * n), b = (i / n) % n, c = i % n; if (!assoc(a, b, c)) continue;
      for (int r = 0; r < 5; r++) { if (mu < 0) mu = N[r][i]; else if (N[r][i] != mu) { bad = 1; break; } } }
    if (bad) { nf14++; continue; }
    if (mu == 0) { nmu0++; continue; }
    int lam = tab_check23();
    if (lam < 1) { nf23++; continue; }
    ns++; printf("SURV %ld %d %d\n", T, lam, mu); }
}

int main(int argc, char **argv) {
  if (argc != 5) { fprintf(stderr, "usage: census rel|tab n start end\n"); return 2; }
  n = atoi(argv[2]); long start = atol(argv[3]), end = atol(argv[4]);
  n3 = n * n * n; n4 = n3 * n; n6 = n3 * n3; n9 = n6 * n3;
  int k = 0; for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) { E5[k][0] = a; E5[k][1] = b; eid[a][b] = k; k++; }
  if (!strcmp(argv[1], "rel")) { if (n > 3) return 2; rel_setup(); rel_run(start, end); }
  else if (!strcmp(argv[1], "tab")) { if (n > 4) return 2; tab_run(start, end); }
  else return 2;
  printf("STATS empty=%ld mu0=%ld fail14=%ld fail23=%ld surv=%ld\n", nempty, nmu0, nf14, nf23, ns);
  return 0;
}
