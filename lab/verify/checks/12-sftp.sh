#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need nc
f=$(lab_ip files01)
banner=$(nc -w3 "$f" 22 </dev/null | head -1)
case $banner in SSH-*) pass "SSH/SFTP on $f:22" ;; *) fail "no SSH banner from $f:22" ;; esac
