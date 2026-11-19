// Overlapping, exactly normalized greedy paths through maximal candidate sets.
#include <algorithm>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Word = std::uint64_t;
using Bits = std::vector<Word>;
using Factor = std::pair<int, int>;

void require(bool test, const char* reason) {
    if (!test) throw std::runtime_error(reason);
}

void insert(Bits& set, int u) { set[u / 64] |= Word{1} << (u % 64); }
void erase(Bits& set, int u) { set[u / 64] &= ~(Word{1} << (u % 64)); }
bool has(const Bits& set, int u) { return set[u / 64] >> (u % 64) & 1; }

template <class F>
void each(const Bits& set, F use) {
    for (int i = 0; i < int(set.size()); ++i)
        for (Word w = set[i]; w; w &= w - 1) use(64 * i + std::countr_zero(w));
}

int size(const Bits& set) {
    int count = 0;
    for (Word w : set) count += std::popcount(w);
    return count;
}

int select(const Bits& set, int rank) {
    for (int i = 0; i < int(set.size()); ++i) {
        Word w = set[i];
        int count = std::popcount(w);
        if (rank < count) {
            for (; rank > 0; --rank) w &= w - 1;
            return 64 * i + std::countr_zero(w);
        }
        rank -= count;
    }
    throw std::runtime_error("selection outside a set");
}

bool includes(const Bits& all, const Bits& part) {
    for (int i = 0; i < int(all.size()); ++i) if (part[i] & ~all[i]) return false;
    return true;
}

int intersection_size(const Bits& a, const Bits& b) {
    int count = 0;
    for (int i = 0; i < int(a.size()); ++i) count += std::popcount(a[i] & b[i]);
    return count;
}

struct Roster {
    int n = 0, words = 0, cache_limit = 0;
    bool reverse;
    bool conditional_neighborhoods;
    std::vector<std::vector<int>> blocks, parents;
    std::vector<std::vector<int>> parents_by_size;
    std::vector<Bits> block_masks;
    std::vector<int> anchors;
    std::unordered_map<int, Bits> cached;
    std::deque<int> cache_order;
    Bits missed;
    std::vector<int> remaining_words;

    Roster(const std::string& path, int anchor_count, bool reverse_order)
        : reverse(reverse_order), conditional_neighborhoods(std::getenv("HUB_SPARSE_NEIGHBORHOODS") != nullptr) {
        std::ifstream in(path);
        int m;
        require(bool(in >> n >> m) && n >= 0 && m >= 0, "invalid input header");
        words = (n + 63) / 64;
        cache_limit = std::clamp((32 * 1024 * 1024) / std::max(8, 8 * words), 64, 12000);
        parents.resize(n);
        blocks.resize(m);
        block_masks.resize(m);
        std::string line;
        std::getline(in, line);
        for (int b = 0; b < m; ++b) {
            require(bool(std::getline(in, line)), "short block list");
            std::istringstream stream(line);
            for (int u; stream >> u;) {
                require(u >= 0 && u < n, "invalid block member");
                blocks[b].push_back(u);
            }
            require(stream.eof(), "malformed block");
            auto& row = blocks[b];
            std::sort(row.begin(), row.end());
            require(std::adjacent_find(row.begin(), row.end()) == row.end(), "duplicate block member");
            for (int u : row) parents[u].push_back(b);
        }
        require(!(in >> line), "extra block data");
        anchors.resize(m);
        std::iota(anchors.begin(), anchors.end(), 0);
        if (reverse) std::reverse(anchors.begin(), anchors.end());
        std::stable_sort(anchors.begin(), anchors.end(), [&](int a, int b) {
            return blocks[a].size() > blocks[b].size();
        });
        anchors.resize(std::min(m, anchor_count));
        // Large blocks are bitsets. The sparse ones retain their member lists.
        if (conditional_neighborhoods)
            require(std::size_t(m) * words * sizeof(Word) < 256 * 1024 * 1024,
                    "conditional neighborhood backend exceeded its mask budget");
        for (int b = 0; b < m; ++b)
            if (conditional_neighborhoods || int(blocks[b].size()) >= std::max(64, words / 4) ||
                std::find(anchors.begin(), anchors.end(), b) != anchors.end()) {
                block_masks[b].resize(words);
                for (int u : blocks[b]) insert(block_masks[b], u);
            }
        if (conditional_neighborhoods) {
            parents_by_size = parents;
            for (auto& members : parents_by_size)
                std::stable_sort(members.begin(), members.end(), [&](int a, int b) {
                    return blocks[a].size() > blocks[b].size();
                });
        }
    }

