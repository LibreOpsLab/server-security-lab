#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need curl
out=$(curl -sf --max-time 8 "https://grafana.$domain/api/health") || fail "https://grafana.$domain did not answer (make monitoring)"
echo "$out" | grep -q '"database": *"ok"' || fail "Grafana health: $out"
pass "Grafana is healthy"
