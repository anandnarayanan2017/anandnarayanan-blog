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
| `route53/email-records.json` | MX, SPF and DMARC records that forward `hello@anandnarayanan.net` (see [Email](#email)) |

## Content-Security-Policy

`script-src` lists the SHA-256 hash of each inline script Astro writes into the pages. Today
that is only the dark-mode script in `BaseLayout.astro`, which must run before first paint.
The theme toggle and tag filter live in `public/js/site.js`, which `'self'` allows, so
changing them needs no new hash; keep new behaviour in that file rather than inline. `scripts/check-csp.mjs` runs after every build in `site-build`
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
> Response headers policy, choose `blog-security-headers` and save. Prefer the console for
this step.

> **Warning:** `update-distribution` replaces the whole distribution config with the one you
> send. An AWS CLI older than origin access control (August 2022) drops
> `OriginAccessControlId` when it reads the config, so writing it back removes OAC from the S3
> origin and every request returns 403. Before editing the distribution with the CLI, check
> that `aws cloudfront get-distribution-config --id ESTVCZ8II465N --query
> 'DistributionConfig.Origins.Items[0].OriginAccessControlId'` prints the OAC ID, not `null`.
> If you do use the CLI, set `DefaultCacheBehavior.ResponseHeadersPolicyId` in the config and
> run `update-distribution` with the config's ETag.

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

## Email

`hello@anandnarayanan.net` is the public contact address (`SITE.email` in `src/consts.ts`).
It is a forwarding alias, not a mailbox: [ImprovMX](https://improvmx.com) (free plan)
receives the mail and forwards it to the owner's personal inbox. Route 53 cannot forward
mail, and the AWS-only alternative (SES receiving, S3, and a Lambda forwarder) is code to
maintain for years; this is three DNS records that never change.

The address on the site never changes. To move to another provider, change the alias there
and replace these records; nothing in the site or the repository needs editing.

### Set up or rebuild

1. In ImprovMX, add the domain `anandnarayanan.net` and the alias `hello` pointing to the
   personal inbox. Turn on two-factor authentication for the ImprovMX account.
2. Check the records ImprovMX shows against `route53/email-records.json`; if they differ,
   update the file first. Then apply it:

   ```bash
   ZONE=$(aws route53 list-hosted-zones-by-name --dns-name anandnarayanan.net \
     --query "HostedZones[0].Id" --output text)
   aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" \
     --change-batch file://infra/route53/email-records.json
   ```

   The file uses `UPSERT`, so it **replaces** the whole root TXT record. If the root already
   has other TXT values (for example a domain verification), add them to the file first:

   ```bash
   aws route53 list-resource-record-sets --hosted-zone-id "$ZONE" \
     --query "ResourceRecordSets[?Type=='TXT' || Type=='MX']"
   ```

3. Wait until ImprovMX shows the domain as verified (minutes, sometimes up to an hour).
4. Send a test message to `hello@anandnarayanan.net` from an account *other than* the
   destination inbox (Gmail hides a message you sent to yourself), and check it arrives.
5. Optional: to reply as `hello@`, add it in Gmail under Settings > Accounts > Send mail as,
   using the SMTP details ImprovMX gives you.

### Security notes

- **The provider can read forwarded mail.** It is a public contact address, so that is
  acceptable; do not use it for anything confidential or regulated.
- **Never use `hello@` as the login or recovery address of another account.** Whoever
  controls the ImprovMX account or these DNS records can redirect the alias and receive
  password-reset mail. Keep two-factor authentication on ImprovMX and on the AWS account.
- **Don't publish a catch-all alias (`*@`).** It attracts spam and lets anyone create
  addresses on the domain that look official.
- **Tighten DMARC later.** `p=none` only reports. If mail is ever *sent* from the domain,
  set up DKIM and SPF for that sender, then move to `p=quarantine`.
- **Check yearly** that the free plan still exists and the alias still forwards (step 4).
  If the provider shuts down, mail bounces until the records point somewhere else.
