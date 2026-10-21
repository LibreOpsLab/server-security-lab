import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
GEN = REPO / "scripts" / "gen-secrets.sh"
BACKUP = REPO / "scripts" / "backup-secrets.sh"
NAMES = [
    "samba_admin_password", "authelia_jwt_secret", "authelia_session_secret", "authelia_storage_key",
    "authelia_oidc_hmac", "authelia_oidc_nextcloud_secret", "nextcloud_db_password", "nextcloud_admin_password",
    "vaultwarden_admin_token", "grafana_admin_password", "radius_shared_secret", "mail_ldap_bind_password",
    "pbs_admin_password",
]


def run(script, *args, cwd=REPO):
    return subprocess.run([str(script), *args], cwd=cwd, capture_output=True, text=True)


def snapshot(d: Path) -> dict:
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.rglob("*")) if p.is_file()}


@pytest.fixture
def secrets(tmp_path):
    d = tmp_path / "secrets"
    r = run(GEN, "--dir", str(d))
    assert r.returncode == 0, r.stderr
    return d, r


def test_creates_all_named_secrets_with_private_mode(secrets):
    d, _ = secrets
    for n in NAMES:
        p = d / n
        assert p.is_file() and p.stat().st_size >= 16, n
        assert oct(p.stat().st_mode)[-3:] == "600", n
    assert oct(d.stat().st_mode)[-3:] == "700"


def test_creates_a_two_tier_ca_that_verifies(secrets):
    d, _ = secrets
    ca = d / "ca"
    assert (ca / "root" / "certs" / "ca.cert.pem").exists()
    assert (ca / "intermediate" / "certs" / "ca-chain.cert.pem").exists()
    r = subprocess.run(["openssl", "verify", "-CAfile", str(ca / "root/certs/ca.cert.pem"),
                        str(ca / "intermediate/certs/intermediate.cert.pem")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert b"ENCRYPTED" in (ca / "root/private/ca.key.pem").read_bytes()  # CA keys are passphrase protected


def test_second_run_changes_nothing_and_says_kept(secrets):
    d, first = secrets
    before = snapshot(d)
    again = run(GEN, "--dir", str(d))
    assert again.returncode == 0
    assert snapshot(d) == before
    assert "kept samba_admin_password" in again.stdout and "created" not in again.stdout
    assert "created samba_admin_password" in first.stdout


def test_never_prints_secret_values(secrets):
    d, first = secrets
    out = first.stdout + first.stderr + run(GEN, "--dir", str(d)).stdout
    for n in NAMES:
        assert (d / n).read_text().strip() not in out


def test_secrets_dir_is_gitignored():
    r = subprocess.run(["git", "check-ignore", "lab/secrets/samba_admin_password"], cwd=REPO, capture_output=True)
    assert r.returncode == 0


@pytest.mark.skipif(shutil.which("age") is None or shutil.which("age-keygen") is None, reason="age not installed")
def test_backup_and_restore_roundtrip_without_overwriting(secrets, tmp_path):
    d, _ = secrets
    key = tmp_path / "key.txt"
    subprocess.run(["age-keygen", "-o", str(key)], check=True, capture_output=True)
    pub = [ln for ln in subprocess.run(["age-keygen", "-y", str(key)], capture_output=True, text=True).stdout.split() if ln.startswith("age1")][0]
    archive = tmp_path / "secrets.age"
    assert run(BACKUP, str(archive), "--dir", str(d), "--recipient", pub).returncode == 0
    assert archive.exists() and b"samba_admin_password" not in archive.read_bytes()

    original = (d / "samba_admin_password").read_text()
    (d / "samba_admin_password").unlink()
    (d / "radius_shared_secret").write_text("changed-on-purpose")  # restore must not overwrite existing files
    assert run(BACKUP, "--restore", str(archive), "--dir", str(d), "--identity", str(key)).returncode == 0
    assert (d / "samba_admin_password").read_text() == original
    assert (d / "radius_shared_secret").read_text() == "changed-on-purpose"


def test_issue_cert_signs_a_server_cert_the_chain_verifies(secrets):
    d, _ = secrets
    issue = REPO / "lab" / "pki" / "issue-cert.sh"
    first = run(issue, str(d / "ca"), "docker01.lab.internal", "DNS:docker01.lab.internal,DNS:*.lab.internal")
    assert first.returncode == 0 and "created" in first.stdout, first.stderr
    out = d / "ca" / "issued" / "docker01.lab.internal"
    v = subprocess.run(["openssl", "verify", "-CAfile", str(d / "ca/root/certs/ca.cert.pem"),
                        "-untrusted", str(d / "ca/intermediate/certs/intermediate.cert.pem"), str(out / "cert.pem")],
                       capture_output=True, text=True)
    assert v.returncode == 0, v.stderr
    assert oct((out / "key.pem").stat().st_mode)[-3:] == "600"
    assert "kept" in run(issue, str(d / "ca"), "docker01.lab.internal").stdout


def test_issue_cert_rejects_a_hostile_common_name(secrets):
    d, _ = secrets
    r = run(REPO / "lab" / "pki" / "issue-cert.sh", str(d / "ca"), "x; rm -rf /")
    assert r.returncode == 2 and "invalid common name" in r.stderr
