// One scalar affine premise and conclusion, five path products.
// Input: one unordered forbidden-flat key and its orbit size per line.
// All searches use C++20 and integer arithmetic; leave assertions enabled.
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <unordered_map>
#include <vector>

using M = uint64_t;
using V = std::vector<int>;

int pc(int x) { return std::popcount(unsigned(x)) & 1; }

int delta(int x, int blocks) {
    int output = 0;
    for (int i=0; i<blocks; ++i) {
        int t = (x >> (3*i)) & 7;
        int error = ((t >> 2) ^ ((t & 1) & (t >> 1))) & 1;
        output |= error << i;
    }
    return output;
}

// Original data in slots x0,...,x5,s,u,v. These source predicates are also
// used on all lifted chart points, independently of the defect shortcut.
int original_word(int z) {
    int x1=z&1, x0=(z>>1)&1, u=(z>>2)&1, x2=(z>>3)&1;
    int x3=((z>>4)&1)^x1, v=(z>>5)&1, x4=(z>>6)&1;
    int x5=((z>>7)&1)^x3, s=((z>>8)&1)^u^v;
    return x0 | (x1<<1) | (x2<<2) | (x3<<3) | (x4<<4)
           | (x5<<5) | (s<<6) | (u<<7) | (v<<8);
}

std::pair<bool,bool> original_sources(int word) {
    int products = (word & (word>>1)) & 31;
    int s=(word>>6)&1, u=(word>>7)&1, v=(word>>8)&1;
    return {s==pc(products) && u==(products&1) && v==pc(products&6),
            s!=pc(products)};
}

struct TracePair {
    M r, p;
    bool operator==(const TracePair& y) const { return r==y.r && p==y.p; }
};
struct TraceHash {
    size_t operator()(const TracePair& x) const {
        uint64_t u=x.r+0x9e3779b97f4a7c15ULL+(x.p<<6)+(x.p>>2);
        u=(u^x.p)*0xbf58476d1ce4e5b9ULL;
        return u^(u>>32);
    }
};

struct Six {
    std::array<M,64> rows{};
    std::unordered_map<M,M> cached_hulls;
    std::unordered_map<TracePair,int,TraceHash> prices;

    Six() {
        for(int row=0;row<64;++row) for(int x=0;x<64;++x)
            if(pc(x&row)) rows[row]|=M(1)<<x;
    }
    M hull(M points) {
        if (!points) return 0;
        if (auto it=cached_hulls.find(points); it!=cached_hulls.end()) return it->second;
        int origin=std::countr_zero(points);
        std::array<int,6> basis{};
        for (M rest=points;rest;rest&=rest-1) {
            int v=std::countr_zero(rest)^origin;
            while(v) {
                int i=std::bit_width(unsigned(v))-1;
                if (!basis[i]) { basis[i]=v; break; }
                v^=basis[i];
            }
        }
        std::array<int,64> span{origin};
        int size=1;
        for(int v:basis) if(v) {
            for(int i=0;i<size;++i) span[size+i]=span[i]^v;
            size*=2;
        }
        M result=0;
        for(int i=0;i<size;++i) result|=M(1)<<span[i];
        cached_hulls[points]=result;
        return result;
    }

    // Without learned guards, only the two surviving traces matter. A paid
    // operation with unchanged traces may be removed. Left/right are symmetric.
    int ordinary(M r,M p) {
        if(!r || !p) return 1;
        if(r>p) std::swap(r,p);
        TracePair key{r,p};
        if(auto it=prices.find(key);it!=prices.end()) return it->second;
        M rp=p&hull(r), pr=r&hull(p);
        if(!rp || !pr) return 2;
        int best=100;
        if(rp!=p) best=std::min(best,1+ordinary(r,rp));
        if(pr!=r) best=std::min(best,1+ordinary(pr,p));
        for(int q=1;q<64;++q) {
            M r0=r&rows[q], p0=p&rows[q], r1=r^r0, p1=p^p0;
            if(!(r0|p0) || !(r1|p1)) continue;
            int a=1+bool(r0&&p0), b=1+bool(r1&&p1);
            if(1+a+b>=best) continue;
            a=ordinary(r0,p0);
            if(1+a+b<best) best=std::min(best,1+a+ordinary(r1,p1));
        }
        assert(best<100);
        prices[key]=best;
        return best;
    }
};

