#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need curl
m=$(lab_ip mon01)
curl -sf --max-time 5 "http://$m:3100/ready" | grep -qi ready || fail "Loki not ready on $m:3100"
pass "Loki is ready"
