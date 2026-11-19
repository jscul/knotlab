// Enumerate weighted immediate predecessors under a bound on current width.
#include <numeric>

#define main inherited_reach_main
#include "../../GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.cpp"
#undef main

namespace repeat_bound {

using Edges = std::vector<std::pair<int,int>>;
using Counts = std::array<std::uint64_t, 12>;
constexpr std::array names{
    "histories", "at_most_one_movable", "offshoots_next", "pooled_group_carries_span",
    "exact_group_carries_span", "successor_extends", "failed", "unresolved",
    "exact_generators", "noncarrying_generators", "successor_rooted", "fresh_searches",
};

struct Span {
    std::array<Wide,128> basis{};

    static int highest(Wide word) {
        const std::uint64_t upper = word >> 64;
        return upper ? 63 + std::bit_width(upper) : std::bit_width(std::uint64_t(word))-1;
    }

    Wide reduce(Wide word) const {
        while (word) {
            const auto high = highest(word);
            if (!basis[high]) break;
            word ^= basis[high];
        }
        return word;
    }

    explicit Span(const Rows& rows) {
        for (const auto& row : rows) {
            Wide word = 0;
            for (int x : row) word |= wide(x);
            word = reduce(word);
            if (word) basis[highest(word)] = word;
        }
    }

    bool carries(const Rows& rows, const std::vector<int>& image) const {
        for (const auto& row : rows) {
            Wide word = 0;
            for (int x : row) word |= wide(x < int(image.size()) ? image[x] : x);
            if (reduce(word)) return false;
        }
        return true;
    }
};

int endpoint_classes(const Incidence& inc) {
    int twice = 0;
    for (Mask adjacent : inc.ordinary) twice += std::popcount(adjacent);
    return twice/2 + std::popcount(inc.live);
}

void score(const Rows& source, const Rows& current, int movable, Counts& count) {
    ++count[0];
    if (movable < 2) {
        ++count[1];
        return;
    }
    const Incidence inc(current);
    const auto groups = Rule(inc.ordinary).groups(inc.live);
    if (groups.empty()) {
        ++count[2];
        return;
    }
    if (inc.own.size() > 128 || movable >= 64) {
        ++count[7];
        return;
    }
    std::vector<int> requested(movable);
    std::iota(requested.begin(), requested.end(), 0);
    const Span codes(current);
    {
        const Table pooled(current,inc,requested,Cutoff);
        if (Symmetries(pooled,movable).grade([&](const auto& image) { return codes.carries(current,image); })) {
            ++count[3];
            return;
        }
    }
    const Table exact(current,inc,requested,Inf);
    std::vector<std::vector<int>> noncarrying;
    Symmetries(exact,movable).grade([&](const auto& image) {
        ++count[8];
        if (!codes.carries(current,image)) noncarrying.push_back(image);
        return true;
    });
    count[9] += noncarrying.size();
    if (noncarrying.empty()) {
        ++count[4];
        return;
    }
    const Rows next = grow(current,inc,groups);
    require(!next.empty(), "a reached stage supplied less than its lookahead demands");
    const Incidence later(next);
    const int augmented = next.size() + bool(later.live);
    if (augmented > 60 || endpoint_classes(later) > 128) {
        ++count[7];
        return;
    }
    bool rooted = augmented > MaxMeasuredVertices;
    count[10] += rooted;
    const Table partial(next,later,requested,Inf,rooted);
    std::optional<Table> full;
    for (const auto& image : noncarrying) {
        auto result = extends(partial, image, inc.own.size(),false);
        if (!result.possible && result.first < 0) {
            ++count[11];
            if (!full) full.emplace(next,later,std::vector<int>{},Inf,rooted);
            result = extends(*full,image,inc.own.size());
        }
        if (!result.possible) {
            ++count[6];
            std::cout << "{\"failure\":";
            witness_json(Witness{source,current,next,image,result});
            std::cout << "}\n" << std::flush;
            return;
        }
    }
    ++count[5];
}

Rows weighted_start(int n, const Edges& edges, const std::vector<int>& multiplicity,
                    const std::vector<int>& loose) {
    Rows rows(n);
    int name = 0;
    for (int i = 0; i < int(edges.size()); ++i) {
        auto [a,b] = edges[i];
        for (int x = 0; x < multiplicity[i]; ++x) {
            rows[a].push_back(name);
            rows[b].push_back(name++);
        }
    }
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < loose[i]; ++j) rows[i].push_back(name++);
    return rows;
}

struct Search {
    int cap_junctions, cap_width, cap_multiplicity;
    std::map<std::pair<int,int>,Counts> totals;
    std::uint64_t simple_supports = 0;
    std::uint64_t live_subsets = 0;
    std::uint64_t loose_shapes = 0;

