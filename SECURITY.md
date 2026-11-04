# Security

Report a vulnerability in this site privately through GitHub's
"Report a vulnerability" button on this repository (Security tab), not in a
public issue.

The site is static (Astro build, served from S3 through CloudFront). There is
no server-side code, database, or form handling.

The AWS configuration (CloudFront security headers, the S3 bucket policy and the deploy
role's permissions) is documented in [infra/README.md](infra/README.md).
