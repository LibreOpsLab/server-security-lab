#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The domain controller answers for the lab names, including a friendly alias.
need dig
dc=$(lab_ip samba-dc01)
a=$(dig +short +time=3 +tries=1 "@$dc" "samba-dc01.$domain" A)
[ "$a" = "$dc" ] || fail "samba-dc01.$domain did not resolve to $dc (got '${a:-nothing}')"
cname=$(dig +short +time=3 +tries=1 "@$dc" "cloud.$domain" CNAME)
[ -n "$cname" ] || fail "alias cloud.$domain has no CNAME"
pass "$dc answers for $domain, including aliases"
