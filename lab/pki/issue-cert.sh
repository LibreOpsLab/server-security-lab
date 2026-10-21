#!/usr/bin/env bash
# Issue a server certificate from the lab's issuing CA.
# Usage: issue-cert.sh CA_DIR COMMON_NAME [SAN]      (SAN defaults to DNS:COMMON_NAME)
# Output: CA_DIR/issued/COMMON_NAME/{key,cert,chain,fullchain}.pem. Existing certificates are kept.
set -euo pipefail

ca_dir=${1:?usage: issue-cert.sh CA_DIR COMMON_NAME [SAN]}
cn=${2:?usage: issue-cert.sh CA_DIR COMMON_NAME [SAN]}
san=${3:-DNS:$cn}
[[ $cn =~ ^[A-Za-z0-9.-]+$ ]] || { echo "invalid common name: $cn" >&2; exit 2; }
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
inter=$ca_dir/intermediate
out=$ca_dir/issued/$cn

if [ -f "$out/cert.pem" ]; then echo "kept $cn"; exit 0; fi
mkdir -p "$out"
openssl req -new -nodes -newkey rsa:2048 -keyout "$out/key.pem" -subj "/O=LAB/CN=$cn" -out "$out/csr.pem" 2>/dev/null
chmod 600 "$out/key.pem"
(
  cd "$inter"
  SAN="$san" openssl ca -config "$here/openssl/intermediate-ca.cnf" -batch -passin "file:$ca_dir/intermediate.pass" \
    -extensions server_cert -days 397 -notext -md sha384 -in "$out/csr.pem" -out "$out/cert.pem" 2>/dev/null
)
cp "$inter/certs/ca-chain.cert.pem" "$out/chain.pem"
cat "$out/cert.pem" "$out/chain.pem" >"$out/fullchain.pem"
echo "created $cn"
