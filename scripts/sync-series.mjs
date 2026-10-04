// Single source of truth for the Agent Sentinel series is the agent-sentinel/
// folder of this repository (agent-sentinel/docs/blog/...). This script
// generates the site's posts and images from it at build time; the generated
// files are git-ignored, so the series is only ever edited in that folder.
//
//   node scripts/sync-series.mjs     # run automatically before `npm run dev` / `npm run build`
//
// A part appears on the site once its write-up exists in that folder.
import { cpSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, posix } from "node:path";

const REPO = "https://github.com/anandnarayanan2017/anandnarayanan-blog";
const SERIES = "agent-sentinel"; // folder in this repo, also its path on GitHub
const TAGS = ["Agent Sentinel", "AI Security", "Compliance"];
const OUT_POSTS = "src/content/blog";
const OUT_IMAGES = "public/images/agent-sentinel";

const dir = process.env.SERIES_DIR ?? SERIES;
const blog = join(dir, "docs/blog");

// Site release date per part: the "On the site" column of the publishing-plan
// table in docs/blog/README.md (| LinkedIn week | N. Title | site date | goal |).
const readme = readFileSync(join(blog, "README.md"), "utf8");
const dates = new Map(
  [...readme.matchAll(/^\| \d{4}-\d{2}-\d{2} \| (\d+)\. [^|]*\| (\d{4}-\d{2}-\d{2}) \|/gm)].map((m) => [Number(m[1]), m[2]]),
);

const files = readdirSync(join(blog, "technical-details")).filter((f) => /^\d{2}-.*\.md$/.test(f)).sort();
const parts = files.map((f) => {
  const text = readFileSync(join(blog, "technical-details", f), "utf8");
  const n = Number(f.slice(0, 2));
  const slug = f.replace(/\.md$/, "");
  const title = text.match(/^# Part \d+ — (.+)$/m)?.[1];
  const li = readFileSync(join(blog, "linkedin", f), "utf8");
  const excerpt = li.split(/\n\s*\n/)[0].replace(/\s*\n\s*/g, " ").trim();
  if (!title || !dates.has(n)) throw new Error(`Part ${n}: missing title or release date`);
  return { n, f, slug, title, excerpt, date: dates.get(n), text };
});
const published = new Set(parts.map((p) => p.n));

// Rewrite relative links/images in a markdown body for the site.
function rewrite(body, srcFile) {
  return body
    .replace(/!\[([^\]]*)\]\(\.\.\/images\/([^)]+)\)/g, "![$1](/images/agent-sentinel/$2)")
    .replace(/(?<!!)\[([^\]]+)\]\(([^)\s]+)\)/g, (all, label, url) => {
      if (/^(https?:|mailto:|#|\/)/.test(url)) return all;
      const part = url.match(/^(\d{2})-([^#]*)\.md(#.*)?$/);
      if (part) return `[${label}](/blog/agent-sentinel-${part[1]}-${part[2]}/${part[3] ?? ""})`;
      const target = posix.normalize(posix.join(posix.dirname(srcFile), url));
      return `[${label}](${REPO}/blob/main/${SERIES}/${target})`;
    });
}

rmSync(OUT_POSTS, { recursive: true, force: true });
mkdirSync(OUT_POSTS, { recursive: true });
mkdirSync(OUT_IMAGES, { recursive: true });

for (const p of parts) {
  const start = p.text.search(/^## /m); // first section, after the title and reader-path line
  const end = p.text.indexOf("## Design and implementation");
  if (start < 0 || end < 0) throw new Error(`Part ${p.n}: expected a first "## " section and a "## Design and implementation" heading`);
  const words = p.text.slice(start, end).split(/\s+/).length;
  const img = `${p.slug}-1.png`;
  const next = parts.find((q) => q.n === p.n + 1);
  const body = rewrite(p.text.slice(start, end).trimEnd(), `docs/blog/technical-details/${p.f}`);
  const fm = [
    "---",
    `title: ${JSON.stringify(`Agent Sentinel, Part ${p.n}: ${p.title}`)}`,
    `date: ${p.date}`,
    `excerpt: ${JSON.stringify(p.excerpt)}`,
    `tags: [${TAGS.map((t) => JSON.stringify(t)).join(", ")}]`,
    `readTime: ${Math.max(1, Math.ceil(words / 200))}`,
    `series: "Agent Sentinel"`,
    `part: ${p.n}`,
    "---",
  ].join("\n");
  const out = [
    fm,
    "",
    `![${p.title}](/images/agent-sentinel/${img})`,
    "",
    body,
    "",
    "---",
    "",
    `**For architects and engineers:** the design, diagrams, and links into the code and tests are in the [technical deep dive on GitHub](${REPO}/blob/main/${SERIES}/docs/blog/technical-details/${p.f}).`,
    ...(next ? ["", `Next: [Part ${next.n} — ${next.title}](/blog/agent-sentinel-${next.slug}/).`] : []),
    "",
  ].join("\n");
  writeFileSync(join(OUT_POSTS, `agent-sentinel-${p.slug}.md`), out);
  cpSync(join(blog, "images", img), join(OUT_IMAGES, img));
}
console.log(`synced ${parts.length} part(s): ${[...published].join(", ")}`);
