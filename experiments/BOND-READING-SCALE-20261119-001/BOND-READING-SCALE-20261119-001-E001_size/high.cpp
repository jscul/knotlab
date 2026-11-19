// Exact folded minimax and connected pair cuts for higher-order shield hosts.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

using Counts = std::array<int, 3>;
using Weights = std::array<int, 7>;  // test hub, test v, each shield hub, each branch, unit
using Size = std::array<int, 2>;
constexpr int Infinity = 1'000'000;

int total(Counts x) { return x[0] + x[1] + x[2]; }

template<class Range>
void integers(const Range& values) {
    bool beginning = true;
    std::cout << '[';
    for (int v : values) {
        if (!beginning) std::cout << ',';
        beginning = false;
        std::cout << v;
    }
    std::cout << ']';
}

int dot(const Weights& left, const Weights& right) {
    int sum = 0;
    for (int i = 0; i < int(left.size()); ++i) sum += left[i] * right[i];
    return sum;
}

struct Component {
    int weak, special, hub;  // special means the distinguished anchor v.
    int order() const { return weak + special + hub; }
};

struct Option {
    int weak, special;
    Counts marked_negative;
    auto operator<=>(const Option&) const = default;
};

struct Pattern {
    Counts marked;
    std::vector<Option> options;
    auto operator<=>(const Pattern&) const = default;
};

std::vector<Pattern> folded_patterns(int r) {
    const int weak = r - 2;
    std::set<Pattern> unique;
    auto evaluate = [&](const std::vector<Component>& outer) {
        std::vector<Counts> chosen(outer.size());
        auto assignments = [&](auto&& again, int i, int budget, Counts used) -> void {
            if (i == int(outer.size())) {
                if (!used[0]) return;  // Only queries involving a test middle can move.
                Pattern row{used, {}};
                // The hub component is first and always stays on its own shore.
                for (int subset = 1; subset < (1 << (outer.size() - 1)); ++subset) {
                    Option side{};
                    for (int j = 1; j < int(outer.size()); ++j) if (subset & (1 << (j - 1))) {
                        side.weak += outer[j].weak;
                        side.special += outer[j].special;
                        for (int t = 0; t < 3; ++t) side.marked_negative[t] += chosen[j][t];
                    }
                    row.options.push_back(side);
                }
                std::ranges::sort(row.options);
                auto end = std::ranges::unique(row.options).begin();
                row.options.erase(end, row.options.end());
                unique.insert(std::move(row));
                return;
            }
            int outer_cost = outer[i].order() - 1;
            int spare = budget - outer_cost;
            for (int tests = 0; tests <= std::min(4 - used[0], spare); ++tests)
                for (int red = 0; red <= spare - tests; ++red)
                    for (int blue = 0; blue <= spare - tests - red; ++blue) {
                        Counts add{tests, red, blue};
                        if (!total(add) && outer_cost) continue;
                        if (i >= 2 && !outer[i - 1].hub && !outer[i - 1].special && !outer[i].special &&
                            outer[i].weak == outer[i - 1].weak && add < chosen[i - 1]) continue;
                        chosen[i] = add;
                        again(again, i + 1, spare - total(add),
                              {used[0] + tests, used[1] + red, used[2] + blue});
                    }
        };
        assignments(assignments, 0, r, {});
    };
    auto add_weak = [&](auto&& again, std::vector<Component>& outer, int remaining, int smallest) -> void {
        if (!remaining) { evaluate(outer); return; }
        for (int n = smallest; n <= remaining; ++n) {
            outer.push_back({n, 0, 0});
            again(again, outer, remaining - n, n);
            outer.pop_back();
        }
    };
    for (int a = 0; a <= weak; ++a) {
        std::vector<Component> joined{{a, 1, 1}};
        add_weak(add_weak, joined, weak - a, 1);
        for (int b = 0; b <= weak - a; ++b) {
            std::vector<Component> separate{{a, 0, 1}, {b, 1, 0}};
            add_weak(add_weak, separate, weak - a - b, 1);
        }
    }
    std::vector<Pattern> result;
    result.reserve(unique.size());
    while (!unique.empty()) result.push_back(std::move(unique.extract(unique.begin()).value()));
    return result;
}

