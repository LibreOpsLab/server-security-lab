#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The web vault goes through single sign-on; the app API path does not need it.
need curl
loc=$(curl -s --max-time 8 -o /dev/null -w '%{http_code} %{redirect_url}' "https://vault.$domain/") || fail "https://vault.$domain did not answer"
case $loc in 30*"auth.$domain"*) ;; *) fail "web vault did not redirect to the sign-in portal: $loc" ;; esac
code=$(curl -s --max-time 8 -o /dev/null -w '%{http_code}' "https://vault.$domain/alive") || fail "vault /alive did not answer"
[ "$code" = 200 ] || fail "vault /alive returned $code"
pass "web vault behind SSO, API path reachable"
