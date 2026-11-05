// RSS 2.0 feed at /rss.xml, written by hand so it needs no extra dependency.
// Lists every published post, newest first, with its summary.
import type { APIContext } from "astro";
import { getCollection } from "astro:content";
import { SITE } from "../consts";

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");

export async function GET(context: APIContext) {
  const site = context.site!;
  const posts = (await getCollection("blog")).sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf() || (a.data.part ?? 0) - (b.data.part ?? 0),
  );
  const items = posts
    .map((p) => {
      const link = new URL(`/blog/${p.id}/`, site).href;
      return [
        "    <item>",
        `      <title>${esc(p.data.title)}</title>`,
        `      <link>${esc(link)}</link>`,
        `      <guid isPermaLink="true">${esc(link)}</guid>`,
        `      <pubDate>${p.data.date.toUTCString()}</pubDate>`,
        `      <description>${esc(p.data.excerpt)}</description>`,
        ...p.data.tags.map((t) => `      <category>${esc(t)}</category>`),
        "    </item>",
      ].join("\n");
    })
    .join("\n");
  const latest = posts[0]?.data.updated ?? posts[0]?.data.date;
  const xml = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">`,
    "  <channel>",
    `    <title>${esc(SITE.name)}</title>`,
    `    <link>${esc(site.href)}</link>`,
    `    <description>${esc(SITE.tagline)}</description>`,
    "    <language>en</language>",
    `    <atom:link href="${esc(new URL("/rss.xml", site).href)}" rel="self" type="application/rss+xml"/>`,
    ...(latest ? [`    <lastBuildDate>${latest.toUTCString()}</lastBuildDate>`] : []),
    items,
    "  </channel>",
    "</rss>",
    "",
  ].join("\n");
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
}