std::vector<int> stable_split(int capacity) {
    int parents = 1;
    if (capacity >= 6) parents = 2;
    if (capacity >= 11) parents = 3;
    for (int g=4; g*g<=capacity; ++g) parents=g;
    std::vector<int> shares(parents, capacity / parents);
    for (int i=0; i<capacity % parents; ++i) ++shares[i];
    return shares;
}

struct Parameters {
    int r, red, blue, plan;
    Weights w;
    int weak() const { return r - 2; }
    Counts middles() const { return {4, red, blue}; }

    std::array<Size,3> static_sizes() const {
        int anchors=r-1;
        int j=r+6+red+blue;
        int n=4*(w[0]+w[1]+weak())+red*(w[2]+w[4]+anchors)+blue*(w[3]+w[5]+anchors);
        return {Size{j,n+1},Size{j+2,n+5},Size{j+6,n+13}};
    }

    std::array<Size, 3> sizes() const {
        int k = weak();
        Size core{r + 5 + red + blue, 4 * (w[0] + w[1] + k) + red * (w[2] + k + 1) + blue * (w[3] + k + 1)};
        std::array<Size, 3> stages{core, core, core};
        auto add = [&](int qty, int c, bool shrinks) {
            std::array<Size, 3> piece{};
            if (shrinks) {
                if (c == 2) piece = {Size{3, 9}, Size{5, 11}, Size{6, 12}};
                else if (c == 3) piece = {Size{3, 9}, Size{6, 12}, Size{7, 13}};
                else piece = {Size{c + 1, 5*c - 2}, Size{2*c + 1, 6*c - 2}, Size{2*c + 2, 6*c - 1}};
            } else {
                const auto shares = stable_split(c);
                int g=shares.size(), pairs=g*(g-1)/2, fresh=0, late=g*(g-1)*(g-2)/6;
                for (int i=0; i<g; ++i) {
                    int unary = shares[i]-g+1;
                    int demand = shares[i]-1;
                    int f = std::max(2, demand);
                    fresh += unary*f;
                    late += unary*(unary-1)/2 + unary*(g-1) + unary*(f-demand);
                    for (int j=i+1; j<g; ++j) fresh += std::max(1, g-2+unary+shares[j]-g+1);
                }
                piece = {Size{g,2*c}, Size{c + g - pairs, 2*c + fresh},
                         Size{c+g-pairs+late, -1}};
            }
            for (int age = 0; age < 3; ++age) for (int stat = 0; stat < 2; ++stat) {
                if (piece[age][stat] < 0) stages[age][stat] = -1;
                else if (stages[age][stat] >= 0) stages[age][stat] += qty * piece[age][stat];
            }
        };
        add(red, w[4], true);
        add(blue, w[5], plan == 2);
        return stages;
    }
};

struct ColourCost {
    int base;
    Counts delta;
    std::array<int, 3> cheapest;
};

struct Folded {
    int r;
    Counts available, degree;
    std::vector<ColourCost> colors;

    explicit Folded(const Parameters& x) : r(x.r), available(x.middles()) {
        const auto [p, v, hr, hb, br, bb, unit] = x.w;
        int k = x.weak(), n = total(available);
        degree = {p + v + k, hr + br + k + 1, hb + bb + k + 1};
        for (int special : {0, 1}) for (int weak = 0; weak <= k; ++weak) {
            ColourCost c{special * (4*v + x.red + x.blue) + n*weak,
                         {degree[0] - 2*(special*v + weak),
                          degree[1] - 2*(special + weak), degree[2] - 2*(special + weak)}, {0,1,2}};
            std::ranges::sort(c.cheapest, [&](int a, int b) { return c.delta[a] < c.delta[b]; });
            colors.push_back(c);
        }
    }

