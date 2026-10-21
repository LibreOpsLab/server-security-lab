#!/usr/bin/env bash
# shellcheck source=../lib.sh
# shellcheck disable=SC2154
source "${BASH_SOURCE[0]%/*}/../lib.sh"
# A real EAP exchange (PEAP-MSCHAPv2) against FreeRADIUS, without a wireless card.
need eapol_test
r=$(lab_ip radius01)
secret_file=$VERIFY_ROOT/lab/secrets/radius_shared_secret
[ -r "$secret_file" ] || skip "no generated secrets on this machine"
user=alice
pw=$(awk -F, -v u="$user" '$1 == u {print $4}' "$VERIFY_ROOT/lab/data/users.csv")
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
chmod 600 "$tmp"
printf 'network={\n ssid="lab-wifi"\n key_mgmt=WPA-EAP\n eap=PEAP\n identity="%s"\n password="%s"\n phase2="auth=MSCHAPV2"\n ca_cert="/usr/local/share/ca-certificates/lab-root-ca.crt"\n}\n' "$user" "$pw" >"$tmp"
eapol_test -c "$tmp" -a "$r" -s "$(cat "$secret_file")" 2>&1 | grep -q "^SUCCESS" || fail "EAP exchange for $user was not accepted by $r"
pass "PEAP-MSCHAPv2 login for $user accepted"
