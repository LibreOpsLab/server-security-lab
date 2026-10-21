# Security policy

## Responsible use (please read)

This repository contains offensive security tooling for **education**. Use it only against:

- systems you own, or
- systems you have **written permission** to test, such as your own classroom lab.

Testing anything else may be illegal where you live, whatever your intentions. The tools check a scope file
that the learner writes first and refuse targets outside it, but that guard is a **teaching aid, not a
security control**: it will not stop a determined person, and you remain responsible for what you run.

If you teach with this repo, tell learners this on day one, keep lab networks isolated from production and
from the internet, and put the permission boundary in writing.

## Reporting a vulnerability in the tooling

If you find a flaw in the code here (for example a way for hostile scan output to execute code, escape the
report escaping, or bypass the scope check), please report it privately:

1. Use **Report a vulnerability** under the repository's *Security* tab (GitHub private vulnerability
   reporting), or
2. If that is unavailable, message the repository owner on GitHub and ask for a private channel.

Please include what you found, how to reproduce it, and its impact. You will get an acknowledgement, and a
fix or an explanation as soon as practical. Do not open a public issue for security reports.

## Supported versions

Only the latest `main` is supported. This is a young teaching project, not a production product.

## Scope notes

Intentionally weak lab configurations (see [docs/instructor-weak-defaults.md](docs/instructor-weak-defaults.md))
are teaching material, not vulnerabilities in this repo.