    int value(const Pattern& pattern) const {
        Counts free{};
        for (int t = 0; t < 3; ++t) {
            if (pattern.marked[t] > available[t]) return -1;
            free[t] = available[t] - pattern.marked[t];
        }
        int best = total(pattern.marked) == 1 ? degree[0] : Infinity;
        const int unmarked = total(free);
        for (auto& side : pattern.options) {
            const int outer = side.special + side.weak;
            int negative = total(side.marked_negative), positive = total(pattern.marked) - negative;
            int least = outer > 1 && !positive;
            int most = unmarked - (r - outer > 1 && !negative);
            if (least > most) continue;
            const auto& c = colors[side.special*(r - 1) + side.weak];
            int cost = c.base;
            for (int t = 0; t < 3; ++t) cost += c.delta[t] * (pattern.marked[t] - side.marked_negative[t]);
            int added = 0;
            for (int t : c.cheapest) {
                int k = std::min(free[t], c.delta[t] < 0 ? most - added : std::max(0, least - added));
                added += k;
                cost += k * c.delta[t];
            }
            best = std::min(cost, best);
        }
        return best;
    }
};

// Concavity in the number of positive weak anchors reduces the unrestricted
// splitting cut to its two endpoint counts. The same argument applies when
// a specified test mark must cross: its own contribution is affine.
int splitter(const Parameters& x) {
    int answer = Infinity;
    const auto [p, v, hr, hb, br, bb, unit] = x.w;
    int k = x.weak();
    for (int hubs = 1; hubs < 4; ++hubs) for (int special : {0, 1}) for (int weak : {0, k}) {
        int cut = 0;
        for (int color : {0,1}) {
            int h = (hubs >> color) & 1;
            int at_test = h*p + special*v + weak;
            cut += 2 * std::min(at_test, p + v + k - at_test);
            int weight = color ? hb : hr, branch = color ? bb : br;
            int at_shield = h*weight + special + weak;
            cut += (color ? x.blue : x.red) * std::min(at_shield, weight + branch + k + 1 - at_shield);
        }
        answer = std::min(cut, answer);
    }
    return answer;
}

struct Cut {
    Weights coefficients{};
    std::array<int, 7> positives{}; // hub mask, v, weak, two test and two shield counts
};

bool connected(int outer, const std::array<int, 4>& middle, int weak) {
    int used = outer;
    for (int t = 0; t < 4; ++t) if (middle[t]) used |= 1 << (t + 5);
    if (!used) return false;
    if (std::popcount(unsigned(used)) == 1) {
        int v = std::countr_zero(unsigned(used));
        return v < 4 || (v == 4 ? weak == 1 : middle[v - 5] == 1);
    }
    // No two sites of the same part meet. Groups with several sites share
    // all their neighbors and are connected precisely when their proxy is.
    constexpr std::array<int,4> neighbors{25,26,29,30}; // h0,h1,O,v,weak
    std::array<int,9> adjacent{};
    for (int i = 0; i < 4; ++i) if (middle[i]) {
        adjacent[5+i] = neighbors[i] & outer;
        for (int j = 0; j < 5; ++j) if (adjacent[5+i] & (1 << j)) adjacent[j] |= 1 << (5+i);
    }
    int visited = used & -used, pending = visited;
    while (pending) {
        int a = std::countr_zero(unsigned(pending));
        pending &= pending - 1;
        int next = adjacent[a] & ~visited;
        visited |= next;
        pending |= next;
    }
    return visited == used;
}

