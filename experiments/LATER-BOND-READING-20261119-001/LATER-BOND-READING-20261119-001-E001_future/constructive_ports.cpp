// Exact three-port split-hub family. Every virtual link ends at middle (0,1).
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <vector>

using Edge = std::pair<int,int>;
using Mask = uint64_t;
constexpr int absent = 10000;

struct Model {
    int n, m, nv;
    std::vector<Edge> pairs, edges;
    std::vector<unsigned> adj;
    std::vector<Mask> stars;
    std::vector<std::array<int,3>> queries;
    std::vector<int> index;
    std::vector<std::array<int,8>> values;
    std::vector<std::vector<int>> permutations;
    std::vector<std::vector<int>> index_permutations;

    Model(int count, int dark): n(count) {
        for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) pairs.emplace_back(i,j);
        int k=pairs.size();
        m=3*k;
        nv=n+k+2;
        adj.resize(nv);
        stars.resize(nv);
        for (int d=0;d<k;d++) {
            auto [i,j]=pairs[d];
            int h=n+k+((dark>>d)&1), mid=n+d;
            for (int u: {i,j,h}) {
                int x=edges.size();
                edges.emplace_back(u,mid);
                adj[u] |= 1u<<mid;
                adj[mid] |= 1u<<u;
                stars[u] |= Mask(1)<<x;
                stars[mid] |= Mask(1)<<x;
            }
        }
        index.assign(m*m*m,-1);
        for (int a=0;a<m;a++) for (int b=a+1;b<m;b++) {
            add_query(a,b,b);
            for (int c=b+1;c<m;c++) add_query(a,b,c);
        }
        values.resize(queries.size());
        for (auto &v:values) v.fill(absent);
        std::vector<int> perm(n);
        std::iota(perm.begin(),perm.end(),0);
        do {
            int moved_color=0;
            std::vector<int> ep(m);
            for (int d=0;d<k;d++) {
                auto [i,j]=pairs[d];
                int p=perm[i],q=perm[j];
                int dest=std::lower_bound(pairs.begin(),pairs.end(),Edge(std::min(p,q),std::max(p,q)))-pairs.begin();
                if ((dark>>d)&1) moved_color |= 1<<dest;
                ep[3*d]=3*dest+(p>q);
                ep[3*d+1]=3*dest+(p<q);
                ep[3*d+2]=3*dest+2;
            }
            if (moved_color==dark || (moved_color^dark)==(1<<k)-1) continue;
            std::vector<int> qp;
            for (auto [a,b,c]:queries) {
                int p=ep[a],q=ep[b],r=ep[c];
                if (b==c) {
                    if (p>q) std::swap(p,q);
                    r=q;
                } else {
                    if (p>q) std::swap(p,q);
                    if (q>r) std::swap(q,r);
                    if (p>q) std::swap(p,q);
                }
                qp.push_back(index[(p*m+q)*m+r]);
            }
            permutations.push_back(std::move(qp));
            index_permutations.push_back(perm);
        } while (std::next_permutation(perm.begin()+2,perm.end()));
    }

    void add_query(int a,int b,int c) {
        index[(a*m+b)*m+c]=queries.size();
        queries.push_back({a,b,c});
    }

    bool connected(unsigned side) const {
        unsigned seen=side&-side, todo=seen;
        while (todo) {
            int j=std::countr_zero(todo);
            todo &= todo-1;
            unsigned add=adj[j]&side&~seen;
            seen |= add;
            todo |= add;
        }
        return seen==side;
    }

    void make_tables() {
        unsigned full=(1u<<nv)-1,side=0;
        Mask cut=0;
        std::vector<int> names(m);
        for (unsigned step=1;step<(1u<<(nv-1));step++) {
            unsigned change=step&-step;
            side^=change;
            cut^=stars[std::countr_zero(change)];
            if (!connected(side) || !connected(full^side)) continue;
            int count=0,sig=cut&7;
            for (Mask q=cut;q;q&=q-1) names[count++]=std::countr_zero(q);
            for (int i=0;i<count;i++) for (int j=i+1;j<count;j++) {
                int base=(names[i]*m+names[j])*m;
                int &p=values[index[base+names[j]]][sig];
                p=std::min(count,p);
                for (int k=j+1;k<count;k++) {
                    int &t=values[index[base+names[k]]][sig];
                    t=std::min(count,t);
                }
            }
        }
    }

    std::vector<int> price(std::array<int,3> weights) const {
        std::array<int,8> extra{};
        for (int s=1;s<8;s++) for (int k=0;k<3;k++)
            if (s&(1<<k)) extra[s]+=weights[k]-1;
        std::vector<int> out;
        for (const auto &row:values) {
            int v=absent;
            for (int s=0;s<8;s++) v=std::min(v,row[s]+extra[s]);
            out.push_back(v);
        }
        return out;
    }
};