// Affine chart on the span of the nonempty union of its two traces.
struct Chart {
    V points;
    std::array<int,512> index;
    Chart(const V& r,const V& p) {
        assert(!r.empty() || !p.empty());
        index.fill(-1);
        int origin=r.empty()?p.front():r.front();
        points={origin};
        index[origin]=0;
        auto insert=[&](int x) {
            if(index[x]>=0) return;
            int d=x^origin, size=points.size();
            for(int i=0;i<size;++i) {
                int y=points[i]^d;
                index[y]=points.size();
                points.push_back(y);
            }
        };
        for(int x:r) insert(x);
        for(int x:p) insert(x);
    }
    M mask(const V& rows) const {
        M out=0;
        for(int x:rows) {
            int i=index[x];
            assert(i>=0 && i<64);
            out|=M(1)<<i;
        }
        return out;
    }
    V restrict_to_span(const V& rows) const {
        V out;
        for(int x:rows) if(index[x]>=0) out.push_back(x);
        return out;
    }
};

int training(const V& r,const V& p) {
    if(r.empty() || p.empty()) return 1;
    Six solver;
    auto small=[&](const V& a,const V& b) {
        if(a.empty() || b.empty()) return 1;
        Chart sub(a,b);
        assert(sub.points.size()<=64);
        return solver.ordinary(sub.mask(a),sub.mask(b));
    };
    Chart ctx(r,p);
    if(ctx.points.size()<=64) return small(r,p);
    assert(ctx.points.size()==128);
    int best=100;
    V after_rich=Chart(r,{}).restrict_to_span(p);
    V after_plain=Chart({},p).restrict_to_span(r);
    if(after_rich.size()<p.size()) best=1+small(r,after_rich);
    if(after_plain.size()<r.size()) best=std::min(best,1+small(after_plain,p));
    for(int q=1;q<128;++q) {
        V rc[2],pcell[2];
        for(int x:r) rc[pc(ctx.index[x]&q)].push_back(x);
        for(int x:p) pcell[pc(ctx.index[x]&q)].push_back(x);
        if((rc[0].empty()&&pcell[0].empty()) || (rc[1].empty()&&pcell[1].empty())) continue;
        int left=small(rc[0],pcell[0]);
        if(left+2<best) best=std::min(best,1+left+small(rc[1],pcell[1]));
    }
    assert(best<100);
    return best;
}

struct Emb { std::array<int,64> img; };

