// Enumerate colored meet-once starts and measure exact pair minima on demand.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

#define main predecessor_main
#include "reach_bound.cpp"
#undef main

namespace census {

using Wide = unsigned __int128;
using Word = std::uint64_t;
constexpr int MaxStart = 10;
constexpr int MaxTableVertices = 23;
// 22 ordinary sites plus the exterior have at most C(23,2) endpoint classes.
constexpr int ClassWords = 4;
using Row = std::array<Word, ClassWords>;

constexpr Word bit(int i) { return Word{1} << i; }

int pop(Word& word) {
    int i = std::countr_zero(word);
    word &= word - 1;
    return i;
}

void require(bool test, const char* message) {
    if (!test) throw std::runtime_error(message);
}

bool connected(const auto& adjacency, Word side) {
    if (!side) return false;
    Word pending = side & -side;
    Word visited = pending;
    while (pending) {
        int i = pop(pending);
        Word more = adjacency[i] & side & ~visited;
        visited |= more;
        pending |= more;
    }
    return visited == side;
}

struct Start {
    int n = 0;
    std::array<Word, MaxStart+1> adjacency{};
    std::array<int, MaxStart> loose{};

    int edges() const {
        int twice = 0;
        for (int i = 0; i < n; ++i) twice += std::popcount(adjacency[i]);
        return twice / 2;
    }
    int deficit(int i) const { return std::max(0, 3 - std::popcount(adjacency[i])); }
    int min_width() const {
        int total = edges();
        for (int i = 0; i < n; ++i) total += deficit(i);
        return total;
    }
    bool admissible() const {
        auto wired = adjacency;
        for (int i = 0; i < n; ++i) if (loose[i]) {
            wired[i] |= bit(n);
            wired[n] |= bit(i);
        }
        Word vertices = bit(n + (wired[n] != 0)) - 1;
        for (int i = 0; i < n; ++i)
            if (!connected(wired, vertices ^ bit(i))) return false;
        return true;
    }
};

using Partition = std::vector<Word>;

Wide pack(const Start& graph, const Partition& order) {
    Wide packed = 0;
    for (int i = 0; i < graph.n; ++i) {
        int v = std::countr_zero(order[i]);
        Word lower = 0;
        for (int j = 0; j < i; ++j) if (graph.adjacency[v] & order[j]) lower |= bit(j);
        packed = (packed << (i + 4)) | (Wide{lower} << 4) | graph.loose[v];
    }
    return packed;
}

Start unpack(Wide packed, int n) {
    Start graph;
    graph.n = n;
    for (int i = n - 1; i >= 0; --i) {
        graph.loose[i] = packed & 15;
        packed >>= 4;
        Word lower = Word(packed) & (bit(i) - 1);
        packed >>= i;
        graph.adjacency[i] |= lower;
        while (lower) graph.adjacency[pop(lower)] |= bit(i);
    }
    return graph;
}

Partition refine(const Start& graph, Partition cells) {
    while (int(cells.size()) < graph.n) {
        Partition next;
        for (Word cell : cells) {
            std::map<Word, Word> by_signature;
            while (cell) {
                int v = pop(cell);
                Word signature = 0;
                for (Word part : cells) signature = (signature << 4) | std::popcount(part & graph.adjacency[v]);
                by_signature[signature] |= bit(v);
            }
            for (const auto& entry : by_signature) next.push_back(entry.second);
        }
        if (next.size() == cells.size()) return next;
        cells = std::move(next);
    }
    return cells;
}

Wide canonical_search(const Start& graph, Partition cells) {
    cells = refine(graph, std::move(cells));
    if (int(cells.size()) == graph.n) return pack(graph, cells);
    int chosen = -1, smallest = graph.n + 1;
    for (int i = 0; i < int(cells.size()); ++i) {
        int size = std::popcount(cells[i]);
        if (size > 1 && size < smallest) chosen = i, smallest = size;
    }
    Wide best = ~Wide{0};
    Word todo = cells[chosen];
    while (todo) {
        int v = pop(todo);
        Word peers = todo;
        while (peers) {
            int w = pop(peers);
            if (((graph.adjacency[v] ^ graph.adjacency[w]) & ~(bit(v) | bit(w))) == 0) todo &= ~bit(w);
        }
        Partition child = cells;
        child[chosen] ^= bit(v);
        child.insert(child.begin() + chosen, bit(v));
        best = std::min(best, canonical_search(graph, std::move(child)));
    }
    return best;
}

Wide canonical(const Start& graph) {
    std::map<std::pair<int,int>, Word> colors;
    for (int i = 0; i < graph.n; ++i)
        colors[{graph.loose[i], std::popcount(graph.adjacency[i])}] |= bit(i);
    Partition cells;
    for (const auto& entry : colors) cells.push_back(entry.second);
    return canonical_search(graph, std::move(cells));
}

void population(int width) {
    require(3 <= width && width <= 15, "unsupported starting-width diagonal");
    std::vector<std::set<Wide>> starts(width + 1);
    std::set<Wide> current{0};
    for (int n = 1; n <= 2 * width / 3; ++n) {
        std::set<Wide> next;
        for (Wide key : current) {
            Start graph = unpack(key, n);
            int edges = graph.edges();
            int floor = graph.min_width();
            auto allocate = [&](auto&& again, int i, int used, int spare) -> void {
                if (i == n) {
                    starts[used].insert((Wide(n) << 96) | canonical(graph));
                    return;
                }
                for (int extra = 0; extra <= spare; ++extra) {
                    graph.loose[i] = graph.deficit(i) + extra;
                    again(again, i+1, used + extra, spare - extra);
                }
                graph.loose[i] = 0;
            };
            if (floor <= width) allocate(allocate, 0, floor, width - floor);
            if (n == 2 * width / 3) continue;
            for (Word parents = 1; parents < bit(n); ++parents) {
                if (edges + std::popcount(parents) > width) continue;
                Start enlarged = graph;
                ++enlarged.n;
                enlarged.adjacency[n] = parents;
                Word links = parents;
                while (links) enlarged.adjacency[pop(links)] |= bit(n);
                if (enlarged.min_width() <= width) next.insert(canonical(enlarged));
            }
        }
        current = std::move(next);
    }
    for (int w = 3; w <= width; ++w) for (Wide code : starts[w]) {
        int n = code >> 96;
        Start graph = unpack(code & ((Wide{1} << 96) - 1), n);
        Word bits = 0;
        int index = 0;
        for (int i = 0; i < n; ++i) for (int j = i+1; j < n; ++j, ++index)
            if (graph.adjacency[i] & bit(j)) bits |= bit(index);
        std::cout << w << ' ' << n << ' ' << graph.admissible() << ' ' << bits;
        for (int i = 0; i < n; ++i) std::cout << ' ' << graph.loose[i];
        std::cout << '\n';
    }
}

struct Edge {
    int u, v, weight;
};

std::vector<std::vector<int>> shore_table(int n, const std::vector<Edge>& edges, const std::vector<int>& queries) {
    int width = edges.size();
    require(2 <= n && n <= MaxTableVertices && width <= 64*ClassWords, "table bound exceeded");
    std::vector<Word> neighbors(n, 0);
    std::vector<Row> rows(n);
    std::vector<int> local(width, -1);
    Row queried{};
    for (int i = 0; i < int(queries.size()); ++i) {
        int j = queries[i];
        require(j >= 0 && j < width && local[j] < 0, "invalid query class");
        local[j] = i;
        queried[j / 64] |= bit(j % 64);
    }
    for (int i = 0; i < width; ++i) {
        auto [u,v,weight] = edges[i];
        require(0 <= u && u < n && 0 <= v && v < n && u != v && weight > 0, "invalid endpoint class");
        neighbors[u] |= bit(v);
        neighbors[v] |= bit(u);
        rows[u][i/64] |= bit(i%64);
        rows[v][i/64] |= bit(i%64);
    }
    Word all = bit(n)-1;
    require(connected(neighbors, all), "disconnected augmented graph");
    std::vector<std::vector<int>> minima(queries.size(), std::vector<int>(width, -1));
    std::vector<Row> cuts(bit(n-1));
    int chunks = (width + 63) / 64;
    // Omit the final vertex, so each cut is visited once. Most cuts do not
    // cross a queried class and need no connectivity or weight calculation.
    for (Word shore = 1; shore < cuts.size(); ++shore) {
        int first = std::countr_zero(shore);
        Word rest = shore & (shore-1);
        Row& boundary = cuts[shore];
        bool relevant = false;
        for (int c = 0; c < chunks; ++c) {
            boundary[c] = cuts[rest][c] ^ rows[first][c];
            relevant |= (boundary[c] & queried[c]) != 0;
        }
        if (!relevant || !connected(neighbors, shore) || !connected(neighbors, all ^ shore)) continue;
        std::array<int, 64*ClassWords> support{};
        int length = 0, cost = 0;
        for (int c = 0; c < chunks; ++c) {
            Word active = boundary[c];
            while (active) {
                int edge = 64 * c + pop(active);
                cost += edges[edge].weight;
                support[length++] = edge;
            }
        }
        for (int i = 0; i < length; ++i) if (int q = local[support[i]]; q >= 0) {
            auto& min = minima[q];
            for (int j = 0; j < length; ++j) {
                int& current = min[support[j]];
                if (current < 0 || cost < current) current = cost;
            }
        }
    }
    return minima;
}

int endpoint_classes(const Incidence& inc) {
    int degrees = 0;
    for (Mask row : inc.ordinary) degrees += std::popcount(row);
    return degrees / 2 + std::popcount(inc.live);
}

Rows movable_names_first(const Rows& here, const Incidence& inc, int& movable) {
    std::vector<int> image(inc.own.size(), -1);
    movable = 0;
    for (int b = 0; b < int(image.size()); ++b) {
        bool pinned = false;
        for (int j : inc.own[b]) pinned |= bool(inc.live & bit(j));
        if (!pinned) image[b] = movable++;
    }
    int next = movable;
    for (int& slot : image) if (slot == -1) slot = next++;
    Rows renamed = here;
    for (auto& row : renamed) {
        for (int& b : row) b = image[b];
        std::ranges::sort(row);
    }
    return renamed;
}

int planned_births(const Incidence& inc, const std::vector<Mask>& groups) {
    if (!inc.live) return 0;
    const auto use = demands(groups, inc.loose.size());
    int total = groups.size();
    for (int j = 0; j < int(inc.loose.size()); ++j) {
        int left = int(inc.loose[j].size()) - use[j];
        if (left < 0) return -1;
        total += left;
    }
    return total;
}

// A bond lies in one block of the wired graph. Inside that block, pin the
// two queried endpoint pairs and use cut flow as a lower bound.
struct PairTable {
    struct Block {
        using Capacity = std::array<std::array<int,60>,60>;
        Capacity capacity{};
        std::array<Mask,60> neighbors{};
        Mask vertices = 0;

