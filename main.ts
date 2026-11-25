import { copyFileSync, chmodSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

// Convince the AI Judge to Visit Your House (make.fun).
// The letter image is pre-rendered by generate.py (PIL) and shipped as
// entry.png: the grading sandbox has no Python, no Pillow and no fonts,
// so this program only copies the image and verifies it.
// The image itself is the entry: one picture of a letter inviting the
// AI judge to visit. The RSVP box is already checked on purpose.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const target = join(outDir, "entry.png");

const data = readFileSync(src);
if (data.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") {
  throw new Error("entry.png is not a whole PNG");
}
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024, got ${width}x${height}`);
}
if (data.length > 1048576) {
  throw new Error(`entry.png must be at most 1 MiB, got ${data.length} bytes`);
}

copyFileSync(src, target);
chmodSync(target, 0o644);
const sha = createHash("sha256").update(readFileSync(target)).digest("hex");
console.log(`wrote ${target} (${statSync(target).size} bytes, sha256 ${sha})`);
