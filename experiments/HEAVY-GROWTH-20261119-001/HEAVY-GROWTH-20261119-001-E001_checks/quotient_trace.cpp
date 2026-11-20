// Trace maximal compatible sets on a literal true-twin quotient.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <tuple>
#include <vector>

template<int W>
struct Enumeration {
    using Mask = std::array<uint64_t,W>;
    const std::vector<Mask>& conflicts;
    int width;
    uint64_t cap;
    uint64_t nodes = 0, maxima = 0;
    bool capped = false;

    static void set(Mask& m,int v) { m[v/64] |= uint64_t{1} << (v%64); }
    static void clear(Mask& m,int v) { m[v/64] &= ~(uint64_t{1} << (v%64)); }
    static bool has(const Mask& m,int v) { return m[v/64] >> (v%64) & 1; }

    int common(const Mask& a,const Mask& b) const {
        int count = 0;
        for (int k = 0; k < width; ++k) count += std::popcount(a[k] & b[k]);
        return count;
    }

    Mask remove(Mask a,const Mask& b) const {
        for (int k = 0; k < width; ++k) a[k] &= ~b[k];
        return a;
    }

    template<typename F>
    void visit(const Mask& a,F operation) const {
        for (int k = 0; k < width; ++k) {
            for (uint64_t row = a[k]; row; row &= row-1) {
                if (!operation(k*64 + std::countr_zero(row))) return;
            }
        }
    }

    std::pair<int,int> pivot(const Mask& p,const Mask& x) const {
        int best = -1, cost = std::numeric_limits<int>::max();
        for (const auto* row : {&x,&p}) {
            int considered = 0;
            visit(*row,[&](int u) {
                int unavailable = common(p,conflicts[u]);
                if (unavailable < cost) { best = u; cost = unavailable; }
                return ++considered < 32 && cost > int(row == &p);
            });
            if (cost == 0) break;
        }
        return {best,cost};
    }

    void emit(const Mask& selected,const Mask& x) {
        if (common(x,x)) return;
        ++maxima;
        std::cout.write(reinterpret_cast<const char*>(selected.data()),width*sizeof(uint64_t));
    }

    void recur(Mask selected,Mask p,Mask x) {
        if (nodes == cap) { capped = true; return; }
        ++nodes;
        if (!common(p,p)) { emit(selected,x); return; }
        auto [u,cost] = pivot(p,x);
        if (cost == 0) return;
        if (cost == 1 && has(p,u)) {
            Mask forced{};
            visit(p,[&](int v) {
                if (common(p,conflicts[v]) == 1) {
                    set(forced,v);
                    set(selected,v);
                    x = remove(x,conflicts[v]);
                }
                return true;
            });
            p = remove(p,forced);
            if (!common(p,p)) { emit(selected,x); return; }
            std::tie(u,cost) = pivot(p,x);
            if (cost == 0) return;
        }
        Mask choices{};
        for (int k = 0; k < width; ++k) choices[k] = p[k] & conflicts[u][k];
        visit(choices,[&](int v) {
            set(selected,v);
            recur(selected,remove(p,conflicts[v]),remove(x,conflicts[v]));
            clear(selected,v);
            clear(p,v);
            set(x,v);
            return !capped;
        });
    }
};

template<int W>
int solve(uint32_t n,uint64_t cap) {
    using Search = Enumeration<W>;
    using Mask = typename Search::Mask;
    std::vector<Mask> rows(n);
    int width = (n+63)/64;
    Mask full{};
    for (uint32_t v = 0; v < n; ++v) {
        if (!std::cin.read(reinterpret_cast<char*>(rows[v].data()),width*sizeof(uint64_t))) return 2;
        Search::set(full,v);
        Search::set(rows[v],v);
    }
    Search engine{rows,width,cap};
    engine.recur({},full,{});
    std::cerr << engine.nodes << ' ' << engine.maxima << ' ' << !engine.capped << '\n';
    return !std::cout;
}

int main(int argc,char** argv) {
    static_assert(std::endian::native == std::endian::little);
    std::ios::sync_with_stdio(false);
    if (argc != 2) return 2;
    uint64_t cap = std::stoull(argv[1]);
    uint32_t n = 0;
    if (!std::cin.read(reinterpret_cast<char*>(&n),sizeof(n)) || !n || n > 5056 || !cap) return 2;
    if (n <= 384) return solve<6>(n,cap);
    if (n <= 1024) return solve<16>(n,cap);
    if (n <= 2304) return solve<36>(n,cap);
    return solve<79>(n,cap);
}