        Mask component(Mask side, Mask seed) const {
            Mask seen = seed, queue = seed;
            while (queue) {
                Mask extra = neighbors[pop(queue)] & side & ~seen;
                seen |= extra;
                queue |= extra;
            }
            return seen;
        }

        std::pair<int,Mask> relax(Mask in, Mask out, int ceiling) const {
            Capacity residual = capacity;
            int sent = 0;
            for (;;) {
                std::array<int,60> parent, queue;
                int size = 0, hit = -1;
                Mask reached = in;
                for (Mask roots = in; roots;) {
                    int a = pop(roots);
                    parent[a] = a;
                    queue[size++] = a;
                }
                for (int pos = 0; pos < size && hit < 0; ++pos) {
                    int u = queue[pos];
                    for (Mask todo = neighbors[u] & ~reached; todo;) {
                        int v = pop(todo);
                        if (residual[u][v] <= 0) continue;
                        reached |= bit(v);
                        parent[v] = u;
                        queue[size++] = v;
                        if (out & bit(v)) { hit = v; break; }
                    }
                }
                if (hit < 0) return {sent,reached};
                int add = ceiling - sent;
                for (int v = hit; parent[v] != v; v = parent[v]) add = std::min(add, residual[parent[v]][v]);
                sent += add;
                if (sent >= ceiling) return {ceiling,0};
                for (int v = hit; parent[v] != v;) {
                    int u = parent[v];
                    residual[u][v] -= add;
                    residual[v][u] += add;
                    v = u;
                }
            }
        }

