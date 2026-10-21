from pathlib import Path

from sslab.findings import Finding, Run, load_run, save_run


def make_run(**kw) -> Run:
    base = dict(
        label="default",
        tool="lynis",
        host="docker01",
        student="alex",
        fork="alex/server-security-lab",
        lab_range="10.10.0.0/24",
        started="2026-11-16T01:02:03Z",
        findings=[
            Finding(
                "lynis:SSH-7440",
                "host",
                "Root login allowed",
                "high",
                "PermitRootLogin yes",
            )
        ],
        not_run=[],
    )
    base.update(kw)
    return Run(**base)


def test_roundtrip(tmp_path: Path):
    run = make_run(not_run=["nmap"])
    assert load_run(save_run(run, tmp_path)) == run


def test_same_second_does_not_overwrite(tmp_path: Path):
    a = save_run(make_run(), tmp_path)
    b = save_run(make_run(), tmp_path)
    assert a != b and a.exists() and b.exists()


def test_filename_carries_host_and_label(tmp_path: Path):
    name = save_run(make_run(), tmp_path).name
    assert name.startswith("default-lynis-docker01-") and name.endswith(".json")


def test_metrics_roundtrip_and_default(tmp_path: Path):
    assert make_run().metrics == {}
    run = make_run(metrics={"hardening_index": "62"})
    assert load_run(save_run(run, tmp_path)).metrics == {"hardening_index": "62"}
