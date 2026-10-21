#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need nc
b=$(lab_ip pbs01)
nc -z -w3 "$b" 8007 || fail "Proxmox Backup Server web port 8007 closed on $b (make backup)"
pass "Proxmox Backup Server answers on $b:8007"