std::vector<Cut> connected_pair(int r, int red, int blue, bool image, bool anchor) {
    int k = r - 2;
    std::map<Weights, Cut> unique;
    const std::array<int,4> counts{2,2,red,blue};
    const std::array<int,2> occupied{image ? 1 : 2, image ? 1 : 0};
    auto extreme = [](int n) {
        if (n <= 1) return n ? std::vector{0,1} : std::vector{0};
        if (n == 2) return std::vector{0,1,2};
        return std::vector{0,1,n-1,n};
    };
    for (int h = 0; h < 4; ++h) for (int v : {0,1}) for (int w = 0; w <= k; ++w) {
        int positive_outer = h | (v << 3) | (w ? 16 : 0);
        int negative_outer = (h ^ 3) | 4 | ((1-v) << 3) | (w < k ? 16 : 0);
        int red_forced = occupied[0] * (1 - (anchor ? v : h&1));
        int blue_forced = occupied[1] * (1 - (anchor ? v : h>>1));
        for (int rt = red_forced; rt <= red_forced + 2 - occupied[0]; ++rt)
            for (int bt = blue_forced; bt <= blue_forced + 2 - occupied[1]; ++bt)
                for (int rs : extreme(red)) for (int bs : extreme(blue)) {
                    std::array<int,4> yes{rt,bt,rs,bs}, no{};
                    for (int t = 0; t < 4; ++t) no[t] = counts[t] - yes[t];
                    if (!connected(positive_outer, yes, w) || !connected(negative_outer, no, k-w)) continue;
                    Cut row{{}, {h,v,w,rt,bt,rs,bs}};
                    for (int t = 0; t < 4; ++t) for (int side : {0,1}) {
                        int n = side ? yes[t] : no[t];
                        if (side != ((h >> (t&1)) & 1)) row.coefficients[t < 2 ? 0 : t] += n;
                        if (side != v) row.coefficients[t < 2 ? 1 : 6] += n;
                        row.coefficients[6] += n * (side ? k - w : w);
                        if (t >= 2 && side) row.coefficients[t + 2] += n;
                    }
                    unique.try_emplace(row.coefficients, row);
                }
    }
    std::vector<Cut> sorted, frontier;
    for (auto [_, cut] : unique) sorted.push_back(cut);
    std::ranges::sort(sorted, [](const auto& a, const auto& b) {
        return dot(a.coefficients, {1,1,1,1,1,1,1}) < dot(b.coefficients, {1,1,1,1,1,1,1});
    });
    for (auto cut : sorted) {
        auto dominates = [&](const auto& prev) {
            for (int j = 0; j < 7; ++j) if (prev.coefficients[j] > cut.coefficients[j]) return false;
            return true;
        };
        if (std::ranges::none_of(frontier, dominates)) frontier.push_back(cut);
    }
    return frontier;
}

std::pair<int,Cut> pair_value(const std::vector<Cut>& data, const Weights& w) {
    std::pair<int,Cut> result{Infinity,{}};
    for (const auto& row : data) {
        int value = dot(row.coefficients, w);
        if (value < result.first) result = {value,row};
    }
    return result;
}

using PairDeck = std::array<std::vector<Cut>, 4>;

PairDeck make_pair_deck(int r, int red, int blue) {
    return {connected_pair(r, red, blue, false, false), connected_pair(r, red, blue, true, false),
            connected_pair(r, red, blue, false, true), connected_pair(r, red, blue, true, true)};
}

struct Receipt {
    Parameters p;
    int worst, minsplit, pair_kind;
    std::array<int,2> current, later;
    std::array<Cut,2> later_cuts;
};

std::optional<Size> certificate(const Parameters& p, const std::vector<Pattern>& patterns, std::size_t& last_failure) {
    const Folded folded(p);
    int threshold=splitter(p);
    if (folded.value(patterns[last_failure])>=threshold) return {};
    int upper=-1;
    for (std::size_t j=0; j<patterns.size(); ++j) {
        int value=folded.value(patterns[j]);
        if (value>=threshold) { last_failure=j; return {}; }
        upper=std::max(upper,value);
    }
    return Size{upper,threshold};
}

std::optional<Receipt> inspect(const Parameters& p, const PairDeck& pairs, const std::vector<Pattern>& patterns,
                               std::size_t& last_failure, std::map<std::string, std::uint64_t>& counts) {
    auto future = p.w;
    future[4] = 1;
    if (p.plan == 2) future[5] = 1;
    for (int target : {0,2}) {
        auto a = pair_value(pairs[target], future), b = pair_value(pairs[target+1], future);
        if (a.first == b.first) continue;
        ++counts["successor_pair_differences"];
        auto checked=certificate(p,patterns,last_failure);
        if (!checked) { ++counts["not_certified_by_folding"]; return {}; }
        auto u = pair_value(pairs[target], p.w), v = pair_value(pairs[target+1], p.w);
        if (u.first != v.first) throw std::runtime_error("certified pair changes at observation");
        ++counts["certified"];
        return Receipt{p, (*checked)[0], (*checked)[1], target/2, {u.first,v.first}, {a.first,b.first}, {a.second,b.second}};
    }
    return {};
}

