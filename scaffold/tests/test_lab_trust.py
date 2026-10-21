from pathlib import Path

LAB = Path(__file__).parents[2] / "lab"


def test_trust_role_installs_both_lab_ca_certificates_and_refreshes_the_store():
    tasks = (LAB / "ansible/roles/pki_trust/tasks/main.yml").read_text()
    assert "root/certs/ca.cert.pem" in tasks and "intermediate/certs/intermediate.cert.pem" in tasks
    assert "/usr/local/share/ca-certificates" in tasks and "update-ca-certificates" in LAB.joinpath("ansible/roles/pki_trust/handlers/main.yml").read_text()


def test_trust_role_never_copies_a_private_key():
    lines = (LAB / "ansible/roles/pki_trust/tasks/main.yml").read_text().splitlines()
    code = "\n".join(ln for ln in lines if not ln.strip().startswith("#"))
    assert "key.pem" not in code and "private" not in code


def test_trust_playbook_covers_every_guest_and_the_admin_machine():
    play = (LAB / "ansible/playbooks/25-trust.yml").read_text()
    assert "pki_trust" in play and "lxc:vm:admin" in play
