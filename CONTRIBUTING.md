# Contributing

Thanks for helping. This is a teaching repo, so the most valuable contributions make it **more correct on
real labs** and **clearer for learners**.

## Most wanted

1. **Real tool output.** Run the week 12 checks on a real lab and send trimmed, anonymised output of Lynis
   (`lynis-report.dat`), `nmap -oX`, and a Windows audit to replace the hand-written fixtures in
   `scaffold/tests/fixtures/`. Parsers that break on real output are the highest-value bug reports.
2. **Verifying the weak defaults** in [docs/instructor-weak-defaults.md](docs/instructor-weak-defaults.md):
   does a normal build really have this, and does the named attack really find it?
3. A **Windows audit collector** for an open-source tool (the parser assumes a HardeningKitty-style CSV).
4. Week guides for other platforms or distributions, and clearer wording anywhere a learner could get stuck.

## Ground rules

- **Authorised targets only.** Do not add attacks that target anything but a learner's own lab. The scope
  guard must stay in front of every command that touches the network.
- **Small and standard.** Python 3.11+ standard library only; justify any dependency in the pull request.
  Open-source tools only. Prefer lightweight over feature-rich.
- **Stable finding ids.** Changing an id breaks comparisons for learners mid-course. Add new ids rather than
  renaming old ones, and note it in the changelog.
- **Untrusted text stays untrusted.** Anything from a scanned host (banners, tool output) must go through
  the report escaping (`md()` / `esc()`); add a test with hostile input for any new renderer.
- **No secrets or real data** in fixtures, examples or reports. Use documentation addresses or `10.10.0.0/24`.
- **LF line endings** (`.gitattributes` and `.editorconfig` enforce this).
- Docs in Markdown, diagrams in Mermaid, and record the *why* as well as the how.

## Development

```bash
cd scaffold
python -m pytest            # all tests; no lab or real tools needed (commands are injected)
shellcheck ../weeks/*/check.sh
```

Work test-first: write the failing test, watch it fail, then make it pass. Tests inject a fake `runner`, so
nothing in the suite touches the network.

## Pull requests

1. Open an issue first for anything larger than a fix, so we can agree the shape.
2. Branch from `main`, keep the change focused, add or update tests and the [changelog](CHANGELOG.md).
3. Explain what changed and why, and for a parser change, include the real output that motivated it.
4. CI must pass (tests and shellcheck).

## Reporting problems

Bugs and unclear guides: open an issue using the templates. Security concerns about the tooling itself:
see [SECURITY.md](SECURITY.md); please do not open a public issue for those.

By contributing you agree your contribution is licensed under the [MIT licence](LICENSE).
