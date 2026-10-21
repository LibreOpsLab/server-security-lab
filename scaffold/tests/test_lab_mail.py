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


def test_spf_record_data_embeds_literal_quote_characters_as_one_txt_string():
    # samba-tool dns add's TXT handling splits an UNQUOTED value on whitespace into several DNS
    # character-strings, which receivers then join with NO separator ("v=spf1ip4:...-all"). The fix is to
    # embed literal double-quote characters around the content, so samba-tool sees one quoted token.
    import yaml

    dns = yaml.safe_load((LAB / "ansible/roles/samba_dc/tasks/dns.yml").read_text())
    task = next(t for t in dns if "loop" in t and isinstance(t["loop"], list)
                and any(isinstance(i, dict) and "spf1" in str(i.get("data", "")) for i in t["loop"]))
    spf = next(i for i in task["loop"] if isinstance(i, dict) and "spf1" in str(i.get("data", "")))
    # The rendered value must start and end with a literal `"` character, not just the YAML string quoting.
    quote = chr(34)
    assert spf["data"][0] == quote and spf["data"][-1] == quote
    assert "v=spf1" in spf["data"] and "-all" in spf["data"]


def test_mx_record_is_also_a_single_quoted_data_value():
    import yaml

    dns = yaml.safe_load((LAB / "ansible/roles/samba_dc/tasks/dns.yml").read_text())
    task = next(t for t in dns if "loop" in t and isinstance(t["loop"], list) and any(i.get("type") == "MX" for i in t["loop"]))
    mx = next(i for i in task["loop"] if i["type"] == "MX")
    quote = chr(34)
    assert mx["data"][0] == quote and mx["data"][-1] == quote


def test_postfix_config_task_hides_the_ldap_bind_password_from_diff_output():
    import yaml

    tasks = yaml.safe_load((ROLE / "tasks/main.yml").read_text())
    task = next(t for t in tasks if "ansible.builtin.template" in t
                and any(isinstance(i, dict) and "ldap-virtual-mailbox" in str(i.get("src", "")) for i in t["loop"]))
    assert task.get("no_log") is True


def test_dovecot_userdb_allows_lookups_without_a_separate_passdb_round_trip():
    # A static userdb with an LDAP auth_bind passdb cannot answer "does this user exist?" on its own;
    # without allow_all_users, Dovecot tempfails every LMTP delivery.
    conf = (ROLE / "templates/99-lab.conf.j2").read_text()
    assert "allow_all_users=yes" in conf


def test_opendkim_and_opendmarc_socket_overrides_match_the_conf_files():
    # Debian's init scripts for both daemons read /etc/default/<name> and, if SOCKET is unset there, pass
    # their own default (a unix socket), overriding the inet socket set in opendkim.conf/opendmarc.conf.
    import yaml

    tasks = yaml.safe_load((ROLE / "tasks/main.yml").read_text())
    task = next(t for t in tasks if "ansible.builtin.lineinfile" in t
                and any(isinstance(i, dict) and "default/opendkim" in str(i.get("path", "")) for i in t.get("loop", [])))
    sockets = {i["path"]: i["socket"] for i in task["loop"]}
    assert sockets["/etc/default/opendkim"] == "inet:8891@127.0.0.1"
    assert sockets["/etc/default/opendmarc"] == "inet:8893@127.0.0.1"
    assert "inet:8891@127.0.0.1" in (ROLE / "templates/opendkim.conf.j2").read_text()
    assert "inet:8893@127.0.0.1" in (ROLE / "templates/opendmarc.conf.j2").read_text()


def test_postconf_chroot_task_can_actually_report_changed_and_notify():
    # A task with changed_when: false can never trigger its own notify. The chroot setting must be
    # checked and only changed (and only then notify) when it is not already correct.
    import yaml

    tasks = yaml.safe_load((ROLE / "tasks/main.yml").read_text())
    task = next(t for t in tasks if "ansible.builtin.command" in t and "postconf -F" in str(t["ansible.builtin.command"]))
    assert task.get("changed_when") is not False and "notify" in task
    assert "when" in task  # it only runs (and so only reports changed) when the setting is actually wrong