struct Model {
    std::array<std::array<std::vector<Emb>,2>,512> embs;
    V rawr,rawp;
    int embedding_count=0;
    Model() {
        std::set<int> raw;
        for(int z=0;z<512;++z) {
            int word=original_word(z);
            raw.insert(word);
            auto [r,p]=original_sources(word);
            assert(r==(delta(z,3)==0) && p==bool(pc(delta(z,3))));
            if(r) rawr.push_back(z);
            if(p) rawp.push_back(z);
        }
        assert(raw.size()==512 && rawr.size()==64 && rawp.size()==256);
        auto insert=[](int z,int i,int t) {
            int low=(1<<(3*i))-1;
            return (z&low) | ((z&~low)<<3) | (t<<(3*i));
        };
        for(int q=1;q<512;++q) for(int i=0;i<3;++i) {
            int local=(q>>(3*i))&7;
            for(int lo:{0,1,2,7}) for(int hi:{0,1,2,7}) {
                if(pc(local&lo)!=0 || pc(local&hi)!=1) continue;
                for(int a=0;a<2;++a) {
                    Emb e;
                    std::set<int> image;
                    for(int z=0;z<64;++z) {
                        int outside=insert(z,i,0);
                        e.img[z]=insert(z,i,(pc(q&outside)^a)?hi:lo);
                        auto [r,p]=original_sources(original_word(e.img[z]));
                        assert(pc(e.img[z]&q)==a);
                        assert(r==(delta(z,2)==0) && p==bool(pc(delta(z,2))));
                        image.insert(e.img[z]);
                    }
                    assert(image.size()==64);
                    for(int z=0;z<64;++z) {
                        int v=e.img[0];
                        for(int j=0;j<6;++j) if((z>>j)&1) v^=e.img[1<<j]^e.img[0];
                        assert(v==e.img[z]);
                    }
                    embs[q][a].push_back(e);
                    ++embedding_count;
                }
            }
        }
    }
};
// A local affine equation is encoded by its low-six coefficient mask and rhs bit 6.
// All context transitions below keep the actual affine cell, including strict
// source-based shrinkage that changes no surviving set of traces.
struct Cell {
    M mask;
    int after_rich;
    int after_plain;
    std::vector<std::pair<int,int>> splits;
};

M equation_mask(const Six& six, int eq) {
    return (eq & 64) ? six.rows[eq & 63] : ~six.rows[eq & 63];
}

class GivenTwo {
    Six core;
    std::unordered_map<M,int> index;
    std::vector<Cell> cells;
    std::array<std::array<int,128>,7> gens{};
    std::array<int,16384> orbit{};
    std::array<int,16384> price{};
    std::vector<int> values;
    void build_cells(){
        M rich = 0, plain = 0;
        for (int z=0;z<64;++z) {
            int e=delta(z,2);
            if (e==0) rich|=M(1)<<z;
            if (pc(e)) plain|=M(1)<<z;
        }
        std::vector<M> todo{~M(0)};
        std::unordered_map<M,bool> seen{{~M(0), true}};
        for (size_t i=0;i<todo.size();++i) {
            M h=todo[i];
            for (int j=1;j<64;++j) {
                M a=h & core.rows[j], b=h ^ a;
                if (a==0 || b==0) continue;
                if (seen.emplace(a,true).second) todo.push_back(a);
                if (seen.emplace(b,true).second) todo.push_back(b);
            }
        }
        assert(todo.size()==26387);
        todo.push_back(0);
        std::sort(todo.begin(),todo.end(),[](M a,M b){
            int pa=std::popcount(a),pb=std::popcount(b);
            return pa!=pb?pa<pb:a<b;
        });
        for (size_t i=0;i<todo.size();++i) index[todo[i]]=i;
        for (M h:todo) {
            Cell cell{h,index.at(core.hull(h&rich)),index.at(core.hull(h&plain)),{}};
            std::set<std::pair<int,int>> splits;
            for (int q=1;q<64;++q) {
                M a=core.rows[q]&h,b=h^a;
                if (!a || !b) continue;
                int ia=index.at(a),ib=index.at(b);
                splits.emplace(std::min(ia,ib),std::max(ia,ib));
            }
            cell.splits.assign(splits.begin(),splits.end());
            cells.push_back(std::move(cell));
        }
        values.resize(cells.size());
    }
    void build_orbits(){
        for (int ig=0;ig<7;++ig) {
            std::array<int,64> map{};
            for (int z=0;z<64;++z) {
                if (ig==6) {
                    map[z]=((z&7)<<3)|(z>>3);
                    continue;
                }
                int block=ig/3,adj=ig%3;
                std::array<int,4> t{0,1,2,7};
                std::swap(t[adj],t[adj+1]);
                int shift=3*block,x=(z>>shift)&7,y=t[0];
                int cols[3]={t[0]^t[1],t[0]^t[2],t[0]^t[1]^t[2]^t[3]};
                for (int j=0;j<3;++j) if (x & (1<<j)) y^=cols[j];
                map[z]=(z & ~(7<<shift)) | (y<<shift);
                assert((delta(z,2)==0)==(delta(map[z],2)==0));
                assert(pc(delta(z,2))==pc(delta(map[z],2)));
            }
            for (int eq=0;eq<128;++eq) {
                int row=eq&63,c=(eq>>6)^pc(row&map[0]);
                int image=c<<6;
                for(int j=0;j<6;++j)
                    image |= pc(row&(map[0]^map[1<<j]))<<j;
                gens[ig][eq]=image;
            }
        }
        orbit.fill(-1);
        for(int seed=0;seed<16384;++seed) {
            if(orbit[seed]>=0) continue;
            std::vector<int> queue{seed};
            orbit[seed]=seed;
            for(size_t i=0;i<queue.size();++i) {
                int code=queue[i],g=code>>7,l=code&127;
                for(const auto &gen:gens) {
                    int next=(gen[g]<<7)|gen[l];
                    if(orbit[next]<0) {orbit[next]=seed;queue.push_back(next);}
                }
            }
        }
        price.fill(-1);
    }
    int solve(int guard,int conclusion) {
        M g=equation_mask(core,guard), l=equation_mask(core,conclusion);
        values[0]=0;
        for(size_t i=1;i<cells.size();++i) {
            const Cell &h=cells[i];
            int best=100;
            if(h.after_rich!=int(i)) best=std::min(best,1+values[h.after_rich]);
            if(h.after_plain!=int(i)) best=std::min(best,1+values[h.after_plain]);
            if(!(h.mask&~g) && (h.mask&~l))
                best=std::min(best,1+values[index.at(h.mask&l)]);
            if(best>3) for(auto [a,b]:h.splits)
                best=std::min(best,1+values[a]+values[b]);
            assert(best<100);
            values[i]=best;
        }
        return values.back();
    }
public:
    GivenTwo(){build_cells();build_orbits();}
    int cost(int g,int l) {
        int rep=orbit[(g<<7)|l];
        if(price[rep]<0) price[rep]=solve(rep>>7,rep&127);
        return price[rep];
    }
};

