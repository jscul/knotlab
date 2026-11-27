#include "read_pattern.hpp"

#include <chrono>
#include <iostream>
#include <string_view>
#include <sys/resource.h>

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    const bool counts_only = argc == 2 && std::string_view(argv[1]) == "--counts-only";
    if (argc != 1 && !counts_only) {
        return 2;
    }
    std::size_t cases;
    if (!(std::cin >> cases)) {
        return 2;
    }
    for (std::size_t i = 0; i < cases; ++i) {
        std::size_t n;
        if (!(std::cin >> n)) {
            return 2;
        }
        std::vector<four_read::Clause> clauses(n);
        for (auto& clause : clauses) {
            for (auto& literal : clause) {
                if (!(std::cin >> literal)) {
                    return 2;
                }
            }
        }
        auto started = std::chrono::steady_clock::now();
        const auto patterns = four_read::patterns(clauses);
        const std::chrono::duration<double> elapsed = std::chrono::steady_clock::now() - started;
        std::cout << patterns.size();
        if (counts_only) {
            rusage usage{};
            if (getrusage(RUSAGE_SELF, &usage) != 0) {
                return 2;
            }
            std::cout << ' ' << elapsed.count() << ' ' << usage.ru_maxrss << '\n';
            continue;
        }
        std::cout << '\n';
        for (const auto& family : patterns) {
            for (const auto& clause : family) {
                for (auto literal : clause) {
                    std::cout << literal << ' ';
                }
            }
            for (const auto& pair : four_read::pairs_of(family)) {
                std::cout << pair[0] << ' ' << pair[1] << ' ';
            }
            std::cout << '\n';
        }
    }
}
