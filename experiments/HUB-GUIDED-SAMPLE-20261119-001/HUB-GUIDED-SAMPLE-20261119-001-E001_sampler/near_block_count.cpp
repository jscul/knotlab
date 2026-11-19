// Independent full-quotient maximal-set enumeration using the conflict graph.
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <vector>

using Word = uint64_t;
constexpr int W = 10;
using Mask = std::array<Word, W>;

void add(Mask& row, int v) { row[v / 64] |= Word{1} << (v % 64); }
void remove(Mask& row, int v) { row[v / 64] &= ~(Word{1} << (v % 64)); }

struct Counter {
    int width;
    const std::vector<Mask>& closed_conflict;
    uint64_t count = 0;
    uint64_t calls = 0;

    int intersections(const Mask& a, const Mask& b) const {
        int total = 0;
        for (int i = 0; i < width; ++i) total += std::popcount(a[i] & b[i]);
        return total;
    }

    Mask without(Mask a, const Mask& b) const {
        for (int i = 0; i < width; ++i) a[i] &= ~b[i];
        return a;
    }

    template<typename F>
    void visit(const Mask& row, F call) const {
        for (int i = 0; i < width; ++i) {
            for (Word bits = row[i]; bits; bits &= bits - 1) call(i * 64 + std::countr_zero(bits));
        }
    }

    void recur(Mask p, Mask x) {
        ++calls;
        if (intersections(p, p) == 0) {
            count += intersections(x, x) == 0;
            return;
        }
        Mask mandatory{};
        visit(p, [&](int v) {
            if (intersections(p, closed_conflict[v]) == 1) add(mandatory, v);
        });
        visit(mandatory, [&](int v) { x = without(x, closed_conflict[v]); });
        p = without(p, mandatory);
        if (intersections(p, p) == 0) {
            count += intersections(x, x) == 0;
            return;
        }

        int pivot = -1, least = std::numeric_limits<int>::max();
        const auto consider = [&](int v) {
            int conflicts = intersections(p, closed_conflict[v]);
            if (conflicts >= least) return;
            pivot = v;
            least = conflicts;
        };
        visit(x, consider);
        if (least == 0) return;
        if (least > 1) visit(p, consider);
        if (pivot < 0) throw 1;
        Mask choices{};
        for (int i = 0; i < width; ++i) choices[i] = p[i] & closed_conflict[pivot][i];
        visit(choices, [&](int v) {
            recur(without(p, closed_conflict[v]), without(x, closed_conflict[v]));
            remove(p, v);
            add(x, v);
        });
    }
};

int main() {
    int n, m;
    if (!(std::cin >> n >> m) || n < 1 || n > 64*W || m < 0) return 2;
    std::vector<Mask> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        if (!(std::cin >> u >> v) || u < 0 || u >= v || v >= n) return 2;
        add(graph[u], v);
        add(graph[v], u);
    }
    std::map<Mask, int> classes;
    std::vector<int> current(n), original;
    for (int v = 0; v < n; ++v) {
        auto [it, created] = classes.try_emplace(graph[v], original.size());
        current[v] = it->second;
        if (created) original.push_back(v);
    }
    int reduced = original.size();
    int width = (reduced + 63) / 64;
    std::vector<Mask> conflicts(reduced);
    Mask all{};
    for (int i = 0; i < reduced; ++i) {
        for (int v = 0; v < n; ++v) {
            if (graph[original[i]][v/64] & (Word{1} << (v%64))) add(conflicts[i], current[v]);
        }
        add(conflicts[i], i);
        add(all, i);
    }
    Counter checker{width, conflicts};
    checker.recur(all, {});
    std::cout << reduced << ' ' << checker.count << ' ' << checker.calls << '\n';
}
