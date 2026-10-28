# 04: admin01

## What you will build

`admin01`: an Ubuntu Desktop VM. This is where you run every `make` command from here on, and later where
the security tools live.

**Time and difficulty:** 2 to 3 hours in two parts. Ubuntu's installer is friendly; the new skills are
static IP addresses and SSH keys.

> **Do this in two parts.** Part A comes _before_ [02-pfsense.md](02-pfsense.md), because your Windows PC
> cannot see the private `LAN-LAB` network, and you need a browser on that network to configure pfSense.
> Part B comes _after_ [03-proxmox.md](03-proxmox.md), because it connects to Proxmox.

## Why

Keeping the control machine separate from the things it manages is standard practice, and it mirrors how a
real small business would run its administration.

> **What's going on:** `admin01` has two network adapters. One is on the private lab network (`LAN-LAB`),
> so it can reach every lab machine. The other is on VMware NAT, so it can reach the internet to install
> software. That makes it the only machine that bridges your PC's world and the lab's world, so protect it.

## Steps

### Part A: build the machine (before pfSense)

1. Create a new VM: 2 vCPU, 3 GB RAM, 40 GB disk, one adapter on `LAN-LAB`, one on VMware NAT (so you can
   fetch packages and this repo). Attach the Ubuntu Desktop 24.04 ISO.

   > **Beginner tip:** In VMware, choose **Custom** when creating the VM, so you can set two network
   > adapters. If you finish with only one, add the other under **VM > Settings > Add > Network Adapter**.
   > Which adapter is which matters later; note down "adapter 1 = `LAN-LAB`, adapter 2 = NAT" in your
   > evidence.

2. Install Ubuntu Desktop 24.04. Create your user account with a password you will remember, and write the
   username in your evidence. Skip the optional extras.
3. **Make the lab network address permanent ("static").** Servers need fixed addresses so other machines can
   always find them. In Ubuntu: **Settings > Network**, click the cog beside the _lab_ adapter, **IPv4**
   tab, choose **Manual**, then:

   | Field   | Value                               |
   | ------- | ----------------------------------- |
   | Address | `10.10.10.10`                       |
   | Netmask | `255.255.255.0` (the same as `/24`) |
   | Gateway | leave blank for now                 |
   | DNS     | leave blank for now                 |

   > **What's going on:** The lab network has no DHCP server yet, because pfSense does not exist yet. So you
   > give `admin01` its address by hand. The gateway and DNS are blank because the NAT adapter already
   > provides your internet connection; if you also set a gateway here, the two adapters will fight over the
   > way out. After pfSense is up, DHCP and routing for the lab are pfSense's job.

   > **Beginner tip:** Not sure which adapter is which? In a terminal, `ip -br a` lists adapters and their
   > addresses. The one with a `192.168.x.x` or similar address from VMware NAT is the internet one; the
   > other is the lab.

4. Install the tools you need now. Open a terminal (`Ctrl + Alt + T`):

   ```bash
   sudo apt update
   sudo apt install -y git python3 gh
   ```

5. Clone your private course repository, using the URL your lecturer gave you:

   ```bash
   gh auth login
   git clone https://github.com/YOUR-ACCOUNT/server-security-lab.git
   cd server-security-lab
   ```

   > **Beginner tip:** `gh auth login` shows a short code and asks you to open a web page to sign in. Choose
   > **HTTPS**, and say yes to authenticating Git. Never type your password or a token into a command or a
   > file. If your lecturer has not given you a private repository, see
   > [05](05-the-repo-inventory-and-secrets.md) for how to make one, then come back.

