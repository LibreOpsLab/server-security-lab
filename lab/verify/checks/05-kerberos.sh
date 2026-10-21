#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The Kerberos service is reachable and DNS advertises it.
need nc dig
dc=$(lab_ip samba-dc01)
nc -z -w3 "$dc" 88 || fail "Kerberos port 88 closed on $dc"
srv=$(dig +short +time=3 +tries=1 "@$dc" "_kerberos._tcp.$domain" SRV)
[ -n "$srv" ] || fail "no _kerberos._tcp SRV record in $domain"
pass "Kerberos on $dc:88 and advertised in DNS"
