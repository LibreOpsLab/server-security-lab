#!/usr/bin/env bash
# Back up (or restore) the lab secrets and CA as an age-encrypted archive, kept OUTSIDE the repo
# (for example on your USB drive), so a wiped PC does not lose your CA.
#
# Back up:  scripts/backup-secrets.sh OUT.age [--dir lab/secrets] [--recipient AGE_PUBLIC_KEY]
#           Without --recipient, age asks for a passphrase.
# Restore:  scripts/backup-secrets.sh --restore IN.age [--dir lab/secrets] [--identity KEYFILE]
#           Restoring never overwrites a file that already exists.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dir=$repo/lab/secrets
mode=backup file="" recipient="" identity=""
while [ $# -gt 0 ]; do
  case $1 in
    --restore) mode=restore; file=${2:?--restore needs a file}; shift 2 ;;
    --dir) dir=${2:?--dir needs a path}; shift 2 ;;
    --recipient) recipient=${2:?--recipient needs a key}; shift 2 ;;
    --identity) identity=${2:?--identity needs a file}; shift 2 ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) file=$1; shift ;;
  esac
done
[ -n "$file" ] || { echo "usage: see the header of $0" >&2; exit 2; }
command -v age >/dev/null 2>&1 || { echo "install age first (https://github.com/FiloSottile/age)" >&2; exit 2; }

if [ "$mode" = backup ]; then
  [ -d "$dir" ] || { echo "no secrets at $dir; run scripts/gen-secrets.sh first" >&2; exit 2; }
  umask 077
  if [ -n "$recipient" ]; then
    tar -C "$dir" -cf - . | age -r "$recipient" -o "$file"
  else
    tar -C "$dir" -cf - . | age -p -o "$file"
  fi
  echo "wrote $file (keep it outside the repo)"
else
  umask 077
  mkdir -p "$dir"
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  if [ -n "$identity" ]; then age -d -i "$identity" "$file" | tar -C "$tmp" -xf -; else age -d "$file" | tar -C "$tmp" -xf -; fi
  (cd "$tmp" && find . -type f) | while read -r f; do
    if [ -e "$dir/$f" ]; then echo "kept $f"; else mkdir -p "$(dirname "$dir/$f")"; cp -p "$tmp/$f" "$dir/$f"; echo "restored $f"; fi
  done
fi