        int through(const Edge& a, const Edge& b) const {
            int best = Inf;
            auto short_path = [&](Mask pins, Mask forbidden) -> Mask {
                Mask start = pins & -pins;
                if (start == pins) return pins;
                Mask reached = start, open = start;
                std::array<int,60> parent;
                while (open && (reached & pins) != pins) {
                    int u = pop(open);
                    Mask seen = neighbors[u] & ~reached & ~forbidden;
                    reached |= seen;
                    open |= seen;
                    while (seen) parent[pop(seen)] = u;
                }
                if ((reached & pins) != pins) return 0;
                Mask path = pins;
                for (int j = std::countr_zero(pins ^ start); bit(j) != start;)
                    j = parent[j], path |= bit(j);
                return path;
            };
            auto use_path = [&](Mask path, Mask other) {
                if (!path) return;
                Mask rest = component(vertices ^ path, other & -other);
                if ((rest & other) != other) return;
                int cost = 0;
                for (Mask inside = vertices ^ rest; inside;) {
                    int i = pop(inside);
                    for (Mask crossings = neighbors[i] & rest; crossings;)
                        cost += capacity[i][pop(crossings)];
                }
                best = std::min(best,cost);
            };
            auto heuristic = [&](Mask in, Mask out) {
                if (in & out) return;
                for (int attempt = 0; attempt < 2; ++attempt) {
                    Mask path = short_path(in,out);
                    use_path(path,out);
                    for (Mask extra = path & ~in; extra;)
                        use_path(short_path(in,out | bit(pop(extra))),out);
                    std::swap(in,out);
                }
            };
            heuristic(bit(a.u) | bit(b.u),bit(a.v) | bit(b.v));
            heuristic(bit(a.u) | bit(b.v),bit(a.v) | bit(b.u));
            auto search = [&](auto&& again, Mask in, Mask out) -> void {
                if (in & out) return;
                if ((component(vertices ^ out, in & -in) & in) != in ||
                    (component(vertices ^ in, out & -out) & out) != out) return;
                auto [lower, side] = relax(in,out,best);
                if (lower >= best) return;
                Mask other = vertices ^ side;
                Mask first = component(side, side & -side), second = component(other, other & -other);
                if (first == side && second == other) {
                    best = lower;
                    return;
                }
                // Every disconnected side component of a relaxed minimum
                // has a pin, or moving it would lower that minimum. A legal
                // cut connects its pins across at least one currently
                // opposite-side neighbor of that component.
                bool flipped = first == side;
                if (flipped) std::swap(in,out), std::swap(side,other), first = second;
                Mask alternatives = 0;
                for (Mask members = first; members;) alternatives |= neighbors[pop(members)];
                alternatives &= other & ~out;
                while (alternatives) {
                    Mask pick = bit(pop(alternatives));
                    if (flipped) again(again,out,in | pick);
                    else again(again,in | pick,out);
                    out |= pick;
                }
            };
            search(search,bit(a.u) | bit(b.u),bit(a.v) | bit(b.v));
            search(search,bit(a.u) | bit(b.v),bit(a.v) | bit(b.u));
            return best;
        }
    };

