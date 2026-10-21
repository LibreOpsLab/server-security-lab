#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# LDAP over TLS works and the lab CA is trusted (no certificate errors).
need ldapsearch
r=$(ldapsearch -x -H "ldaps://samba-dc01.$domain" -s base -b "" namingContexts 2>&1)
echo "$r" | grep -q "namingContexts" || fail "LDAPS to samba-dc01.$domain failed (is the lab CA trusted? make trust)"
pass "LDAPS answers and the certificate is trusted"
