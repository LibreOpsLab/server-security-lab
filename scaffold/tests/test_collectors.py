import ipaddress
from pathlib import Path

from sslab.collectors import collect
from sslab.collectors.lynis import parse_lynis_index, parse_lynis_report
from sslab.collectors.nmap import parse_nmap_xml
from sslab.collectors.windows import parse_windows_audit

FIX = Path(__file__).parent / "fixtures"
NETS = [ipaddress.ip_network("10.10.0.0/24")]


def read(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


def collect_args(**kw):
    base = dict(
        target="10.10.0.5", nets=NETS, label="default", student="alex", fork="alex/ssl"
    )
    base.update(kw)
    return base


def test_lynis_findings_and_index():
    fs = parse_lynis_report(read("lynis-report.dat"))
    assert len(fs) == 4
    root = next(f for f in fs if f.id == "lynis:SSH-7412")
    assert (
        root.severity == "high" and root.layer == "host"
    )  # warnings are high, suggestions medium
    assert next(f for f in fs if f.id == "lynis:AUTH-9286").severity == "medium"
    assert next(f for f in fs if f.id == "lynis:NETW-3200").layer == "network"
    assert parse_lynis_index(read("lynis-report.dat")) == 62


def test_nmap_open_ports_only_with_versions():
    fs = parse_nmap_xml(read("nmap.xml"))
    assert [f.id for f in fs] == ["nmap:22/tcp", "nmap:21/tcp", "nmap:80/tcp"]
    assert "OpenSSH 8.2p1" in fs[0].detail
    assert (
        next(f for f in fs if f.id == "nmap:21/tcp").severity == "medium"
    )  # cleartext protocol
    assert all(f.layer == "service" for f in fs)


def test_windows_failed_checks_only():
    fs = parse_windows_audit(read("windows-audit.csv"))
    assert [f.id for f in fs] == ["win:WIN-1001", "win:WIN-1002"]
    assert fs[0].severity == "high"


def test_collect_lynis_builds_run_with_index_metric():
    run = collect(
        "lynis", runner=lambda cmd: read("lynis-report.dat"), **collect_args()
    )
    assert run.tool == "lynis" and run.label == "default" and run.host == "10.10.0.5"
    assert (
        run.metrics == {"hardening_index": "62"}
        and len(run.findings) == 4
        and run.not_run == []
    )
    assert run.lab_range == "10.10.0.0/24" and run.started.endswith("Z")


def test_out_of_scope_target_never_calls_runner():
    def runner(cmd):
        raise AssertionError("runner must not be called")

    try:
        collect("nmap", runner=runner, **collect_args(target="8.8.8.8"))
    except Exception as e:
        assert type(e).__name__ == "ScopeError"
    else:
        raise AssertionError("expected ScopeError")


def test_tool_failure_lands_in_not_run():
    def runner(cmd):
        raise FileNotFoundError("nmap")

    run = collect("nmap", runner=runner, **collect_args())
    assert run.not_run == ["nmap"] and run.findings == []


def test_unknown_tool_is_an_error():
    try:
        collect("nikto", runner=lambda c: "", **collect_args())
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_garbled_tool_output_lands_in_not_run():
    run = collect("nmap", runner=lambda cmd: "not xml", **collect_args())
    assert run.not_run == ["nmap"] and run.findings == []


def test_malformed_index_does_not_discard_the_findings():
    text = "warning[]=AUTH-1|weak password policy|-|\nhardening_index=\n"
    run = collect("lynis", runner=lambda cmd: text, **collect_args())
    assert (
        [f.id for f in run.findings] == ["lynis:AUTH-1"]
        and run.not_run == []
        and run.metrics == {}
    )