void receipt(const Receipt& result) {
    auto d = result.p;
    std::cout << "{\"r\":" << d.r << ",\"anchors\":" << d.r-1 << ",\"shield_counts\": [" << d.red << ',' << d.blue
              << "],\"shrink_both\":" << std::boolalpha << (d.plan == 2) << ",\"weights\":";
    integers(d.w);
    std::cout << ",\"sizes\":[";
    for (int i=0;i<3;++i) { if (i) std::cout << ','; integers(d.sizes()[i]); }
    std::cout << "],\"worst_folded_minimum\":" << result.worst << ",\"least_splitting_cut\":" << result.minsplit
              << ",\"pair_kind\":\"" << (result.pair_kind ? "anchor" : "hub") << "\",\"current_pair_cardinalities\":";
    integers(result.current);
    std::cout << ",\"successor_pair_cardinalities\":";
    integers(result.later);
    std::cout << ",\"successor_cut_parameters\":[";
    integers(result.later_cuts[0].positives);
    std::cout << ',';
    integers(result.later_cuts[1].positives);
    std::cout << "]}";
}

void single(int r, int red, int blue, Weights w) {
    Parameters p{r,red,blue,2,w};
    const auto patterns=folded_patterns(r);
    const Folded folded(p);
    int maximum=-1;
    for (auto& pattern:patterns) maximum=std::max(maximum,folded.value(pattern));
    auto pairs=make_pair_deck(r,red,blue);
    std::cout << "{\"worst_folded_minimum\":" << maximum << ",\"least_splitting_cut\":" << splitter(p)
              << ",\"pair_cardinalities\":[";
    for (int i=0; i<4; ++i) {
        if (i) std::cout << ',';
        std::cout << pair_value(pairs[i],w).first;
    }
    std::cout << "]}\n";
}

std::vector<Pattern> ordered_patterns(int r) {
    auto patterns=folded_patterns(r);
    std::ranges::sort(patterns, [](const auto& a, const auto& b) {
        return std::pair{total(a.marked), -int(a.options.size())} > std::pair{total(b.marked), -int(b.options.size())};
    });
    if (patterns.empty()) throw std::runtime_error("empty folded pattern roster");
    return patterns;
}

void static_panel(int r) {
    const auto patterns=ordered_patterns(r);
    std::map<std::string,std::uint64_t> counts;
    std::optional<std::pair<Parameters, Size>> best;
    std::size_t last_failure=0;
    int limit=3*r+2;
    for (int total=2; total<=2*limit; ++total) {
        ++counts["shield_sum_layers"];
        for (int x=1; x<=limit; ++x) {
            int y=total-x;
            if (y<1 || y>limit || std::abs(x-y)>2) continue;
            for (int a=2; a<=5*r*r; ++a) for (int extra : {0,1}) {
                int b=(x*a+y-1)/y+extra;
                if (b<2 || b>5*r*r) continue;
                for (int spoke : {1,2}) for (int v : {1,2}) {
                    ++counts["parameter_assignments"];
                    Parameters p{r,x,y,0,{spoke,v,a,b,a,b,1}};
                    if (best && p.static_sizes()[1]>=best->first.static_sizes()[1]) { ++counts["bound_by_incumbent"] ; continue; }
                    auto exact=certificate(p,patterns,last_failure);
                    if (exact) { best=std::pair{p,*exact}; ++counts["certified"] ; }
                    else ++counts["not_certified_by_folding"];
                }
            }
        }
        if (best) break;
    }
    std::cout << "{\"r\":" << r << ",\"arbitrary_later_set\":true,\"folded_patterns\":" << patterns.size() << ",\"counts\":{";
    bool first=true;
    for (auto [key,value]:counts) { if (!first) std::cout<<','; first=false; std::cout << '"' << key << "\":" << value; }
    std::cout << "},\"winner\":";
    if (!best) std::cout << "null";
    else {
        auto [p,exact]=*best;
        std::cout << "{\"r\":" << r << ",\"anchors\":" << r-1 << ",\"shield_counts\": [" << p.red << ',' << p.blue
                  << "],\"arbitrary_later_set\":true,\"weights\":";
        integers(p.w);
        std::cout << ",\"sizes\":[";
        for (int i=0;i<3;++i) { if (i) std::cout << ','; integers(p.static_sizes()[i]); }
        std::cout << "],\"worst_folded_minimum\":" << exact[0] << ",\"least_splitting_cut\":" << exact[1] << '}';
    }
    std::cout << "}\n";
}

