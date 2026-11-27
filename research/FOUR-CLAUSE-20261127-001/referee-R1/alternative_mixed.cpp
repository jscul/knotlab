// Six raw carriers that could admit four clauses with opposite excluded
// values on at least one of their shared readings.
#include <algorithm>
#include <array>
#include <cstdint>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using C = std::uint32_t;
using U = std::uint64_t;
using Three = std::array<C,3>;
using Six = std::array<C,6>;

static U pair_key(C a,C b) {
    if (a>b) std::swap(a,b);
    return (U(a)<<32) | b;
}

static U triple_key(C a,C b,C c) {
    Three x{a,b,c};
    std::sort(x.begin(),x.end());
    return (U(x[0])<<42) | (U(x[1])<<21) | x[2];
}

struct SixHash {
    std::size_t operator()(const Six& items) const {
        U v = 14695981039346656037ULL;
        for (C x : items) v=(v^x)*1099511628211ULL;
        return v;
    }
};

struct Group {
    Six masks{};
    C occupied=0;
};

struct Screening {
    std::unordered_map<U,std::vector<C>> by_pair;
    std::unordered_map<C,std::vector<std::array<C,2>>> by_one;
    std::unordered_set<U> rules;
    std::array<std::unordered_set<Six,SixHash>,2> seen_seeds;
    std::unordered_set<Six,SixHash> shortlisted;
    U examined=0;
    int distinctions=0;

    void test(Six x) {
        std::sort(x.begin(),x.end());
        int count=0;
        ++examined;
        for(int i=0;i<4;++i) for(int j=i+1;j<5;++j) for(int k=j+1;k<6;++k)
            if(rules.count(triple_key(x[i],x[j],x[k])) && ++count==4) {
                shortlisted.insert(x);
                return;
            }
    }

    void extend(Group x,int size) {
        if (__builtin_popcount(x.occupied)+2*(6-size)>distinctions) return;
        std::sort(x.masks.begin(),x.masks.begin()+size);
        if (!seen_seeds[size-4].insert(x.masks).second) return;
        for (int i=0;i<size;++i) for (int j=i+1;j<size;++j) {
            auto pair=by_pair.find(pair_key(x.masks[i],x.masks[j]));
            if (pair==by_pair.end()) continue;
            for(C fresh:pair->second) if (!(fresh & x.occupied)) {
                Group next=x;
                next.masks[size]=fresh;
                if(size==5) test(next.masks);
                else { next.occupied|=fresh; extend(next,5); }
            }
        }
        // Two new carriers can appear together in a single remaining clause.
        if(size==4) for(int i=0;i<4;++i) {
            for(const auto& p:by_one.at(x.masks[i])) if(!((p[0]|p[1]) & x.occupied)) {
                Six six=x.masks;
                six[4]=p[0]; six[5]=p[1];
                test(six);
            }
        }
    }
};

struct MixedResult {
    std::vector<Six> sets;
    std::array<U,3> counts{};
};

extern "C" MixedResult* mixed_find(const C* data, std::size_t number) {
    Screening screen;
    std::unordered_map<C,std::array<std::vector<Three>,2>> occurrences;
    C all=0;
    for(std::size_t t=0;t<number;++t) {
        Three x{data[3*t]>>1,data[3*t+1]>>1,data[3*t+2]>>1};
        all|=x[0]|x[1]|x[2];
        screen.rules.insert(triple_key(x[0],x[1],x[2]));
        for (int i=0;i<3;++i) {
            C b=x[(i+1)%3],c=x[(i+2)%3];
            screen.by_pair[pair_key(b,c)].push_back(x[i]);
            screen.by_one[x[i]].push_back({b,c});
            occurrences[x[i]][data[3*t+i]&1].push_back(x);
        }
    }
    screen.distinctions=__builtin_popcount(all);
    for(const auto& entry:occurrences) {
        const auto& signs=entry.second;
        for(const Three& first:signs[0]) for(const Three& second:signs[1]) {
            Group s{{first[0],first[1],first[2],0,0,0},first[0]|first[1]|first[2]};
            int size=3;
            bool disjoint=true;
            for (C m:second) {
                if(std::find(first.begin(),first.end(),m)!=first.end()) continue;
                if(s.occupied&m) {disjoint=false; break;}
                s.masks[size++]=m; s.occupied|=m;
            }
            if(disjoint && (size==4 || size==5)) screen.extend(s,size);
        }
    }
    auto* result=new MixedResult();
    result->counts={screen.seen_seeds[0].size(),screen.seen_seeds[1].size(),screen.examined};
    result->sets.assign(screen.shortlisted.begin(),screen.shortlisted.end());
    std::sort(result->sets.begin(),result->sets.end());
    return result;
}

extern "C" std::size_t mixed_size(MixedResult* r) { return r->sets.size(); }
extern "C" const Six* mixed_sets(MixedResult* r) {return r->sets.data();}
extern "C" const U* mixed_counts(MixedResult* r) {return r->counts.data();}
extern "C" void mixed_release(MixedResult* r) {delete r;}
