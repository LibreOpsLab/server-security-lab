#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need curl
out=$(curl -sf --max-time 10 "https://cloud.$domain/status.php") || fail "https://cloud.$domain/status.php did not answer (make apps)"
echo "$out" | grep -q '"installed":true' || fail "NextCloud is not installed yet: $out"
pass "NextCloud is installed"