bool canon(int n,int mask) {
    std::vector<Edge> pairs;
    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) pairs.emplace_back(i,j);
    int k=pairs.size();
    if (std::popcount(unsigned(mask))<3 || k-std::popcount(unsigned(mask))<3) return false;
    std::vector<int> perm(n);
    std::iota(perm.begin(),perm.end(),0);
    do {
        int img=0;
        for (int d=0;d<k;d++) if (mask&(1<<d)) {
            auto [i,j]=pairs[d];
            int a=perm[i],b=perm[j];
            auto pos=std::lower_bound(pairs.begin(),pairs.end(),Edge(std::min(a,b),std::max(a,b)));
            img |= 1<<(pos-pairs.begin());
        }
        if (std::min(img, ((1<<k)-1)^img)<mask) return false;
    } while (std::next_permutation(perm.begin()+2,perm.end()));
    return true;
}

int main() {
    std::cout << "[\n";
    for (int n: {4,5}) {
        int k=n*(n-1)/2;
        long long cases=0,maps=0,matched=0,breaks=0,weights_tested=0;
        for (int mask=0;mask<(1<<k);mask++) if (canon(n,mask)) {
            Model g(n,mask);
            cases++;
            if (g.permutations.empty()) continue;
            g.make_tables();
            for (int a=1;a<=5;a++) for (int b=1;b<=5;b++) for (int c=1;c<=5;c++) {
                std::array<int,3> weight={a,b,c},next=weight;
                if (std::find(weight.begin(),weight.end(),3)==weight.end()) continue;
                std::replace(next.begin(),next.end(),3,1);
                weights_tested++;
                auto cur=g.price(weight);
                for (int j=0;j<int(g.permutations.size());j++) {
                    maps++;
                    const auto &perm=g.permutations[j];
                    bool ok=true;
                    for (int i=0;i<int(cur.size());i++) if (cur[i]!=cur[perm[i]]) {ok=false;break;}
                    if (!ok) continue;
                    matched++;
                    auto succ=g.price(next);
                    for (int i=0;i<int(succ.size());i++) if (succ[i]!=succ[perm[i]]) {
                        auto [x,y,z]=g.queries[i];
                        std::cerr<<"HIT "<<n<<" "<<mask<<" "<<a<<" "<<b<<" "<<c<<" "<<j;
                        for (auto u:g.index_permutations[j]) std::cerr<<" "<<u;
                        std::cerr<<" marks "<<x<<" "<<y<<" "<<z<<" "<<succ[i]<<" "<<succ[perm[i]]<<"\n";
                        breaks++;
                        break;
                    }
                }
            }
        }
        std::cout << "  {\n"
                  << "    \"indices\": " << n << ",\n"
                  << "    \"canonical_colorings\": " << cases << ",\n"
                  << "    \"priced_colorings_with_color_changing_candidate\": " << weights_tested << ",\n"
                  << "    \"color_changing_maps_tested\": " << maps << ",\n"
                  << "    \"preserving_current_pairs_and_triples\": " << matched << ",\n"
                  << "    \"later_failures_among_preserving_maps\": " << breaks << "\n"
                  << "  }" << (n == 4 ? "," : "") << "\n";
    }
    std::cout << "]\n";
}
