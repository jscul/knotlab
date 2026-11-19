// Certify full equation transport on small widths for every choice of multiplicities.
// Input is one biconnected simple support per isomorphism class (see small_width.py).
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>
using Mask=uint32_t;
struct Check {
    int n,e,limit;
    std::vector<std::pair<int,int>> links;
    std::vector<int> multiplicity,degree;
    std::vector<Mask> adj,star,bonds;
    std::vector<long long> &stats;
    bool connected(Mask side) const {
        if (!side) return false;
        Mask seen=0,todo=side&-side;
        while(todo){auto b=todo&-todo;todo^=b;seen|=b;todo|=adj[std::countr_zero(b)] & side & ~seen;}
        return seen==side;
    }
    struct Span {
        std::array<Mask,32> rows{};unsigned rank{};
        void add(Mask v){while(v){auto c=std::bit_width(v)-1;if(rows[c])v^=rows[c];else{rows[c]=v;++rank;return;}}}
    };
    void score() {
        Mask possible=0;
        for(int v=0;v<n;v++){
            if(degree[v]<2) continue;
            bool ok=true;
            for(int u=0;u<n;u++) if(u!=v&&degree[u]<3) ok=false;
            // Every live junction was born in the last complete round. Two live
            // junctions never meet each other at a positive open stage.
            for(int u=0;u<n;u++) if((adj[v]>>u&1) && (adj[v]&adj[u]))ok=false;
            if(ok)possible|=1U<<v;
        }
        if(!possible)return;
        auto nroots=std::popcount(possible);stats[0]++;stats[1]+=nroots;
        Span span;
        std::vector<int> cost;cost.reserve(bonds.size());
        std::array<int,32> m; m.fill(limit+1);
        for(auto support:bonds){
            int k=0; for(auto b=support;b;b&=b-1)k+=multiplicity[std::countr_zero(b)];
            cost.push_back(k);
            for(auto b=support;b;b&=b-1){auto q=std::countr_zero(b);m[q]=std::min(m[q],k);}
        }
        for(size_t k=0;k<bonds.size();k++){
            bool keep=cost[k]<=3;
            for(auto b=bonds[k];!keep&&b;b&=b-1)keep=(m[std::countr_zero(b)]==cost[k]);
            if(keep)span.add(bonds[k]);
        }
        if(span.rank==unsigned(n-1)){stats[2]+=nroots;return;}
        // The union of all minimum bonds through a pair is known from the triple
        // table. A unique minimum has exactly its own cardinality in that union.
        std::array<std::array<int,32>,32> prices{},which{};
        for(auto&row:prices)row.fill(limit+1);
        for(size_t k=0;k<bonds.size();k++)for(auto b=bonds[k];b;b&=b-1){
            int i=std::countr_zero(b);
            for(auto z=b&(b-1);z;z&=z-1){
                int j=std::countr_zero(z);
                if(cost[k]<prices[i][j]){prices[i][j]=cost[k];which[i][j]=int(k)+1;}
                else if(cost[k]==prices[i][j])which[i][j]=0;
            }
        }
        for(int i=0;i<e;i++)for(int j=i+1;j<e;j++)if(which[i][j])span.add(bonds[which[i][j]-1]);
        if(span.rank==unsigned(n-1)){stats[3]+=nroots;return;}
        for(auto b=possible;b;b&=b-1){
            int v=std::countr_zero(b);
            auto marked=span; marked.add(star[v]);
            for(auto z=adj[v];z;z&=z-1) marked.add(star[std::countr_zero(z)]);
            if(marked.rank==unsigned(n-1))stats[4]++;
            else {
                stats[5]++;
                std::cout<<"R "<<v<<" "<<n<<" "<<e;
                for(int i=0;i<e;i++)std::cout<<" "<<links[i].first<<" "<<links[i].second<<" "<<multiplicity[i];
                std::cout<<"\n";
            }
        }
    }
    void weights(int i,int budget) {
        if(i==e){score();return;}
        auto [u,v]=links[i];
        for(int extra=0;extra<=budget;extra++){
            multiplicity[i]=1+extra;degree[u]+=extra;degree[v]+=extra;
            weights(i+1,budget-extra); degree[u]-=extra;degree[v]-=extra;
        }
    }
    void run(){
        multiplicity.assign(e,1);degree.assign(n,0);adj.assign(n,0);star.assign(n,0);
        for(int i=0;i<e;i++){
            auto[u,v]=links[i];adj[u]|=1U<<v;adj[v]|=1U<<u;
            star[u]|=1U<<i;star[v]|=1U<<i;degree[u]++;degree[v]++;
        }
        Mask full=(1U<<n)-1;
        for(Mask s=1;s<(1U<<(n-1));s++){
            if(!connected(s)||!connected(full^s))continue;
            Mask crossing=0;
            for(auto b=s;b;b&=b-1)crossing^=star[std::countr_zero(b)];
            bonds.push_back(crossing);
        }
        weights(0,limit-e);
    }
};
int main(int argc,char**argv){
    if(argc!=2)return 2;
    int n,e;std::vector<long long> stats(6);
    while(std::cin>>n>>e){
        Check c{n,e,std::stoi(argv[1]),{},{},{},{},{},{},stats};
        for(int i=0;i<e;i++){int u,v;std::cin>>u>>v;c.links.emplace_back(u,v);}
        c.run();
    }
    std::cout<<"C";for(auto x:stats)std::cout<<" "<<x;std::cout<<"\n";
}
