#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
need nc
m=$(lab_ip mail01)
nc -z -w3 "$m" 993 || fail "IMAPS port 993 closed on $m"
pass "IMAPS on $m:993"
