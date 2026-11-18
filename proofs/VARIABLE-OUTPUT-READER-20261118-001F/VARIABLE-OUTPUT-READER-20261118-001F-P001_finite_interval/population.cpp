// Reachable colored ordinary meeting graphs, modulo relabeling.
#include <array>
#include <bit>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int max_width = 26;
constexpr int max_sites = 1 + (max_width - 3) / 2;
using Mask = std::uint16_t;
using Packed = unsigned __int128;
using Clock = std::chrono::steady_clock;

constexpr Mask bit(int i) { return Mask{1} << i; }

int take(Mask& remaining) {
    const int i = std::countr_zero(remaining);
    remaining &= remaining - 1;
    return i;
}

struct Graph {
    int sites = 0;
    std::array<Mask, max_sites> neighbors{};
    std::array<std::uint8_t, max_sites> loose{};
};

struct Key {
    std::uint64_t low = 0;
    std::uint64_t high = 0;

    explicit operator bool() const { return (low | high) != 0; }
    bool operator==(const Key&) const = default;
    bool operator<(const Key& rhs) const {
        return high == rhs.high ? low < rhs.low : high < rhs.high;
    }
};

struct Partition {
    std::array<Mask, max_sites> cells{};
    int count = 0;

    void push(Mask cell) { cells[count++] = cell; }
};

bool twins(const Graph& graph, int i, int j) {
    return graph.loose[i] == graph.loose[j]
        && ((graph.neighbors[i] ^ graph.neighbors[j]) & ~(bit(i) | bit(j))) == 0;
}

Key encode(const Graph& graph, const Partition& order) {
    Packed result = 0;
    for (int i = 0; i < graph.sites; ++i) {
        const int v = std::countr_zero(order.cells[i]);
        Mask lower = 0;
        for (int j = 0; j < i; ++j) {
            if (graph.neighbors[v] & order.cells[j]) lower |= bit(j);
        }
        result = (result << (i + 2)) | (Packed{lower} << 2) | graph.loose[v];
    }
    return {static_cast<std::uint64_t>(result), static_cast<std::uint64_t>(result >> 64)};
}

Graph decode(Key key, int sites) {
    Packed packed = (Packed{key.high} << 64) | key.low;
    Graph graph;
    graph.sites = sites;
    for (int i = sites - 1; i >= 0; --i) {
        graph.loose[i] = packed & 3;
        packed >>= 2;
        Mask lower = static_cast<Mask>(packed) & (bit(i) - 1);
        packed >>= i;
        graph.neighbors[i] |= lower;
        while (lower) graph.neighbors[take(lower)] |= bit(i);
    }
    return graph;
}

// Refine ordered cells by their vectors of neighbor counts. Three bits
// per count suffice since the ordinary degree is at most six.
Partition refine(const Graph& graph, Partition partition) {
    while (partition.count < graph.sites) {
        std::array<std::uint64_t, max_sites> weights;
        for (int c = 0; c < partition.count; ++c) {
            Mask cell = partition.cells[c];
            while (cell) weights[take(cell)] = std::uint64_t{1} << (3 * c);
        }

        Partition next;
        for (int c = 0; c < partition.count; ++c) {
            Mask cell = partition.cells[c];
            if (std::has_single_bit(cell)) {
                next.push(cell);
                continue;
            }
            std::array<std::uint64_t, max_sites> signatures;
            std::array<Mask, max_sites> groups;
            int filled = 0;
            while (cell) {
                const int v = take(cell);
                std::uint64_t signature = 0;
                for (Mask adjacent = graph.neighbors[v]; adjacent; ) signature += weights[take(adjacent)];
                int slot = 0;
                while (slot < filled && signatures[slot] < signature) ++slot;
                if (slot < filled && signatures[slot] == signature) {
                    groups[slot] |= bit(v);
                } else {
                    for (int right = filled; right > slot; --right) {
                        signatures[right] = signatures[right - 1];
                        groups[right] = groups[right - 1];
                    }
                    signatures[slot] = signature;
                    groups[slot] = bit(v);
                    ++filled;
                }
            }
            for (int i = 0; i < filled; ++i) next.push(groups[i]);
        }
        if (next.count == partition.count) return next;
        partition = next;
    }
    return partition;
}