    std::vector<int> cls;
    std::vector<std::vector<int>> minima;

    PairTable(const Incidence& inc, const std::vector<int>& query) {
        int ordinary = inc.ordinary.size(), vertices = ordinary + bool(inc.live);
        require(vertices <= 60, "pinned cut vertex bound");
        std::vector<Edge> edges;
        std::map<std::pair<int,int>,int> endpoints;
        std::vector<std::vector<std::pair<int,int>>> incident(vertices);
        for (const auto& users : inc.own) {
            int x = users[0], y = users.size() == 2 ? users[1] : ordinary;
            auto [item,new_pair] = endpoints.try_emplace({x,y},edges.size());
            int e = item->second;
            if (new_pair) {
                edges.push_back({x,y,0});
                incident[x].push_back({y,e});
                incident[y].push_back({x,e});
            }
            ++edges[e].weight;
            cls.push_back(e);
        }
        std::vector<int> time(vertices), low(vertices), stack, block_index(edges.size());
        std::vector<Block> blocks;
        int clock = 0;
        auto dfs = [&](auto&& again, int u, int parent_edge) -> void {
            time[u] = low[u] = ++clock;
            for (auto [v,e] : incident[u]) if (e != parent_edge) {
                if (!time[v]) {
                    stack.push_back(e);
                    again(again,v,e);
                    low[u] = std::min(low[u],low[v]);
                    if (low[v] >= time[u]) {
                        blocks.emplace_back();
                        Block& b = blocks.back();
                        for (;;) {
                            int d = stack.back(); stack.pop_back();
                            auto [a,c,weight] = edges[d];
                            block_index[d] = int(blocks.size()) - 1;
                            b.vertices |= bit(a) | bit(c);
                            b.neighbors[a] |= bit(c); b.neighbors[c] |= bit(a);
                            b.capacity[a][c] = b.capacity[c][a] = weight;
                            if (d == e) break;
                        }
                    }
                } else if (time[v] < time[u]) {
                    stack.push_back(e);
                    low[u] = std::min(low[u],time[v]);
                }
            }
        };
        dfs(dfs,0,-1);
        int count = edges.size();
        std::vector<bool> needed(count,query.empty());
        for (int b : query) needed[cls[b]] = true;
        minima.assign(count,std::vector<int>(count,Inf));
        for (int a = 0; a < count; ++a) for (int b = a; b < count; ++b)
            if ((needed[a] || needed[b]) && block_index[a] == block_index[b])
                minima[a][b] = minima[b][a] = blocks[block_index[a]].through(edges[a],edges[b]);
    }

