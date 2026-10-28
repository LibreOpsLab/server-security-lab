# Troubleshooting: how to find out what is wrong

Every build guide ends with _If it goes wrong_ and a _Where to look_ table for that guide. This page is the
general method behind them. Troubleshooting is the main skill this lab teaches, so practise it rather than
guessing.

## The method

1. **Read the error. Copy it exactly.** The message nearly always names the problem. Paste it into your
   evidence before you change anything, because a second attempt may hide the first error.
2. **Say what you expected and what happened.** "I expected `ssh root@10.10.10.21 hostname` to print
   `samba-dc01`. It asked for a password."
3. **Check the layers from the bottom up.** Most failures sit in the lowest broken layer:

   | Layer   | Question                | Check                                                |
   | ------- | ----------------------- | ---------------------------------------------------- |
   | Power   | Is the machine running? | VMware or Proxmox console                            |
   | Network | Can I reach it?         | `ping -c 2 ADDRESS`                                  |
   | Name    | Does its name resolve?  | `getent hosts NAME` or `dig NAME`                    |
   | Time    | Are the clocks close?   | `chronyc tracking`, `date`                           |
   | Login   | Can I sign in?          | `ssh -v root@ADDRESS`                                |
   | Service | Is the program running? | `systemctl status NAME`                              |
   | Logs    | What does it say?       | `journalctl -u NAME -n 50 --no-pager`                |
   | Config  | Is the setting right?   | The service's own test command (listed in the guide) |

4. **Change one thing, then test again.** If you change three things and it works, you do not know which one
   fixed it, and you cannot explain it.
5. **Write down what worked.** The fix is part of your evidence.
6. **Ask well.** Bring: the guide and step, the exact error, what you already tried, and the result of the
   guide's `make preflight` if it has one.

## Use the lab's own tools

| Tool                             | When                                                                      |
| -------------------------------- | ------------------------------------------------------------------------- |
| `make preflight STAGE=...`       | **Before** a build step. Checks the things it needs and says what to fix. |
| `make verify`                    | **After** building. One `PASS` or `FAIL` line per service.                |
| `./verify/verify.sh --only NAME` | Re-run a single check while you fix it.                                   |
| `make evidence GUIDE=NN`         | Save the guide's command output, stamped with your name and the date.     |
| `ansible-playbook ... -vv`       | See exactly what Ansible did. `-vvv` shows the SSH commands.              |

## Reading Ansible output

- `ok` means already correct. `changed` means Ansible changed something. `failed` is the problem.
- The failed task's **name** says what it was doing, and the red text under it says why.
- `UNREACHABLE` means Ansible could not log in (the machine is off, the address is wrong, or the SSH key is
  missing). It is not a problem with the task.
- Tasks marked `no_log` hide their output on purpose because they handle secrets. To debug one, run the
  command it wraps by hand on the target machine.
- It is safe to run a playbook again after you fix the cause.

## Common problems across the whole lab

| Symptom                           | Likely cause                                         | First check                                                                  |
| --------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------- |
| Everything is slow                | Nested virtualisation off                            | Guide 03: `egrep -c '(vmx\|svm)' /proc/cpuinfo` inside `pve01`               |
| `Connection timed out` to a guest | Guest off, or wrong network                          | Console, then `ping`                                                         |
| `Permission denied (publickey)`   | Your key is not installed on that machine            | `ssh -v ...`, then guide 04 or the [Debian VM reference](build/debian-vm.md) |
| `Host key verification failed`    | You rebuilt a machine; its fingerprint changed       | `ssh-keygen -R ADDRESS`                                                      |
| Names do not resolve              | Wrong DNS, or the DC is down                         | `cat /etc/resolv.conf`, `dig NAME @10.10.10.21`                              |
| Certificate errors                | The lab CA is not trusted on that machine or browser | `make trust` (system), import the CA (browser)                               |
| Kerberos or sign-in failures      | Clock drift                                          | `chronyc tracking` on both machines                                          |
| `sudo: a password is required`    | Ansible needs sudo on `admin01`                      | `ANSIBLE_BECOME_ASK_PASS=true make ...`                                      |
| Out of disk space                 | Thin disks and snapshots filled the drive            | `df -h` in the guest; delete old VMware snapshots                            |
| Out of memory, lab crawls         | Too many VMs running                                 | Shut down `win-client01` while working on other guides                       |

## When to stop and ask

Ask your lecturer if you have been stuck for 20 minutes, if a step could erase something you cannot recover,
or if a message mentions a policy, a licence or an administrator. Recording where you got stuck, and what you
tried, is evidence of the skill, not a failure.
