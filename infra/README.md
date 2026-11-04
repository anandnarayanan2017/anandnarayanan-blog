# AWS setup for anandnarayanan.net

The site is a static Astro build. It is stored in a private S3 bucket and served only
through CloudFront. GitHub Actions publishes it through OIDC (`.github/workflows/deploy.yml`).
The files in this folder are the reference configuration. Apply them with the AWS CLI;
nothing applies them automatically, and the deploy role can't change them.

| Resource | Value |
|---|---|
| Account | `825822360935` |
| S3 bucket | `anandnarayanan-net-site` (eu-central-1) |
| CloudFront distribution | `ESTVCZ8II465N` |
| Deploy role | `github-blog-deploy`, inline policy `blog-deploy-permissions` |

## Files

| File | What it is |
|---|---|
| `cloudfront/security-headers-policy.json` | Response headers policy: HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, COOP |
| `s3/bucket-policy.json` | Bucket policy: read access for this distribution only (OAC), and TLS-only access |
| `iam/blog-deploy-permissions.json` | Least-privilege permissions for the deploy role |

## Content-Security-Policy

`script-src` lists the SHA-256 hash of each inline script Astro writes into the pages (the
dark-mode script in `BaseLayout.astro`, and the small scripts Astro inlines for the theme
toggle and tag filter). `scripts/check-csp.mjs` runs after every build in `site-build`
and `deploy`, and fails if a page has an inline script the policy doesn't allow. When it
fails, it prints the new `script-src`:

1. Copy that `script-src` into `cloudfront/security-headers-policy.json`.
2. Update the policy in CloudFront *before* the change reaches `main` (see below). Extra
   hashes are harmless, but a missing hash breaks the script on the live site.

`style-src` allows `'unsafe-inline'` because Shiki code highlighting writes `style=""`
attributes. Injected CSS is a much smaller risk than injected script.

## Applying the headers policy

Create it once and attach it to the distribution's default cache behavior:

```bash
aws cloudfront create-response-headers-policy \
  --response-headers-policy-config file://infra/cloudfront/security-headers-policy.json \
  --query 'ResponseHeadersPolicy.Id' --output text
```

Then, in the console under CloudFront > Distributions > `ESTVCZ8II465N` > Behaviors > Default
> Response headers policy, choose `blog-security-headers` and save. With the CLI, set
`DefaultCacheBehavior.ResponseHeadersPolicyId` in the distribution config and run
`update-distribution` with the config's ETag.

To change the policy later:

```bash
ID=$(aws cloudfront list-response-headers-policies --type custom \
  --query "ResponseHeadersPolicyList.Items[?ResponseHeadersPolicy.ResponseHeadersPolicyConfig.Name=='blog-security-headers'].ResponseHeadersPolicy.Id" --output text)
ETAG=$(aws cloudfront get-response-headers-policy --id "$ID" --query ETag --output text)
aws cloudfront update-response-headers-policy --id "$ID" --if-match "$ETAG" \
  --response-headers-policy-config file://infra/cloudfront/security-headers-policy.json
```

Check it on the live site:

```bash
curl -sI https://anandnarayanan.net/ | grep -iE 'strict-transport|content-security|x-content-type|referrer|x-frame|permissions-policy|cross-origin'
```

HSTS is set with `includeSubDomains` and without `preload`. Add `preload` and submit the
domain at hstspreload.org only when every subdomain is permanently HTTPS-only.

## Bucket policy, versioning and logging

```bash
aws s3api put-bucket-policy --bucket anandnarayanan-net-site --policy file://infra/s3/bucket-policy.json
aws s3api put-bucket-versioning --bucket anandnarayanan-net-site --versioning-configuration Status=Enabled
```

Versioning lets you recover from a bad `s3 sync --delete`. Add a lifecycle rule that expires
noncurrent versions (for example after 30 days) so old versions don't pile up.

## Deploy role

Compare the role's current inline policy with `iam/blog-deploy-permissions.json`:

```bash
aws iam get-role-policy --role-name github-blog-deploy --policy-name blog-deploy-permissions
```

To replace it:

```bash
aws iam put-role-policy --role-name github-blog-deploy --policy-name blog-deploy-permissions \
  --policy-document file://infra/iam/blog-deploy-permissions.json
```
