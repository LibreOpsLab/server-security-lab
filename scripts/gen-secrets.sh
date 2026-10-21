#!/usr/bin/env bash
# Generate the lab's service secrets and CA once, into a gitignored folder. Re-running is safe: anything
# that already exists is kept untouched. Values are never printed.
#
# Usage: scripts/gen-secrets.sh [--dir lab/secrets]
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dir=$repo/lab/secrets
if [ "${1:-}" = "--dir" ]; then dir=${2:?--dir needs a path}; fi

names=(
  samba_admin_password authelia_jwt_secret authelia_session_secret authelia_storage_key authelia_oidc_hmac
  authelia_oidc_nextcloud_secret nextcloud_db_password nextcloud_admin_password vaultwarden_admin_token
  grafana_admin_password radius_shared_secret mail_ldap_bind_password pbs_admin_password authelia_ldap_password
  nextcloud_db_root_password
)

umask 077
mkdir -p "$dir/ca"
chmod 700 "$dir" "$dir/ca"

new_secret() { # name file
  if [ -f "$2" ]; then echo "kept $1"; return; fi
  # 48 hex characters: strong, and safe inside YAML, shell and URLs
  openssl rand -hex 24 >"$2"
  chmod 600 "$2"
  echo "created $1"
}

for n in "${names[@]}"; do new_secret "$n" "$dir/$n"; done
# Authelia signs OIDC tokens with this RSA key (a PEM file, so it is created differently from the text secrets).
if [ -f "$dir/authelia_oidc_key.pem" ]; then
  echo "kept authelia_oidc_key"
else
  openssl genrsa -out "$dir/authelia_oidc_key.pem" 2048 2>/dev/null
  chmod 600 "$dir/authelia_oidc_key.pem"
  echo "created authelia_oidc_key"
fi
new_secret ca_root_passphrase "$dir/ca/root.pass"
new_secret ca_intermediate_passphrase "$dir/ca/intermediate.pass"

"$repo/lab/pki/init-ca.sh" "$dir/ca"
