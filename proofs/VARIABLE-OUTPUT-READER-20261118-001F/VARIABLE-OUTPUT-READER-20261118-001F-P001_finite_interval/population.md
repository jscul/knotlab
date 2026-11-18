# Exact population producer

Build the C++20 producer from the repository root. The directory must
already exist with no files at the requested output names.

```sh
scratch=/var/tmp/presp-interval-ERF-20261118
source=proofs/VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/population.cpp
g++ -std=c++20 -O3 -march=native -Wall -Wextra "$source" -o "$scratch/population"
"$scratch/population" 21 26 "$scratch"
```

Each `widthNN.txt` is published atomically. Each headerless line gives
`j`, then `j` decimal masks of ordinary neighbors, then `j` loose counts.
Bit `i` of a neighbor mask stands for site `i`, starting at zero. The row
labels come from canonical labeling. The physical width is the number of
ordinary meetings plus the sum of the loose counts.

## Why the population is complete

A representation consists of the ordinary graph and one loose count per
site. Loose distinctions at the same holder are interchangeable, so an
extension is specified up to isomorphism by its parent set and its fresh
count. The producer starts from the one-site, three-distinction seed. It
visits each set of one, two, or three distinct loose holders, requires a
common ordinary neighbor for every pair, and rejects a common ordinary
neighbor of all three. It applies both fresh counts. The consequence of
each move depends only on the current representation.

The parent loop treats sites with the same loose count and a swappable
ordinary neighborhood as interchangeable. It selects the first members
of each such class. The omitted choices are carried to included choices
by transpositions preserving the old graph and its loose counts.

Canonicalization starts with cells ordered by loose count and ordinary
degree. It refines each cell by its members' neighbor counts in all cells.
For a remaining cell it tries every individualization, with the same
transposition reduction, and selects the smallest full graph encoding.
The ordering of cells and the choice of a cell to split are invariant
under relabeling. Thus two isomorphic inputs reach the same minimum.
Equality of the full encodings at each site count implies isomorphism,
since the encoding gives every ordinary meeting and loose count. The hash
table stores and compares the full encodings.

Induction on width now gives completeness. Each nonseed presentation is
obtained by a legal extension of a smaller width, and substituting its
canonical predecessor preserves all subsequent choices up to relabeling.
Every inserted type has a legal history by construction. Distinct
histories realizing the same type are counted once.

## Validation and output

An independent exact colored graph matching gave a bijection with the
archived populations at widths 18, 19, and 20, containing 3,495, 8,191,
and 19,414 types. Computing every literal legal triple directly from the
output masks and loose counts matched the archived site-stratum counts
at widths 19 and 20. A separate subset search found a legal birth order
for 65 deterministic samples per target width. This search used only the
finished graph and loose counts. [Width 18](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/result.json) · [Width 19](../../VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/result.json) · [Width 20](../../VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/result.json)

| Width | 7 sites | 8 sites | 9 sites | 10 sites | 11 sites | 12 sites | Total |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 21 | 432 | 13,600 | 28,312 | 4,105 | 0 | 0 | 46,449 |
| 22 | 0 | 12,731 | 64,016 | 35,588 | 0 | 0 | 112,335 |
| 23 | 0 | 7,720 | 102,080 | 148,891 | 15,151 | 0 | 273,842 |
| 24 | 0 | 2,334 | 118,708 | 396,093 | 155,289 | 0 | 672,424 |
| 25 | 0 | 0 | 98,241 | 745,098 | 762,451 | 55,962 | 1,661,752 |
| 26 | 0 | 0 | 52,428 | 1,037,818 | 2,373,823 | 667,274 | 4,131,343 |

The serial producer ran in 11.37 seconds with peak resident memory of
233,272 KiB. Its 6,898,145 rows occupy 426,389,843 bytes in the designated
scratch directory. The file hashes are recorded below.

```text
1386477d994ff1df589ebce1679ece43c0a027d5f3545f7f318e673cb7c5933f  width21.txt
66ad8b342fea98d5ee20c27ffe8913a7fabbea31e48158d6819b191adbc77252  width22.txt
9621b1940db686529babf128634a42c98b3f506e0e6f7a488b196417ce3b20be  width23.txt
7afe43a6472c15a438530ae7339fa4d6de4c24e816fdfffff90dc35435b7bb1a  width24.txt
55ae51a7c198b3895d5f409d7cd08e4a4c9b4d897567f0873aaeeba48a226413  width25.txt
abfff74b2b6fa91625f295527c5016fe2b25e33e465a85976908092378264fed  width26.txt
```
