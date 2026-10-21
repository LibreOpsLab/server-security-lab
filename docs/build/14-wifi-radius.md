# 14: Wi-Fi: RADIUS

## What you will build

`radius01`: FreeRADIUS, so a wireless network (or a simulation of one) can authenticate against Samba AD
using WPA-Enterprise.

## Why

WPA-Enterprise (802.1X) is how real organisations run Wi-Fi: each person signs in with their own directory
account, not a single shared password everyone knows.

## Steps

```bash
cd lab
make services
```

If you have Wi-Fi hardware on the lab's second NIC, point its RADIUS settings at `10.10.10.23` with the
secret in `lab/secrets/radius_shared_secret`. If not, use `eapol_test` instead (no wireless hardware
needed): a template is written to `/root/eapol_test.conf.example` on `radius01`.

## Check it worked

```bash
eapol_test -c eapol_test.conf -a 10.10.10.23 -s "$(cat lab/secrets/radius_shared_secret)"
```
ends with `SUCCESS` for a user in the `wifi` group, and is rejected for one who is not.

## If it goes wrong

- "no response from server": check the shared secret matches on both ends, and that port 1812/UDP reaches
  `radius01`.
