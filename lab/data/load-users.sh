#!/usr/bin/env bash
# Create the lab's groups and users from a CSV, on the domain controller.
#
# Usage: load-users.sh users.csv
# Columns: username,display_name,groups,initial_password   (groups separated by ';')
# or, for a directory that feels like a real company:
#          username,display_name,groups,initial_password,title,department,office,employee_type,manager
# `manager` is the username of another row (or empty). Title, department, office and employee type are stored on
# the account; the manager and employee type are set in a second step, once every account exists.
#
# Every line is validated BEFORE anything is created, and values are passed to samba-tool as separate
# arguments (never through a shell), so a hostile line cannot inject commands. Safe to re-run: existing
# users and groups are skipped.
set -euo pipefail

csv=${1:?usage: load-users.sh users.csv}
tool=${SAMBA_TOOL:-samba-tool}
allowed_groups=" lab-staff finance admins wifi shared-mailbox "
ou=${LAB_USERS_OU:-LabUsers}
domain=${LAB_DOMAIN:-boab.lab}
ldbmodify=${LDBMODIFY:-ldbmodify}
sam_ldb=${SAM_LDB:-/var/lib/samba/private/sam.ldb}
base_dn="DC=${domain//./,DC=}"
company=${LAB_COMPANY:-Boab Ridge Mining Services}

text_re='^[A-Za-z][A-Za-z0-9 &/().'"'"'-]{0,63}$'

fail() { echo "$csv: line $1: $2" >&2; exit 2; }

declare -a users=() names=() groups=() passwords=() titles=() depts=() offices=() types=() managers=()
declare -A known=()
extended=0
declare -A seen_groups=()
n=0
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n + 1))
  line=${line%$'\r'}
  if [ "$n" -eq 1 ]; then
    case "$line" in
      "username,display_name,groups,initial_password") extended=0 ;;
      "username,display_name,groups,initial_password,title,department,office,employee_type,manager") extended=1 ;;
      *) fail 1 "missing or wrong header row" ;;
    esac
    continue
  fi
  [ -z "$line" ] && continue
  [[ $line == \#* ]] && continue
  t="" dep="" off="" et="" mgr=""
  if [ "$extended" -eq 1 ]; then
    IFS=, read -r u d g p t dep off et mgr extra <<<"$line"
  else
    IFS=, read -r u d g p extra <<<"$line"
  fi
  [ -z "${extra:-}" ] || fail "$n" "too many columns (commas are not allowed inside values)"
  [[ $u =~ ^[a-z][a-z0-9._-]{1,31}$ ]] || fail "$n" "invalid username"
  [[ $d =~ ^[A-Za-z][A-Za-z\ .\'-]{0,63}$ ]] || fail "$n" "invalid display name"
  [[ $p =~ ^[[:graph:]]{4,64}$ ]] || fail "$n" "password must be 4 to 64 printable characters without spaces"
  [ -n "$g" ] || fail "$n" "no group"
  if [ "$extended" -eq 1 ]; then
    for v in "$t" "$dep" "$off" "$et"; do
      [[ $v =~ $text_re ]] || fail "$n" "invalid title, department, office or employee type"
    done
    [ -z "$mgr" ] || [[ $mgr =~ ^[a-z][a-z0-9._-]{1,31}$ ]] || fail "$n" "invalid manager username"
  fi
  IFS=';' read -ra gs <<<"$g"
  for one in "${gs[@]}"; do
    [[ $allowed_groups == *" $one "* ]] || fail "$n" "unknown group '$one'"
    seen_groups[$one]=1
  done
  [ -z "${known[$u]:-}" ] || fail "$n" "duplicate username '$u'"
  known[$u]=${#users[@]}
  users+=("$u") names+=("$d") groups+=("$g") passwords+=("$p") titles+=("$t") depts+=("$dep") offices+=("$off") types+=("$et") managers+=("$mgr")
done <"$csv"
[ "${#users[@]}" -gt 0 ] || fail 1 "no users"
for i in "${!users[@]}"; do
  m=${managers[$i]}
  [ -z "$m" ] || [ -n "${known[$m]:-}" ] || fail "?" "manager '$m' of '${users[$i]}' is not a user in the file"
done

"$tool" ou list 2>/dev/null | grep -qx "OU=$ou" || "$tool" ou create "OU=$ou" >/dev/null 2>&1 || true

for g in "${!seen_groups[@]}"; do
  "$tool" group show "$g" >/dev/null 2>&1 || "$tool" group add "$g"
done

for i in "${!users[@]}"; do
  u=${users[$i]} d=${names[$i]} p=${passwords[$i]}
  if "$tool" user show "$u" >/dev/null 2>&1; then
    echo "kept $u"
  else
    extra_args=()
    if [ "$extended" -eq 1 ]; then
      extra_args=(--job-title="${titles[$i]}" --department="${depts[$i]}" --physical-delivery-office="${offices[$i]}" --company="$company")
    fi
    "$tool" user create "$u" "$p" --given-name="${d%% *}" --surname="${d#* }" --mail-address="$u@$domain" --userou="OU=$ou" "${extra_args[@]}"
    echo "created $u"
  fi
  IFS=';' read -ra gs <<<"${groups[$i]}"
  for one in "${gs[@]}"; do "$tool" group addmembers "$one" "$u" >/dev/null 2>&1 || true; done
done

# Manager and employee type have no samba-tool option, so set them in one LDIF after every account exists.
# (The account's CN is its display name, which is what samba-tool uses when --use-username-as-cn is not given.)
if [ "$extended" -eq 1 ]; then
  ldif=$(mktemp)
  trap 'rm -f "$ldif"' EXIT
  for i in "${!users[@]}"; do
    dn="CN=${names[$i]},OU=$ou,$base_dn"
    {
      echo "dn: $dn"
      echo "changetype: modify"
      echo "replace: employeeType"
      echo "employeeType: ${types[$i]}"
      if [ -n "${managers[$i]}" ]; then
        mi=${known[${managers[$i]}]}
        echo "-"
        echo "replace: manager"
        echo "manager: CN=${names[$mi]},OU=$ou,$base_dn"
      fi
      echo
    } >>"$ldif"
  done
  "$ldbmodify" -H "$sam_ldb" "$ldif" >/dev/null
  echo "set manager and employee type for ${#users[@]} users"
fi
