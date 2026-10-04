import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://anandnarayanan.net",
  vite: { plugins: [tailwindcss()] },
  markdown: {
    shikiConfig: { theme: "github-dark" },
  },
});
