// Measure successive incidence records with the verified connected-cut engine.
#define main finite_interval_main
#include "../../VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/compare.cpp"
#undef main

int main() {
    try {
        std::string row;
        std::uint64_t line = 0;
        while (std::getline(std::cin, row)) {
            Fixture fixture = parse(row, ++line);
            Table table = remeasure(fixture);
            for (int a = 0; a < table.width; ++a) {
                for (int b = a + 1; b < table.width; ++b) {
                    const int d = table.rows[a][b];
                    require(d != Infinity, "disconnected pair in a binary-third incidence");
                    std::cout.put(static_cast<char>('!' + d + 1));
                }
            }
            std::cout.put('\n');
        }
    } catch (const std::exception& error) {
        std::cerr << "census: " << error.what() << '\n';
        return 1;
    }
}
