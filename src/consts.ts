export const SITE = {
  name: "Anand Kumar Narayanan",
  eyebrow: "Cloud · Data · AI security",
  tagline: "Solutions Architect writing about cloud, data platforms, and enterprise AI.",
  intro:
    "I have over 20 years of experience in enterprise architecture across fintech, manufacturing, automotive, and telecom. My fintech background has shaped my interest in designing scalable, secure, and audit-ready cloud, data, and AI platforms, with a particular focus on regulated environments and alignment with CSSF requirements, DORA, and ISO 27001.",
  personalNote:
    "Alongside my full-time role as a Solutions Architect, I pursue this blog and projects such as Agent Sentinel as personal interests in my spare time.",
  footerNote: "Personal writing and projects · Full-time Solutions Architect",
  linkedin: "https://linkedin.com/in/anandkn2012",
  github: "https://github.com/anandnarayanan2017",
  seriesRepo: "https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/agent-sentinel",
  series: "/blog/agent-sentinel-01-why-agents-need-a-flight-recorder/",
  // Default social-preview image (1200x627) for pages without their own.
  ogImage: "/images/agent-sentinel/01-why-agents-need-a-flight-recorder-1.png",
  email: "anandkn.2026@gmail.com",
};

// "02 Oct 2026" in post lists, "02 October 2026" on the article page.
export const fmtShort = (d: Date) =>
  d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });
export const fmtLong = (d: Date) =>
  d.toLocaleDateString("en-GB", { day: "2-digit", month: "long", year: "numeric", timeZone: "UTC" });
export const isoDate = (d: Date) => d.toISOString().slice(0, 10);
