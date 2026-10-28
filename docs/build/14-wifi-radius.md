# 14: Wi-Fi: RADIUS

## What you will build

`radius01`: FreeRADIUS, so a wireless network (or a simulation of one) can authenticate against Samba AD
using WPA-Enterprise.

**Time and difficulty:** 2 to 3 hours. Hard. This is the most technical service in the build (it joins the
domain and uses a Windows-style authentication helper). Do not be discouraged if it needs a second attempt.

## Why

WPA-Enterprise (802.1X) is how real organisations run Wi-Fi: each person signs in with their own directory
account, not a single shared password everyone knows.

> **What's going on:** At home, one Wi-Fi password is shared with everyone. If someone leaves, you change it
> for everyone. In a business, **WPA-Enterprise** makes each person prove who they are with their own
> account. The access point does not decide; it asks a **RADIUS** server (`radius01`), which asks the
> directory. Removing someone's account removes their Wi-Fi at the same time. You probably have no Wi-Fi
> hardware on the lab network, so you will use `eapol_test`, a tool that performs the same exchange a laptop
> would, to prove the server works.

## Before you start

- Guides 07 and 08 are complete, and time is in sync.
- Take a snapshot of `pve01` called `before-make-radius`.

## Steps

1. Read first. Open `lab/ansible/roles/radius/tasks/main.yml` and find where the machine joins the domain
   and where users in the `wifi` group are allowed. Note both.
2. Build the server:

   ```bash
   cd lab
   make radius
   ```

3. Test the sign-in. If you have Wi-Fi hardware on the lab's second NIC, point its RADIUS settings at
   `10.10.10.23` with the secret in `lab/secrets/radius_shared_secret`. If not (the usual case), use
   `eapol_test`, which performs the same exchange a laptop would. Run it **on `admin01`**:

   ```bash
   sudo apt install -y eapoltest
   scp -i ~/.ssh/lab_admin root@10.10.10.23:/root/eapol_test.conf.example ~/eapol_test.conf
   ```

   Open `~/eapol_test.conf` and replace `CHANGE-ME` with the starting password of a user in the `wifi`
   group (see `lab/data/users.csv`). The file's own comments explain each line.

   > **Careful:** The shared secret between the access point and RADIUS is a password. Passing it on the
   > command line (as below) briefly puts it in your shell history. In the lab that is acceptable; do not
   > screenshot it, and clear it with `history -c` afterwards. The conf file now holds a user's password,
   > so keep it in your home folder and never inside the repository.

## Check it worked

From the repository root on `admin01`:

```bash
eapol_test -c ~/eapol_test.conf -a 10.10.10.23 -s "$(cat lab/secrets/radius_shared_secret)"
```

ends with `SUCCESS` for a user in the `wifi` group, and is rejected for one who is not.

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=14` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/14-wifi-radius/`:

| File                | What it shows                                                                      |
| ------------------- | ---------------------------------------------------------------------------------- |
| `reading-notes.md`  | Where the domain join and the `wifi` group rule are in the role                    |
| `make-radius.txt`   | Output of `make radius` ending with the recap                                      |
| `eapol-success.txt` | A `SUCCESS` result for a `wifi` user (the shared secret **must not** appear in it) |
| `eapol-reject.txt`  | A rejection for a user who is not in the `wifi` group                              |
| `evidence.md`       | Your filled-in evidence log                                                        |

## Explain it in your own words

1. Why is WPA-Enterprise better than one shared Wi-Fi password when an employee leaves?
2. What are the three parties in the exchange (the device, the access point, and the server)? What does
   each do?
3. Why did one user succeed and the other fail?

## If it goes wrong

**Run this first:** `make preflight STAGE=services`. It checks what this guide depends on and says what to fix.

- "no response from server": check the shared secret matches on both ends, and that port 1812/UDP reaches
  `radius01`.
- The join to the domain failed: confirm time is in sync (guide 08) and `make identity` completed.
- `eapol_test: command not found` after installing: the package name may differ on your Ubuntu version.
  Search with `apt search eapol`, or ask your lecturer. Record which package you used.
- To test a user outside the `wifi` group, change `identity` and `password` in the conf file (for example
  to `carol`, who is not in the `wifi` group) and run the same command; it should be rejected.

### Where to look

| What                      | Command or place                                                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| RADIUS service            | `ssh root@10.10.10.23 systemctl status freeradius winbind`                                                                   |
| See its decisions live    | `ssh -t root@10.10.10.23 'systemctl stop freeradius && freeradius -X'` (Ctrl+C, then `systemctl start freeradius` when done) |
| Does it trust the domain? | `ssh root@10.10.10.23 wbinfo -t`                                                                                             |
| Can winbind check a user? | `ssh -t root@10.10.10.23 ntlm_auth --request-nt-key --username=alice --domain=LAB` (asks for the password)                   |