    // The existing extension search consumes only these fields and at().
    Table extension_table() const {
        Rows seed{{0,1,2}};
        Table out(seed,Incidence(seed),{},0);
        out.cls = cls;
        out.minima = minima;
        return out;
    }
};

void read_tables(bool compare) {
    int n, width, q;
    while (std::cin >> n >> width >> q) {
        require(width > 0 && q > 0 && q <= width, "empty table query");
        std::vector<Edge> edges(width);
        std::vector<int> queries(q);
        for (auto& e : edges) require(bool(std::cin >> e.u >> e.v >> e.weight), "missing endpoint class");
        for (int& index : queries) require(bool(std::cin >> index), "missing query");
        const auto minima = shore_table(n, edges, queries);
        if (compare) {
            Rows parity(n);
            std::vector<int> bundle_start;
            int name = 0;
            for (const auto& [u, v, weight] : edges) {
                bundle_start.push_back(name);
                for (int i = 0; i < weight; ++i) {
                    parity[u].push_back(name);
                    parity[v].push_back(name++);
                }
            }
            std::vector<int> target;
            for (int index : queries) target.push_back(bundle_start[index]);
            const PairTable rooted(Incidence(parity), target);
            for (int i = 0; i < q; ++i) for (int j = 0; j < width; ++j) {
                int exact = rooted.minima[rooted.cls[target[i]]][rooted.cls[bundle_start[j]]];
                require((exact == Inf ? -1 : exact) == minima[i][j], "rooted and whole-cut minima disagree");
            }
        }
        bool beginning = true;
        for (const auto& row : minima) for (int value : row) {
            if (!beginning) std::cout << ' ';
            beginning = false;
            std::cout << value;
        }
        std::cout << '\n';
    }
    require(std::cin.eof(), "malformed input");
}

struct Outcome {
    std::string method;
    int short_generators = 0, full_generators = 0, failing_generators = 0;
    int rooted_successor = 0, unresolved_maps = 0, non_equation_generators = 0;
    std::optional<Witness> failure;
};

bool fresh_extension(const Table& table, const std::vector<int>& image, int old_width) {
    int width = table.cls.size();
    std::vector<std::vector<int>> blocks;
    for (int a = old_width; a < width; ++a) {
        bool inserted = false;
        for (auto& group : blocks) {
            int b = group[0];
            bool twins = true;
            if (table.cls[a] != table.cls[b])
                for (int x = 0; x < width && twins; ++x)
                    if (x != a && x != b) twins = table.at(x,a) == table.at(x,b);
            if (twins) { group.push_back(a); inserted = true; break; }
        }
        if (!inserted) blocks.push_back({a});
    }
    int n = blocks.size();
    std::vector<std::vector<int>> allowed(n);
    for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) {
        const auto& x = blocks[a];
        const auto& y = blocks[b];
        if (x.size() != y.size() || (x.size() > 1 && table.at(x[0],x[1]) != table.at(y[0],y[1]))) continue;
        bool matches = true;
        for (int z = 0; z < old_width && matches; ++z)
            matches = table.at(z,x[0]) == table.at(z < int(image.size()) ? image[z] : z,y[0]);
        if (matches) allowed[a].push_back(b);
    }
    std::vector<int> mapped(n,-1);
    std::vector<bool> used(n,false);
    auto search = [&](auto&& again, int left) -> bool {
        if (!left) return true;
        int selected = -1;
        std::vector<int> best;
        for (int a = 0; a < n; ++a) if (mapped[a] == -1) {
            std::vector<int> options;
            for (int b : allowed[a]) if (!used[b]) {
                bool matches = true;
                for (int z = 0; z < n && matches; ++z)
                    if (mapped[z] != -1)
                        matches = table.at(blocks[a][0],blocks[z][0]) == table.at(blocks[b][0],blocks[mapped[z]][0]);
                if (matches) options.push_back(b);
            }
            if (options.empty()) return false;
            if (selected < 0 || options.size() < best.size()) selected = a, best = std::move(options);
        }
        for (int candidate : best) {
            mapped[selected] = candidate; used[candidate] = true;
            if (again(again,left-1)) return true;
            used[candidate] = false; mapped[selected] = -1;
        }
        return false;
    };
    return search(search,n);
}

