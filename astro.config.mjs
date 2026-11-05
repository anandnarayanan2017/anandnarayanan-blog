import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://anandnarayanan.net",
  // /sitemap-index.xml and /sitemap-0.xml, listing every built page.
  integrations: [sitemap()],
  markdown: {
    shikiConfig: { theme: "github-dark" },
  },
});