Key canonical_search(const Graph& graph, Partition partition) {
    partition = refine(graph, partition);
    if (partition.count == graph.sites) return encode(graph, partition);

    int chosen = 0;
    int smallest = max_sites + 1;
    for (int i = 0; i < partition.count; ++i) {
        const int size = std::popcount(partition.cells[i]);
        if (size > 1 && size < smallest) {
            chosen = i;
            smallest = size;
        }
    }
    Key best;
    for (Mask pending = partition.cells[chosen]; pending; ) {
        const int v = take(pending);
        for (Mask alternatives = pending; alternatives; ) {
            const int w = take(alternatives);
            if (twins(graph, v, w)) pending &= ~bit(w);
        }
        Partition child;
        for (int i = 0; i < chosen; ++i) child.push(partition.cells[i]);
        child.push(bit(v));
        child.push(partition.cells[chosen] ^ bit(v));
        for (int i = chosen + 1; i < partition.count; ++i) child.push(partition.cells[i]);
        const Key result = canonical_search(graph, child);
        if (!best || result < best) best = result;
    }
    return best;
}

Key canonical(const Graph& graph) {
    std::array<Mask, 4 * 7> colors{};
    for (int i = 0; i < graph.sites; ++i) {
        const int color = 7 * graph.loose[i] + std::popcount(graph.neighbors[i]);
        colors[color] |= bit(i);
    }
    Partition initial;
    for (const Mask color : colors) if (color) initial.push(color);
    return canonical_search(graph, initial);
}

template<class Consumer>
void parent_sets(const Graph& graph, Consumer consume) {
    Mask live = 0;
    std::array<Mask, max_sites> earlier_twins{};
    for (int i = 0; i < graph.sites; ++i) {
        if (!graph.loose[i]) continue;
        for (Mask earlier = live; earlier; ) {
            const int j = take(earlier);
            if (twins(graph, i, j)) earlier_twins[i] |= bit(j);
        }
        live |= bit(i);
    }

    // Select the earliest members of each freely interchangeable twin class.
    for (Mask first = live; first; ) {
        const int i = take(first);
        if (earlier_twins[i]) continue;
        consume(bit(i));
        for (Mask second = first; second; ) {
            const int j = take(second);
            const Mask pair = bit(i) | bit(j);
            if (earlier_twins[j] & ~pair) continue;
            const Mask common = graph.neighbors[i] & graph.neighbors[j];
            if (!common) continue;
            consume(pair);
            for (Mask third = second; third; ) {
                const int k = take(third);
                const Mask triple = pair | bit(k);
                if (earlier_twins[k] & ~triple) continue;
                const Mask neighbors = graph.neighbors[k];
                if ((neighbors & graph.neighbors[i]) && (neighbors & graph.neighbors[j])
                    && !(neighbors & common)) consume(triple);
            }
        }
    }
}

std::uint64_t hash_key(Key key) {
    std::uint64_t h = key.low ^ (key.high * 0x9e3779b97f4a7c15ULL);
    h = (h ^ (h >> 30)) * 0xbf58476d1ce4e5b9ULL;
    h = (h ^ (h >> 27)) * 0x94d049bb133111ebULL;
    return h ^ (h >> 31);
}

class KeySet {
public:
    const std::vector<Key>& slots() const { return slots_; }
    std::size_t size() const { return size_; }

    void insert(Key key) {
        if (slots_.empty() || size_ * 4 >= slots_.size() * 3) {
            auto old = std::move(slots_);
            slots_ = std::vector<Key>(old.empty() ? 16 : old.size() * 2);
            size_ = 0;
            for (const Key prior : old) if (prior) insert_into_slots(prior);
        }
        insert_into_slots(key);
    }

private:
    void insert_into_slots(Key key) {
        const std::size_t mask = slots_.size() - 1;
        std::size_t i = hash_key(key) & mask;
        while (slots_[i] && !(slots_[i] == key)) i = (i + 1) & mask;
        if (!slots_[i]) {
            slots_[i] = key;
            ++size_;
        }
    }

    std::vector<Key> slots_;
    std::size_t size_ = 0;
};

