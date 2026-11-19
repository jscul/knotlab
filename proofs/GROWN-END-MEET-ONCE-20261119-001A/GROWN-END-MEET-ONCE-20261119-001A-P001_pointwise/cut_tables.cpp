// Compute every minimum common bond by scanning all connected shores.
// Input gives the holders of each distinction. The final vertex is outside.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

using Mask = std::uint64_t;

bool connected(Mask shore, const std::vector<Mask>& adjacent) {
    if (!shore) return false;
    Mask pending = shore & -shore;
    Mask seen = pending;
    while (pending && seen != shore) {
        int u = std::countr_zero(pending);
        pending &= pending - 1;
        Mask unseen = adjacent[u] & shore & ~seen;
        seen |= unseen;
        pending |= unseen;
    }
    return seen == shore;
}

int main() {
    int ordinary, width;
    if (!(std::cin >> ordinary >> width) || ordinary < 1 || ordinary > 28 || width < 2 || width > 63)
        throw std::runtime_error("unsupported literal table dimensions");
    std::vector<Mask> adjacency(ordinary+1), rows(ordinary+1);
    for (int i=0; i<width; ++i) {
        int u,v;
        if (!(std::cin >> u >> v) || u < 0 || v <= u || v > ordinary)
            throw std::runtime_error("invalid holders");
        adjacency[u] |= Mask{1} << v;
        adjacency[v] |= Mask{1} << u;
        rows[u] |= Mask{1} << i;
        rows[v] |= Mask{1} << i;
    }
    const Mask limit = Mask{1} << ordinary;
    const Mask all = (limit << 1) - 1;
    if (!connected(all,adjacency)) throw std::runtime_error("disconnected");
    std::vector<std::vector<int>> minimum(width,std::vector<int>(width,width+1));
    Mask shore=0, cut=0, bonds=0;
    for (Mask i=1; i<limit; ++i) {
        int changed = std::countr_zero(i);
        shore ^= Mask{1} << changed;
        cut ^= rows[changed];
        if (!connected(shore,adjacency) || !connected(all ^ shore,adjacency)) continue;
        ++bonds;
        int size = std::popcount(cut);
        for (Mask left=cut; left; left &= left-1) {
            int a=std::countr_zero(left);
            for (Mask right=left&(left-1); right; right &= right-1) {
                int b=std::countr_zero(right);
                minimum[a][b]=std::min(minimum[a][b],size);
            }
        }
    }
    std::cout << bonds << '\n';
    for (int i=0; i<width-1; ++i) {
        for (int j=i+1; j<width; ++j)
            std::cout << (minimum[i][j]<=width ? minimum[i][j]-1 : -1) << ' ';
        std::cout << '\n';
    }
}
