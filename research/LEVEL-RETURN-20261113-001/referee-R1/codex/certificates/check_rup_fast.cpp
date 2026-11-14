// Fresh DRUP verifier: input DIMACS and gzipped proof; no SAT-solver dependency.
// Deletions are ignored. Every retained addition must be RUP, ending in empty.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>
#include <zlib.h>

class Checker {
    int variables;
    std::vector<std::vector<int>> clauses, watches;
    std::vector<int> units, trail;
    std::vector<int8_t> values;
    bool initially_empty = false;
    static std::size_t key(int lit) { return 2 * std::abs(lit) + (lit < 0); }
    int value(int lit) const { return lit > 0 ? values[lit] : -values[-lit]; }
    bool assign(int lit) {
        int state = value(lit);
        if (state) return state > 0;
        values[std::abs(lit)] = lit > 0 ? 1 : -1;
        trail.push_back(lit);
        return true;
    }
public:
    explicit Checker(int n) : variables(n), watches(2 * (n + 1)), values(n + 1, 0) {}
    void add(const std::vector<int>& raw) {
        std::vector<int> clause;
        std::unordered_set<int> used;
        for (int lit : raw) {
            if (!lit || std::abs(lit) > variables) throw std::runtime_error("literal out of bounds");
            if (used.insert(lit).second) clause.push_back(lit);
        }
        if (clause.empty()) initially_empty = true;
        else if (clause.size() == 1) units.push_back(clause[0]);
        else {
            int id = static_cast<int>(clauses.size());
            clauses.push_back(std::move(clause));
            watches[key(clauses[id][0])].push_back(id);
            watches[key(clauses[id][1])].push_back(id);
        }
    }
    bool rup(const std::vector<int>& candidate) {
        for (int lit : trail) values[std::abs(lit)] = 0;
        trail.clear();
        if (initially_empty) return true;
        for (int lit : units) if (!assign(lit)) return true;
        // Assumption order changes runtime, never the unit-propagation closure.
        // Expanded conditional proofs place their common guard last: queue it
        // first, without changing the stored clause's watch order.
        for (auto position = candidate.rbegin(); position != candidate.rend(); ++position) {
            int lit = *position;
            if (!lit || std::abs(lit) > variables) throw std::runtime_error("proof variable out of bounds");
            if (!assign(-lit)) return true;
        }
        std::size_t cursor = 0;
        while (cursor < trail.size()) {
            int false_lit = -trail[cursor++];
            auto& bucket = watches[key(false_lit)];
            std::size_t i = 0;
            while (i < bucket.size()) {
                auto& clause = clauses[bucket[i]];
                if (clause[0] == false_lit) std::swap(clause[0], clause[1]);
                if (clause[1] != false_lit) throw std::runtime_error("invalid watch invariant");
                if (value(clause[0]) > 0) { ++i; continue; }
                std::size_t replacement = 2;
                while (replacement < clause.size() && value(clause[replacement]) < 0) ++replacement;
                if (replacement < clause.size()) {
                    std::swap(clause[1], clause[replacement]);
                    watches[key(clause[1])].push_back(bucket[i]);
                    bucket[i] = bucket.back();
                    bucket.pop_back();
                } else {
                    if (!assign(clause[0])) return true;
                    ++i;
                }
            }
        }
        return false;
    }
};

static bool gzline(gzFile file, std::string& line) {
    char buffer[65536];
    line.clear();
    while (gzgets(file, buffer, sizeof(buffer))) {
        line += buffer;
        if (!line.empty() && line.back() == '\n') return true;
    }
    return !line.empty();
}

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("usage: check_rup_fast input.cnf proof.drup.gz");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("cannot open DIMACS");
        std::string line;
        int n = -1, expected = -1, count = 0;
        while (std::getline(input, line)) {
            if (line.empty() || line[0] == 'c') continue;
            std::istringstream header(line);
            std::string p, format;
            if (!(header >> p >> format >> n >> expected) || p != "p" || format != "cnf" || n < 0 || expected < 0)
                throw std::runtime_error("invalid DIMACS header");
            break;
        }
        if (n < 0) throw std::runtime_error("missing DIMACS header");
        Checker checker(n);
        std::vector<int> clause;
        while (std::getline(input, line)) {
            if (line.empty() || line[0] == 'c') continue;
            std::istringstream parser(line);
            int lit;
            while (parser >> lit) {
                if (!lit) { checker.add(clause); clause.clear(); ++count; }
                else clause.push_back(lit);
            }
            if (!parser.eof()) throw std::runtime_error("invalid DIMACS token");
        }
        if (!clause.empty() || count != expected) throw std::runtime_error("DIMACS clause count mismatch");
        gzFile proof = gzopen(argv[2], "rb");
        if (!proof) throw std::runtime_error("cannot open proof");
        std::size_t line_no = 0, additions = 0, deletions = 0;
        while (gzline(proof, line)) {
            ++line_no;
            if (line.empty() || line[0] == '\n' || line[0] == 'c') continue;
            if (line[0] == 'd') { ++deletions; continue; }
            std::istringstream parser(line);
            clause.clear();
            int lit;
            bool terminated = false;
            while (parser >> lit) {
                if (terminated) throw std::runtime_error("tokens after proof terminator");
                if (!lit) terminated = true;
                else clause.push_back(lit);
            }
            if (!terminated || !parser.eof()) throw std::runtime_error("invalid proof clause");
            if (!checker.rup(clause)) {
                gzclose(proof);
                std::cout << "{\"valid\":false,\"line\":" << line_no << ",\"reason\":\"addition is not RUP\"}\n";
                return 1;
            }
            ++additions;
            if (clause.empty()) {
                gzclose(proof);
                std::cout << "{\"valid\":true,\"additions\":" << additions
                          << ",\"ignored_deletions\":" << deletions
                          << ",\"empty_clause_line\":" << line_no << "}\n";
                return 0;
            }
            checker.add(clause);
        }
        gzclose(proof);
        std::cout << "{\"valid\":false,\"reason\":\"no derived empty clause\"}\n";
        return 1;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}
