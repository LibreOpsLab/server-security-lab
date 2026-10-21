#!/usr/bin/env bash
# Create the lab's two-tier CA (root + issuing) non-interactively. Safe to re-run: it never replaces
# an existing CA. Passphrases are read from files, never from the command line or the terminal.
#
# Usage: init-ca.sh CA_DIR     (CA_DIR must contain root.pass and intermediate.pass)
# Adapted from the lab-small-business PKI scripts, made non-interactive for automation.
set -euo pipefail

ca_dir=${1:?usage: init-ca.sh CA_DIR}
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root_cnf=$here/openssl/root-ca.cnf
int_cnf=$here/openssl/intermediate-ca.cnf
root=$ca_dir/root
inter=$ca_dir/intermediate

[ -f "$ca_dir/root.pass" ] && [ -f "$ca_dir/intermediate.pass" ] || { echo "missing passphrase files in $ca_dir" >&2; exit 2; }

init_tree() {
  mkdir -p "$1"/{certs,crl,csr,private,db}
  chmod 700 "$1/private"
  [ -f "$1/db/index.txt" ] || : >"$1/db/index.txt"
  [ -f "$1/db/index.txt.attr" ] || echo "unique_subject = no" >"$1/db/index.txt.attr"
  [ -f "$1/db/serial" ] || echo 1000 >"$1/db/serial"
  [ -f "$1/db/crlnumber" ] || echo 1000 >"$1/db/crlnumber"
}

if [ -f "$root/private/ca.key.pem" ] && [ -f "$inter/certs/ca-chain.cert.pem" ]; then
  echo "kept ca"
  exit 0
fi

# The issuing CA config reads $SAN for leaf certificates; OpenSSL 3 still needs it defined when it loads the file.
export SAN="DNS:lab-ca-placeholder"

init_tree "$root"
(
  cd "$root"
  openssl genrsa -aes256 -passout "file:$ca_dir/root.pass" -out private/ca.key.pem 4096 2>/dev/null
  chmod 400 private/ca.key.pem
  openssl req -config "$root_cnf" -key private/ca.key.pem -passin "file:$ca_dir/root.pass" \
    -new -x509 -days 7300 -sha384 -extensions v3_ca -subj "/O=LAB/CN=LAB Root CA" -out certs/ca.cert.pem
)

init_tree "$inter"
(
  cd "$inter"
  openssl genrsa -aes256 -passout "file:$ca_dir/intermediate.pass" -out private/intermediate.key.pem 4096 2>/dev/null
  chmod 400 private/intermediate.key.pem
  openssl req -config "$int_cnf" -new -sha384 -key private/intermediate.key.pem -passin "file:$ca_dir/intermediate.pass" \
    -subj "/O=LAB/CN=LAB Issuing CA" -out csr/intermediate.csr.pem
)

(
  cd "$root"
  openssl ca -config "$root_cnf" -batch -passin "file:$ca_dir/root.pass" -extensions v3_intermediate_ca -days 3650 \
    -notext -md sha384 -in "$inter/csr/intermediate.csr.pem" -out "$inter/certs/intermediate.cert.pem" 2>/dev/null
)
chmod 444 "$inter/certs/intermediate.cert.pem"
openssl verify -CAfile "$root/certs/ca.cert.pem" "$inter/certs/intermediate.cert.pem" >/dev/null
cat "$inter/certs/intermediate.cert.pem" "$root/certs/ca.cert.pem" >"$inter/certs/ca-chain.cert.pem"
echo "created ca"
