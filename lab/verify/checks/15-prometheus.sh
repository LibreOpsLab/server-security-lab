#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need curl
m=$(lab_ip mon01)
curl -sf --max-time 5 "http://$m:9090/-/ready" >/dev/null || fail "Prometheus not ready on $m:9090 (make monitoring)"
down=$(curl -sf --max-time 5 "http://$m:9090/api/v1/query?query=count(up%7Bjob%3D%22nodes%22%7D%3D%3D0)" || true)
case $down in *'"result":[]'*) pass "Prometheus ready, every node target up" ;; *) fail "some node targets are down: ${down:0:120}" ;; esac
