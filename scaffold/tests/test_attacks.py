import ipaddress
import re
from pathlib import Path

import pytest

from sslab.attacks import ATTACKS, run_attacks
from sslab.findings import LAYERS
from sslab.scope import ScopeError

NETS = [ipaddress.ip_network("10.10.0.0/24")]
DOC = Path(__file__).parents[2] / "docs" / "attack-set.md"
ARGS = dict(nets=NETS, label="default", student="alex", fork="alex/ssl")


def by_id(attack_id):
    return next(a for a in ATTACKS if a.id == attack_id)


def test_attack_ids_are_unique_and_match_the_docs():
    ids = [a.id for a in ATTACKS]
    assert len(ids) == len(set(ids))
    assert ids == re.findall(r"^\| `([a-z-]+)`", DOC.read_text(), re.M)


def test_each_attack_has_an_allowed_layer():
    assert all(a.layer in LAYERS for a in ATTACKS)


def test_run_attacks_refuses_out_of_scope_before_running_anything():
    def runner(cmd):
        raise AssertionError("runner must not be called")

    with pytest.raises(ScopeError):
        run_attacks("8.8.8.8", runner=runner, **ARGS)


def test_attack_that_cannot_run_goes_to_not_run_and_others_continue():
    def runner(cmd):
        if cmd[0] == "hydra":
            raise FileNotFoundError("hydra")
        return "<nmaprun/>" if "-oX" in cmd else ""

    run = run_attacks("10.10.0.5", runner=runner, **ARGS)
    assert run.not_run == ["ssh-weak-creds"] and run.tool == "attack-set"


def test_ssh_weak_creds_parses_hydra_hit():
    out = "[22][ssh] host: 10.10.0.5   login: admin   password: password\n1 of 1 target successfully completed"
    fs = by_id("ssh-weak-creds").parse(out)
    assert [f.id for f in fs] == ["attack:ssh-weak-creds:admin"] and fs[0].severity == "high"


def test_ssh_weak_creds_no_hit_is_no_finding():
    assert by_id("ssh-weak-creds").parse("0 of 1 target completed, 0 valid password found") == []


def test_web_basics_reports_missing_headers_and_banner():
    out = "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0\r\nContent-Type: text/html\r\n"
    ids = {f.id for f in by_id("web-basics").parse(out)}
    assert "attack:web-basics:no-hsts" in ids and "attack:web-basics:server-banner" in ids
    hardened = "HTTP/1.1 200 OK\r\nServer: nginx\r\nStrict-Transport-Security: max-age=1\r\nX-Frame-Options: DENY\r\nContent-Security-Policy: default-src 'self'\r\nX-Content-Type-Options: nosniff\r\n"
    assert by_id("web-basics").parse(hardened) == []


def test_mail_basics_open_relay_and_vrfy():
    fs = by_id("mail-basics").parse("smtp-open-relay: Server is an open relay (16/16 tests)\nsmtp-commands: VRFY, EXPN")
    assert {f.id for f in fs} == {"attack:mail-basics:open-relay", "attack:mail-basics:vrfy"}
    assert by_id("mail-basics").parse("Server doesn't seem to be an open relay, all tests failed") == []


def test_anon_directory_lists_disk_shares():
    out = "\tSharename       Type      Comment\n\t---------       ----      -------\n\tpublic          Disk      Public files\n\tIPC$            IPC       IPC Service"
    assert [f.id for f in by_id("anon-directory").parse(out)] == ["attack:anon-directory:public"]


def test_unparseable_output_goes_to_not_run_not_a_crash():
    run = run_attacks("10.10.0.5", runner=lambda cmd: "", **ARGS)
    assert "enum-services" in run.not_run
