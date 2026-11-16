// Read the topologically sorted reachable affine guards and price every signed coordinate lemma.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

using Bits = std::array<std::uint64_t, 8>;
using Costs = std::array<int, 4>;
constexpr int infinity = 100000;

struct State {
    int ordinary, implied;
    Bits fixed;
    std::array<int, 2> checks;
    std::array<int, 18> branches;
};

bool intersects(const Bits& a, const Bits& b) {
    for (int word = 0; word < 8; ++word)
        if (a[word] & b[word]) return true;
    return false;
}

Bits sector(int guard, int conclusion) {
    Bits out{};
    for (int row = 0; row < 512; ++row) {
        auto accepts = [row](int literal) { return ((row >> (literal / 2)) & 1) == (literal % 2); };
        if (accepts(guard) && accepts(conclusion)) out[row / 64] |= std::uint64_t{1} << (row % 64);
    }
    return out;
}

Costs price(const std::vector<State>& states, int guard, int conclusion) {
    const Bits good = sector(guard, conclusion), bad = sector(guard, conclusion ^ 1);
    std::vector<Costs> score(states.size());
    for (std::size_t i = 0; i < states.size(); ++i) {
        const auto& s = states[i];
        auto& cost = score[i];
        cost = {s.ordinary, infinity, infinity, infinity};
        if (!intersects(s.fixed, good) || !intersects(s.fixed, bad)) continue;
        const bool has_guard = (s.implied >> guard) & 1;
        if (has_guard) {
            int after = s.branches[conclusion];
            if (after < 0) throw std::runtime_error("live cut did not divide raw guard");
            if (intersects(states[after].fixed, good)) cost[1] = 1 + states[after].ordinary;
        }
        for (int child : s.checks) {
            if (child < 0) continue;
            for (int k = 1; k <= 3; ++k) cost[k] = std::min(cost[k], 1 + score[child][k]);
        }
        for (int q = 0; q < 9; ++q) {
            int lo = s.branches[2*q], hi = s.branches[2*q+1];
            if (lo < 0) continue;
            for (int left = 0; left <= 3; ++left) {
                if (score[lo][left] == infinity) continue;
                for (int right = 0; right <= 3; ++right) {
                    if (left + right == 0 || score[hi][right] == infinity) continue;
                    int k = std::min(2, left + right);
                    if (left == 3 || right == 3 || (left && right && !has_guard)) k = 3;
                    cost[k] = std::min(cost[k], 1 + score[lo][left] + score[hi][right]);
                }
            }
        }
    }
    const int under_guard = states.back().branches[guard];
    const int forbidden = states.at(under_guard).branches[conclusion ^ 1];
    auto result = score.back();
    for (int k = 1; k <= 3; ++k)
        result[k] = std::min(infinity, result[k] + states.at(forbidden).ordinary);
    return result;
}

int main() {
    int count;
    if (!(std::cin >> count) || count < 1) return 1;
    std::vector<State> states(count);
    for (int i = 0; i < count; ++i) {
        auto& s = states[i];
        std::cin >> s.ordinary >> s.implied;
        for (auto& word : s.fixed) std::cin >> word;
        for (int& child : s.checks) std::cin >> child;
        for (int& child : s.branches) std::cin >> child;
        if (!std::cin) throw std::runtime_error("missing reachable-state input");
        int ordinary = infinity;
        for (int child : s.checks) {
            if (child >= i) throw std::runtime_error("non-decreasing check child");
            if (child >= 0) ordinary = std::min(ordinary, 1 + states[child].ordinary);
        }
        for (int q = 0; q < 9; ++q) {
            int lo = s.branches[2*q], hi = s.branches[2*q+1];
            if (lo >= i || hi >= i || (lo < 0) != (hi < 0)) throw std::runtime_error("invalid query children");
            if (lo >= 0) ordinary = std::min(ordinary, 1 + states[lo].ordinary + states[hi].ordinary);
        }
        if (ordinary == infinity) ordinary = 1;
        if (ordinary != s.ordinary) throw std::runtime_error("ordinary cost mismatch");
    }
    for (int guard = 0; guard < 18; ++guard) {
        for (int conclusion = 0; conclusion < 18; ++conclusion) {
            if (guard / 2 == conclusion / 2) continue;
            auto result = price(states, guard, conclusion);
            std::cout << guard << ' ' << conclusion;
            for (int cost : result) std::cout << ' ' << cost;
            std::cout << '\n';
        }
    }
}
