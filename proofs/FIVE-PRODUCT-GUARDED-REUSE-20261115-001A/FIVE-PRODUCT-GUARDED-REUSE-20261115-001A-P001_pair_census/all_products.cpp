// Independent lower bound with *all five* left product values revealed.
// Build: c++ -std=c++20 -O3 all_products.cpp -o all_products
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using SourceSet = std::uint64_t;
constexpr SourceSet full_source = ~SourceSet{0};

int first_bit(SourceSet value) { return std::countr_zero(value); }
int size_of(SourceSet value) { return std::popcount(value); }
int parity(unsigned value) { return std::popcount(value) & 1; }
int products(int x) { return x & (x >> 1); }
int total(int x) { return parity(products(x)); }
int polar(int x, int y) { return parity(((x << 1) ^ (x >> 1)) & y); }
SourceSet singleton(int i) { return SourceSet{1} << i; }

int colex_index(int a, int b, int c, int d) {
    return a + b*(b-1)/2 + c*(c-1)*(c-2)/6 + d*(d-1)*(d-2)*(d-3)/24;
}

SourceSet translation_class(SourceSet source) {
    constexpr std::array<SourceSet,6> low_half = {
        0x5555555555555555ULL, 0x3333333333333333ULL, 0x0f0f0f0f0f0f0f0fULL,
        0x00ff00ff00ff00ffULL, 0x0000ffff0000ffffULL, 0x00000000ffffffffULL
    };
    std::array<SourceSet,64> translates{};
    translates[0] = source;
    SourceSet smallest = source;
    for (int bit=0; bit<6; ++bit) {
        int step = 1 << bit;
        for (int i=0; i<step; ++i) {
            SourceSet x = translates[i];
            SourceSet moved = ((x & low_half[bit]) << step) | ((x & ~low_half[bit]) >> step);
            translates[step+i] = moved;
            smallest = std::min(smallest,moved);
        }
    }
    return smallest;
}

std::vector<int> affine_hull(const std::vector<int>& points) {
    if (points.empty()) return {};
    std::array<int,7> pivots{};
    int origin=points.front();
    for (int point:points) {
        unsigned v=point ^ origin;
        while (v) {
            int high=std::bit_width(v)-1;
            if (!pivots[high]) { pivots[high]=v; break; }
            v ^= pivots[high];
        }
    }
    std::vector<int> span{origin};
    for (int d:pivots) if (d) {
        int old=span.size();
        for (int i=0;i<old;++i) span.push_back(span[i]^d);
    }
    return span;
}

bool raw_terminal(SourceSet source) {
    if (!source) return true;
    std::vector<int> honest;
    for (SourceSet x=source; x; x&=x-1) {
        int i=first_bit(x);
        honest.push_back(i | (total(i)<<6));
    }
    auto cell=affine_hull(honest);
    std::vector<int> plain;
    for (int p:cell) if ((p>>6)!=total(p&63)) plain.push_back(p);
    auto other_hull=affine_hull(plain);
    if (other_hull.size()==cell.size()) return false;
    // A nonspanning plain quadratic level is itself affine.
    assert(other_hull.size()==plain.size());
    return true;
}

class Search {
    std::vector<SourceSet> candidate_sets;
    std::vector<std::vector<int>> containing_four;
    std::vector<SourceSet> rows;
    std::unordered_map<SourceSet,unsigned> infeasible_budget;

    void build_terminals() {
        // Pick an isotropic two-space E, a coset of E-perp, and one E-coset to omit.
        for (int a=1;a<64;++a) for (int b=a+1;b<64;++b) {
            if ((a^b)<b || polar(a,b)) continue;
            for (int side=0;side<4;++side) {
                SourceSet flat=0;
                for (int x=0;x<64;++x)
                    if ((polar(x,a) | (polar(x,b)<<1))==side) flat |= singleton(x);
                SourceSet remainder=flat;
                while (remainder) {
                    int x=first_bit(remainder);
                    SourceSet omitted=singleton(x)|singleton(x^a)|singleton(x^b)|singleton(x^a^b);
                    candidate_sets.push_back(flat ^ omitted);
                    remainder &= ~omitted;
                }
            }
        }
        std::sort(candidate_sets.begin(),candidate_sets.end());
        assert(std::adjacent_find(candidate_sets.begin(),candidate_sets.end())==candidate_sets.end());
        assert(candidate_sets.size()==5040);
        containing_four.resize(635376);  // binomial(64,4)
        for (unsigned id=0;id<candidate_sets.size();++id) {
            std::array<int,12> points{};
            int n=0;
            assert(size_of(candidate_sets[id])==12);
            for (SourceSet m=candidate_sets[id];m;m&=m-1) points[n++]=first_bit(m);
            for (int a=0;a<9;++a) for (int b=a+1;b<10;++b)
                for (int c=b+1;c<11;++c) for (int d=c+1;d<12;++d)
                    containing_four[colex_index(points[a],points[b],points[c],points[d])].push_back(id);
        }
    }

