/* Minimum parity decision tree (tree-like Res(xor)) size and depth for small CNFs, exhaustively.
   States are affine subspaces given as point sets (bitmasks over 2^N points, N <= 8). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef struct { uint64_t w[4]; } M;
static int N, P, NC; static M FAL[512], LIN[256];
static int sub(M a, M b){ for(int i=0;i<4;i++) if(a.w[i]&~b.w[i]) return 0; return 1; }
static M and_(M a, M b){ M r; for(int i=0;i<4;i++) r.w[i]=a.w[i]&b.w[i]; return r; }
static M andn(M a, M b){ M r; for(int i=0;i<4;i++) r.w[i]=a.w[i]&~b.w[i]; return r; }
static int empty(M a){ return !(a.w[0]|a.w[1]|a.w[2]|a.w[3]); }
static int eq(M a, M b){ return !memcmp(&a,&b,sizeof a); }
#define HS (1u<<25)
static M *K; static int *VS, *VD; static unsigned char *U;
static uint64_t hsh(M a){ uint64_t h=a.w[0]*0x9E3779B97F4A7C15ULL ^ a.w[1]*0xC2B2AE3D27D4EB4FULL ^ a.w[2]*0x165667B19E3779F9ULL ^ a.w[3]*0xD6E8FEB86659FD93ULL; return h^(h>>29); }
static long nstates=0;
static void solve(M a, int *sz, int *dp){
  for(int c=0;c<NC;c++) if(sub(a,FAL[c])){ *sz=1; *dp=0; return; }
  uint64_t h=hsh(a)&(HS-1);
  while(U[h]){ if(eq(K[h],a)){ *sz=VS[h]; *dp=VD[h]; return; } h=(h+1)&(HS-1); }
  int bs=1<<30, bd=1<<30;
  for(int l=1;l<P;l++){
    M x=and_(a,LIN[l]); if(empty(x)) continue; M y=andn(a,LIN[l]); if(empty(y)) continue;
    int s1,d1,s2,d2; solve(x,&s1,&d1); solve(y,&s2,&d2);
    if(s1+s2<bs) bs=s1+s2; int d=1+(d1>d2?d1:d2); if(d<bd) bd=d;
  }
  h=hsh(a)&(HS-1); while(U[h]) h=(h+1)&(HS-1);
  U[h]=1; K[h]=a; VS[h]=bs; VD[h]=bd; nstates++;
  *sz=bs; *dp=bd;
}
static void setb(M *m, int p){ m->w[p>>6]|=1ULL<<(p&63); }
/* clause given as list of (var, value making the literal FALSE); falsified iff all vars take those values */
static void addclause(int k, int *var, int *fv){ M m; memset(&m,0,sizeof m);
  for(int p=0;p<P;p++){ int ok=1; for(int i=0;i<k;i++) if(((p>>var[i])&1)!=fv[i]) {ok=0;break;} if(ok) setb(&m,p);} FAL[NC++]=m; }
int main(int argc, char **argv){
  int kind=atoi(argv[1]); /* 0: WLP_2 (4 pigeons), 1: LP_3 (3 pigeons), 2: BPHP 3->2, 3: BPHP 4->2 */
  int npig = kind==0?4: kind==1?3: kind==2?3:4;
  if(kind<=1){ N=npig+4; } else N=npig;
  P=1<<N; NC=0;
  for(int l=0;l<P;l++){ memset(&LIN[l],0,sizeof(M)); for(int p=0;p<P;p++) if(__builtin_parity(l&p)) setb(&LIN[l],p); }
  if(kind<=1){ /* f_x = var x (1 bit), g_{h,j} = var npig + 2h + j */
    for(int x=0;x<npig;x++) for(int h=0;h<2;h++) for(int j=0;j<2;j++){
      int var[2]={x, npig+2*h+j}; int fv[2]={h, 1-((x>>j)&1)}; addclause(2,var,fv); }
  } else {
    for(int x=0;x<npig;x++) for(int y=x+1;y<npig;y++) for(int h=0;h<2;h++){ int var[2]={x,y}; int fv[2]={h,h}; addclause(2,var,fv);} }
  K=calloc(HS,sizeof(M)); VS=calloc(HS,sizeof(int)); VD=calloc(HS,sizeof(int)); U=calloc(HS,1);
  M all; memset(&all,0,sizeof all); for(int p=0;p<P;p++) setb(&all,p);
  int s,d; solve(all,&s,&d);
  printf("kind=%d vars=%d clauses=%d min_size(leaves)=%d min_depth=%d states=%ld\n",kind,N,NC,s,d,nstates);
  return 0;
}
