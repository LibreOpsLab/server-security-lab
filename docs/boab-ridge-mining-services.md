# Boab Ridge Mining Services: the example company

Everything in this lab is built for one fictional business. If you are using the lab on your own (not in a
class), this page tells you who the business is, so the servers you build have a reason to exist.

> **Boab Ridge Mining Services is fictional.** Its people, address, phone number, dates and figures are
> invented, and the phone number is in a range reserved for fiction. Any resemblance to a real business or
> person is accidental. You are welcome to reuse the company in your own teaching or practice lab.

## The company in one page

Boab Ridge is a Perth company of about 60 staff that keeps mines working. When a crusher stops, a haul truck
needs servicing or a plant shuts down for a week of repairs, Boab Ridge sends the fitters, welders and
planners. It works for mid-sized and large mine operators in the Pilbara and the Goldfields.

| Fact         | Detail                                                                                         |
| ------------ | ---------------------------------------------------------------------------------------------- |
| Founded      | 2011, in Welshpool, Perth                                                                      |
| Motto        | "Keep the site running"                                                                        |
| People       | About 60 staff (45 in Perth, 15 at the remote site office) plus about 25 rostered contractors  |
| Perth office | Weekdays 7am to 5pm. Management, finance, payroll, HR, planning and engineering, two-person IT |
| Remote site  | Pilbara, 24 hours, two 12-hour shifts. Generator power and a slow, unreliable satellite link   |
| Clients      | Three contracts. The largest is with a mine operator that is part of an international group    |

What it does: **fabrication** (steel and equipment repairs made to order), **fleet servicing** (scheduled
servicing of heavy equipment) and **shutdown crews** (teams that take over a plant for a planned shutdown).
Each job is quoted, rostered, carried out, recorded and invoiced. A lost or late job record costs money,
which is why backup and availability matter to this business.

## The company in detail

- [Company profile](company/profile.md): the brochure (history, what the company does, who is who, the client's rules, what matters).
- [Organisation chart](company/org-chart.md): all 60 staff, generated from `lab/data/users.csv`.
- `lab/data/users.csv`: the staff directory that `make identity` imports into Samba AD, with email address, title, office, business unit, employee type and manager, plus the shared mailboxes `info`, `sales`, `accounts`, `service`, `security` and `hr`.
- The lab's domain is `boab.lab` (`lab_domain` in `lab/inventory/group_vars/all.yml`); see [guide 05](build/05-the-repo-inventory-and-secrets.md) for changing it to match a different client.

## How the lab maps to the company

| In the company             | In the lab                                           |
| -------------------------- | ---------------------------------------------------- |
| Staff accounts and sign-in | Samba AD on `samba-dc01`, single sign-on on `auth01` |
| Email                      | Postfix and Dovecot on `mail01`                      |
| Shared files               | `files01` (SMB and SFTP), NextCloud on `docker01`    |
| Public website             | `www.boab.lab` on `docker01` (see below)             |
| Firewall and web filtering | `pfsense01`, Squid                                   |
| Monitoring and backup      | `mon01`, `pbs01`                                     |

## The company website

`https://www.boab.lab` is a five-page brochure site: Home, About, Services, People and Contact. The About page
tells visitors that the company is fictional and that every asset is public domain or Creative Commons.
It is the only page in the lab that is public (no sign-in), which makes it a natural target for the attack
weeks.

**How it works.** Two containers on `docker01`, both behind Traefik:

| Container      | What it does                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `brms-web`     | nginx serving the pages that Eleventy builds when the image is built (`lab/docker/brms-web/Dockerfile`). Read-only, no capabilities. |
| `brms-contact` | A small Python program. The Contact form posts to it; it checks the form and emails it through `mail01` |

The contact email goes to the mailbox named by `lab_contact_to` in `lab/inventory/group_vars/all.yml`
(default `info@boab.lab`, a shared mailbox: the `info` account in `lab/data/users.csv`, which several staff can sign in to with an IMAP client). It is sent
from `website@boab.lab` with the visitor's address in `Reply-To`. The handler ignores a hidden spam-trap
field, limits each client to five messages per ten minutes, rejects oversized forms and strips line breaks
from names (so a visitor cannot inject mail headers). It logs what happened, never the message text.

**Deploy.** It is part of `make apps` (guide 10). The `www` name is added to DNS by `make identity`; if you
built the lab before this site existed, run `make identity` and then `make apps` again.

**Check.** `make verify` runs `21-website`: the four pages load without a sign-in and the form handler
answers. Then send a real message from the Contact page and read it in the mailbox.

**Things to notice (security).** The mail relay accepts the Docker VM because it is on the lab subnet (a
deliberate weak default that the hardening week narrows), mail from the form travels on port 25 without
TLS, and the site sends no HSTS header. When you harden mail and the web tier, work out what has to change
here so the contact form keeps working. That is a real lesson: a hardening change that silently breaks the
business.

## Changing the site (optional)

This course teaches server security, not web development, so the finished site is committed and you never
need Node.js. If you do want to edit it, the source is a small [Eleventy](https://www.11ty.dev/) project:

```bash
cd lab/docker/brms-web/site
npm install
npm run build      # writes ../html
```

Edit the text in `src/*.njk` and the facts (name, phone, address) in `src/_data/company.json`, rebuild, then
run `make apps` to copy the new `html/` to `docker01`.

## Assets and licences

- The logo and icons are original vector drawings made for this lab and released under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain).
- The page text is original and CC0 1.0.
- The styling is hand-written CSS. The site loads no fonts, scripts or images from other sites.
- The pictures are placeholder illustrations (`docs/company/images/`, also used by the website). If you add photographs, use only public domain or Creative Commons images and record
  the creator, title and licence of each in this section.
