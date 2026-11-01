// Each series is a top-level folder of this repository with its write-ups in
// <folder>/docs/blog/ and its settings in <folder>/docs/blog/series.json. That
// folder is the single source of truth: this script generates the site's posts
// and images from it at build time, and the generated files are git-ignored, so
// a series is only ever edited in its own folder.
//
//   node scripts/sync-series.mjs     # run automatically before `npm run dev` / `npm run build`
//
// A part appears on the site once its write-up exists; its date comes from the
// "dates" map in that series' series.json. Two layouts are supported:
//
//   "technical" (Agent Sentinel): technical-details/NN-<slug>.md, cut at
//     "## Design and implementation", excerpt from linkedin/NN-<slug>.md, and a
//     link to the full deep dive on GitHub.
//   "essay": posts/NN-<slug>.md, published whole; the "# " heading is the title
//     and the excerpt comes from "excerpts" in series.json.
//
// Images live in images/ and are named <NN-slug>-1.png (the hero) and so on.
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, posix } from "node:path";

const REPO = "https://github.com/anandnarayanan2017/anandnarayanan-blog";
const OUT_POSTS = "src/content/blog";
const ROOT = process.env.SERIES_ROOT ?? ".";

const folders = readdirSync(ROOT, { withFileTypes: true })
  .filter((e) => e.isDirectory() && !e.name.startsWith(".") && e.name !== "node_modules")
  .map((e) => e.name)
  .filter((f) => existsSync(join(ROOT, f, "docs/blog/series.json")))
  .sort();

rmSync(OUT_POSTS, { recursive: true, force: true });
mkdirSync(OUT_POSTS, { recursive: true });

for (const folder of folders) sync(folder);

function sync(folder) {
  const blog = join(ROOT, folder, "docs/blog");
  const where = `${folder}/docs/blog/series.json`;
  const cfg = JSON.parse(readFileSync(join(blog, "series.json"), "utf8"));
  for (const k of ["name", "layout", "tags", "dates"]) if (!(k in cfg)) throw new Error(`${where}: missing "${k}"`);
  if (!["technical", "essay"].includes(cfg.layout)) throw new Error(`${where}: "layout" must be "technical" or "essay"`);

  // Site release date per part ({ "1": "2026-10-02", ... }), kept next to the
  // series so its public README needs no publishing plan.
  const dates = new Map(
    Object.entries(cfg.dates)
      .filter(([k]) => /^\d+$/.test(k))
      .map(([k, v]) => {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) throw new Error(`${where}: part ${k} has "${v}", expected YYYY-MM-DD`);
        return [Number(k), v];
      }),
  );

  const outImages = `public/images/${folder}`;
  const src = cfg.layout === "technical" ? "technical-details" : "posts";
  const files = readdirSync(join(blog, src)).filter((f) => /^\d{2}-.*\.md$/.test(f)).sort();
  const parts = files.map((f) => {
    const text = readFileSync(join(blog, src, f), "utf8");
    const n = Number(f.slice(0, 2));
    const slug = f.replace(/\.md$/, "");
    let title, excerpt;
    if (cfg.layout === "technical") {
      title = text.match(/^# Part \d+ — (.+)$/m)?.[1];
      const li = readFileSync(join(blog, "linkedin", f), "utf8");
      excerpt = li.split(/\n\s*\n/)[0].replace(/\s*\n\s*/g, " ").trim();
      if (!title) throw new Error(`${folder} part ${n}: missing "# Part ${n} — <title>" heading`);
    } else {
      title = text.match(/^# (.+)$/m)?.[1];
      excerpt = cfg.excerpts?.[String(n)];
      if (!title) throw new Error(`${folder} part ${n}: missing "# <title>" heading`);
      if (!excerpt) throw new Error(`${folder} part ${n}: no excerpt in ${where} "excerpts"`);
    }
    if (!dates.has(n)) throw new Error(`${folder} part ${n}: no date in ${where}`);
    return { n, f, slug, title, excerpt, date: dates.get(n), text };
  });

  // Rewrite relative links/images in a markdown body for the site.
  function rewrite(body, srcFile) {
    return body
      .replace(/!\[([^\]]*)\]\(\.\.\/images\/([^)]+)\)/g, `![$1](/images/${folder}/$2)`)
      .replace(/(?<!!)\[([^\]]+)\]\(([^)\s]+)\)/g, (all, label, url) => {
        if (/^(https?:|mailto:|#|\/)/.test(url)) return all;
        const part = url.match(/^(\d{2})-([^#]*)\.md(#.*)?$/);
        if (part) return `[${label}](/blog/${folder}-${part[1]}-${part[2]}/${part[3] ?? ""})`;
        const target = posix.normalize(posix.join(posix.dirname(srcFile), url));
        return `[${label}](${REPO}/blob/main/${folder}/${target})`;
      });
  }

  mkdirSync(outImages, { recursive: true });

  for (const p of parts) {
    const img = `${p.slug}-1.png`;
    const next = parts.find((q) => q.n === p.n + 1);
    let section, siteTitle, lead, tail;
    if (cfg.layout === "technical") {
      const start = p.text.search(/^## /m); // first section, after the title and reader-path line
      const end = p.text.indexOf("## Design and implementation");
      if (start < 0 || end < 0) throw new Error(`${folder} part ${p.n}: expected a first "## " section and a "## Design and implementation" heading`);
      section = p.text.slice(start, end);
      siteTitle = `${cfg.name}, Part ${p.n}: ${p.title}`;
      lead = [`![${p.title}](/images/${folder}/${img})`, ""];
      tail = [
        "",
        "---",
        "",
        `**For architects and engineers:** the design, diagrams, and links into the code and tests are in the [technical deep dive on GitHub](${REPO}/blob/main/${folder}/docs/blog/technical-details/${p.f}).`,
      ];
    } else {
      section = p.text.replace(/^[\s\S]*?^# .+$\n?/m, ""); // everything after the title
      siteTitle = p.title;
      lead = []; // an essay places its own images
      tail = [];
    }
    const words = section.split(/\s+/).length;
    const body = rewrite(section.trimEnd(), `docs/blog/${src}/${p.f}`);
    const fm = [
      "---",
      `title: ${JSON.stringify(siteTitle)}`,
      `date: ${p.date}`,
      `excerpt: ${JSON.stringify(p.excerpt)}`,
      `tags: [${cfg.tags.map((t) => JSON.stringify(t)).join(", ")}]`,
      `readTime: ${Math.max(1, Math.ceil(words / 200))}`,
      `series: ${JSON.stringify(cfg.name)}`,
      `part: ${p.n}`,
      `image: "/images/${folder}/${img}"`,
      "---",
    ].join("\n");
    const out = [
      fm,
      "",
      ...lead,
      body,
      ...tail,
      ...(next ? ["", `Next: [Part ${next.n} — ${next.title}](/blog/${folder}-${next.slug}/).`] : []),
      "",
    ].join("\n");
    writeFileSync(join(OUT_POSTS, `${folder}-${p.slug}.md`), out);
    // Every image of this part: <slug>-1.png (the hero) plus any it embeds.
    for (const f of readdirSync(join(blog, "images")).filter((f) => f.startsWith(`${p.slug}-`))) {
      cpSync(join(blog, "images", f), join(outImages, f));
    }
  }
  console.log(`synced ${folder}: ${parts.length} part(s): ${parts.map((p) => p.n).join(", ")}`);
}