    Bits all() const {
        Bits result(words, ~Word{0});
        if (n % 64) result.back() = (Word{1} << (n % 64)) - 1;
        return result;
    }

    bool meets(int u, int v) const {
        if (u == v) return false;
        const auto& a = parents[u];
        const auto& b = parents[v];
        std::size_t i = 0, j = 0;
        while (i < a.size() && j < b.size()) {
            if (a[i] == b[j]) return true;
            if (a[i] < b[j]) ++i;
            else ++j;
        }
        return false;
    }

    const Bits& neighbors(int u) {
        if (auto seen = cached.find(u); seen != cached.end()) return seen->second;
        Bits result(words);
        for (int b : parents[u]) {
            if (block_masks[b].empty()) {
                for (int v : blocks[b]) insert(result, v);
            } else {
                const auto& mask = block_masks[b];
                for (int i = 0; i < words; ++i) result[i] |= mask[i];
            }
        }
        erase(result, u);
        if (int(cached.size()) >= cache_limit) {
            cached.erase(cache_order.front());
            cache_order.pop_front();
        }
        cache_order.push_back(u);
        return cached.emplace(u, std::move(result)).first->second;
    }

    void find_missed(int u, const Bits& target) {
        // Subtract exactly the same union as neighbors(u), but skip words
        // as soon as every target name in them has been met.
        missed = target;
        erase(missed, u);
        remaining_words.clear();
        for (int i = 0; i < words; ++i) if (missed[i]) remaining_words.push_back(i);
        for (int b : parents_by_size[u]) {
            std::size_t survivors = 0;
            for (int i : remaining_words)
                if (missed[i] &= ~block_masks[b][i]) remaining_words[survivors++] = i;
            remaining_words.resize(survivors);
            if (!survivors) break;
        }
    }

    bool meets_all(int u, const Bits& target) {
        if (conditional_neighborhoods) {
            find_missed(u, target);
            return remaining_words.empty();
        }
        const auto& meeting = neighbors(u);
        for (int j = 0; j < words; ++j) {
            Word bad = target[j] & ~meeting[j];
            if (j == u / 64) bad &= ~(Word{1} << (u % 64));
            if (bad) return false;
        }
        return true;
    }

    int restrict_to_neighbors(int u, Bits& remaining) {
        if (conditional_neighborhoods) {
            find_missed(u, remaining);
            erase(remaining, u);
            for (int i : remaining_words) remaining[i] &= ~missed[i];
            return size(remaining);
        }
        const auto& next = neighbors(u);
        int new_count = 0;
        for (int i = 0; i < words; ++i) {
            remaining[i] &= next[i];
            new_count += std::popcount(remaining[i]);
        }
        return new_count;
    }

    int best_anchor(const Bits& remaining) const {
        int best = -1, count = 0;
        for (int anchor : anchors) {
            int candidate = intersection_size(remaining, block_masks[anchor]);
            if (candidate > count) best = anchor, count = candidate;
        }
        return best;
    }
};

int uniform(std::mt19937_64& rng, int n) {
    require(n > 0, "empty random choice");
    return std::uniform_int_distribution<int>(0, n - 1)(rng);
}

