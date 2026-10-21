#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need nc
m=$(lab_ip mail01)
banner=$(printf 'QUIT\r\n' | nc -w3 "$m" 25 | head -1)
case $banner in 220*) pass "SMTP on $m:25 says: ${banner:0:40}" ;; *) fail "no SMTP banner from $m:25 (got '${banner:-nothing}')" ;; esac