using Layer = std::array<KeySet, max_sites + 1>;

std::filesystem::path filename(const std::filesystem::path& directory, int width) {
    return directory / ("width" + std::to_string(width) + ".txt");
}

std::size_t publish(const Layer& layer, const std::filesystem::path& output) {
    const auto pending = output.string() + ".part";
    std::FILE* file = std::fopen(pending.c_str(), "wx");
    if (!file) throw std::runtime_error("could not create " + pending);
    std::size_t rows = 0;
    char data[1 << 16];
    std::setvbuf(file, data, _IOFBF, sizeof(data));
    for (int n = 1; n <= max_sites; ++n) {
        for (const Key key : layer[n].slots()) {
            if (!key) continue;
            const Graph graph = decode(key, n);
            char line[256];
            char* pos = std::to_chars(line, line + sizeof(line), n).ptr;
            auto write_column = [&](unsigned value) {
                *pos++ = ' ';
                pos = std::to_chars(pos, line + sizeof(line), value).ptr;
            };
            for (int i = 0; i < n; ++i) write_column(graph.neighbors[i]);
            for (int i = 0; i < n; ++i) write_column(graph.loose[i]);
            *pos++ = '\n';
            const std::size_t length = pos - line;
            if (std::fwrite(line, 1, length, file) != length) {
                std::fclose(file);
                throw std::runtime_error("write failed for " + pending);
            }
            ++rows;
        }
    }
    if (std::fclose(file)) throw std::runtime_error("close failed for " + pending);
    std::filesystem::rename(pending, output);
    return rows;
}

void generate(int first_width, int last_width, const std::filesystem::path& directory) {
    std::array<Layer, max_width + 1> layers;
    Graph seed;
    seed.sites = 1;
    seed.loose[0] = 3;
    layers[3][1].insert(canonical(seed));
    const auto start = Clock::now();
    for (int width = 3; width <= last_width; ++width) {
        auto& layer = layers[width];
        if (width >= first_width) {
            std::size_t total = 0;
            for (const auto& set : layer) total += set.size();
            if (!directory.empty() && publish(layer, filename(directory, width)) != total) {
                throw std::runtime_error("wrong number of published rows");
            }
            std::cout << "width=" << width << " total=" << total << " by_sites=";
            for (int n = 1; n <= max_sites; ++n) {
                if (layer[n].size()) std::cout << n << ':' << layer[n].size() << ',';
            }
            std::cout << " elapsed=" << std::chrono::duration<double>(Clock::now() - start).count()
                      << std::endl;
        }
        if (width + 2 <= last_width) {
            for (int n = 1; n < max_sites; ++n) {
                for (const Key key : layer[n].slots()) {
                    if (!key) continue;
                    const Graph graph = decode(key, n);
                    parent_sets(graph, [&](Mask parents) {
                        Graph next = graph;
                        next.sites = n + 1;
                        next.neighbors[n] = parents;
                        while (parents) {
                            const int i = take(parents);
                            next.neighbors[i] |= bit(n);
                            --next.loose[i];
                        }
                        for (int h = 2; h <= 3 && width + h <= last_width; ++h) {
                            next.loose[n] = h;
                            layers[width + h][n + 1].insert(canonical(next));
                        }
                    });
                }
            }
        }
        layer = Layer{};
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3 && argc != 4) throw std::runtime_error("usage: population first_width last_width [output_directory]");
        const int first = std::stoi(argv[1]);
        const int last = std::stoi(argv[2]);
        if (first < 3 || last < first || last > max_width) throw std::runtime_error("require 3 <= first_width <= last_width <= 26");
        const std::filesystem::path output = argc == 4 ? argv[3] : "";
        if (!output.empty()) {
            if (!std::filesystem::is_directory(output)) throw std::runtime_error("output directory must already exist");
            for (int width = first; width <= last; ++width) {
                const auto path = filename(output, width);
                if (std::filesystem::exists(path) || std::filesystem::exists(path.string() + ".part")) {
                    throw std::runtime_error("output already exists for " + path.string());
                }
            }
        }
        generate(first, last, output);
    } catch (const std::exception& error) {
        std::cerr << "population: " << error.what() << '\n';
        return 1;
    }
}
