// Exact weighted bonds through six. The Python caller groups parallel distinctions.
#include <algorithm>
#include <array>
#include <cstdint>
#include <utility>
#include <vector>

namespace {

struct Syndrome {
    uint64_t lo, hi;
    bool operator==(const Syndrome&) const = default;
    bool operator<(const Syndrome& other) const {
        return lo < other.lo || (lo == other.lo && hi < other.hi);
    }
    Syndrome operator^(const Syndrome& other) const {
        return {lo ^ other.lo, hi ^ other.hi};
    }
    void operator^=(const Syndrome& other) { *this = *this ^ other; }
};

uint64_t mix(uint64_t x) {
    x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31);
}

Syndrome chord_tag(unsigned chord) {
    if (chord < 64) return {UINT64_C(1) << chord, 0};
    if (chord < 128) return {0, UINT64_C(1) << (chord - 64)};
    // A linear projection for wider cycle spaces. It only introduces extra
    // candidates, because each candidate is validated on the actual graph.
    return {mix(chord + UINT64_C(0x243f6a8885a308d3)),
            mix(chord + UINT64_C(0x13198a2e03707344))};
}

struct Link {
    int a, b, weight;
};

struct Half {
    Syndrome key;
    std::array<uint16_t, 3> ids;
    uint8_t size, weight;
};

using Adjacent = std::vector<std::vector<std::pair<int, int>>>;

bool bond(const Adjacent& adjacency, const std::vector<Link>& links,
          const std::vector<int>& deleted, const std::array<int, 6>& support,
          int size, int stamp, std::vector<int>& component, std::vector<int>& queue) {
    std::fill(component.begin(), component.end(), -1);
    int count = 0;
    for (int start = 0; start < static_cast<int>(adjacency.size()); ++start) {
        if (component[start] != -1) continue;
        if (count == 2) return false;
        component[start] = count++;
        queue.assign(1, start);
        for (size_t i = 0; i < queue.size(); ++i) {
            for (auto [v, link] : adjacency[queue[i]]) {
                if (deleted[link] == stamp || component[v] != -1) continue;
                component[v] = component[start];
                queue.push_back(v);
            }
        }
    }
    if (count != 2) return false;
    for (int i = 0; i < size; ++i) {
        const auto& link = links[support[i]];
        if (component[link.a] == component[link.b]) return false;
    }
    return true;
}

}  // namespace

// A return of 2 or 3 is a limit hit. The partially filled table then has no authority.
extern "C" int short_bond_table(int vertices, int m, const int* raw, int cutoff,
                                uint64_t half_limit, uint64_t match_limit,
                                uint8_t* table, uint64_t* stats) {
    if (vertices < 2 || m < 1 || m > UINT16_MAX || cutoff < 1 || cutoff > 6) return 1;
    std::fill_n(stats, 10, UINT64_C(0));
    std::fill_n(table, static_cast<size_t>(m) * m, static_cast<uint8_t>(cutoff + 1));
    Adjacent adjacency(vertices);
    std::vector<Link> links;
    for (int i = 0; i < m; ++i) {
        auto [a, b, weight] = Link{raw[3*i], raw[3*i+1], raw[3*i+2]};
        if (a < 0 || b < 0 || a >= vertices || b >= vertices || a == b || weight < 1) return 1;
        links.push_back({a, b, weight});
        adjacency[a].emplace_back(b, i);
        adjacency[b].emplace_back(a, i);
    }

    // Chord coordinates are the fundamental cycles of this spanning tree.
    std::vector<int> parent(vertices, -1), parent_link(vertices, -1), order{0};
    std::vector<bool> tree(m);
    parent[0] = 0;
    for (size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        for (auto [v, link] : adjacency[u]) {
            if (parent[v] != -1) continue;
            parent[v] = u;
            parent_link[v] = link;
            tree[link] = true;
            order.push_back(v);
        }
    }
    if (order.size() != static_cast<size_t>(vertices)) return 1;
    std::vector<Syndrome> syndromes(m), branch(vertices);
    unsigned chord = 0;
    for (int i = 0; i < m; ++i) {
        if (tree[i]) continue;
        const auto& [a, b, _] = links[i];
        syndromes[i] = chord_tag(chord++);
        branch[a] ^= syndromes[i];
        branch[b] ^= syndromes[i];
    }
    for (size_t i = order.size() - 1; i > 0; --i) {
        int u = order[i];
        syndromes[parent_link[u]] = branch[u];
        branch[parent[u]] ^= branch[u];
    }
    stats[0] = chord;

    std::vector<uint16_t> eligible;
    for (int i = 0; i < m; ++i) {
        if (links[i].weight <= cutoff) eligible.push_back(i);
    }
    std::vector<Half> halves{{{0, 0}, {}, 0, 0}};
    auto save = [&](const Half& half) {
        if (halves.size() >= half_limit) return false;
        halves.push_back(half);
        ++stats[1];
        return true;
    };
    stats[1] = 1;
    for (size_t p = 0; p < eligible.size(); ++p) {
        uint16_t i = eligible[p];
        int cost = links[i].weight;
        if (!save({syndromes[i], {i}, 1, static_cast<uint8_t>(cost)})) return 2;
        for (size_t q = p + 1; q < eligible.size(); ++q) {
            uint16_t j = eligible[q];
            int two = cost + links[j].weight;
            if (two > cutoff) continue;
            Syndrome key = syndromes[i] ^ syndromes[j];
            if (!save({key, {i, j}, 2, static_cast<uint8_t>(two)})) return 2;
            for (size_t r = q + 1; r < eligible.size(); ++r) {
                uint16_t k = eligible[r];
                int three = two + links[k].weight;
                if (three > cutoff) continue;
                if (!save({key ^ syndromes[k], {i, j, k}, 3, static_cast<uint8_t>(three)})) return 2;
            }
        }
    }

    std::sort(halves.begin(), halves.end(), [](const Half& a, const Half& b) { return a.key < b.key; });
    std::vector<int> component(vertices), queue, deleted(m);
    queue.reserve(vertices);
    int stamp = 0;
    for (size_t first = 0; first < halves.size();) {
        size_t end = first + 1;
        while (end < halves.size() && halves[first].key == halves[end].key) ++end;
        for (size_t i = first; i < end; ++i) {
            for (size_t j = i + 1; j < end; ++j) {
                if (++stats[2] > match_limit) return 3;
                const Half* left = &halves[i];
                const Half* right = &halves[j];
                if (!right->size || (left->size && left->ids[0] > right->ids[0])) std::swap(left, right);
                // The first floor(k/2) indices give a unique split for each k-set.
                if (left->size > right->size || left->size + 1 < right->size) continue;
                if (left->size && left->ids[left->size - 1] >= right->ids[0]) continue;
                int cost = left->weight + right->weight;
                if (cost > cutoff) continue;
                int size = left->size + right->size;
                std::array<int, 6> support{};
                std::copy_n(left->ids.begin(), left->size, support.begin());
                std::copy_n(right->ids.begin(), right->size, support.begin() + left->size);
                ++stamp;
                ++stats[3];
                for (int x = 0; x < size; ++x) deleted[support[x]] = stamp;
                if (!bond(adjacency, links, deleted, support, size, stamp, component, queue)) continue;
                ++stats[3 + cost];
                for (int x = 0; x < size; ++x) {
                    for (int y = 0; y < size; ++y) {
                        auto& entry = table[static_cast<size_t>(support[x]) * m + support[y]];
                        entry = std::min(entry, static_cast<uint8_t>(cost));
                    }
                }
            }
        }
        first = end;
    }
    return 0;
}