std::vector<Factor> diagnostic_partners(Roster& roster, const std::string& path) {
    std::vector<Factor> pairs;
    if (path != "-") {
        std::ifstream in(path);
        require(bool(in), "cannot read the partner reference");
        for (int u, v; in >> u >> v;) pairs.emplace_back(u, v);
        require(in.eof(), "malformed partner reference");
    } else {
        Bits remaining = roster.all();
        for (int k = 0; k < 24; ++k) {
            int count = size(remaining);
            if (count < 2) break;
            int anchor = roster.best_anchor(remaining);
            if (anchor >= 0 && includes(roster.block_masks[anchor], remaining)) break;
            bool found = false;
            int attempts = std::min(count, 64);
            for (int r = 0; r < attempts && !found; ++r) {
                int u = select(remaining, std::int64_t(r) * count / attempts);
                const auto& nu = roster.neighbors(u);
                for (int i = 0; i < roster.words; ++i) {
                    Word missing = remaining[i] & ~nu[i];
                    if (i == u / 64) missing &= ~(Word{1} << (u % 64));
                    if (!missing) continue;
                    int v = 64 * i + std::countr_zero(missing);
                    pairs.emplace_back(u, v);
                    for (int j = 0; j < roster.words; ++j) remaining[j] &= nu[j];
                    const auto& nv = roster.neighbors(v);
                    for (int j = 0; j < roster.words; ++j) remaining[j] &= nv[j];
                    found = true;
                    break;
                }
            }
            if (!found) break;
        }
    }
    for (int i = 0; i < int(pairs.size()); ++i) {
        auto [u,v] = pairs[i];
        require(0 <= u && u < roster.n && 0 <= v && v < roster.n && u != v && !roster.meets(u,v),
                "invalid partner pair");
        for (int j = 0; j < i; ++j) {
            auto [x,y] = pairs[j];
            require(roster.meets(u,x) && roster.meets(u,y) && roster.meets(v,x) && roster.meets(v,y),
                    "invalid cross-pair candidacy");
        }
    }
    return pairs;
}

struct Suffix {
    Bits sample;
    int count = 0;
};

Suffix exact_suffix(Roster& roster, const Bits& inside, const Bits& outside, std::mt19937_64& rng) {
    std::vector<int> names;
    each(outside, [&](int v) { names.push_back(v); });
    if (roster.reverse) std::reverse(names.begin(), names.end());
    std::vector<Bits> touch;
    std::vector<Word> compatibility(names.size());
    for (int i = 0; i < int(names.size()); ++i) {
        touch.push_back(roster.neighbors(names[i]));
        for (int j = 0; j < int(names.size()); ++j)
            if (has(touch.back(), names[j])) compatibility[i] |= Word{1} << j;
    }
    Suffix result{Bits(roster.words), 0};
    auto visit = [&](auto&& self, const Bits& emb, Word chosen, Word possible, int first) -> void {
        bool extends = false;
        for (Word mask = possible; mask; mask &= mask - 1)
            if (includes(touch[std::countr_zero(mask)], emb)) {
                extends = true;
                break;
            }
        if (!extends) {
            ++result.count;
            if (!uniform(rng, result.count)) {
                result.sample = emb;
                for (Word mask = chosen; mask; mask &= mask - 1)
                    insert(result.sample, names[std::countr_zero(mask)]);
            }
        }
        for (int i = first; i < int(names.size()); ++i) if (possible >> i & 1) {
            Bits bound = emb;
            for (int j = 0; j < roster.words; ++j) bound[j] &= touch[i][j];
            self(self, bound, chosen | (Word{1} << i), possible & compatibility[i], i + 1);
        }
    };
    visit(visit, inside, 0, (Word{1} << names.size()) - 1, 0);
    require(result.count > 0, "suffix has no maximal completion");
    return result;
}

