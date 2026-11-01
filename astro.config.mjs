import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://anandnarayanan.net",
  // /sitemap-index.xml and /sitemap-0.xml, listing every built page.
  integrations: [sitemap()],
  vite: { plugins: [tailwindcss()] },
  markdown: {
    shikiConfig: { theme: "github-dark" },
  },
});
