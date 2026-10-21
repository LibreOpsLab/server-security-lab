import os
import subprocess
from pathlib import Path

REPO = Path(__file__).parents[2]
SCRIPT = REPO / "scripts" / "create-private-copy.sh"


def git(*a, cwd=None):
    return subprocess.run(
        ["git", *a], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_private_copy_keeps_history_and_adds_upstream(tmp_path: Path):
    upstream = tmp_path / "upstream.git"
    seed = tmp_path / "seed"
    git("init", "-q", "-b", "main", str(seed))
    (seed / "a.txt").write_text("one\n")
    git("-c", "user.name=t", "-c", "user.email=t@t", "add", "-A", cwd=seed)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "first", cwd=seed)
    git("clone", "-q", "--bare", str(seed), str(upstream))

    remote_root = tmp_path / "github"  # stands in for https://github.com
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gh = fake_bin / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = "api" ]; then echo tester; exit 0; fi\n'
        'if [ "$1" = "repo" ] && [ "$2" = "create" ]; then\n'
        '  grep -q -- "--private" <<<"$*" || { echo "not private" >&2; exit 9; }\n'
        '  git init -q -b main --bare "$GH_BASE/tester/${3##*/}.git"; exit 0; fi\n'
        "exit 1\n"
    )
    gh.chmod(0o755)
    (remote_root / "tester").mkdir(parents=True)

    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "GH_BASE": str(remote_root),
        "UPSTREAM_URL": str(upstream),
    }
    work = tmp_path / "work"
    work.mkdir()
    out = subprocess.run(
        [str(SCRIPT), "my-lab"], cwd=work, env=env, capture_output=True, text=True
    )
    assert out.returncode == 0, out.stderr

    clone = work / "my-lab"
    assert (
        git("log", "--format=%s", cwd=clone) == "first"
    )  # history kept, so upstream merges work cleanly
    assert git("remote", "get-url", "upstream", cwd=clone) == str(upstream)
    assert git("remote", "get-url", "origin", cwd=clone).endswith("tester/my-lab.git")


def test_refuses_without_gh(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    env = {"PATH": str(tmp_path / "empty"), "HOME": str(tmp_path)}
    out = subprocess.run(
        ["/bin/bash", str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert out.returncode == 2 and "GitHub CLI" in out.stderr
