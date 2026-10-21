import re
from pathlib import Path

LAB = Path(__file__).parents[2] / "lab"
ROLE = LAB / "ansible/roles/mail"


def code(path):
    return "\n".join(ln for ln in path.read_text().splitlines() if not ln.strip().startswith("#"))


def test_vrfy_is_left_on_explicitly():
    assert re.search(r"^disable_vrfy_command\s*=\s*no\s*$", code(ROLE / "templates/main.cf.j2"), re.M)


def test_relay_is_allowed_for_the_local_subnet():
    main = code(ROLE / "templates/main.cf.j2")
    assert "{{ lab_subnet }}" in re.search(r"^mynetworks\s*=.*$", main, re.M).group(0)
    assert "permit_mynetworks" in main


def test_tls_uses_the_lab_ca_issued_files():
    main = code(ROLE / "templates/main.cf.j2")
    assert "/etc/postfix/tls/fullchain.pem" in main and "/etc/postfix/tls/key.pem" in main
    dovecot = code(ROLE / "templates/99-lab.conf.j2")
    assert "/etc/dovecot/tls/fullchain.pem" in dovecot and "ssl = required" in dovecot


def test_ldap_bind_password_is_a_variable_not_a_literal():
    for name in ("ldap-virtual-mailbox.cf.j2", "dovecot-ldap.conf.ext.j2"):
        text = code(ROLE / "templates" / name)
        assert "mail_ldap_bind_password" in text or "mail_ldap_bind_pw" in text, name
        assert not re.search(r"(bind_pw|dnpass)\s*=\s*[A-Za-z0-9]{8,}\s*$", text, re.M), name


def test_mail_is_delivered_to_dovecot_over_lmtp_and_sasl_uses_dovecot():
    main = code(ROLE / "templates/main.cf.j2")
    assert "virtual_transport = lmtp:unix:private/dovecot-lmtp" in main
    assert "smtpd_sasl_type = dovecot" in main


def test_dkim_and_dmarc_are_wired_as_milters_and_dns_records_published():
    main = code(ROLE / "templates/main.cf.j2")
    assert "inet:127.0.0.1:8891" in main and "inet:127.0.0.1:8893" in main
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "_domainkey" in tasks and "opendkim-genkey" in tasks and "delegate_to: samba-dc01" in tasks


def test_samba_role_creates_the_service_accounts_from_secrets_without_logging_them():
    tasks = (LAB / "ansible/roles/samba_dc/tasks/main.yml").read_text()
    block = tasks.split("Create the service accounts")[1].split("- name:")[0]
    assert "lab_service_accounts" in block and "lookup" in block and "no_log: true" in block


def test_services_playbook_issues_certificates_then_builds_mail():
    play = (LAB / "ansible/playbooks/40-services.yml").read_text()
    assert "lab_certificates" in play and "role: mail" in play.replace("- mail", "role: mail") or "mail" in play
    assert play.index("lab_certificates") < play.index("mail")


def test_dc_publishes_mx_spf_and_dmarc_records():
    dns = (LAB / "ansible/roles/samba_dc/tasks/dns.yml").read_text()
    assert "type: MX" in dns and "v=spf1" in dns and "v=DMARC1" in dns and "_dmarc" in dns
