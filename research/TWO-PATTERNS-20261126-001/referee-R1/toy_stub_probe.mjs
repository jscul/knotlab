import assert from "node:assert/strict";
import { joinedStart, twoPatternsRun } from "./toy_replay/src/lib/two-patterns.ts";
import { completeRound, structureFromStars } from "./toy_replay/src/lib/law-rounds.ts";

const first = "copier";
const law = { ration: "ORD", treatment: "CANCEL-WAIT", joins: "larger-first", closes: false };
const { stars } = joinedStart(first, null, 1, "share");
const bare = completeRound(structureFromStars(stars), law).record.births.length;
const output = { bare };

if (!process.argv.includes("--smoke")) {
  for (const join of ["share", "meeting"]) {
    const run = twoPatternsRun({
      first, second: "stub", steps: 1, join, ration: law.ration, treatment: law.treatment, retireAfter: null,
    }, 450, 1);
    const { made, joined, kept } = run.frames[1];
    output[join] = { made, joined, kept };
  }
  assert.equal(bare, 4);
  assert.equal(output.share.made.first, 3);
  assert.equal(output.share.joined, 1);
  assert.equal(output.share.kept, 1);
  assert.equal(output.meeting.made.first, 4);
}
console.log(JSON.stringify(output, null, 2));