    bool terminal(SourceSet s) const {
        int size=size_of(s);
        if (size<=3) return true;
        if (size>12) return false;
        std::array<int,4> first{};
        SourceSet remaining=s;
        for (int& p:first) { p=first_bit(remaining); remaining&=remaining-1; }
        int key=colex_index(first[0],first[1],first[2],first[3]);
        for (int id:containing_four[key]) if ((candidate_sets[id]&s)==s) return true;
        return false;
    }

public:
    unsigned root_partitions=0, raw_checks=0;

    Search() {
        build_terminals();
        for (int row=0;row<2048;++row) {
            SourceSet answers=0;
            for (int x=0;x<64;++x)
                if (parity((row & x) ^ ((row >> 6) & products(x)))) answers |= singleton(x);
            rows.push_back(answers);
        }
        assert(std::unordered_set<SourceSet>(rows.begin(),rows.end()).size()==2048);
    }

    void verify_terminals() {
        auto check=[this](SourceSet s){ assert(terminal(s)==raw_terminal(s)); ++raw_checks; };
        for (SourceSet s:candidate_sets) check(s);
        for (int a=0;a<64;++a) for (int b=a+1;b<64;++b) for (int c=b+1;c<64;++c)
            check(singleton(a)|singleton(b)|singleton(c));
        std::mt19937_64 rng(20261115);
        for (int i=0;i<6000;++i) {
            SourceSet cap=candidate_sets[rng()%candidate_sets.size()];
            SourceSet subset=cap & rng();
            check(subset);
            check(subset | singleton(rng()%64));
            SourceSet s=0;
            for (int j=0;j<4+(i%11);++j) s |= singleton(rng()%64);
            check(s);
        }
        for (int value=0;value<8;++value) {
            SourceSet leaf=0;
            for (int x=0;x<64;++x)
                if (((x&1)|((x>>1)&2)|((x>>2)&4))==value) leaf |= singleton(x);
            assert(size_of(leaf)==8 && terminal(leaf) && raw_terminal(leaf));
        }
    }

    bool affordable(SourceSet s,unsigned budget,bool root=false) {
        if (size_of(s)>static_cast<int>(12*budget)) return false;
        if (terminal(s)) return true;
        if (budget<=1) return false;
        SourceSet key=translation_class(s);
        if (auto it=infeasible_budget.find(key);it!=infeasible_budget.end() && it->second>=budget) return false;
        std::unordered_set<SourceSet> root_types;
        for (unsigned q=1;q<rows.size();++q) {
            SourceSet small=s&rows[q], large=s^small;
            if (!small || !large) continue;
            if (size_of(small)>size_of(large)) std::swap(small,large);
            if (root) {
                SourceSet type=translation_class(small);
                if (size_of(small)==size_of(large)) type=std::min(type,translation_class(large));
                if (!root_types.insert(type).second) continue;
                ++root_partitions;
            }
            unsigned small_mass=(size_of(small)+11)/12, large_mass=(size_of(large)+11)/12;
            if (small_mass+large_mass>budget) continue;
            bool small_stops=terminal(small), large_stops=terminal(large);
            unsigned minimum_small=small_stops?1:std::max(2u,small_mass);
            unsigned minimum_large=large_stops?1:std::max(2u,large_mass);
            if (minimum_small+minimum_large>budget) continue;
            for (unsigned i=minimum_small;i<=budget-minimum_large;++i)
                if ((small_stops || affordable(small,i)) && (large_stops || affordable(large,budget-i))) return true;
        }
        infeasible_budget[key]=std::max(infeasible_budget[key],budget);
        return false;
    }
    unsigned cache_size() const { return infeasible_budget.size(); }
};

int main() {
    Search search;
    search.verify_terminals();
    bool fits=search.affordable(full_source,7,true);
    assert(!fits);
    std::cout<<"{\"status\":\"passed\",\"visible_left_products\":5,\"sources\":64,"
             <<"\"nonconstant_honest_questions_up_to_complement\":2047,\"maximal_terminal_source_sets\":5040,"
             <<"\"direct_terminal_crosschecks\":"<<search.raw_checks<<",\"root_translation_classes\":"<<search.root_partitions
             <<",\"cached_infeasible_source_classes\":"<<search.cache_size()<<",\"seven_leaves_feasible\":false,"
             <<"\"verified_upper_leaves\":8}\n";
}