bool maximal_inside(Roster& roster, const Bits& inside, const Bits& outside) {
    if (!size(inside)) return !size(outside);
    std::vector<int> probes;
    int total = size(inside), count = std::min(total, 12);
    for (int i = 0; i < count; ++i) probes.push_back(select(inside, std::int64_t(i) * total / count));
    for (int i = 0; i < roster.words; ++i)
        for (Word w = outside[i]; w; w &= w - 1) {
            int v = 64 * i + std::countr_zero(w);
            if (std::all_of(probes.begin(), probes.end(), [&](int x) { return roster.meets(v,x); }) &&
                roster.meets_all(v, inside)) return false;
        }
    return true;
}

bool is_clique(Roster& roster, const Bits& remaining, const Bits& outside) {
    // The part inside the anchor already meets throughout.
    for (int i = 0; i < roster.words; ++i)
        for (Word w = outside[i]; w; w &= w - 1) {
            int v = 64 * i + std::countr_zero(w);
            if (!roster.meets_all(v, remaining)) return false;
        }
    return true;
}

struct Choice {
    int anchor_slot, selected, branches;
};

struct Draw {
    bool valid = true;
    Bits group;
    std::vector<Factor> factors;
    std::vector<int> inverse_proposal;
    int greedy_steps = 0, exact_suffix_count = 0;
};

Draw sample(Roster& roster, int exact_threshold, int slots, std::mt19937_64& rng) {
    Bits remaining = roster.all();
    Bits inside(roster.words), outside(roster.words);
    std::vector<Choice> choices;
    Draw result{roster.n > 0, Bits(roster.words), {}, {}, 0, 0};
    int remaining_count = roster.n, no_conflict_losses = 0;
    while (remaining_count) {
        int anchor = roster.best_anchor(remaining);
        int anchor_slot = -1;
        if (anchor >= 0)
            anchor_slot = std::find(roster.anchors.begin(), roster.anchors.end(), anchor) - roster.anchors.begin();
        for (int i = 0; i < roster.words; ++i) {
            inside[i] = anchor >= 0 ? remaining[i] & roster.block_masks[anchor][i] : 0;
            outside[i] = remaining[i] & ~inside[i];
        }
        const int available = size(outside);
        if (!available || no_conflict_losses == 8) {
            if (is_clique(roster, remaining, outside)) {
                result.group = remaining;
                result.exact_suffix_count = 1;
                break;
            }
            no_conflict_losses = 0;
        }
        if (available <= exact_threshold) {
            Suffix suffix = exact_suffix(roster, inside, outside, rng);
            result.group = std::move(suffix.sample);
            result.exact_suffix_count = suffix.count;
            if (suffix.count > 1) {
                result.factors.emplace_back(suffix.count, 1);
                result.inverse_proposal.push_back(suffix.count);
            }
            break;
        }

        // The finish option is included even if it will be rejected. It has
        // zero contribution in that case and keeps the proposal unconditional.
        // Each outside name has 'slots' tickets. The one finish ticket keeps
        // positive support without frequent rejection near the end of a path.
        const int branch_count = slots * available + (anchor >= 0);
        const int selected = uniform(rng, branch_count);
        result.inverse_proposal.push_back(branch_count);
        if (selected == slots * available) {
            if (!maximal_inside(roster, inside, outside)) {
                result.valid = false;
                result.greedy_steps = choices.size();
                return result;
            }
            result.group = inside;
            result.factors.emplace_back(branch_count, 1);
            break;
        }
        int outside_rank = selected / slots;
        int u = select(outside, roster.reverse ? available - 1 - outside_rank : outside_rank);
        choices.push_back({anchor_slot, u, branch_count});
        const int new_count = roster.restrict_to_neighbors(u, remaining);
        no_conflict_losses = new_count + 1 == remaining_count ? no_conflict_losses + 1 : 0;
        remaining_count = new_count;
    }
    int total = size(result.group);
    std::vector<int> in_anchor;
    for (int b : roster.anchors) in_anchor.push_back(intersection_size(result.group, roster.block_masks[b]));
    for (auto it = choices.rbegin(); it != choices.rend(); ++it) {
        insert(result.group, it->selected);
        ++total;
        for (int j = 0; j < int(in_anchor.size()); ++j)
            in_anchor[j] += has(roster.block_masks[roster.anchors[j]], it->selected);
        int matches = slots * (total - (it->anchor_slot >= 0 ? in_anchor[it->anchor_slot] : 0));
        require(0 < matches && matches <= it->branches, "bad conditional path denominator");
        if (matches != it->branches) result.factors.emplace_back(it->branches, matches);
    }
    result.greedy_steps = choices.size();
    return result;
}

