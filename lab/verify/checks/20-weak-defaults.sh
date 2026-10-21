#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The security loop needs something to find: this lab must still be functional but NOT hardened.
# If one of these is missing, something was hardened before the baseline (week 12). That is worth knowing.
need nc curl smbclient
missing=""
m=$(lab_ip mail01); f=$(lab_ip files01); d=$(lab_ip docker01)
# enum: the management and service ports an attacker enumerates are open
for target in "$f:22" "$m:25" "$d:80"; do nc -z -w3 "${target%%:*}" "${target##*:}" || missing="$missing enum($target)"; done
# mail-basics: VRFY is on. Postfix's own EHLO reply starts with "250", so matching any 25x line would
# also match the banner; only the literal refusal text is unambiguous.
v=$(printf 'EHLO lab\r\nVRFY alice\r\nQUIT\r\n' | nc -w4 "$m" 25)
echo "$v" | grep -qi "VRFY command is disabled" && missing="$missing VRFY"
# anon-directory: the public share lists without a login
smbclient -N -L "//$f" 2>/dev/null | grep -q "notices" || missing="$missing smbclient-notices"
# web-basics: no Strict-Transport-Security header on the web tier
curl -sIk --max-time 8 "https://$d/" -H "Host: cloud.$domain" | grep -qi "Strict-Transport-Security" && missing="$missing Strict-Transport-Security"
# ssh-weak-creds: password login is accepted by SSH
ssh -o BatchMode=yes -o PreferredAuthentications=none -o StrictHostKeyChecking=no -o ConnectTimeout=5 "nobody@$f" 2>&1 | grep -q "password" || missing="$missing PasswordAuthentication"
[ -z "$missing" ] && pass "all five weak defaults are present (baseline can start)"
fail "weak defaults missing:$missing (was something hardened early?)"
