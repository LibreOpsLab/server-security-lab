# Glossary

Plain-language meanings for the words the build guides use. Skim it in week 1, then come back whenever a
word is new. If a word is missing, ask your lecturer and add it (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

## Computers and virtual machines

| Word                      | What it means here                                                                                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Host**                  | The real Windows PC in front of you.                                                                                                                                    |
| **Guest / VM**            | A "computer inside the computer": a virtual machine running in VMware or Proxmox.                                                                                       |
| **Hypervisor**            | Software that runs VMs. VMware Workstation and Proxmox VE are both hypervisors.                                                                                         |
| **Nested virtualisation** | A hypervisor (Proxmox) running inside a VM that is itself running on a hypervisor (VMware). It only works if the host passes the CPU's virtualisation features through. |
| **LXC container**         | A lighter kind of guest that shares the Proxmox host's Linux kernel instead of pretending to be a whole PC. Fast and small, which is why most lab services use them.    |
| **Snapshot**              | A saved point in time of a VM that you can roll back to. Take one before anything risky.                                                                                |
| **ISO**                   | A file that is a copy of an install disc. You "insert" it into a VM to install an operating system.                                                                     |
| **Console**               | The screen and keyboard of a VM, seen through VMware or Proxmox, not over the network.                                                                                  |

## Networking

| Word                          | What it means here                                                                                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **IP address**                | A computer's address on a network, such as `10.10.10.5`.                                                                             |
| **Subnet / `/24`**            | A block of addresses that belong together. `10.10.10.0/24` means `10.10.10.0` to `10.10.10.255`.                                     |
| **Gateway**                   | The address of the router that leads out of the subnet. In the lab it is pfSense, `10.10.10.1`.                                      |
| **DNS**                       | The phone book that turns a name (`samba-dc01.lab.internal`) into an IP address.                                                     |
| **DHCP**                      | The service that hands out addresses automatically to machines that ask. Servers in this lab use fixed ("static") addresses instead. |
| **NAT**                       | Lets machines on a private network reach the internet through one shared address.                                                    |
| **Firewall**                  | Rules that allow or block traffic. pfSense is the lab's firewall.                                                                    |
| **Proxy (forward / reverse)** | A forward proxy sits in front of _users_ going out (Squid). A reverse proxy sits in front of _servers_ being visited (Traefik).      |
| **Port**                      | A numbered door on a computer. Web is usually 443, SSH is 22, DNS is 53.                                                             |
| **TLS / HTTPS**               | Encryption for network traffic, proven by a certificate. The padlock in the browser.                                                 |
| **LAN Segment**               | A private virtual network in VMware that only VMs can see. Your Windows host cannot reach it directly.                               |

## Identity and security

| Word                                  | What it means here                                                                                                                                        |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Directory / Active Directory (AD)** | One central list of users, groups and computers that many services check against. Samba AD is the lab's.                                                  |
| **LDAP / LDAPS**                      | The protocol for asking a directory questions. The "S" means it is encrypted.                                                                             |
| **Kerberos**                          | A ticket-based sign-in system used by AD. It fails if computer clocks differ by more than a few minutes.                                                  |
| **SSO (single sign-on)**              | Sign in once, use many applications. Authelia does this in the lab.                                                                                       |
| **OIDC (OpenID Connect)**             | A standard way for an application to trust a sign-in portal.                                                                                              |
| **TOTP / MFA**                        | The six-digit code from an authenticator app: a second proof of who you are.                                                                              |
| **Certificate / CA**                  | A certificate proves a server's identity. A certificate authority (CA) signs certificates. The lab runs its own CA, so machines must be told to trust it. |
| **RADIUS / WPA-Enterprise**           | Wi-Fi where each person signs in with their own account instead of one shared Wi-Fi password.                                                             |
| **Hardening**                         | Making something harder to attack by removing, locking down or restricting things.                                                                        |
| **Attack surface**                    | Everything an attacker could try to talk to.                                                                                                              |
| **Baseline**                          | The "as built" state you measure before you change anything.                                                                                              |
| **Secret**                            | A password, key or token. Secrets never go in Git, screenshots or chat.                                                                                   |

## Automation and Git

| Word                     | What it means here                                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Ansible**              | A tool that reads a description of how a server should look ("playbook") and makes it so. Running it twice is safe. |
| **Playbook / role**      | A playbook is a list of jobs. A role is a reusable bundle of jobs for one service.                                  |
| **Idempotent**           | Safe to run again: it only changes what is not already right.                                                       |
| **`make`**               | A tool that gives short names to long commands. `make guests` runs the "create the guests" playbook.                |
| **Inventory**            | The list of machines and their details. Here: `lab/inventory/group_vars/all.yml`.                                   |
| **Repository (repo)**    | A project folder that Git tracks.                                                                                   |
| **Commit / push / pull** | Save a snapshot locally / upload it / download others' changes.                                                     |
| **Branch**               | A separate line of work, so unfinished work stays off `main`.                                                       |
| **Pull request (PR)**    | A proposal to merge one branch into another, with a place to review it.                                             |
| **SSH / SSH key**        | Encrypted remote command-line access. A key pair lets you sign in without typing a password.                        |
| **`sudo`**               | Run one command with administrator rights on Linux.                                                                 |
