// Exact binary prefix children with bit-packed blocker certificates.
struct PackedWitness {
    Id vertex;
    bool earlier;
    std::vector<std::pair<Id, Word>> blockers;
};

struct Packed {
    std::vector<Word> names;
    std::vector<PackedWitness> cache;
    std::uint32_t weight = 1, ancestor = 0, next_witness = 0;

    explicit Packed(int words) : names(words) {}
    Packed(int words, const Clique& c, int label) : names(words), ancestor(label) {
        for (Id u : c) names[u / 64] |= Word{1} << (u % 64);
    }
    Clique list() const {
        Clique c;
        for (int w = 0; w < int(names.size()); ++w) {
            Word x = names[w];
            while (x) { c.push_back(w * 64 + std::countr_zero(x)); x &= x - 1; }
        }
        return c;
    }
};

struct PackedSplitter {
    const Graph& graph;
    std::vector<Word> kept, possible;

    explicit PackedSplitter(const Graph& g) : graph(g), kept(g.stride), possible(g.stride) {}

    void remember(Packed& c, int vertex, int words) const {
        PackedWitness witness{static_cast<Id>(vertex), true, {}};
        const Word* neighbors = graph.row(vertex);
        for (int w = 0; w < words; ++w) {
            const Word blockers = c.names[w] & ~neighbors[w];
            if (!blockers) continue;
            witness.blockers.emplace_back(w, blockers);
            if (blockers & before(w, vertex)) witness.earlier = false;
        }
        require(!witness.blockers.empty(), "prefix parent was extendible");
        if (c.cache.size() < 12) c.cache.push_back(std::move(witness));
        else c.cache[c.next_witness++ % 12] = std::move(witness);
    }

    bool secondary(Packed& c, int v) {
        const int words = (v + 63) / 64;
        const Word* adjacent = graph.row(v);
        for (const auto& test : c.cache) {
            if (!test.earlier && !graph.meets(v, test.vertex)) continue;
            bool still_blocks = false;
            for (const auto& [w, mask] : test.blockers) if (adjacent[w] & mask) { still_blocks = true; break; }
            if (!still_blocks) return false;
        }
        int last_drop = -1;
        for (int w = 0; w < words; ++w) {
            kept[w] = c.names[w] & adjacent[w];
            const Word dropped = c.names[w] ^ kept[w];
            if (dropped) last_drop = w * 64 + 63 - std::countl_zero(dropped);
        }
        if (last_drop < 0) {
            const int w = v / 64;
            const Word bit = Word{1} << (v % 64);
            c.names[w] |= bit;
            for (auto& test : c.cache) if (!graph.meets(test.vertex, v)) {
                if (!test.blockers.empty() && test.blockers.back().first == w) test.blockers.back().second |= bit;
                else test.blockers.emplace_back(w, bit);
            }
            return false;
        }
        for (int w = 0; w < words; ++w)
            possible[w] = (adjacent[w] | before(w, last_drop)) & before(w, v) & ~c.names[w];
        // Each incompatible witness supplies a whole-neighborhood constraint common
        // to every subsequent test. Thus a failed candidate prunes other candidates too.
        for (int w = 0; w < words; ++w) {
            while (possible[w]) {
                const int y = w * 64 + std::countr_zero(possible[w]);
                const Word* neighbors = graph.row(y);
                int blocker = -1;
                for (int k = 0; k < words; ++k) {
                    const Word obstruction = kept[k] & ~neighbors[k];
                    if (obstruction) { blocker = k * 64 + std::countr_zero(obstruction); break; }
                }
                if (blocker >= 0) {
                    const Word* admissible = graph.row(blocker);
                    for (int k = w; k < words; ++k) possible[k] &= admissible[k];
                    continue;
                }
                bool earlier = true;
                if (!graph.meets(v, y)) {
                    for (int k = 0; k <= w; ++k) {
                        if (c.names[k] & ~neighbors[k] & before(k, y)) { earlier = false; break; }
                    }
                }
                if (earlier) { remember(c, y, words); return false; }
                possible[w] &= possible[w] - 1;
            }
        }
        // A prior branch test could have left data above this prefix.
        std::fill(kept.begin() + words, kept.end(), 0);
        kept[v / 64] |= Word{1} << (v % 64);
        return true;
    }

    void advance(std::vector<Packed>& population, std::vector<Packed>& scratch, int v) {
        scratch.clear();
        for (auto& old : population) {
            if (secondary(old, v)) {
                Packed child(graph.stride);
                child.names = kept;
                child.ancestor = old.ancestor;
                child.weight = old.weight;
                scratch.push_back(std::move(child));
            }
            scratch.push_back(std::move(old));
        }
        population.swap(scratch);
    }
};

void resample_packed(std::vector<Packed>& particles, Word n, Word mass, Word offset) {
    Word end = 0, previous = 0;
    std::size_t kept = 0;
    for (auto& c : particles) {
        end += c.weight;
        const Word boundary = end * n;
        const Word count = boundary > offset ? 1 + (boundary - 1 - offset) / mass : 0;
        if (count > previous) {
            c.weight = count - previous;
            if (kept != static_cast<std::size_t>(&c - particles.data())) particles[kept] = std::move(c);
            ++kept;
            previous = count;
        }
    }
    require(end == mass && previous == n, "packed resampling lost population");
    particles.erase(particles.begin() + kept, particles.end());
}
