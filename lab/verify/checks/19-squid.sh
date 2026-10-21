#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# Squid on pfSense proxies a request to a lab web page.
need curl nc
gw=$(lab_ip pfsense01)
nc -z -w3 "$gw" 3128 || fail "Squid is not listening on $gw:3128 (docs/build/09-squid.md)"
curl -sf --max-time 10 -x "http://$gw:3128" -o /dev/null "https://auth.$domain/api/health" || fail "a request through the proxy to auth.$domain failed"
pass "requests go through the proxy on $gw:3128"
