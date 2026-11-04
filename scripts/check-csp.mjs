// Checks that the Content-Security-Policy in the CloudFront response headers
// policy (infra/cloudfront/security-headers-policy.json) allows every inline
// script in the built site (dist/). Run after `npm run build`.
//
// An inline script whose SHA-256 hash is not in script-src is blocked by the
// browser on the live site (for example the dark-mode script), so a change to
// an inline script, or an Astro upgrade that minifies one differently, fails
// here. Copy the printed script-src into the policy file, then update the
// policy in CloudFront (infra/README.md).
//
//   node scripts/check-csp.mjs
import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const POLICY = "infra/cloudfront/security-headers-policy.json";
const DIST = "dist";
// Script types the browser does not run (data blocks), so CSP ignores them.
const DATA_TYPES = /type\s*=\s*["']?(application\/(ld\+)?json|text\/plain)/i;

const htmlFiles = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? htmlFiles(join(dir, e.name)) : e.name.endsWith(".html") ? [join(dir, e.name)] : [],
  );

const csp = JSON.parse(readFileSync(POLICY, "utf8")).SecurityHeadersConfig.ContentSecurityPolicy.ContentSecurityPolicy;
const scriptSrc = csp.split(";").map((d) => d.trim()).find((d) => d.startsWith("script-src ")) ?? "";
const allowed = new Set(scriptSrc.match(/'sha256-[A-Za-z0-9+/=]+'/g) ?? []);

const needed = new Map(); // hash -> first file that uses it
const handlers = [];
for (const file of htmlFiles(DIST)) {
  const html = readFileSync(file, "utf8");
  for (const [, attrs, body] of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (/\bsrc\s*=/i.test(attrs) || DATA_TYPES.test(attrs)) continue;
    const hash = `'sha256-${createHash("sha256").update(body, "utf8").digest("base64")}'`;
    if (!needed.has(hash)) needed.set(hash, file);
  }
  if (/<[^>]+\son[a-z]+\s*=/i.test(html)) handlers.push(file);
}

let failed = false;
for (const [hash, file] of needed) {
  if (!allowed.has(hash)) {
    console.error(`::error::inline script in ${file} has hash ${hash}, which is not in script-src (${POLICY})`);
    failed = true;
  }
}
for (const file of handlers) {
  console.error(`::error::${file} has an inline event handler (onclick= and similar); the CSP blocks it, use addEventListener`);
  failed = true;
}
const unused = [...allowed].filter((h) => !needed.has(h));
for (const hash of unused) console.log(`::warning::${hash} in script-src is no longer used by any page; remove it`);

if (failed || unused.length) {
  console.log(`\nscript-src for ${POLICY}:\nscript-src 'self' ${[...needed.keys()].join(" ")}`);
}
if (failed) process.exit(1);
console.log(`OK: the CSP allows all ${needed.size} inline script(s) in ${DIST}/.`);