int block_cover(Roster& roster, const Bits& group_mask, const std::vector<int>& group,
                const std::vector<int>& coverage, int biggest) {
    if (!biggest) return 0;
    if (biggest == int(group.size())) return 1;
    for (int a = 0; a < int(coverage.size()); ++a) {
        if (2 * coverage[a] < int(group.size())) continue;
        auto in = [&](int b, int v) {
            if (!roster.block_masks[b].empty()) return has(roster.block_masks[b], v);
            return std::binary_search(roster.blocks[b].begin(), roster.blocks[b].end(), v);
        };
        int witness = *std::find_if(group.begin(), group.end(), [&](int v) { return !in(a,v); });
        for (int b : roster.parents[witness]) {
            if (coverage[a] + coverage[b] < int(group.size())) continue;
            if (roster.block_masks[a].empty() || roster.block_masks[b].empty()) {
                if (std::all_of(group.begin(), group.end(), [&](int v) { return in(a,v) || in(b,v); })) return 2;
            } else {
                bool union_covers = true;
                for (int i = 0; i < roster.words && union_covers; ++i)
                    union_covers = !(group_mask[i] & ~(roster.block_masks[a][i] | roster.block_masks[b][i]));
                if (union_covers) return 2;
            }
        }
    }
    return 3;
}

void print_draw(Roster& roster, const std::vector<Factor>& partners, const Draw& draw,
                int index, int& remaining_witnesses, bool& first_maximal) {
    std::cout << "{\"sample\":" << index << ",\"greedy_choices\":" << draw.greedy_steps
              << ",\"inverse_path_probability_progressions\":[";
    for (int i = 0; i < int(draw.inverse_proposal.size());) {
        const int first = draw.inverse_proposal[i];
        const int delta = i + 1 < int(draw.inverse_proposal.size()) ? draw.inverse_proposal[i + 1] - first : 0;
        int stop = i + 1;
        while (stop < int(draw.inverse_proposal.size()) &&
               draw.inverse_proposal[stop] - draw.inverse_proposal[stop - 1] == delta) ++stop;
        if (i) std::cout << ',';
        std::cout << '[' << first << ',' << delta << ',' << stop - i << ']';
        i = stop;
    }
    std::cout << ']';
    if (!draw.valid) {
        std::cout << ",\"maximal\":false,\"zero_reason\":\""
                  << (roster.n ? "finish extendible" : "empty stage") << "\"}\n";
        return;
    }
    std::vector<int> group, coverage(roster.blocks.size());
    each(draw.group, [&](int u) {
        group.push_back(u);
        for (int b : roster.parents[u]) ++coverage[b];
    });
    const int biggest = coverage.empty() ? 0 : *std::max_element(coverage.begin(), coverage.end());
    const int met = std::count_if(coverage.begin(), coverage.end(), [](int c) { return c > 0; });
    const int cover = block_cover(roster, draw.group, group, coverage, biggest);
    Word fingerprint = 14695981039346656037ULL;
    for (Word w : draw.group) fingerprint = (fingerprint ^ w) * 1099511628211ULL;
    int hits = 0;
    for (auto [u,v] : partners) {
        require(!(has(draw.group,u) && has(draw.group,v)), "maximal set contains both partners");
        hits += has(draw.group,u) || has(draw.group,v);
    }
    const bool held = biggest == int(group.size());
    const bool group_birth = group.size() >= 3 && !held;
    long double log_weight = 0;
    std::cout << ",\"maximal\":true,\"held\":" << (held ? "true" : "false")
              << ",\"large_join\":" << (group_birth ? "true" : "false")
              << ",\"size\":" << group.size() << ",\"partner_pairs_met\":" << hits
              << ",\"blocks_met\":" << met << ",\"largest_block_intersection\":" << biggest
              << ",\"block_cover_1_2_or_at_least_3\":" << cover
              << ",\"exact_suffix_count\":" << draw.exact_suffix_count
              << ",\"fingerprint\":\"" << fingerprint << "\",\"weight_progressions\":[";
    for (int i = 0; i < int(draw.factors.size());) {
        auto [a,b] = draw.factors[i];
        int da = 0, db = 0, stop = i + 1;
        if (stop < int(draw.factors.size())) {
            da = draw.factors[stop].first - a;
            db = draw.factors[stop].second - b;
        }
        while (stop < int(draw.factors.size()) &&
               draw.factors[stop].first - draw.factors[stop - 1].first == da &&
               draw.factors[stop].second - draw.factors[stop - 1].second == db) ++stop;
        if (i) std::cout << ',';
        std::cout << '[' << a << ',' << da << ',' << b << ',' << db << ',' << stop - i << ']';
        i = stop;
    }
    for (auto [a, b] : draw.factors)
        log_weight += std::log10(static_cast<long double>(a) / b);
    std::cout << "],\"log10_weight\":" << std::setprecision(18) << log_weight;
    const bool print_group = first_maximal || (group_birth && remaining_witnesses > 0);
    if (print_group) {
        std::cout << ",\"literal_members_le_hex\":\"";
        for (Word w : draw.group) std::cout << std::hex << std::setw(16) << std::setfill('0') << w;
        std::cout << std::dec << std::setfill(' ') << '"';
    }
    first_maximal = false;
    if (group_birth && remaining_witnesses > 0) --remaining_witnesses;
    std::cout << "}\n";
}

