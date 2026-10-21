#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# Stirling PDF must send you to the sign-in portal first.
need curl
loc=$(curl -s --max-time 8 -o /dev/null -w '%{http_code} %{redirect_url}' "https://pdf.$domain/") || fail "https://pdf.$domain did not answer"
case $loc in 30*"auth.$domain"*) pass "redirects to the sign-in portal" ;; *) fail "expected a redirect to auth.$domain, got: $loc" ;; esac
