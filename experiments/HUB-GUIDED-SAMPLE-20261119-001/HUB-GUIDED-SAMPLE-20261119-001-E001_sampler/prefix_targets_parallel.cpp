// Schedule independent replicas with one read-only prepared graph.
// Compile beside the frozen anneal.cpp and its frozen dependency files.
#include <filesystem>
#include <sys/wait.h>
#include <unistd.h>
#include "anneal_entry_adapter.cpp"

namespace {
bool held_part(const Roster& input, const Prepared& prepared, int left, int past) {
    if (left == past) return true;
    for (const auto& block : input.members) {
        int seen = 0;
        for (int original : block) {
            const int local = prepared.position[original];
            seen += left <= local && local < past;
        }
        if (seen == past - left) return true;
    }
    return false;
}

SeedPopulation read_two_block_bank(std::istream& in, const Prepared& data, int population,
                                   const std::vector<bool>& initial, int inside) {
    SeedPopulation start;
    start.prefix = data.prefix;
    auto positive = [](const std::string& s) {
        return !s.empty() && s.find_first_not_of("0123456789") == std::string::npos
               && s.find_first_not_of('0') != std::string::npos;
    };
    require(bool(in >> start.numerator >> start.denominator) && positive(start.numerator) && positive(start.denominator),
            "invalid bank mass");
    const int words = (inside + 63) / 64;
    for (int i = 0; i < population; ++i) {
        int length;
        require(bool(in >> length) && length > 0 && length <= data.prefix, "invalid bank clique size");
        Clique names;
        names.reserve(length);
        std::vector<Word> retained(words), expected(words);
        std::vector<bool> picked(data.prefix - inside);
        for (int j = 0; j < length; ++j) {
            int physical;
            require(bool(in >> physical) && physical >= 0 && physical < int(initial.size()) && initial[physical],
                    "bank member outside prefix");
            const int u = data.position[physical];
            names.push_back(u);
            if (u < inside) retained[u / 64] |= Word{1} << (u % 64);
            else picked[u - inside] = true;
        }
        std::sort(names.begin(), names.end());
        require(std::adjacent_find(names.begin(), names.end()) == names.end(), "duplicate bank name");
        for (int w = 0; w < words; ++w) expected[w] = before(w, inside);
        for (int u = inside; u < data.prefix; ++u) {
            if (!picked[u - inside]) continue;
            const Word* neighbors = data.graph.row(u);
            for (int w = 0; w < words; ++w) expected[w] &= neighbors[w];
        }
        require(expected == retained, "bank did not retain the full compatible part of its large block");
        for (int u = inside; u < data.prefix; ++u) {
            if (picked[u - inside]) continue;
            const Word* neighbors = data.graph.row(u);
            bool blocked = false;
            for (int w = 0; w < words; ++w) blocked |= bool(retained[w] & ~neighbors[w]);
            require(blocked, "bank excluded a compatible outsider");
        }
        start.samples.push_back(std::move(names));
    }
    return start;
}

void wait_one(int& running) {
    int status = 0;
    const pid_t done = waitpid(-1, &status, 0);
    require(done > 0 && WIFEXITED(status) && WEXITSTATUS(status) == 0, "replicate failed");
    --running;
}

void save_seed(const Prepared& prepared, const SeedPopulation& start, const Observations& observer, int particles, Word seed,
               const std::filesystem::path& output) {
    const std::filesystem::path final = output / ("seed-" + std::to_string(seed) + ".jsonl");
    const std::filesystem::path pending = final.string() + ".pending";
    std::ofstream spool(pending);
    require(bool(spool), "cannot open replicate receipt");
    auto* prior = std::cout.rdbuf(spool.rdbuf());
    estimate(prepared.graph, particles, 0, 0, 4, 0, seed, prepared.graph.size, &start, &observer);
    std::cout.flush();
    std::cout.rdbuf(prior);
    spool.close();
    require(bool(spool), "cannot write replicate receipt");
    std::filesystem::rename(pending, final);
}
}  // namespace

int main(int argc, char** argv) {
    try {
        require(argc == 11, "usage: parallel ROSTER BANK OUT ORDER_SEED BASE_SEED PARTICLES BEGIN END WORKERS INSIDE");
        const auto input = read(argv[1]);
        std::ifstream bank(argv[2]);
        const std::filesystem::path output(argv[3]);
        const Word order_seed = std::stoull(argv[4]), base = std::stoull(argv[5]);
        const int particles = std::stoi(argv[6]), begin = std::stoi(argv[7]), end = std::stoi(argv[8]);
        const int workers = std::stoi(argv[9]), inside = std::stoi(argv[10]);
        require(particles > 0 && begin >= 0 && begin < end && workers > 0, "invalid replica range");
        std::vector<bool> initial(input.n);
        int n;
        require(bool(bank >> n) && n > 0 && n <= input.n, "invalid prefix length");
        std::vector<int> prefix(n);
        for (int& u : prefix) {
            require(bool(bank >> u) && u >= 0 && u < input.n && !initial[u], "invalid prefix member");
            initial[u] = true;
        }
        std::string unused;
        std::getline(bank, unused);
        for (int k = 0; k < begin * (particles + 1); ++k)
            require(bool(std::getline(bank, unused)), "short bank before the requested range");
        const Prepared prepared = seeded_order(input, prefix, "degree-up", order_seed);
        require(inside > 0 && inside <= n && n - inside <= 14 && prepared.prefix == n && prepared.graph.size == input.n,
                "invalid prefolded two-block boundary");
        for (int i = 0; i < n; ++i) require(prepared.position[prefix[i]] == i, "prefix order changed");
        require(held_part(input, prepared, 0, inside) && held_part(input, prepared, inside, n),
                "each part of the prefix must lie in an actual block");
        auto observer = marks(prepared, input);
        observer.draws = 0;
        std::filesystem::create_directories(output);
        int running = 0;
        for (int i = begin; i < end; ++i) {
            if (running == workers) wait_one(running);
            const auto offset = bank.tellg();
            require(offset >= 0, "missing bank offset");
            for (int j = 0; j <= particles; ++j)
                require(bool(std::getline(bank, unused)), "short bank at a requested replica");
            const pid_t child = fork();
            require(child >= 0, "could not fork independent replicate");
            if (child == 0) {
                try {
                    std::ifstream source(argv[2]);
                    source.seekg(offset);
                    require(bool(source), "could not locate independent bank rows");
                    const auto seeds = read_two_block_bank(source, prepared, particles, initial, inside);
                    save_seed(prepared, seeds, observer, particles, base + i, output);
                    std::_Exit(0);
                } catch (const std::exception& error) {
                    std::cerr << error.what() << '\n';
                    std::_Exit(1);
                }
            }
            ++running;
        }
        while (running) wait_one(running);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