6. Configure Git on `admin01`, as you did on Windows in [DevOps 101](../devops-101.md#2-configure-git-once):
   `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`.

You can now carry on to [02-pfsense.md](02-pfsense.md).

### Part B: connect it to the lab (after Proxmox exists)

Come back here when `pve01` is installed and answering at `10.10.10.5` (guide 03).

7.  Install Ansible: `sudo apt install -y ansible` (or `pipx install ansible-core`).

    > **What's going on:** Ansible is the tool that will configure all the other machines for you. You
    > describe the end state in files (playbooks); Ansible logs in over SSH and makes it so. Running it twice
    > is safe, because it only changes what is not already correct.

8.  Confirm `sudo` works without a password prompt for your user (`sudo -n true`), since several playbooks
    use `become: true` locally on this machine (for example the certificate-issuing plays). If it asks for a
    password, put `ANSIBLE_BECOME_ASK_PASS=true` in front of each `make` command (for example
    `ANSIBLE_BECOME_ASK_PASS=true make baseline`) and Ansible will ask for it, or ask your lecturer about
    passwordless sudo for this lab user.
9.  Generate the SSH key pair the automation expects. The name matters, because it is read from
    `ansible_ssh_private_key_file` in the inventory:

    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/lab_admin -N ''
    ```

    > **What's going on:** An SSH key pair is two files: a private key (`lab_admin`, never share it) and a
    > public key (`lab_admin.pub`, safe to hand out). A machine that has your public key lets you in without a
    > password if you hold the matching private key. Ansible will use this to log into every guest.

    > **Careful:** `-N ''` makes a key with no passphrase so automation can use it unattended. That is a
    > lab convenience. A key with no passphrase is a password-free way into every guest, so the file must
    > never leave `admin01`, and never be committed or screenshotted.

10. Tell SSH to use this key for the lab, so plain `ssh root@10.10.10.5` works (by default SSH only tries
    keys with standard names):

        ```bash
        printf 'Host 10.10.10.* *.lab.internal
        IdentityFile ~/.ssh/lab_admin

    ' >> ~/.ssh/config
    chmod 600 ~/.ssh/config
    ```

11. Copy the public key to `pve01` (`guest.sh` installs it on every guest it creates; `pve01` itself needs it
    copied by hand once, since nothing created it yet):

    ```bash
    ssh-copy-id -i ~/.ssh/lab_admin.pub root@10.10.10.5
    ```

    You will be asked for `pve01`'s root password once, and to type `yes` to trust its fingerprint.

## Check it worked

- `ansible --version` runs.
- `ssh root@10.10.10.5 pveversion` works without a password prompt.
- `ip -br a` shows `10.10.10.10/24` on the lab adapter.
- `ping -c 3 10.10.10.1` reaches pfSense (after guide 02) and `ping -c 3 example.com` reaches the internet.

## Evidence to capture

Save in `portfolio/evidence/04-admin01/`:

| File                         | What it shows                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| `vm-settings.png`            | VMware VM settings with both network adapters and which network each is on                        |
| `ip-addr.txt`                | Output of `ip -br a` on `admin01`, with the prompt visible                                        |
| `ansible-version.txt`        | Output of `ansible --version`                                                                     |
| `ssh-pveversion.txt`         | The `ssh ... pveversion` command and its output, showing no password was asked                    |
| `public-key-fingerprint.txt` | Output of `ssh-keygen -lf ~/.ssh/lab_admin.pub` (the fingerprint only, **never** the private key) |
| `evidence.md`                | Your filled-in evidence log                                                                       |

## Explain it in your own words

1. Why does `admin01` have two network adapters, and what would go wrong if both had a gateway set?
2. What is the difference between the public and private half of an SSH key? Which one did you copy to
   `pve01`?

## If it goes wrong

- No internet on `admin01`: check the NAT adapter is attached and connected in VMware. In Ubuntu **Settings >
  Network**, the NAT adapter should be set to automatic (DHCP).
- `ssh-copy-id` says `Permission denied`: you used the wrong root password, or `pve01` does not allow root
  password login yet. Re-check the password you set during the Proxmox install.
- `gh auth login` fails or the clone says `repository not found`: check the URL is the _private_ one your
  lecturer gave you, and that your GitHub account has been granted access.
- `sudo: a password is required`: see step 8. Put `ANSIBLE_BECOME_ASK_PASS=true` in front of the `make`
  command, or ask your lecturer.