Outcome test(const Rows& start, const Rows& current) {
    Incidence original(current);
    auto groups = Rule(original.ordinary).groups(original.live);
    Outcome result;
    int movable;
    Rows here = movable_names_first(current, original, movable);
    if (movable <= 1) {
        result.method = "fixed";
        return result;
    }
    if (groups.empty()) {
        result.method = "offshoots";
        return result;
    }
    Incidence incidence(here);
    if (here.size() + 1 > MaxMeasuredVertices || endpoint_classes(incidence) > 128) {
        result.method = "unresolved_current_table_bound";
        return result;
    }
    std::vector<int> queries(movable);
    for (int i = 0; i < movable; ++i) queries[i] = i;
    {
        Table clipped(here,incidence,queries,Cutoff);
        if (Symmetries(clipped,movable).grade([&](const auto& perm) {
            ++result.short_generators;
            return carries_equations(clipped,perm);
        })) {
            result.method = "short_equation";
            return result;
        }
    }
    Table exact(here,incidence,queries,Inf);
    std::vector<std::vector<int>> maps;
    Symmetries(exact,movable).grade([&](const auto& perm) {
        ++result.full_generators;
        if (!carries_equations(exact,perm)) maps.push_back(perm);
        return true;
    });
    result.non_equation_generators = maps.size();
    if (maps.empty()) {
        result.method = "full_equation";
        return result;
    }
    if (planned_births(incidence,groups) >= 63 || here.size()+planned_births(incidence,groups) > 60) {
        result.method = "unresolved_successor_junction_bound";
        result.unresolved_maps = maps.size();
        return result;
    }
    Rows after = grow(here,incidence,groups);
    require(!after.empty(), "an open reached stage stalled despite its look-ahead");
    Incidence grown(after);
    if (after.size()+bool(grown.live) > 60) {
        result.method = "unresolved_successor_junction_bound";
        result.unresolved_maps = maps.size();
        return result;
    }
    std::vector<int> moved;
    for (int i = 0; i < movable; ++i)
        if (std::ranges::any_of(maps, [i](const auto& perm) { return perm[i] != i; })) moved.push_back(i);
    bool rooted = after.size()+bool(grown.live) > MaxMeasuredVertices || endpoint_classes(grown) > 128;
    result.rooted_successor = rooted;
    if (std::getenv("CENSUS_TRACE")) std::cerr << "  successor " << after.size() << " classes " << endpoint_classes(grown) << " rooted " << rooted << '\n';
    Table partial = rooted ? PairTable(grown,moved).extension_table() : Table(after,grown,moved,Inf);
    std::optional<Table> full;
    for (const auto& perm : maps) {
        Extension verdict{true};
        for (int a : moved) {
            for (int b = 0; b < int(incidence.own.size()); ++b) {
                if (a == b || incidence.own[b].size() != 2) continue;
                int image_b = b < movable ? perm[b] : b;
                if (partial.at(a,b) != partial.at(perm[a],image_b)) {
                    verdict = {false,a,b,partial.at(a,b),partial.at(perm[a],image_b)};
                    break;
                }
            }
            if (!verdict.possible) break;
        }
        if (verdict.possible) verdict = extends(partial,perm,incidence.own.size(),false);
        if (!verdict.possible && verdict.first < 0) {
            if (std::getenv("CENSUS_TRACE")) std::cerr << "  full fresh search\n";
            if (!full) {
                if (rooted) full = PairTable(grown,{}).extension_table();
                else full.emplace(after,grown,std::vector<int>{},Inf);
            }
            verdict = {fresh_extension(*full,perm,incidence.own.size())};
        }
        if (!verdict.possible) {
            ++result.failing_generators;
            if (!result.failure) result.failure = Witness{start,here,after,perm,verdict};
        }
    }
    result.method = result.failing_generators ? "failure" : "exact_successor";
    return result;
}

