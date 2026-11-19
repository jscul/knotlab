#include <algorithm>
#include <array>
#include <bit>
#include <climits>
#include <iostream>
#include <vector>

struct Pattern {
    int order;
    int used;
    std::vector<int> marked;
};

bool connected(int anchors, bool red_hub, bool blue_hub, int red, int blue) {
    int total = anchors + red_hub + blue_hub + red + blue;
    if (total < 2) return total == 1;
    if (anchors) return red + blue > 0 && (!red_hub || red) && (!blue_hub || blue);
    if ((red || red_hub) && (blue || blue_hub)) return false;
    return red_hub || blue_hub;
}

std::vector<int> corners(int lo, int hi, int size) {
    std::vector<int> limits;
    for (int x : {lo,hi,1,size-1}) {
        if (x >= lo && x <= hi && std::find(limits.begin(),limits.end(),x)==limits.end())
            limits.push_back(x);
    }
    return limits;
}

int minimum(const Pattern& p, int colours, int weak, int per, int weight, int anchor_weight) {
    int best = INT_MAX;
    for (int b=0;b<2;b++) for (int sides=0;sides<(1<<p.used);sides++) {
        int yes[2]={0,0},no[2]={0,0};
        bool valid = true;
        for (int i=0;i<(int)p.marked.size();i++) {
            int blue=(colours>>i)&1;
            int bits=p.marked[i];
            int on=bits & ((sides<<1) | (blue*b));
            if (on && on!=bits) {valid=false;break;}
            if (on) no[blue]++; else yes[blue]++;
        }
        if (!valid) continue;
        const auto reds=corners(yes[0],per-no[0],per);
        const auto blues=corners(yes[1],per-no[1],per);
        int low=std::popcount((unsigned)sides), high=low+weak-p.used;
        for (int a:corners(low,high,weak)) for (int x:reds) for (int y:blues) {
            if (!connected(a,false,b,x,y) || !connected(weak-a,true,!b,per-x,per-y)) continue;
            int cost=anchor_weight*(a*(2*per-x-y)+(weak-a)*(x+y))+weight*(x+(b?per-y:y));
            best=std::min(best,cost);
        }
    }
    return best;
}

int main() {
    int w,s,l,h;
    int number;
    if (!(std::cin>>number)) return 1;
    std::vector<Pattern> patterns;
    for (int i=0;i<number;i++) {
        int k,u,m; std::cin>>k>>u>>m;
        Pattern p{k,u,{}};
        while (m--) {int bits;std::cin>>bits;p.marked.push_back(bits);}
        patterns.push_back(p);
    }
    while (std::cin>>w>>s>>l>>h) {
        int failed=0,comparison=0;
        for (int j=0;j<number;j++) {
            const Pattern& p=patterns[j];
            if (p.used>w || (int)p.marked.size()>2*s) continue;
            int common=-1, m=p.marked.size();
            // Complementing every color is the true interchange of the two hubs.
            for (int colours=0;colours<(1<<(m-1));colours++) {
                int nblue=std::popcount((unsigned)colours);
                if (nblue>s || m-nblue>s) continue;
                int val=minimum(p,colours,w,s,l,h);
                comparison++;
                if (common==-1) common=val;
                else if (common!=val) {failed=p.order;break;}
            }
            if (failed) break;
        }
        std::cout<<w<<" "<<s<<" "<<l<<" "<<h<<" "<<failed<<" "<<comparison<<"\n";
    }
}
