#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# This machine takes its time from the domain controller.
need chronyc
dc=$(lab_ip samba-dc01)
chronyc sources 2>/dev/null | grep -q "$dc" || fail "chrony on this machine is not using $dc (run make baseline)"
pass "time comes from $dc"
