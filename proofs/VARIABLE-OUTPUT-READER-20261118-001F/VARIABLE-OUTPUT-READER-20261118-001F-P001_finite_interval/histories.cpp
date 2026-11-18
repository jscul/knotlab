// Count every chronological history arriving at and leaving a given population.
// This audit is independent of the canonical graph generator and the distance checker.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using Mask = unsigned;
using Count = std::uint64_t;
constexpr int max_sites = 12;
constexpr Count unset = ~Count{0};

int take(Mask& mask) {
    int i = std::countr_zero(mask);
    mask &= mask - 1;
    return i;
}

struct Shape {
    int n{};
    std::array<Mask, max_sites> neighbors{};
    std::array<int, max_sites> loose{};
};

struct History {
    const Shape& g;
    Mask full;
    std::array<int, max_sites> arity{};
    std::array<Count, 1U << max_sites> ways;

    explicit History(const Shape& graph) : g(graph), full((1U << g.n) - 1) {
        std::fill_n(ways.begin(), full + 1, unset);
        for (int i = 0; i < g.n; ++i) arity[i] = std::popcount(g.neighbors[i]) + g.loose[i];
    }

    bool compatible(Mask parents, Mask earlier) const {
        auto remaining = parents;
        std::array<Mask, 3> witnesses{};
        int n = 0;
        while (remaining) witnesses[n++] = g.neighbors[take(remaining)] & earlier;
        if (n == 1) return true;
        if (!(witnesses[0] & witnesses[1])) return false;
        if (n == 2) return true;
        return (witnesses[1] & witnesses[2]) && (witnesses[2] & witnesses[0])
            && !(witnesses[0] & witnesses[1] & witnesses[2]);
    }

    Count histories(Mask active) {
        Count& answer = ways[active];
        if (answer != unset) return answer;
        if (std::has_single_bit(active)) return answer = arity[std::countr_zero(active)] == 3;
        answer = 0;
        for (Mask choices = active; choices; ) {
            const int v = take(choices);
            const Mask parents = g.neighbors[v] & active;
            const int p = std::popcount(parents);
            const int fresh = arity[v] - p;
            if (p < 1 || p > 3 || fresh < 2 || fresh > 3) continue;
            const Mask earlier = active ^ (1U << v);
            if (compatible(parents, earlier)) answer += histories(earlier);
        }
        return answer;
    }

    int actions() const {
        int result = 0;
        for (int i = 0; i < g.n; ++i) if (g.loose[i]) {
            const Mask one = 1U << i;
            ++result;
            for (int j = i + 1; j < g.n; ++j) if (g.loose[j]) {
                const Mask pair = one | (1U << j);
                if (!compatible(pair, full)) continue;
                ++result;
                for (int k = j + 1; k < g.n; ++k) {
                    if (g.loose[k] && compatible(pair | (1U << k), full)) ++result;
                }
            }
        }
        return result;
    }
};

struct Symmetries {
    const Shape& g;
    std::array<Mask, max_sites> domains{}, twins{};
    std::array<int, max_sites> order{}, image{};

    explicit Symmetries(const Shape& graph) : g(graph) {
        for (int i = 0; i < g.n; ++i) for (int j = 0; j < g.n; ++j) {
            if (g.loose[i] != g.loose[j] || std::popcount(g.neighbors[i]) != std::popcount(g.neighbors[j])) continue;
            domains[i] |= 1U << j;
            const Mask other = ~((1U << i) | (1U << j));
            if (!((g.neighbors[i] ^ g.neighbors[j]) & other)) twins[i] |= 1U << j;
        }
        for (;;) {
            std::array<Count, max_sites> code{};
            Mask unused = (1U << g.n) - 1;
            while (unused) {
                const Mask part = domains[std::countr_zero(unused)];
                unused &= ~part;
                for (int i = 0; i < g.n; ++i)
                    code[i] = (code[i] << 3) | std::popcount(g.neighbors[i] & part);
            }
            bool changed = false;
            for (int i = 0; i < g.n; ++i) for (Mask c = domains[i]; c; ) {
                const int j = take(c);
                if (code[i] != code[j]) { domains[i] &= ~(1U << j); changed = true; }
            }
            if (!changed) break;
        }
        std::iota(order.begin(), order.begin() + g.n, 0);
        std::stable_sort(order.begin(), order.begin() + g.n, [&](int a, int b) {
            return std::popcount(domains[a]) < std::popcount(domains[b]);
        });
    }

    Count extend(int depth, Mask used) {
        if (depth == g.n) return 1;
        const int v = order[depth];
        Mask candidates = domains[v] & ~used;
        for (int i = 0; i < depth && candidates; ++i) {
            const int u = order[i];
            candidates &= (g.neighbors[v] & (1U << u)) ? g.neighbors[image[u]] : ~g.neighbors[image[u]];
        }
        Count count = 0;
        while (candidates) {
            const int w = std::countr_zero(candidates);
            const Mask same = candidates & twins[w];
            candidates &= ~same;
            image[v] = w;
            count += std::popcount(same) * extend(depth + 1, used | (1U << w));
        }
        return count;
    }
};

void check_file(const char* filename) {
    std::ifstream input(filename);
    if (!input) throw std::runtime_error("missing population");
    Count count = 0, ending = 0, leaving = 0, errors = 0;
    for (;;) {
        std::vector<Shape> batch;
        batch.reserve(2048);
        int size;
        while (batch.size() < 2048 && input >> size) {
            if (size < 1 || size > max_sites) throw std::runtime_error("bad site count");
            Shape g; g.n = size;
            for (int i = 0; i < size; ++i) input >> g.neighbors[i];
            for (int i = 0; i < size; ++i) input >> g.loose[i];
            if (!input) throw std::runtime_error("truncated record");
            batch.push_back(g);
        }
        if (batch.empty()) { if (!input.eof()) throw std::runtime_error("bad record"); break; }
        #pragma omp parallel for schedule(dynamic, 32) reduction(+:ending,leaving,errors)
        for (int i = 0; i < static_cast<int>(batch.size()); ++i) {
            const Shape& g = batch[i];
            History counter(g);
            const Count births = counter.histories(counter.full);
            const Count sym = Symmetries(g).extend(0, 0);
            if (!births || !sym || births % sym) { ++errors; continue; }
            ending += births / sym;
            leaving += (births / sym) * counter.actions();
        }
        count += batch.size();
    }
    if (errors) throw std::runtime_error("unreachable or nonintegral type in population");
    std::cout << filename << ' ' << count << ' ' << ending << ' ' << leaving << std::endl;
}
}

int main(int argc, char** argv) {
    try {
        for (int i = 1; i < argc; ++i) check_file(argv[i]);
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
