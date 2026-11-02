// The series, read from each <folder>/docs/blog/series.json and joined with
// the published posts. Only published parts appear anywhere on the site.
import type { CollectionEntry } from "astro:content";

type Card = {
  order?: number;
  badge: string;
  question?: string;
  title: string;
  description: string;
  codeUrl?: string;
};
type Config = { name: string; card?: Card };

const configs = Object.values(
  import.meta.glob<Config>("/*/docs/blog/series.json", { eager: true, import: "default" }),
);

export type Series = Card & {
  name: string;
  parts: CollectionEntry<"blog">[]; // published parts, in order
};

export function getSeries(posts: CollectionEntry<"blog">[]): Series[] {
  return configs
    .filter((c) => c.card)
    .map((c) => ({
      ...c.card!,
      name: c.name,
      parts: posts
        .filter((p) => p.data.series === c.name)
        .sort((a, b) => (a.data.part ?? 0) - (b.data.part ?? 0)),
    }))
    .filter((s) => s.parts.length > 0)
    .sort((a, b) => (a.order ?? 99) - (b.order ?? 99));
}
