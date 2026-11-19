// Bounded independent exact count on the literal closed-neighborhood quotient.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using Word = uint64_t;

template<int W>
using Mask = std::array<Word, W>;

template<int W>
struct Count {
    const std::vector<Mask<W>>& conflict;
    uint64_t limit, leaves = 0, calls = 0;
    bool capped = false;

    static void set(Mask<W>& a, int v) { a[v/64] |= Word{1} << (v%64); }
    static void reset(Mask<W>& a, int v) { a[v/64] &= ~(Word{1} << (v%64)); }

    static int common(const Mask<W>& a, const Mask<W>& b) {
        int size = 0;
        for (int i = 0; i < W; ++i) size += std::popcount(a[i] & b[i]);
        return size;
    }

    static bool empty(const Mask<W>& a) {
        return std::none_of(a.begin(), a.end(), [](Word b) { return b; });
    }

    static Mask<W> without(const Mask<W>& a, const Mask<W>& b) {
        Mask<W> result;
        for (int i = 0; i < W; ++i) result[i] = a[i] & ~b[i];
        return result;
    }

    template<typename F>
    static void each(const Mask<W>& a, F f) {
        for (int i = 0; i < W; ++i) {
            for (Word left = a[i]; left; left &= left-1) {
                if (!f(i*64 + std::countr_zero(left))) return;
            }
        }
    }

    std::pair<int,int> pivot(const Mask<W>& p, const Mask<W>& x, int trial = 32) const {
        int best = -1, least = std::numeric_limits<int>::max();
        for (const auto* m : {&x,&p}) {
            int checked = 0;
            each(*m, [&](int v) {
                int misses = common(p,conflict[v]);
                if (misses < least) {
                    best = v;
                    least = misses;
                }
                return ++checked < trial && least > (m == &x ? 0 : 1);
            });
            if (least == 0) break;
        }
        return {best,least};
    }

    void visit(Mask<W> p, Mask<W> x) {
        if (calls == limit) { capped = true; return; }
        ++calls;
        if (empty(p)) { leaves += empty(x); return; }
        auto [chosen, degree] = pivot(p,x);
        // The conflict mask includes the vertex itself. Only an excluded
        // pivot can have zero conflicts with p, ruling out maximal completions.
        if (degree == 0) return;
        if (degree == 1 && (p[chosen/64] & (Word{1} << (chosen%64)))) {
            // Every admissible vertex compatible with the rest of p must
            // occur in every maximal completion of this partial set.
            Mask<W> mandatory{};
            each(p, [&](int u) {
                if (common(p,conflict[u]) == 1) {
                    set(mandatory,u);
                    x = without(x,conflict[u]);
                }
                return true;
            });
            p = without(p,mandatory);
            if (empty(p)) { leaves += empty(x); return; }
            std::tie(chosen,degree) = pivot(p,x);
            if (degree == 0) return;
        }
        // A maximal completion either contains the pivot or a conflict of it.
        Mask<W> choices;
        for (int i = 0; i < W; ++i) choices[i] = p[i] & conflict[chosen][i];
        each(choices, [&](int v) {
            visit(without(p,conflict[v]),without(x,conflict[v]));
            reset(p,v);
            set(x,v);
            return !capped;
        });
    }
};

template<int W>
int solve(const std::vector<std::vector<int>>& blocks, int n, uint64_t budget) {
    using Engine = Count<W>;
    if (n > W*64) return 2;
    std::vector<Mask<W>> adjacent(n);
    for (int u = 0; u < n; ++u) Engine::set(adjacent[u],u);
    for (const auto& block : blocks) {
        Mask<W> full{};
        for (int u : block) Engine::set(full,u);
        for (int u : block) for (int j = 0; j < W; ++j) adjacent[u][j] |= full[j];
    }
    std::map<Mask<W>, int> seen;
    std::vector<int> rep;
    // Identical closed neighborhoods force an all-or-none choice in a maximal set.
    for (int u = 0; u < n; ++u) {
        if (seen.try_emplace(adjacent[u],u).second) rep.push_back(u);
    }
    const int N = rep.size();
    std::vector<int> degree(N);
    for (int i = 0; i < N; ++i) for (int v : rep) {
        if (!(adjacent[rep[i]][v/64] & (Word{1} << (v%64)))) ++degree[i];
    }
    std::vector<int> order(N);
    std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b) { return degree[a] < degree[b]; });
    std::vector<Mask<W>> conflict(N);
    Mask<W> all{};
    for (int i = 0; i < N; ++i) {
        Engine::set(all,i);
        Engine::set(conflict[i],i);
        for (int j = 0; j < N; ++j) {
            int v = rep[order[j]];
            if (!(adjacent[rep[order[i]]][v/64] & (Word{1} << (v%64)))) Engine::set(conflict[i],j);
        }
    }
    Engine result{conflict,budget};
    result.visit(all,{});
    std::cout << N << ' ' << result.leaves << ' ' << result.calls << ' ' << (!result.capped) << '\n';
    return 0;
}

int main(int argc,char** argv) {
    if (argc != 2) return 2;
    uint64_t budget = std::stoull(argv[1]);
    int n, count;
    if (!(std::cin >> n >> count) || n < 1 || n > 5056 || count < 0 || budget < 1) return 2;
    std::string line;
    std::getline(std::cin,line);
    std::vector<std::vector<int>> blocks(count);
    for (auto& block : blocks) {
        if (!std::getline(std::cin,line)) return 2;
        std::istringstream row(line);
        for (int u; row >> u;) {
            if (u < 0 || u >= n) return 2;
            block.push_back(u);
        }
        if (!row.eof() || block.size() < 2) return 2;
    }
    if (n <= 1024) return solve<16>(blocks,n,budget);
    if (n <= 2304) return solve<36>(blocks,n,budget);
    if (n <= 4352) return solve<68>(blocks,n,budget);
    return solve<79>(blocks,n,budget);
}
