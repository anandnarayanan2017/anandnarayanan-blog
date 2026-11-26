import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import rehypeMermaid from "rehype-mermaid";

export default defineConfig({
  site: "https://anandnarayanan.net",
  // /sitemap-index.xml and /sitemap-0.xml, listing every built page.
  integrations: [sitemap()],
  markdown: {
    // Mermaid fences are rendered to static inline SVG at build time by
    // rehype-mermaid (headless Chromium via Playwright); no client-side JS.
    // Exclude them from Shiki so the fence reaches rehype-mermaid as a
    // <code class="language-mermaid"> block instead of highlighted markup.
    syntaxHighlight: { type: "shiki", excludeLangs: ["mermaid"] },
    shikiConfig: { theme: "github-dark" },
    rehypePlugins: [[rehypeMermaid, { strategy: "inline-svg" }]],
  },
});
