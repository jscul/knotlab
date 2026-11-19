// Exact streaming parent groups for a small precursor with a large next roster.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>

using Word = std::uint64_t;
constexpr int reserve_words = 32;
using Mask = std::array<Word, reserve_words>;

void put(Mask& m, int i) { m[i / 64] |= Word{1} << (i % 64); }
void drop(Mask& m, int i) { m[i / 64] &= ~(Word{1} << (i % 64)); }

struct Groups {
    int n, width;
    std::vector<Mask> adjacent, covers, blocks;
    std::vector<std::vector<int>> owners;
    std::vector<int> chosen;
    Mask selected{};

    explicit Groups(std::istream& in) {
        int count;
        if (!(in >> n >> count) || n < 1 || n > 64 * reserve_words || count < 0)
            throw std::runtime_error("expected precursor of up to 2048 live junctions");
        width = (n + 63) / 64;
        adjacent.resize(n);
        covers.resize(n);
        owners.resize(n);
        std::string line;
        std::getline(in, line);
        for (int id = 0; id < count; ++id) {
            if (!std::getline(in, line)) throw std::runtime_error("missing block");
            std::istringstream row(line);
            std::vector<int> members;
            Mask block{};
            for (int v; row >> v;) {
                if (v < 0 || v >= n) throw std::runtime_error("invalid point");
                members.push_back(v);
                put(block, v);
            }
            if (!row.eof() || members.size() < 2) throw std::runtime_error("invalid block");
            blocks.push_back(block);
            for (int v : members) {
                owners[v].push_back(id);
                for (int w = 0; w < width; ++w) adjacent[v][w] |= block[w];
            }
        }
        if (in >> line) throw std::runtime_error("extra block data");
        for (int v = 0; v < n; ++v) drop(adjacent[v], v);
    }

    bool empty(const Mask& m) const {
        return std::none_of(m.begin(), m.begin() + width, [](Word w) { return w; });
    }

    bool subset(const Mask& a, const Mask& b) const {
        for (int w = 0; w < width; ++w)
            if (a[w] & ~b[w]) return false;
        return true;
    }

    void enumerate(Mask p, Mask x, const std::vector<int>& held) {
        if (empty(p)) {
            if (!empty(x) || !held.empty() || chosen.size() < 3) return;
            for (int v : chosen) {
                std::cout << ' ' << v;
                for (int w = 0; w < width; ++w) covers[v][w] |= selected[w];
            }
            std::cout << '\n';
            return;
        }
        // If one block holds R and all of P, this whole subtree is held.
        for (int b : held)
            if (subset(p, blocks[b])) return;

        int pivot = -1, smallest = n + 1;
        for (const auto* pool : {&x, &p}) {
            int checked = 0;
            for (int w = 0; w < width && checked < 64; ++w) {
                for (Word bits = (*pool)[w]; bits && checked < 64; bits &= bits - 1, ++checked) {
                    const int v = 64*w + std::countr_zero(bits);
                    int misses = 0;
                    for (int j = 0; j < width && misses < smallest; ++j)
                        misses += std::popcount(p[j] & ~adjacent[v][j]);
                    if (misses >= smallest) continue;
                    smallest = misses;
                    pivot = v;
                    if (!smallest) return;
                }
            }
        }
        for (int w = 0; w < width; ++w) {
            for (Word bits = p[w] & ~adjacent[pivot][w]; bits; bits &= bits - 1) {
                const int v = 64*w + std::countr_zero(bits);
                Mask next_p{}, next_x{};
                for (int j = 0; j < width; ++j) {
                    next_p[j] = p[j] & adjacent[v][j];
                    next_x[j] = x[j] & adjacent[v][j];
                }
                std::vector<int> common;
                std::set_intersection(held.begin(), held.end(), owners[v].begin(), owners[v].end(),
                                      std::back_inserter(common));
                chosen.push_back(v);
                put(selected, v);
                enumerate(next_p, next_x, common);
                drop(selected, v);
                chosen.pop_back();
                drop(p, v);
                put(x, v);
            }
        }
    }

    void emit() {
        Mask all{}, none{};
        for (int v = 0; v < n; ++v) put(all, v);
        std::vector<int> held;
        for (int i = 0; i < static_cast<int>(blocks.size()); ++i) held.push_back(i);
        enumerate(all, none, held);
        for (int v = 0; v < n; ++v) {
            for (int j = v / 64; j < width; ++j) {
                for (Word bits = adjacent[v][j] & ~covers[v][j]; bits; bits &= bits - 1) {
                    const int u = 64*j + std::countr_zero(bits);
                    if (v < u) std::cout << v << ' ' << u << '\n';
                }
            }
        }
    }
};

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ios::sync_with_stdio(false);
    try {
        std::ifstream in(argv[1]);
        Groups(in).emit();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