    void graph(const Adj& neighbors) {
        ++simple_supports;
        const int n = neighbors.size();
        const int max_births = cap_junctions - n;
        int edge_count = 0;
        Edges edges;
        std::vector<int> simple_degree(n), last_seen(n,-1);
        for (int a = 0; a < n; ++a) for (int b = a+1; b < n; ++b) if (neighbors[a] & bit(b)) {
            last_seen[a] = last_seen[b] = edge_count++;
            edges.push_back({a,b});
            ++simple_degree[a]; ++simple_degree[b];
        }
        const Mask all = bit(n+1)-1;
        const Rule transition(neighbors);
        for (Mask live = 1; live < bit(n); ++live) {
            Adj wired = neighbors;
            wired.push_back(live);
            for (Mask todo = live; todo;) wired[take(todo)] |= bit(n);
            bool eligible = true;
            for (int j = 0; j < n && eligible; ++j) eligible = connected(wired,all ^ bit(j));
            if (!eligible) continue;
            ++live_subsets;
            const auto groups = transition.groups(live,max_births);
            const int group_count = groups.size();
            if (group_count > max_births) continue;
            std::vector<int> loose = demands(groups,n);
            const auto active = indices(live);
            int parents = 0, forced_unary = 0;
            for (int x : loose) parents += x;
            for (int u : active) if (!loose[u]) loose[u] = 1,++forced_unary;
            if (group_count + forced_unary > max_births) continue;

            auto grade_shape = [&](int births, int inputs) {
                ++loose_shapes;
                std::vector<int> degree = simple_degree;
                int deficit = 0;
                for (int j = 0; j < n; ++j) {
                    degree[j] += loose[j];
                    if (degree[j] < 3 && last_seen[j] < 0) return;
                    deficit += std::max(0,3-degree[j]);
                }
                if (cap_width && edge_count+inputs+births+(deficit+1)/2 > cap_width) return;
                std::vector<int> multiplicity(edge_count,1);
                const Rows probe = weighted_start(n,edges,multiplicity,loose);
                const Rows grown = grow(probe,Incidence(probe),groups);
                require(int(grown.size()) == n+births, "loose allocation and growth disagree");
                const int base_width = Incidence(grown).own.size();
                if (cap_width && base_width+(deficit+1)/2 > cap_width) return;

                auto weights = [&](auto&& again,int i,int left,int spent,int missing) -> void {
                    if (missing > 2*left) return;
                    if (i == edge_count) {
                        if (missing) return;
                        const Rows start = weighted_start(n,edges,multiplicity,loose);
                        const Rows current = grow(start,Incidence(start),groups);
                        require(int(current.size()) == n+births, "weighted growth changed parent groups");
                        require(int(Incidence(current).own.size()) == base_width+spent, "unexpected weighted width");
                        score(start,current,edge_count+spent,totals[{n+births,base_width+spent}]);
                        return;
                    }
                    const auto [a,b] = edges[i];
                    const int bound = cap_multiplicity ? std::min(left,cap_multiplicity-1) : left;
                    int at_least = 0;
                    for (int u : {a,b}) if (last_seen[u] == i) at_least = std::max(at_least,3-degree[u]);
                    for (int extra = at_least; extra <= bound; ++extra) {
                        const int improvement = std::min(extra,std::max(0,3-degree[a]))
                                              + std::min(extra,std::max(0,3-degree[b]));
                        degree[a] += extra; degree[b] += extra;
                        multiplicity[i] = 1+extra;
                        again(again,i+1,left-extra,spent+extra,missing-improvement);
                        degree[a] -= extra; degree[b] -= extra;
                    }
                };
                const int extra_budget = cap_width ? cap_width-base_width : edge_count*(cap_multiplicity-1);
                weights(weights,0,extra_budget,0,deficit);
            };
            auto allocate = [&](auto&& again,int i,int spare,int births,int inputs) -> void {
                const int u = active[i];
                if (i+1 == int(active.size())) {
                    loose[u] += spare;
                    grade_shape(births,inputs);
                    loose[u] -= spare;
                    return;
                }
                for (int x = 0; x <= spare; ++x) {
                    loose[u] += x;
                    again(again,i+1,spare-x,births,inputs);
                    loose[u] -= x;
                }
            };
            for (int births = std::max(3,group_count+forced_unary); births <= max_births; ++births) {
                int inputs = parents + births-group_count;
                if (cap_width && edge_count+inputs+births > cap_width) break;
                if (cap_width && 3*n+inputs+2*births > 2*cap_width) break;
                allocate(allocate,0,births-group_count-forced_unary,births,inputs);
            }
        }
    }
};

} // namespace repeat_bound

int main(int argc,char** argv) {
    try {
        require(argc == 5, "usage: low_repeat PREDECESSOR JUNCTION_CAP WIDTH_CAP MULTIPLICITY_CAP_OR_ZERO");
        const int n = std::stoi(argv[1]);
        repeat_bound::Search search{std::stoi(argv[2]),std::stoi(argv[3]),std::stoi(argv[4])};
        require(n >= 1 && n+3 <= search.cap_junctions && search.cap_width <= 40
                && (search.cap_width > 0 || search.cap_multiplicity > 0), "unsupported population bound");
        std::string line;
        while (std::getline(std::cin,line)) if (!line.empty()) search.graph(decode(line,n));
        std::cout << "{\"predecessor\":" << n << ",\"supports\":" << search.simple_supports
                  << ",\"live_subsets\":" << search.live_subsets << ",\"loose_shapes\":" << search.loose_shapes
                  << ",\"tiers\":[";
        bool first = true;
        for (const auto& [key,counts] : search.totals) {
            if (!first) std::cout << ',';
            first = false;
            std::cout << "{\"junctions\":" << key.first << ",\"width\":" << key.second;
            for (int i = 0; i < int(counts.size()); ++i)
                std::cout << ",\"" << repeat_bound::names[i] << "\":" << counts[i];
            std::cout << '}';
        }
        std::cout << "]}\n";
    } catch (const std::exception& problem) {
        std::cerr << problem.what() << '\n';
        return 1;
    }
}
