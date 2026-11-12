/* Referee's independent exhaustive search for the least bond containing i and j with members in [lo, hi].
   Allowed states of the whole line are read through exact boundary sets: fwd = window states reachable from the left
   with nothing fixed, good[m] = window states after position m from which the rest of the line can be completed.
   All 2^|S| patterns are used (no complement trick, no antichain reduction, no pooling). A set is extended only while it
   is free (a constrained set cannot be a proper part of a bond). A constrained set containing i and j is a bond when
   every one-member deletion is free (each deletion checked from scratch).
   Input: N, then N*8*2 ints (next state or -1), then Q queries "lo hi i j K budget". Output per query:
   best_size (0 = none up to K) nodes budget_hit members... */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int N; static int (*T)[8][2];
static int lo, hi, I, Jv, K; static long long budget, nodes; static int hit;
static uint8_t fwd, *good; static uint8_t *MS; /* MS[(p-lo)*2+x][R] */
static uint8_t *JT; static int W; /* JT[((a-lo)*(W+1)+(b-lo+1))*256+R]: free steps over a..b (b=a-1: identity) */
static int best; static int bestS[64]; static int cur[64];
static uint8_t freestep(uint8_t R, int m){ uint8_t o=0; for(int s=0;s<8;s++) if(R>>s&1) for(int x=0;x<2;x++){int t=T[m][s][x]; if(t>=0) o|=1<<t;} return o;}
static uint8_t memstep(uint8_t R, int m, int x){ uint8_t o=0; for(int s=0;s<8;s++) if(R>>s&1){int t=T[m][s][x]; if(t>=0) o|=1<<t;} return o;}
static inline uint8_t jump(int a, int b, uint8_t R){ /* free steps a..b inclusive, lo<=a<=b+1<=hi+1 */
  return JT[((size_t)(a-lo)*(W+1)+(size_t)(b-lo+1))*256+R]; }
static int is_free(int *mem, int k){
  /* every pattern on mem (sorted) extends */
  int np=1<<k; uint8_t *P=malloc(np); int cnt=1; P[0]=fwd; int prev=lo-1;
  for(int t=0;t<k;t++){ int m=mem[t]; for(int a=cnt-1;a>=0;a--){ uint8_t R=jump(prev+1,m-1,P[a]); P[2*a]=MS[((m-lo)*2+0)*256+R]; P[2*a+1]=MS[((m-lo)*2+1)*256+R]; } cnt*=2; prev=m; }
  uint8_t g=good[prev-(lo-1)]; int ok=1; for(int a=0;a<cnt;a++) if(!(P[a]&g)){ok=0;break;}
  free(P); return ok; }
static void dfs(int d, int last, uint8_t *P, int hasI, int hasJ){
  /* P: 2^d sets after position last; current set free */
  if(d>=K) return;
  if(++nodes>budget){hit=1;return;}
  int maxp=hi; if(!hasI) maxp=I; else if(!hasJ) maxp=Jv;
  int np=1<<(d+1); uint8_t *Q=malloc(np);
  for(int p=last+1;p<=maxp;p++){
    if(hit) break;
    for(int a=0;a<(1<<d);a++){ uint8_t R=jump(last+1,p-1,P[a]); Q[2*a]=MS[((p-lo)*2+0)*256+R]; Q[2*a+1]=MS[((p-lo)*2+1)*256+R]; }
    cur[d]=p; int nI=hasI||p==I, nJ=hasJ||p==Jv;
    uint8_t g=good[p-(lo-1)]; int cons=0; for(int a=0;a<np;a++) if(!(Q[a]&g)){cons=1;break;}
    if(cons){
      if(nI&&nJ && d+1<best){
        int ok=1; int tmp[64];
        for(int y=0;y<=d && ok;y++){ int k=0; for(int t=0;t<=d;t++) if(t!=y) tmp[k++]=cur[t]; if(!is_free(tmp,k)) ok=0; }
        if(ok){ best=d+1; memcpy(bestS,cur,sizeof(int)*(d+1)); if(best<=K) K=best; }
      }
      continue; /* constrained: never extend */
    }
    if(nI&&nJ) { /* free set containing both: extend further */ }
    dfs(d+1,p,Q,nI,nJ);
    /* Q may have been reused below: recompute not needed since dfs allocs its own */
  }
  free(Q);
}
int main(){
  if(scanf("%d",&N)!=1) return 1; T=malloc(sizeof(int)*N*16);
  for(int m=0;m<N;m++) for(int s=0;s<8;s++) for(int x=0;x<2;x++) scanf("%d",&T[m][s][x]);
  int Q; scanf("%d",&Q);
  for(int q=0;q<Q;q++){
    int Kmax; scanf("%d %d %d %d %d %lld",&lo,&hi,&I,&Jv,&Kmax,&budget);
    W=hi-lo+1;
    fwd=255; for(int m=0;m<lo;m++) fwd=freestep(fwd,m);
    good=malloc(N+1); /* good[m-(lo-1)] for m in lo-1..N-1 */
    good[(N-1)-(lo-1)]=255;
    for(int m=N-1;m>=lo;m--){ uint8_t gm=good[m-(lo-1)], o=0; for(int s=0;s<8;s++) for(int x=0;x<2;x++){int t=T[m][s][x]; if(t>=0 && (gm>>t&1)) {o|=1<<s;}} good[m-1-(lo-1)]=o; }
    MS=malloc((size_t)W*2*256); for(int p=lo;p<=hi;p++) for(int x=0;x<2;x++) for(int R=0;R<256;R++) MS[((p-lo)*2+x)*256+R]=memstep(R,p,x);
    JT=malloc((size_t)W*(W+1)*256);
    for(int a=lo;a<=hi;a++){ for(int R=0;R<256;R++){ uint8_t r=R; JT[((size_t)(a-lo)*(W+1)+(size_t)(a-1-lo+1))*256+R]=r; for(int b=a;b<=hi;b++){ r=freestep(r,b); if(b-lo+1<=W) JT[((size_t)(a-lo)*(W+1)+(size_t)(b-lo+1))*256+R]=r; } } }
    best=1000; K=Kmax; nodes=0; hit=0;
    uint8_t P0[1]={fwd};
    dfs(0,lo-1,P0,0,0);
    printf("%d %lld %d", best==1000?0:best, nodes, hit);
    if(best<1000) for(int t=0;t<best;t++) printf(" %d",bestS[t]);
    printf("\n"); fflush(stdout);
    free(good); free(MS); free(JT);
  }
  return 0;
}
