import ipaddress
from pathlib import Path

import pytest

from sslab.scope import ScopeError, load_scope, require_in_scope

NETS = [ipaddress.ip_network("10.10.0.0/24")]


def test_in_range_ip_ok():
    assert require_in_scope("10.10.0.5", NETS) == "10.10.0.5"


def test_out_of_range_ip_refused():
    with pytest.raises(ScopeError):
        require_in_scope("8.8.8.8", NETS)


def test_hostname_resolving_outside_range_refused():
    resolve = lambda name: (name, [], ["10.10.0.5", "93.184.216.34"])  # one good, one bad: refuse
    with pytest.raises(ScopeError):
        require_in_scope("docker01.lab", NETS, resolve=resolve)


def test_hostname_resolving_inside_range_ok():
    resolve = lambda name: (name, [], ["10.10.0.7"])
    assert require_in_scope("docker01.lab", NETS, resolve=resolve) == "10.10.0.7"


def test_unresolvable_hostname_refused():
    def resolve(name):
        raise OSError("no such host")

    with pytest.raises(ScopeError):
        require_in_scope("nope.lab", NETS, resolve=resolve)


def test_empty_scope_file_refused(tmp_path: Path):
    f = tmp_path / "scope.txt"
    f.write_text("# nothing yet\n\n")
    with pytest.raises(ScopeError, match="write your scope first"):
        load_scope(f)


def test_missing_scope_file_refused(tmp_path: Path):
    with pytest.raises(ScopeError, match="write your scope first"):
        load_scope(tmp_path / "scope.txt")


def test_comments_and_blank_lines_ignored(tmp_path: Path):
    f = tmp_path / "scope.txt"
    f.write_text("# my lab\n10.10.0.0/24  # LAN-LAB\n\n")
    assert load_scope(f) == NETS


def test_host_bits_set_is_rejected_not_widened(tmp_path: Path):
    f = tmp_path / "scope.txt"
    f.write_text("10.10.0.5/24\n")
    with pytest.raises(ScopeError, match="10.10.0.5/24"):
        load_scope(f)


def test_malformed_line_is_a_scope_error(tmp_path: Path):
    f = tmp_path / "scope.txt"
    f.write_text("not-a-network\n")
    with pytest.raises(ScopeError, match="not-a-network"):
        load_scope(f)


def test_bare_ip_is_a_single_host(tmp_path: Path):
    f = tmp_path / "scope.txt"
    f.write_text("10.10.0.5\n")
    assert load_scope(f) == [ipaddress.ip_network("10.10.0.5/32")]
