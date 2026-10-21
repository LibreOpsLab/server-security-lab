#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# pfSense forwards the lab domain to Samba and everything else out.
need dig
gw=$(lab_ip pfsense01)
a=$(dig +short +time=3 +tries=1 "@$gw" "samba-dc01.$domain" A)
[ "$a" = "$(lab_ip samba-dc01)" ] || fail "pfSense ($gw) did not forward $domain to the domain controller"
pass "pfSense forwards $domain to Samba"
