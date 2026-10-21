#!/usr/bin/env bash
# Helpers for the verify checks. Source this file; do not run it.
#
# A check prints exactly one line: "PASS name message", "FAIL name message" or "SKIP name message".
# Addresses are read from the same inventory file Ansible uses, so nothing is typed twice.
VERIFY_ROOT=${VERIFY_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}
GROUP_VARS=$VERIFY_ROOT/lab/inventory/group_vars/all.yml
check_name=$(basename "$0" .sh)
check_name=${check_name#*-}

lab_ip() { sed -nE "s/^  $1: \{.*ip: ([0-9.]+).*/\1/p" "$GROUP_VARS" | head -1; }
lab_var() { sed -nE "s/^$1: *(.*)$/\1/p" "$GROUP_VARS" | head -1; }

pass() { echo "PASS $check_name $*"; exit 0; }
fail() { echo "FAIL $check_name $*"; exit 0; }
skip() { echo "SKIP $check_name $*"; exit 0; }

# A missing tool is a failure with a fix, not a silent skip: the lab could not be checked.
need() {
  local c
  for c in "$@"; do command -v "$c" >/dev/null 2>&1 || fail "cannot check: install $c"; done
}

# shellcheck disable=SC2034  # used by the checks that source this file
domain=$(lab_var lab_domain)
