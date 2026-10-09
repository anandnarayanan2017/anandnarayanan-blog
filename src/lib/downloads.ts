// Builds the "Download Markdown" / "Download HTML" files for each post, so a
// reader can keep a self-contained copy: site-relative links become absolute.
import { getCollection, type CollectionEntry } from "astro:content";
import { SITE, fmtLong, isoDate } from "../consts";

type Post = CollectionEntry<"blog">;

export async function downloadPaths() {
  const posts = await getCollection("blog");
  return posts.map((post) => ({ params: { slug: post.id }, props: { post } }));
}

const absolute = (text: string, site: URL) => {
  const origin = site.origin;
  return text
    .replace(/\]\(\/(?!\/)/g, `](${origin}/`) // markdown links and images
    .replace(/(href|src)="\/(?!\/)/g, `$1="${origin}/`); // rendered HTML
};

const byline = (post: Post) => `${SITE.name} · ${isoDate(post.data.date)}`;

export function markdown(post: Post, site: URL) {
  const body = absolute(post.body ?? "", site).trim();
  return `# ${post.data.title}\n\n${byline(post)}\n\n${body}\n`;
}

const escape = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export function html(post: Post, site: URL) {
  const url = new URL(`/blog/${post.id}/`, site).href;
  const body = absolute(post.rendered?.html ?? "", site);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escape(post.data.title)} · ${escape(SITE.name)}</title>
<meta name="description" content="${escape(post.data.excerpt)}">
<link rel="canonical" href="${url}">
<style>
body{margin:0 auto;max-width:740px;padding:40px 24px 64px;color:#19232f;background:#fff;font:17px/1.7 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:#125ac0}h1{font-size:40px;line-height:1.15;letter-spacing:-1px;font-weight:600}h2{margin:36px 0 14px}
.meta{font-size:13px;color:#576674}img{display:block;max-width:100%;height:auto;margin:28px auto;border:1px solid #dce3ea;border-radius:8px}
blockquote{border-left:3px solid #125ac0;margin:25px 0;padding-left:20px;color:#576674}pre{overflow-x:auto;background:#f4f7fb!important;padding:18px}
table{border-collapse:collapse;display:block;overflow:auto}th,td{border:1px solid #dce3ea;padding:8px 12px;text-align:left}hr{border:0;border-top:1px solid #dce3ea;margin:36px 0}
</style>
</head>
<body>
<article>
<h1>${escape(post.data.title)}</h1>
<p class="meta">${escape(SITE.name)} · <time datetime="${isoDate(post.data.date)}">${fmtLong(post.data.date)}</time> · <a href="${url}">Read online</a></p>
${body}
</article>
</body>
</html>
`;
}
