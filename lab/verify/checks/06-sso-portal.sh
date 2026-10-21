#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The Authelia sign-in portal answers through Traefik with the lab certificate.
need curl
out=$(curl -sf --max-time 8 "https://auth.$domain/api/health") || fail "https://auth.$domain/api/health did not answer (make services, make apps)"
echo "$out" | grep -qi "ok" || fail "Authelia health check returned: $out"
pass "https://auth.$domain is healthy"
