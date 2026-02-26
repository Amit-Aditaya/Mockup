import { readdir, writeFile } from "node:fs/promises";
import path from "node:path";

const IMG_ROOT = path.resolve("public/clone/assets/img");
const PHOTO_DIR_HINTS = [
  "about",
  "blog",
  "case-study",
  "cta",
  "header",
  "hero",
  "news",
  "project",
  "team",
  "testimonial",
];

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(fullPath)));
    } else {
      files.push(fullPath);
    }
  }

  return files;
}

const files = await walk(IMG_ROOT);

const replaceTargets = files.filter((filePath) => {
  const rel = path.relative(IMG_ROOT, filePath).replaceAll("\\", "/").toLowerCase();
  const ext = path.extname(rel);
  return (ext === ".jpg" || ext === ".jpeg") && PHOTO_DIR_HINTS.some((hint) => rel.startsWith(`${hint}/`));
});

for (const filePath of replaceTargets) {
  const rel = path.relative(IMG_ROOT, filePath).replaceAll("\\", "/");
  const seed = encodeURIComponent(rel.replaceAll("/", "-").replaceAll(".", "-"));
  const width = 1400;
  const height = 900;
  const response = await fetch(`https://picsum.photos/seed/${seed}/${width}/${height}.jpg`);

  if (!response.ok) {
    continue;
  }

  const bytes = new Uint8Array(await response.arrayBuffer());
  await writeFile(filePath, bytes);
}

console.log(`Replaced ${replaceTargets.length} images with open-source placeholders.`);