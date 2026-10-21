#!/usr/bin/env bash
# Create the lab's groups and users from a CSV, on the domain controller.
#
# Usage: load-users.sh users.csv
# Columns: username,display_name,groups,initial_password   (groups separated by ';')
#
# Every line is validated BEFORE anything is created, and values are passed to samba-tool as separate
# arguments (never through a shell), so a hostile line cannot inject commands. Safe to re-run: existing
# users and groups are skipped.
set -euo pipefail

csv=${1:?usage: load-users.sh users.csv}
tool=${SAMBA_TOOL:-samba-tool}
allowed_groups=" staff finance admins wifi "
ou=${LAB_USERS_OU:-LabUsers}
domain=${LAB_DOMAIN:-lab.internal}

fail() { echo "$csv: line $1: $2" >&2; exit 2; }

declare -a users=() names=() groups=() passwords=()
declare -A seen_groups=()
n=0
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n + 1))
  line=${line%$'\r'}
  if [ "$n" -eq 1 ]; then
    [ "$line" = "username,display_name,groups,initial_password" ] || fail 1 "missing or wrong header row"
    continue
  fi
  [ -z "$line" ] && continue
  [[ $line == \#* ]] && continue
  IFS=, read -r u d g p extra <<<"$line"
  [ -z "${extra:-}" ] || fail "$n" "too many columns (commas are not allowed inside values)"
  [[ $u =~ ^[a-z][a-z0-9._-]{1,31}$ ]] || fail "$n" "invalid username"
  [[ $d =~ ^[A-Za-z][A-Za-z\ .\'-]{0,63}$ ]] || fail "$n" "invalid display name"
  [[ $p =~ ^[[:graph:]]{4,64}$ ]] || fail "$n" "password must be 4 to 64 printable characters without spaces"
  [ -n "$g" ] || fail "$n" "no group"
  IFS=';' read -ra gs <<<"$g"
  for one in "${gs[@]}"; do
    [[ $allowed_groups == *" $one "* ]] || fail "$n" "unknown group '$one'"
    seen_groups[$one]=1
  done
  users+=("$u") names+=("$d") groups+=("$g") passwords+=("$p")
done <"$csv"
[ "${#users[@]}" -gt 0 ] || fail 1 "no users"

"$tool" ou list 2>/dev/null | grep -qx "OU=$ou" || "$tool" ou create "OU=$ou" >/dev/null 2>&1 || true

for g in "${!seen_groups[@]}"; do
  "$tool" group show "$g" >/dev/null 2>&1 || "$tool" group add "$g"
done

for i in "${!users[@]}"; do
  u=${users[$i]} d=${names[$i]} p=${passwords[$i]}
  if "$tool" user show "$u" >/dev/null 2>&1; then
    echo "kept $u"
  else
    "$tool" user create "$u" "$p" --given-name="${d%% *}" --surname="${d#* }" --mail-address="$u@$domain" --userou="OU=$ou"
    echo "created $u"
  fi
  IFS=';' read -ra gs <<<"${groups[$i]}"
  for one in "${gs[@]}"; do "$tool" group addmembers "$one" "$u" >/dev/null 2>&1 || true; done
done