int pulled(int eq,const Emb&e) {
    int row=eq&511, c=(eq>>9)^pc(row&e.img[0]), out=c<<6;
    for(int j=0;j<6;++j) out|=pc(row&(e.img[0]^e.img[1<<j]))<<j;
    return out;
}

bool satisfies(int x,int eq) { return pc(x&(eq&511))==(eq>>9); }

int main() {
    Model m;
    GivenTwo given;
    assert(given.cost(0,0)==11);
    assert(given.cost(0,64)==1);
    assert(given.cost(64,64)==11);
    int key,multiplicity,orbits=0,flats=0;
    while(std::cin>>key>>multiplicity) {
        ++orbits;
        flats+=multiplicity;
        int a=key&1023,b=key>>10;
        V r,p;
        for(int x:m.rawr) if(satisfies(x,a)&&satisfies(x,b)) r.push_back(x);
        for(int x:m.rawp) if(satisfies(x,a)&&satisfies(x,b)) p.push_back(x);
        int t=training(r,p);
        for(int g:{a,b,a^b}) {
            int h=g==a?b:a, l=h^512;
            int cheapest=100;
            for(int q=1;q<512;++q) {
                int total=1;
                for(int ans=0;ans<2;++ans) {
                    int expensive=0;
                    assert(!m.embs[q][ans].empty());
                    for(const auto& e:m.embs[q][ans])
                        expensive=std::max(expensive,given.cost(pulled(g,e),pulled(l,e)));
                    total+=expensive;
                }
                cheapest=std::min(cheapest,total);
            }
            std::cout<<key<<' '<<multiplicity<<' '<<g<<' '<<l<<' '<<t<<' '<<cheapest<<'\n';
        }
    }
    assert(orbits==126 && flats==173740);
    std::cerr<<m.embedding_count<<'\n';
}