int main(int argc, char** argv) {
    try {
        require(argc == 11, "hub_greedy ROSTER PARTNERS/- ANCHORS EXACT_SUFFIX SEED DRAWS REPLICATES REVERSE WITNESSES OUTSIDE_SLOTS");
        std::ios::sync_with_stdio(false);
        int anchors = std::stoi(argv[3]), exact = std::stoi(argv[4]), draws = std::stoi(argv[6]);
        int replicates = std::stoi(argv[7]), witnesses = std::stoi(argv[9]);
        Word seed = std::stoull(argv[5]);
        bool reverse = std::stoi(argv[8]);
        int slots = std::stoi(argv[10]);
        require(anchors >= 0 && exact >= 0 && exact <= 16 && draws > 0 && replicates > 0 && witnesses >= 0 &&
                slots >= 1 && slots <= 128,
                "invalid run settings");
        Roster roster(argv[1], anchors, reverse);
        require(roster.n <= 10'000'000, "roster exceeds exact integer ticket bound");
        auto partners = diagnostic_partners(roster, argv[2]);
        std::cout << "{\"names\":" << roster.n << ",\"blocks\":" << roster.blocks.size()
                  << ",\"partner_reference\":[";
        for (int i = 0; i < int(partners.size()); ++i) {
            if (i) std::cout << ',';
            std::cout << '[' << partners[i].first << ',' << partners[i].second << ']';
        }
        std::cout << "]}\n";
        int remaining_witnesses = witnesses;
        bool first_maximal = witnesses > 0;
        for (int replicate = 0; replicate < replicates; ++replicate) {
            std::mt19937_64 rng(seed + replicate);
            std::cout << "{\"replicate\":" << replicate << ",\"seed\":" << seed + replicate << "}\n";
            for (int i = 0; i < draws; ++i) {
                Draw group = sample(roster, exact, slots, rng);
                print_draw(roster, partners, group, i, remaining_witnesses, first_maximal);
            }
            std::cout << std::flush;
        }
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
