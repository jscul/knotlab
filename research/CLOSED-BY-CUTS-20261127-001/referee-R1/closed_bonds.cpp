// Enumerate allowed states and all bonds of three disjoint agreement readings.
// A row records the three carrier masks and an eight-bit image, with the first
// reading the high bit of each word. Source names are densely renumbered.
#include <algorithm>
#include <array>
#include <cstdint>
#include <random>
#include <vector>

namespace {
using Word = std::uint64_t;
using Mask = std::uint32_t;
using Cell = std::array<Word, 4>;
struct Bond {
    Mask a, b, c, image;
};
struct Reading {
    Mask mask;
    std::vector<Word> yes, no;
};
std::vector<Bond> results;
std::vector<Mask> unread;
int state_count = 0;

bool equal_on(Mask values, Mask support) {
    Mask value = values & support;
    return value == 0 || value == support;
}

bool all_pairs_free(unsigned image) {
    // With each one coordinate forgotten, every binary pair must occur.
    return ((image | (image >> 4)) & 15u) == 15u
        && ((image | (image >> 2)) & 51u) == 51u
        && ((image | (image >> 1)) & 85u) == 85u;
}
}

extern "C" {
const Bond* closed_results() { return results.data(); }
const Mask* closed_unread() { return unread.data(); }
int closed_unread_count() { return static_cast<int>(unread.size()); }
int closed_state_count() { return state_count; }

int closed_enumerate(int n, int nk, const Mask* knots, int nr, const Mask* carriers) {
    results.clear();
    unread.clear();
    std::vector<Mask> states;
    for (Mask s = 0; s < (1u << n); ++s) {
        if (std::none_of(knots, knots + nk, [s](Mask k) { return equal_on(s, k); }))
            states.push_back(s);
    }
    state_count = static_cast<int>(states.size());
    if (states.empty())
        return 0;
    // Interleave the allowed states so unconstrained triples can exhibit all
    // eight words in early blocks. Every block is visited if a word is absent.
    std::mt19937 order(314159);
    std::shuffle(states.begin(), states.end(), order);
    const std::size_t blocks = (states.size() + 63) / 64;
    std::vector<std::vector<std::vector<std::size_t>>> fixes;
    for (int k = 0; k < nk; ++k) {
        std::vector<std::vector<std::size_t>> table(1u << __builtin_popcount(knots[k]));
        for (std::size_t s = 0; s < states.size(); ++s) {
            unsigned key = 0;
            for (Mask part = knots[k]; part; part &= part - 1)
                key = 2 * key + ((states[s] & (part & -part)) != 0);
            table[key].push_back(s);
        }
        fixes.push_back(std::move(table));
    }
    std::vector<Reading> reads;
    for (int r = 0; r < nr; ++r) {
        const Mask support = carriers[r];
        bool eligible = true;
        for (const auto& table : fixes) {
            bool varies_at_one_fix = false;
            for (const auto& group : table) {
                if (group.empty())
                    continue;
                const bool first = equal_on(states[group.front()], support);
                if (std::any_of(group.begin() + 1, group.end(), [&](std::size_t s) {
                    return equal_on(states[s], support) != first;
                })) {
                    varies_at_one_fix = true;
                    break;
                }
            }
            if (!varies_at_one_fix) {
                eligible = false;
                break;
            }
        }
        if (!eligible)
            continue;
        unread.push_back(support);
        Reading row{support, std::vector<Word>(blocks), std::vector<Word>(blocks)};
        for (std::size_t s = 0; s < states.size(); ++s) {
            auto& column = equal_on(states[s], support) ? row.yes : row.no;
            column[s / 64] |= Word(1) << (s % 64);
        }
        reads.push_back(std::move(row));
    }
    std::vector<Cell> pairs(blocks);
    for (std::size_t i = 0; i < reads.size(); ++i) {
        const Reading& a = reads[i];
        for (std::size_t j = i + 1; j < reads.size(); ++j) {
            const Reading& b = reads[j];
            if (a.mask & b.mask)
                continue;
            Cell present{};
            for (std::size_t bidx = 0; bidx < blocks; ++bidx) {
                pairs[bidx] = {a.no[bidx] & b.no[bidx], a.no[bidx] & b.yes[bidx],
                               a.yes[bidx] & b.no[bidx], a.yes[bidx] & b.yes[bidx]};
                for (int p = 0; p < 4; ++p)
                    present[p] |= pairs[bidx][p];
            }
            if (std::any_of(present.begin(), present.end(), [](Word w) { return w == 0; }))
                continue;
            const Mask pair_mask = a.mask | b.mask;
            for (std::size_t k = j + 1; k < reads.size(); ++k) {
                const Reading& c = reads[k];
                if (pair_mask & c.mask)
                    continue;
                unsigned image = 0;
                for (std::size_t bidx = 0; bidx < blocks && image != 255; ++bidx) {
                    for (int p = 0; p < 4; ++p) {
                        const Word here = pairs[bidx][p];
                        image |= unsigned((here & c.no[bidx]) != 0) << (2 * p);
                        image |= unsigned((here & c.yes[bidx]) != 0) << (2 * p + 1);
                    }
                }
                if (image != 255 && all_pairs_free(image))
                    results.push_back({a.mask, b.mask, c.mask, image});
            }
        }
    }
    return static_cast<int>(results.size());
}
}
