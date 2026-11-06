# A note: counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs

Status: Proved

Ticket `COUNT-NOTE-20261031-001` (root ticket, program complexity), 2026-10-31.

## What this artifact is

The conversion that `PLAIN-BRACE-20261031-001` recommended and the owner approved ("Yes let's continue"). It contains:
- **The note:** a self-contained 10-page note, `note/counting_note.tex`, built into `note/counting_note.pdf` by `check.py`. The PDF is
  git-ignored.
- **The review package:** a claims table, replay steps and reviewer questions (`review_package.md`).
- **Three scripts:**
  - `replay.py` reruns the eleven cited checks in a temporary copy;
  - `independent.py` recomputes the headline numbers in separately written code;
  - `check.py` ties the note to both.

## What the note states

The theorems are inherited from the cited proofs. The note adds no mathematical claim beyond them.

| Note | Statement | Proved in |
| --- | --- | --- |
| Theorem 1 | On every connected non-2-colourable cubic triple system, #col(H − L) is polynomial: a product of brace factors, the trisum law and two weighted Berman determinants per leaf. | `SEYMOUR-COUNT-20261030-001A`, `-001B` |
| Theorem 2 | Signed systems count in polynomial time unless a trisum square has three twisted branches. | `TWIST-COUNT-20261030-001A` |
| Theorem 3 | #P-hard on Pfaffian graphs under signings. | `SOFT-CROSS-20261031-001A`, `-001B`, `-001C` |
| Theorem 4 | #P-hard without signs, on Pfaffian incidence graphs. | `PLAIN-COUNT-20261031-001A` |
| Theorem 5 | #P-hard on Pfaffian braces. | `PLAIN-BRACE-20261031-001A`, `-001B` |
| Lemma 6 | The signed dictionary: non-colourable iff Pfaffian. | `THREEFOLD-AMPLITUDE-20261030-001C` |
| Theorem 8, Proposition 9 | The trisum law; a leaf's split as weighted determinants. | `SEYMOUR-COUNT` |
| Theorem 11, Proposition 12 | The junction similitude; soft crossings. | `TWIST-COUNT` |
| Lemma 13, Theorem 14 | Snakes and the lattice condition; universality. | `SOFT-CROSS-20261031-001A` |
| Lemma 15, Propositions 16–17 | Signs are path lengths; plain pages twisted; the Fano plane among braces. | `PLAIN-COUNT` |
| Lemmas 18–20, Corollary 21 | The ladder site, the cube junction, the brace lemmas; plain Pfaffian braces. | `PLAIN-BRACE` |

## Evidence

- **`replay.py`.** It copies the eleven cited proofs and the nine proof directories they import from or bind by hash into a temporary
  directory, reruns each check there, and compares each fresh result with the frozen one, ignoring timings.
  - Nine checks reproduce their frozen results exactly.
  - Two depend on Python's per-run hash order. In `SEYMOUR-COUNT-20261030-001B` §2 the symbolic weighted determinants are equal up to
    exchanging a child square's two weights. In `TWIST-COUNT-20261030-001A` §5 the per-instance numbers of random signings of each kind
    agree, with no failures.
  - The tolerance is explicit in the script and recorded per row.
- **`independent.py`.** It imports none of the repository's libraries and recomputes:
  - the soft crossing (40000, −1112, 3336, −192) and the snake multipliers;
  - the cube junction NW and its characteristic polynomial;
  - the K₃,₃ counts through plain braces (80, …, 4159886188) and the recovered 6;
  - sign interpolation;
  - Theorem 1 on Fano compositions (5, 25, 125);
  - the similitude identity (constant 1 in all 32 cases, −1 with a host leg sign flipped).
- **`check.py`.** It ties the 33 numbers quoted in the note to the frozen results and the independent replay, checks that every cited ticket
  is named, compiles the note, and catches four tampering controls.

## Literature (bounded searches, 2026-10-31)

No statement of Theorems 1–5 was found. The searches covered:
- counting 2-colourings of square or non-2-colourable hypergraphs;
- Pfaffian and holographic counting beyond planar graphs;
- #P-hardness on Pfaffian graphs;
- not-all-equal counting with three occurrences.

Nearest results:
- Fan and Cai 2020 (hardness on general graphs);
- Valiant (planar);
- Robertson, Seymour and Thomas, and McCuaig (Pfaffian brace structure; recognition);
- Cai, Guo and Williams, holographic algorithms beyond matchgates (affine and product types, not Pfaffian graphs);
- decision results: bicolourability is polynomial at three occurrences per variable.

Folklore risk is assessed per result in the note's table.

## Nonclaims

- **No human or external review.** Sharing is the owner's decision; nothing has been sent.
- **No new theorem.** The note presents the cited proofs.
- **Not every case is run end to end.** The many-site interpolation is proved, not run, as in the cited tickets.