void audit(int current_limit) {
    require(current_limit >= 16 && current_limit <= 20, "current-site bound outside configuration");
    using Key = std::tuple<int,int,int,int,int,int>;
    std::map<Key,std::map<std::string,std::uint64_t>> stage_bins;
    std::map<Key,Witness> witnesses;
    std::map<std::tuple<int,int,int,int>,std::map<std::string,std::uint64_t>> origins;
    int w,n,admissible;
    Word graph_bits;
    while (std::cin >> w >> n >> admissible >> graph_bits) {
        Adj adjacency(n);
        int index = 0;
        for (int i = 0; i < n; ++i) for (int j = i+1; j < n; ++j,++index) if (graph_bits & bit(index)) {
            adjacency[i] |= bit(j);
            adjacency[j] |= bit(i);
        }
        int l = 0;
        std::vector<int> loose(n);
        for (auto& free : loose) {
            require(bool(std::cin >> free), "malformed start roster");
            l += free;
        }
        auto& origin = origins[{w,n,l,admissible}];
        if (std::getenv("CENSUS_TRACE")) std::cerr << "start " << w << ' ' << n << ' ' << admissible << ' ' << graph_bits << '\n';
        ++origin["starts"];
        Rows start = start_rows(adjacency,loose);
        Rows rows = start;
        for (int age = 0;; ++age) {
            Incidence current(rows);
            if (!current.live) {
                ++origin[age == 0 ? "closed_at_start" : "closed_after_growth"];
                break;
            }
            if (age) {
                if (std::getenv("CENSUS_TRACE")) std::cerr << " age " << age << " sites " << rows.size() << '\n';
                Key key{w,n,l,admissible,age,rows.size()};
                Outcome result = test(start,rows);
                auto& bins = stage_bins[key];
                ++bins["stages"];
                ++bins[result.method];
                bins["short_generators"] += result.short_generators;
                bins["full_generators"] += result.full_generators;
                bins["non_equation_generators"] += result.non_equation_generators;
                bins["failing_generators"] += result.failing_generators;
                bins["rooted_successors"] += result.rooted_successor;
                bins["unresolved_generators"] += result.unresolved_maps;
                if (result.failure && !witnesses.contains(key)) witnesses.emplace(key,std::move(*result.failure));
            }
            const auto groups = Rule(current.ordinary).groups(current.live);
            int births = planned_births(current,groups);
            if (births < 0) {
                ++origin[age == 0 ? "stall_at_start" : "stall_after_growth"];
                break;
            }
            if (rows.size() + births > std::size_t(current_limit)) {
                ++origin["next_outside_current_bound"];
                ++origin["next_outside_age_"+std::to_string(age+1)];
                break;
            }
            rows = grow(rows,current,groups);
            require(!rows.empty(), "a planned complete round failed");
        }
    }
    require(std::cin.eof(), "invalid row in roster");
    auto print_counts = [](const auto& bins) {
        std::cout << '{';
        bool first = true;
        for (const auto& [label, count] : bins) {
            if (!first) std::cout << ',';
            first = false;
            std::cout << '"' << label << "\":" << count;
        }
        std::cout << '}';
    };
    for (const auto& [key, counts] : origins) {
        auto [width,sites,loose,realized] = key;
        std::cout << "{\"origin\":";
        array_json(std::array{width,sites,loose,realized});
        std::cout << ",\"counts\":"; print_counts(counts);
        std::cout << "}\n";
    }
    for (const auto& [key, counts] : stage_bins) {
        auto [width,sites,loose,realized,age,junctions] = key;
        std::cout << "{\"stage\":";
        array_json(std::array{width,sites,loose,realized,age,junctions});
        std::cout << ",\"counts\":"; print_counts(counts);
        if (witnesses.contains(key)) {
            std::cout << ",\"witness\":";
            witness_json(witnesses.at(key));
        }
        std::cout << "}\n";
    }
}

} // namespace census

int main(int argc, char** argv) {
    try {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        if (argc == 3 && std::string(argv[1]) == "population") census::population(std::stoi(argv[2]));
        else if (argc == 3 && std::string(argv[1]) == "audit") census::audit(std::stoi(argv[2]));
        else if (argc == 2 && std::string(argv[1]) == "tables") census::read_tables(false);
        else if (argc == 2 && std::string(argv[1]) == "compare-tables") census::read_tables(true);
        else throw std::runtime_error("usage: census population WIDTH | census audit CURRENT_N | census tables | census compare-tables");
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
