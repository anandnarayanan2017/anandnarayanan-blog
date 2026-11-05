import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    // Last time the post was checked against its sources; shown as "Last reviewed".
    updated: z.coerce.date().optional(),
    // External sources the post relies on, shown in the box at the top of the post.
    sources: z.array(z.object({ title: z.string(), url: z.string().url() })).optional(),
    excerpt: z.string(),
    tags: z.array(z.string()),
    readTime: z.number().optional(),
    series: z.string().optional(),
    part: z.number().optional(),
    image: z.string().optional(),
  }),
});

export const collections = { blog };
