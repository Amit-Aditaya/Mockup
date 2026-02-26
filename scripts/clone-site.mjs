import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const BASE_URL = "https://ex-coders.com/html/exolax/";
const OUTPUT_ROOT = path.resolve("public/clone");

const htmlQueue = [new URL("index.html", BASE_URL).toString()];
const seenHtml = new Set();
const assets = new Set();

function isCrawlable(url) {
  return url.hostname === "ex-coders.com" && url.pathname.startsWith("/html/exolax/");
}

function toOutputPath(absoluteUrl) {
  const url = new URL(absoluteUrl);
  const relative = url.pathname.replace("/html/exolax/", "");
  return path.join(OUTPUT_ROOT, relative);
}

async function saveFile(filePath, data) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, data);
}

function extractUrls(html, currentUrl) {
  const found = new Set();
  const attrRegex = /(href|src)=["']([^"']+)["']/gi;
  const styleRegex = /url\((["']?)([^"')]+)\1\)/gi;

  let match;
  while ((match = attrRegex.exec(html)) !== null) {
    found.add(match[2]);
  }

  while ((match = styleRegex.exec(html)) !== null) {
    found.add(match[2]);
  }

  const resolved = [];
  for (const value of found) {
    if (!value || value.startsWith("#") || value.startsWith("mailto:") || value.startsWith("tel:") || value.startsWith("javascript:")) {
      continue;
    }
    try {
      resolved.push(new URL(value, currentUrl).toString());
    } catch {
      // ignore parse failures
    }
  }

  return resolved;
}

while (htmlQueue.length > 0) {
  const url = htmlQueue.shift();
  if (!url || seenHtml.has(url)) {
    continue;
  }
  seenHtml.add(url);

  const response = await fetch(url);
  if (!response.ok) {
    continue;
  }

  const html = await response.text();
  const localPath = toOutputPath(url);
  await saveFile(localPath, html);

  const discovered = extractUrls(html, url);
  for (const discoveredUrl of discovered) {
    const parsed = new URL(discoveredUrl);
    if (!isCrawlable(parsed)) {
      continue;
    }

    const ext = path.extname(parsed.pathname).toLowerCase();
    const isHtml = ext === ".html" || ext === "";
    if (isHtml) {
      if (!seenHtml.has(discoveredUrl)) {
        htmlQueue.push(discoveredUrl);
      }
    } else {
      assets.add(discoveredUrl);
    }
  }
}

for (const assetUrl of assets) {
  const response = await fetch(assetUrl);
  if (!response.ok) {
    continue;
  }

  const arrayBuffer = await response.arrayBuffer();
  const filePath = toOutputPath(assetUrl);
  await saveFile(filePath, new Uint8Array(arrayBuffer));
}

console.log(`Cloned ${seenHtml.size} HTML files and ${assets.size} assets into ${OUTPUT_ROOT}`);