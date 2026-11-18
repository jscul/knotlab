// One fixture per line: width, number of junctions, then parity supports as
// unsigned decimal bit masks. Output the lexicographic upper triangle of K
// as two hexadecimal digits per entry (ff for infinity).

#include <algorithm>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using Word = std::uint64_t;
using Shore = std::uint32_t;
constexpr unsigned Infinity = 255;

void require(bool condition, const char* message) {
    if (!condition)
        throw std::runtime_error(message);
}

bool connected(Shore side, const std::vector<Shore>& neighbors) {
    Shore pending = side & -side;
    Shore seen = pending;
    while (pending) {
        const Shore add = neighbors[std::countr_zero(pending)] & side & ~seen;
        seen |= add;
        pending = (pending & (pending - 1)) | add;
    }
    return seen == side;
}

std::string table(int width, const std::vector<Word>& stars) {
    const auto exterior = static_cast<int>(stars.size());
    const Shore ordinary = (Shore{1} << exterior) - 1;
    const Shore all = (ordinary << 1) | 1;
    const Word bits = (Word{1} << width) - 1;
    std::vector<Shore> incident(width), neighbors(exterior + 1);
    for (int site = 0; site < exterior; ++site) {
        require(stars[site] && !(stars[site] & ~bits), "invalid parity support");
        for (Word row = stars[site]; row; row &= row - 1)
            incident[std::countr_zero(row)] |= Shore{1} << site;
    }
    for (Shore ends : incident) {
        const int count = std::popcount(ends);
        require(count == 1 || count == 2, "invalid bit incidence");
        const int a = std::countr_zero(ends);
        const int b = count == 1 ? exterior : static_cast<int>(std::bit_width(ends)) - 1;
        neighbors[a] |= Shore{1} << b;
        neighbors[b] |= Shore{1} << a;
    }
    require(connected(all, neighbors), "disconnected augmented junction graph");

    // XORs of the junction rows are precisely cut supports, choosing the
    // shore without the exterior vertex. A nonempty cut is inclusion-minimal
    // exactly when both shores are connected. A disconnected shore gives a
    // proper cut inside it. When both shores are connected, a contained cut
    // must be constant on each shore and so is the whole cut if nonempty.
    std::vector<Word> boundary(ordinary + 1);
    std::vector<std::vector<Word>> bonds(width + 1);
    for (Shore shore = 1; shore <= ordinary; ++shore) {
        boundary[shore] = stars[std::countr_zero(shore)] ^ boundary[shore & (shore - 1)];
        const Word support = boundary[shore];
        if (std::popcount(support) >= 2 && connected(shore, neighbors) && connected(all ^ shore, neighbors))
            bonds[std::popcount(support)].push_back(support);
    }

    std::vector<std::vector<unsigned>> result(width, std::vector<unsigned>(width, Infinity));
    std::vector<Word> unresolved(width);
    int remaining = width * (width - 1) / 2;
    for (int a = 0; a < width; ++a)
        unresolved[a] = bits & ~((Word{1} << (a + 1)) - 1);
    for (int size = 2; size <= width && remaining; ++size) {
        for (Word bond : bonds[size]) {
            for (Word first = bond; first; first &= first - 1) {
                const int a = std::countr_zero(first);
                Word novel = bond & unresolved[a];
                unresolved[a] ^= novel;
                remaining -= std::popcount(novel);
                for (; novel; novel &= novel - 1)
                    result[a][std::countr_zero(novel)] = size;
            }
            if (remaining == 0)
                break;
        }
    }

    constexpr char hex[] = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(width * (width - 1));
    for (int a = 0; a < width; ++a)
        for (int b = a + 1; b < width; ++b) {
            const unsigned value = result[a][b];
            encoded.push_back(hex[value >> 4]);
            encoded.push_back(hex[value & 15]);
        }
    return encoded;
}

}  // namespace

int main() {
    try {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        int width = 0, count = 0;
        while (std::cin >> width) {
            require(static_cast<bool>(std::cin >> count), "missing junction count");
            require(3 <= width && width <= 63 && 1 <= count && count <= 20, "fixture outside supported range");
            std::vector<Word> stars(count);
            for (Word& star : stars)
                require(static_cast<bool>(std::cin >> star), "missing parity support");
            std::cout << table(width, stars) << '\n';
        }
        require(std::cin.eof(), "malformed fixture input");
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
