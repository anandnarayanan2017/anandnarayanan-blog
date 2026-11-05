// schema.org JSON-LD built only from facts already on the site (src/consts.ts
// and post frontmatter). Rendered by BaseLayout through its jsonLd prop.
import { SITE } from "./consts";

const SITE_URL = "https://anandnarayanan.net/";
const PERSON_ID = `${SITE_URL}#person`;

export const person = {
  "@type": "Person",
  "@id": PERSON_ID,
  name: SITE.name,
  url: SITE_URL,
  jobTitle: "Solutions Architect",
  sameAs: [SITE.linkedin, SITE.github],
};

export const website = {
  "@type": "WebSite",
  "@id": `${SITE_URL}#website`,
  name: SITE.name,
  url: SITE_URL,
  description: SITE.tagline,
  inLanguage: "en",
  author: { "@id": PERSON_ID },
};

export function homeJsonLd() {
  return { "@context": "https://schema.org", "@graph": [website, person] };
}

type Post = { title: string; excerpt: string; date: Date; updated?: Date; tags: string[]; image?: string; series?: string };

export function blogPostingJsonLd(post: Post, url: URL) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.excerpt,
    datePublished: post.date.toISOString(),
    dateModified: (post.updated ?? post.date).toISOString(),
    url: url.href,
    mainEntityOfPage: url.href,
    inLanguage: "en",
    keywords: post.tags.join(", "),
    ...(post.image && { image: new URL(post.image, SITE_URL).href }),
    ...(post.series && { isPartOf: { "@type": "CreativeWorkSeries", name: post.series } }),
    author: { "@type": "Person", "@id": PERSON_ID, name: SITE.name, url: SITE_URL },
    publisher: { "@type": "Person", "@id": PERSON_ID, name: SITE.name, url: SITE_URL },
  };
}
