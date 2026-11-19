# Exact growing-end inputs for the hub-guided sample

The input roster preserves all fourteen named unread histories. The target for each is the first round after its last retained WALL-READ stage. Every target has its actual one-round-earlier precursor, with the target's parent IDs in that precursor's numbering. The export also retains age-eight comparisons where the archive supplies them, and age seven of start-03 for the known 28,065-birth calibration. [Input manifest and literal starts](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/stages.json) · [Retained stages](../WALL-READ-20261119-001/wall_read.md)

| History | Live input age | Live junctions | First unread round | Exact offshoots in that round |
|---|---:|---:|---:|---:|
| start-01 | 10 | 21,516 | 11 | 0 |
| start-02 | 9 | 102,871 | 10 | 0 |
| start-03 | 8 | 28,065 | 9 | 1 |
| start-05 | 9 | 102,871 | 10 | 0 |
| start-06 | 7 | 12,004 | 8 | 0 |
| start-07 | 7 | 31,735 | 8 | 0 |
| start-08 | 9 | 102,871 | 10 | 0 |
| start-09 | 6 | 4,652 | 7 | 0 |
| start-10 | 7 | 4,157 | 8 | 0 |
| start-11 | 7 | 3,493 | 8 | 0 |
| start-12 | 7 | 36,394 | 8 | 0 |
| start-13 | 7 | 35,408 | 8 | 0 |
| start-14 | 8 | 162,336 | 9 | 1 |
| start-15 | 8 | 38,001 | 9 | 0 |

## Format and checks

The shared input folder is `/var/tmp/hub-sample-20261119`. Its `index.json` gives the age, target round, exact counts and file hashes. `start-XX-ageYY.txt` has the number of live junctions and maximal blocks on the first line, followed by one row of zero-based live IDs per maximal block. The gzip JSON parent sidecar gives the actual previous live IDs for each child, including parents whose blocks are contained in another. The degree sidecar gives exact candidate degree in the same row order. Where the next roster was retained, the open-count sidecar records the exact spend of every loose distinction by those births. A closing birth is recorded with its parents and a zero-live roster. [Exporter](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/stages.py)

Rebuilding starts from their literal meetings reproduces the archived counts and largest maximal blocks. At each available double count, the incoming parent total agrees with the preceding open total. The exact native check lists the unheld maximal candidate sets at the real precursor, inserts the leftover pairs, and checks the whole multiset of parent sets and offshoots. Start-01 uses the native listing to materialize its last already archived birth. It matches the archived live count, block count, largest block, candidate pair count, and parent total. The other thirteen last births use the archived roster engine and are independently checked by the native listing. [Native group check](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/stages_groups.cpp)

The age-seven and age-eight block files of start-03 are byte-identical to the prior study. The old age-eight parent names run from 270 through 655. Subtracting 270 makes the old rows agree with every supplied local parent row. The 993,164 incidences exactly consume the age-seven open supply. [Archive checks](../NINTH-ROUND-SAMPLE-20261119-001/decision.md)

The latest rosters of start-02, start-05 and start-08 are isomorphic as full incidence inputs. An exact permutation of their five initial live junctions preserves the loose counts and maximal blocks. Lifting that permutation through actual parent sets yields explicit bijections of all 102,871 latest live junctions. Each retained maximal block and actual incoming parent set is checked under the bijections. The three differently named histories retain their own files and manifest rows.

## Exact corrections and controls

On a nonclosing reached roster, a junction with \(p\) parents and group demand \(d\) has \(\max(d,3-p,1)\) loose distinctions. A junction with at least two parents contributes one offshoot exactly when isolated. A junction with one parent shares that parent with all its candidates. Every group through it is therefore a pair, and its demand is its candidate degree \(g\). Its exact offshoot count is \(\max(0,2-g)\). The large inputs store parent counts and these exact corrections without requiring the unknown next group demands. The exporter derives candidate degrees by taking a union of the maximal blocks incident to each junction. It stores block incidence and one union at a time, without retaining a full pair matrix.

The shared folder includes the independently built partnered controls of orders three, four, and five, including reached rosters with held transversals. It includes start-04 at age eight, whose one 781-junction block gives exactly 304,590 pair births and zero offshoots. It includes start-00 from age zero through its age-22 closing birth, whose next round has zero births. The independent control builder supplies ages zero through fourteen, and the archived replay supplies the rest of its binomial tail. [Independent control rosters](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/control_rosters.json)

## Rebuild

The manifest preserves the original starts, the archived input hashes, and the output hashes. Rebuilding can use the original MERGE-BURST runner archive when present or the same literal starts in the manifest. Temporary stage files are retained in the shared folder while the samplers consume them.

```bash
family=experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler
run_dir=$(mktemp -d)
.venv/bin/python -B "$family/stages.py" one start-03
.venv/bin/python -B scripts/longrun.py launch "$family/stages.py" --out "$run_dir" --unit hub-stage-replay --workers 4 --case-timeout 480 --case-mem 1400M --mem-max 8G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$run_dir" --foreground
.venv/bin/python -B "$family/stages.py" collect
```
