#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# The company website is public: pages load without a sign-in, and the contact form's address reaches its handler.
need curl
for page in "" about/ services/ people/ contact/; do
  code=$(curl -s --max-time 8 -o /dev/null -w '%{http_code}' "https://www.$domain/$page") || fail "https://www.$domain/$page did not answer"
  [ "$code" = 200 ] || fail "https://www.$domain/$page returned $code"
done
# An empty POST must be refused by the handler (400), which proves the route reaches it and not the static server (405/404).
code=$(curl -s --max-time 8 -o /dev/null -w '%{http_code}' -X POST -d 'name=' "https://www.$domain/contact/send") || fail "contact form did not answer"
[ "$code" = 400 ] || fail "contact form handler returned $code, expected 400 for an empty form"
pass "website pages load and the contact form handler answers"
