// Decode integer ranks directly into the seeded prefix. Insertion, resampling,
// observation and integer normalization come unchanged from the first panel.
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace warm {
#include "anneal.cpp"
}
using namespace warm;

namespace {
struct RankNode {
    Word count;
    int kind, begin, size;
};

struct SiteCondition {
    int id, side;
    std::vector<Word> trigger;
};

struct RankedCore {
    int physical, width, root;
    Word count;
    std::vector<RankNode> nodes;
    std::vector<int> children, sites;
    std::vector<SiteCondition> conditions;

    explicit RankedCore(const std::string& filename) {
        std::ifstream in(filename);
        std::string magic, line;
        int n, h;
        require(bool(in >> magic >> physical >> width >> n >> h >> root >> count) && magic == "DNNF1" &&
                physical > 0 && width > 0 && h > 0 && root < n && count > 0, "invalid exact-core header");
        int coordinate;
        for (int i = 0; i < width; ++i) require(bool(in >> coordinate), "short coordinate list");
        std::getline(in, line);
        nodes.reserve(n);
        for (int i = 0; i < n; ++i) {
            require(bool(std::getline(in, line)), "short compiled-node list");
            std::istringstream data(line);
            RankNode node{};
            require(bool(data >> node.count >> node.kind), "invalid compiled node");
            node.begin = children.size();
            int child;
            while (data >> child) {
                require(child >= 0 && child < i, "non-topological compiled graph");
                children.push_back(child);
            }
            node.size = int(children.size()) - node.begin;
            require(data.eof() && (node.kind == -1 || (node.kind >= 0 && node.kind < width && node.size == 2) ||
                                   (i <= 1 && node.kind == -2 - i && !node.size)), "bad compiled decision");
            nodes.push_back(node);
        }
        require(nodes[root].count == count, "root count mismatch");
        for (int i = 0; i < h; ++i) {
            SiteCondition condition{};
            require(bool(in >> condition.id >> condition.side) && condition.id >= 0 && condition.id < physical &&
                    (condition.side == 0 || condition.side == 1), "invalid physical signature");
            condition.trigger.resize((width + 63) / 64);
            for (Word& w : condition.trigger) require(bool(in >> w), "short physical signature");
            sites.push_back(condition.id);
            conditions.push_back(std::move(condition));
        }
        require(!(in >> magic), "trailing compiled data");
    }

    void select(int node_id, Word rank, std::vector<Word>& flags) const {
        const auto& node = nodes[node_id];
        require(rank < node.count, "rank outside decision-node count");
        if (node.kind == -3) return;
        if (node.kind >= 0) {
            int lo = children[node.begin], hi = children[node.begin + 1];
            if (rank < nodes[lo].count) select(lo, rank, flags);
            else {
                flags[node.kind / 64] |= Word{1} << (node.kind % 64);
                select(hi, rank - nodes[lo].count, flags);
            }
        } else {
            require(node.kind == -1, "rank reached false node");
            for (int i = 0; i < node.size; ++i) {
                int child = children[node.begin + i];
                Word radix = nodes[child].count;
                require(radix != 0, "rank reached an empty product factor");
                select(child, rank % radix, flags);
                rank /= radix;
            }
            require(!rank, "invalid mixed-radix rank");
        }
    }
};

struct DirectGroups {
    const RankedCore& core;
    int words;
    std::vector<Word> rejected, flags, group;

    DirectGroups(const RankedCore& d, const Prepared& prepared) : core(d), words((prepared.prefix + 63) / 64),
         rejected(std::size_t(d.width) * 2 * words), flags((d.width + 63) / 64), group(words) {
        for (const auto& site : d.conditions) {
            int position = prepared.position[site.id];
            for (int w = 0; w < int(site.trigger.size()); ++w) {
                Word mask = site.trigger[w];
                while (mask) {
                    int i = 64 * w + std::countr_zero(mask);
                    require(i < d.width, "invalid final signature word");
                    rejected[(std::size_t(2 * i + site.side) * words) + position / 64] |= Word{1} << (position % 64);
                    mask &= mask - 1;
                }
            }
        }
    }

    Clique decode(Word rank, int prefix) {
        std::fill(flags.begin(), flags.end(), 0);
        core.select(core.root, rank, flags);
        for (int w = 0; w < words; ++w) group[w] = before(w, prefix);
        // Left membership asks for every flagged feature to be on. Right
        // membership asks for every flagged feature to be off.
        for (int i = 0; i < core.width; ++i) {
            const int bit = (flags[i / 64] >> (i % 64)) & 1;
            const Word* bad = rejected.data() + std::size_t(2 * i + bit) * words;
            for (int w = 0; w < words; ++w) group[w] &= ~bad[w];
        }
        Clique members;
        for (int w = 0; w < words; ++w) {
            Word mask = group[w];
            while (mask) {
                members.push_back(w * 64 + std::countr_zero(mask));
                mask &= mask - 1;
            }
        }
        return members;
    }
};
}

int main(int argc, char** argv) {
    try {
        require(argc == 8, "anneal_native ROSTER CORE ORDER ORDER_SEED POPULATION ISLAND_SEED ISLANDS < RANKS");
        const auto roster = read(argv[1]);
        const RankedCore core(argv[2]);
        require(core.physical == roster.n, "different physical universes");
        const auto data = seeded_order(roster, core.sites, argv[3], std::stoull(argv[4]));
        DirectGroups sampler(core, data);
        auto observer = marks(data, roster);
        const char* profiled = std::getenv("ANNEAL_PROFILE_ISLANDS");
        const int cap = profiled ? std::stoi(profiled) : 0;
        int population = std::stoi(argv[5]), islands = std::stoi(argv[7]);
        Word seed = std::stoull(argv[6]);
        const bool check_ranks = std::getenv("ANNEAL_PRINT_INITIAL") != nullptr;
        require(population > 0 && population <= 1000000 && islands > 0, "invalid population");
        std::cout << "{\"literal\":" << roster.n << ",\"classes\":" << data.graph.size
                  << ",\"seeded_prefix_classes\":" << data.prefix << ",\"induced_groups\":" << core.count
                  << ",\"population\":" << population << "}\n" << std::flush;
        for (int r = 0; r < islands; ++r) {
            SeedPopulation initial;
            initial.prefix = data.prefix;
            initial.numerator = std::to_string(core.count);
            initial.samples.reserve(population);
            for (int i = 0; i < population; ++i) {
                Word rank;
                require(bool(std::cin >> rank), "short rank stream");
                initial.samples.push_back(sampler.decode(rank, data.prefix));
                if (check_ranks) {
                    validate_clique(initial.samples.back(), data.graph, data.prefix);
                    std::vector<int> physical;
                    for (int u : core.sites) if (contains(initial.samples.back(), data.position[u])) physical.push_back(u);
                    std::sort(physical.begin(), physical.end());
                    std::cout << rank;
                    for (int u : physical) std::cout << ' ' << u;
                    std::cout << '\n';
                }
            }
            if (check_ranks) continue;
            if (r >= cap) observer.draws = 0;
            estimate(data.graph, population, 0, 0, 4, 0, seed + r, data.graph.size, &initial, &observer);
        }
        std::string extra;
        require(!(std::cin >> extra), "trailing rank stream");
    } catch (const std::exception& issue) {
        std::cerr << issue.what() << '\n';
        return 1;
    }
    return 0;
}
