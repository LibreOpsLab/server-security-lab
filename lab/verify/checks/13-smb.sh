#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need smbclient
f=$(lab_ip files01)
out=$(smbclient -N -L "//$f" 2>&1) || fail "could not list shares on $f"
echo "$out" | grep -q "staff" || fail "share 'staff' not found on $f"
pass "SMB shares listed on $f"
