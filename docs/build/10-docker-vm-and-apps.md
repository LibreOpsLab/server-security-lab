# 10: Docker VM and apps

## What you will build

`docker01`: Traefik, NextCloud, Stirling PDF and Vaultwarden.

**Time and difficulty:** 2 to 3 hours. Medium. The first run downloads several large container images and
NextCloud takes a few minutes to start, so expect a lot of waiting.

> **Do this after guide 11.** The apps rely on the sign-in portal, so build [11-single-sign-on.md](11-single-sign-on.md)
> first.

## Why

A small business needs shared files, document tools and a password manager. Running them as containers
behind one reverse proxy is how most small teams actually deploy this kind of thing today.

> **What's going on:** A **Docker container** packages an application with everything it needs, so you start
> it with one command and it behaves the same everywhere. **Docker Compose** describes several containers
> in one file. **Traefik** is the reverse proxy: all web traffic arrives at Traefik on `docker01`, which
> looks at the name in the address (`cloud.lab.internal`, `pdf.lab.internal`, ...) and passes the request to
> the right container. It also holds the certificates, which is why the browser shows a padlock. The three
> apps are *NextCloud* (shared files), *Stirling PDF* (document tools), and *Vaultwarden* (a password
> manager).

## Before you start

- Guide 11 is complete: `https://auth.lab.internal` loads.
- Take a snapshot of `pve01` called `before-make-apps`.

## Steps

1. Read first. Open `lab/docker/traefik/docker-compose.yml` and `lab/docker/nextcloud/docker-compose.yml`.
   Find: the image name, the ports, and where a volume (stored data) is declared. Note them in your
   evidence.
2. Deploy:

   ```bash
   cd lab
   make apps
   ```

   NextCloud's first run can take a few minutes; the role waits for it.

   > **Beginner tip:** Open a second terminal and watch progress with
   > `ssh -i ~/.ssh/lab_admin ubuntu@10.10.10.30 docker ps` (run it every minute). Containers appear as they
   > start. `STATUS` should say `Up`, not `Restarting`.

3. Visit each app in the browser on `admin01`: `https://cloud.lab.internal`, `https://pdf.lab.internal`
   and `https://vault.lab.internal`. Sign in through the portal where asked.

## Check it worked

- All three addresses load with a valid certificate (the lab CA, once trusted by your browser or OS; see
  guide 11, step 3).
- You reached NextCloud by signing in through Authelia as a lab user, not with a separate NextCloud password.
- `make verify` later checks all three automatically.

## Evidence to capture

Save in `portfolio/evidence/10-docker-vm-and-apps/`:

| File | What it shows |
| --- | --- |
| `reading-notes.md` | The image, ports and volume you found in the compose files |
| `make-apps.txt` | Output of `make apps` ending with the recap |
| `docker-ps.txt` | `docker ps` on `docker01` showing the containers `Up` |
| `nextcloud.png` | NextCloud after signing in, address bar visible |
| `pdf.png` | Stirling PDF loaded behind the portal |
| `vault.png` | The Vaultwarden login page (do not show any stored passwords) |
| `evidence.md` | Your filled-in evidence log |

## Explain it in your own words

1. What is a container, and how is it different from the VMs and LXC containers you already have?
2. What does Traefik do for the three apps, and how does it know where to send each request?
3. Why do you sign into NextCloud through the portal instead of with its own password?

## If it goes wrong

- A container will not start: `ssh -i ~/.ssh/lab_admin ubuntu@10.10.10.30`, then
  `cd /opt/lab/<stack> && docker compose logs`. Read the last 20 lines; the cause is nearly always there.
- Certificate errors in the browser: your machine does not trust the lab root CA yet; import
  `lab/secrets/ca/root/certs/ca.cert.pem` into its trust store (guide 11, step 3).
- A page says "502 Bad Gateway": Traefik is up but the app behind it is not. Check `docker ps` for that app.
- `make apps` fails early with an SSH error: the Docker VM runs as the `ubuntu` user and its cloud image
  disables root key login by design. Check `ssh -i ~/.ssh/lab_admin ubuntu@10.10.10.30` works by hand.
- Out of memory or very slow: `docker01` has 5 GB. Close other apps in `admin01`, or ask your lecturer.
