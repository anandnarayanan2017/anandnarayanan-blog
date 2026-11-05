# Infrastructure notes for anandnarayanan.net

Configuration that lives outside the code, recorded so it can be rebuilt.

| File | What it is |
|---|---|
| `route53/email-records.json` | MX, SPF and DMARC records that forward `hello@anandnarayanan.net` (see [Email](#email)) |

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
