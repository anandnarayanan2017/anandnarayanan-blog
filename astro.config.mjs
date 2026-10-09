import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://anandnarayanan.net",
  markdown: {
    shikiConfig: { theme: "github-light" },
  },
});