void panel(int r, bool both) {
    auto patterns=ordered_patterns(r);
    struct Family { Parameters p; int branch_total; };
    std::vector<Family> families;
    const int shield_min = r, shield_max = 3*r+4, price_max = 6*r+8, cap = 200*r*r;
    for (int x=shield_min; x<=shield_max; ++x) for (int y=shield_min; y<=shield_max; ++y) {
        if (std::abs(x-y)>2) continue;
        for (int a=2; a<=price_max; ++a) for (int extra : {0,1}) {
            int b = (x*a+y-1)/y+extra;
            if (b<2 || b>price_max) continue;
            Parameters p{r,x,y,both ? 2 : 1,{1,1,a,b,a,b,1}};
            int n = p.sizes()[1][0];
            if (n <= cap) families.push_back({p,n});
        }
    }
    std::ranges::sort(families, [](auto& a, auto& b) {
        return std::tuple{a.branch_total, a.p.red, a.p.blue, a.p.w[4], a.p.w[5]}
             < std::tuple{b.branch_total, b.p.red, b.p.blue, b.p.w[4], b.p.w[5]};
    });
    std::map<std::pair<int,int>, PairDeck> geometry;
    std::map<std::string, std::uint64_t> counts;
    counts["capacity_assignments_in_uncut_panel"] = families.size();
    std::optional<Receipt> winner;
    std::size_t last_failure = 0;
    for (const auto& family : families) {
        if (winner && family.branch_total > winner->p.sizes()[1][0]) break;
        ++counts["capacity_assignments_at_or_below_stop"];
        Parameters p = family.p;
        auto [entry, first] = geometry.try_emplace({p.red,p.blue});
        if (first) entry->second = make_pair_deck(r,p.red,p.blue);
        const auto& pairs = entry->second;
        for (int l=1; l<=r*p.red; ++l) for (int gain : {0,1,2}) {
            p.w[0]=l; p.w[1]=l+gain;
            ++counts["parameter_assignments"];
            if (winner && p.sizes()[1] >= winner->p.sizes()[1]) { ++counts["bound_by_incumbent_size"] ; continue; }
            if (auto ok=inspect(p,pairs,patterns,last_failure,counts)) winner=std::move(ok);
        }
    }
    std::cout << "{\"r\":" << r << ",\"both_colors_shrink\":" << std::boolalpha << both
              << ",\"folded_patterns\":" << patterns.size() << ",\"counts\":{";
    bool first=true;
    for (auto [key,value]:counts) { if (!first) std::cout<<','; first=false; std::cout << '"' << key << "\":" << value; }
    std::cout << "},\"winner\":";
    if (winner) receipt(*winner); else std::cout << "null";
    std::cout << "}\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 11 && std::string(argv[1]) == "case") {
            Weights w{0,0,0,0,0,0,1};
            for (int i=0; i<6; ++i) w[i]=std::stoi(argv[i+5]);
            single(std::stoi(argv[2]),std::stoi(argv[3]),std::stoi(argv[4]),w);
            return 0;
        }
        if (argc!=3) throw std::runtime_error("usage: high ORDER one|both|static");
        int r=std::stoi(argv[1]);
        std::string plan=argv[2];
        if (r<4 || r>8 || (plan!="one" && plan!="both" && plan!="static")) throw std::runtime_error("outside configured panel");
        if (plan=="static") static_panel(r);
        else panel(r,plan=="both");
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
