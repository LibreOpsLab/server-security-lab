"""The authorisation boundary: tools only touch addresses the student wrote into their scope file."""

from __future__ import annotations

import ipaddress
import socket
from pathlib import Path
from typing import Callable


class ScopeError(Exception):
    pass


def load_scope(path: Path) -> list[ipaddress.IPv4Network]:
    """One CIDR per line; `#` starts a comment. An empty or missing file means no testing."""
    nets: list[ipaddress.IPv4Network] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            nets.append(ipaddress.ip_network(line, strict=False))
    if not nets:
        raise ScopeError(f"write your scope first: {path} has no lab ranges")
    return nets


def require_in_scope(
    target: str,
    nets: list[ipaddress.IPv4Network],
    resolve: Callable = socket.gethostbyname_ex,
) -> str:
    """Return the resolved IP, or raise ScopeError. Every address a name resolves to must be in scope."""
    try:
        ips = [str(ipaddress.ip_address(target))]
    except ValueError:
        try:
            ips = list(resolve(target)[2])
        except OSError as e:
            raise ScopeError(f"cannot resolve {target}: {e}") from e
    if not ips:
        raise ScopeError(f"{target} resolves to nothing")
    for ip in ips:
        if not any(ipaddress.ip_address(ip) in n for n in nets):
            raise ScopeError(f"{target} ({ip}) is outside your lab range; refusing")
    return ips[0]
