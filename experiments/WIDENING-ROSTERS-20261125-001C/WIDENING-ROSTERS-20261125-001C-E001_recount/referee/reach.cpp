#include <algorithm>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>

using Count = std::uint32_t;

bool read_numbers(std::vector<Count>& values) {
    return static_cast<bool>(std::cin.read(
        reinterpret_cast<char*>(values.data()),
        static_cast<std::streamsize>(values.size() * sizeof(Count))));
}

int main() {
    std::ios::sync_with_stdio(false);

    // Each member's witnessed steps occupy a consecutive range of neighbors.
    std::vector<Count> header(3);
    if (!read_numbers(header)) {
        return 1;
    }
    const Count member_count = header[0];
    const Count last_step = header[1];
    const Count source_limit = header[2];
    std::vector<Count> offsets(member_count + 1);
    std::vector<Count> part_sizes(member_count);
    if (!read_numbers(offsets) || !read_numbers(part_sizes)) {
        return 1;
    }
    std::vector<Count> neighbors(offsets.back());
    if (!read_numbers(neighbors)) {
        return 1;
    }

    std::vector<Count> visited(member_count, 0);
    std::vector<Count> queue(member_count);
    std::vector<Count> cumulative(last_step + 1);
    std::map<std::vector<Count>, Count> spectra;
    const Count sources = source_limit == 0 ? member_count : std::min(source_limit, member_count);
    for (Count index = 0; index < sources; ++index) {
        const Count source = static_cast<Count>(
            (static_cast<std::uint64_t>(index) * member_count) / sources);
        const Count marker = source + 1;
        queue[0] = source;
        visited[source] = marker;
        Count tail = 1;
        Count read = 0;
        Count step = 1;
        cumulative[0] = 1;

        for (; step <= last_step && tail < part_sizes[source] && read < tail; ++step) {
            const Count frontier_end = tail;
            for (; read < frontier_end && tail < part_sizes[source]; ++read) {
                const Count member = queue[read];
                for (Count i = offsets[member]; i < offsets[member + 1]; ++i) {
                    const Count neighbor = neighbors[i];
                    if (visited[neighbor] != marker) {
                        visited[neighbor] = marker;
                        queue[tail++] = neighbor;
                    }
                }
            }
            cumulative[step] = tail;
        }
        std::fill(cumulative.begin() + step, cumulative.end(), tail);
        ++spectra[cumulative];
    }

    for (const auto& [counts, multiplicity] : spectra) {
        std::cout << multiplicity;
        for (const auto count : counts) {
            std::cout << ' ' << count;
        }
        std::cout << '\n';
    }
}
