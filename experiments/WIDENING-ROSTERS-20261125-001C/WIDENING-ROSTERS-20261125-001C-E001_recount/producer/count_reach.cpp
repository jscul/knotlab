#include <cstddef>
#include <new>
#include <vector>

extern "C" int count_reach(
    const int* offsets,
    const int* adjacent,
    int member_count,
    int maximum_steps,
    int* counts
) {
    try {
        std::vector<int> seen(member_count, -1);
        std::vector<int> queue(member_count);
        const std::size_t stride = std::size_t(maximum_steps) + 1;

        for (int source = 0; source < member_count; ++source) {
            int* from_source = counts + std::size_t(source) * stride;
            int next = 0;
            int reached = 1;
            queue[0] = source;
            seen[source] = source;
            from_source[0] = reached;

            for (int steps = 1; steps <= maximum_steps; ++steps) {
                const int frontier_end = reached;
                while (next < frontier_end) {
                    const int current = queue[next++];
                    for (int i = offsets[current]; i < offsets[current + 1]; ++i) {
                        const int candidate = adjacent[i];
                        if (seen[candidate] != source) {
                            seen[candidate] = source;
                            queue[reached++] = candidate;
                        }
                    }
                }
                from_source[steps] = reached;
            }
        }
    } catch (const std::bad_alloc&) {
        return 1;
    }
    return 0;
}
