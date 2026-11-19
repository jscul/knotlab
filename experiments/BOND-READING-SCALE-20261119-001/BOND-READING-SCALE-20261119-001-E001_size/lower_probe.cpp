// Classify a prescribed name permutation by connected-cut cardinalities.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <vector>

using Mask = uint64_t;
using Table = std::vector<int>;
constexpr int absent = std::numeric_limits<int>::max();

bool connected(Mask side, const std::vector<Mask>& neighbors) {
    Mask remaining = side, pending = side & -side;
    while (pending) {
        Mask site = pending & -pending;
        pending ^= site;
        remaining ^= site;
        pending |= neighbors[std::countr_zero(site)] & remaining;
    }
    return remaining == 0;
}

int main() {
    int sites, width, profiles;
    while (std::cin >> sites >> width >> profiles) {
        if (width >= 64 || sites >= 32) return 2;
        std::vector<Mask> neighbors(sites), stars(sites);
        std::vector<int> image(width);
        for (int e = 0; e < width; ++e) {
            int u, v;
            std::cin >> u >> v >> image[e];
            neighbors[u] |= Mask{1} << v;
            neighbors[v] |= Mask{1} << u;
            stars[u] |= Mask{1} << e;
            stars[v] |= Mask{1} << e;
        }
        Mask all_sites = (Mask{1} << sites) - 1, shore = 0, cut = 0;
        std::vector<std::vector<int>> bonds;
        for (Mask k = 1; k < (Mask{1} << (sites - 1)); ++k) {
            Mask added = k & -k;
            shore ^= added;
            cut ^= stars[std::countr_zero(added)];
            if (!connected(shore, neighbors) || !connected(all_sites ^ shore, neighbors)) continue;
            bonds.emplace_back();
            for (Mask left = cut; left; left &= left - 1) bonds.back().push_back(std::countr_zero(left));
        }
        auto index = [width](int a, int b, int c) { return (a * width + b) * width + c; };
        std::vector<std::pair<int, int>> compare;
        for (int a = 0; a < width; ++a) for (int b = a; b < width; ++b) for (int c = b; c < width; ++c) {
            int p[] = {image[a], image[b], image[c]};
            std::sort(p, p + 3);
            int left = index(a, b, c), right = index(p[0], p[1], p[2]);
            if (left < right) compare.emplace_back(left, right);
        }
        // Quadruples are unnecessary here. Repeated slots include every lower order.
        std::vector<std::vector<int>> lookup;
        Table table(width * width * width);
        for (const auto& b : bonds) {
            auto& slots = lookup.emplace_back();
            for (int a : b) for (int c : b) for (int d : b) {
                if (a <= c && c <= d && (image[a] != a || image[c] != c || image[d] != d))
                    slots.push_back(index(a, c, d));
            }
        }
        std::vector<int> amount(width);
        for (int p = 0; p < profiles; ++p) {
            for (auto& value : amount) std::cin >> value;
            std::fill(table.begin(), table.end(), absent);
            for (size_t j = 0; j < bonds.size(); ++j) {
                int size = 0;
                for (int e : bonds[j]) size += amount[e];
                for (int slot : lookup[j]) table[slot] = std::min(table[slot], size);
            }
            auto bad = std::find_if(compare.begin(), compare.end(), [&](auto pair) {
                return table[pair.first] != table[pair.second];
            });
            std::cout << int(bad == compare.end()) << '\n';
        }
    }
}
