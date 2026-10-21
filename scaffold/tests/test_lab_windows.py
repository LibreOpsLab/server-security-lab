"""PowerShell is not available in the build environment, so these are string-level checks of the scripts' intent.
The scripts themselves are reviewed on a real Windows 11 machine (docs/build/STATUS.md)."""

import re
from pathlib import Path

import pytest

LAB = Path(__file__).parents[2] / "lab"
OPT = (LAB / "windows/Optimize-LabWindows.ps1").read_text()
JOIN = (LAB / "windows/Join-LabDomain.ps1").read_text()


def test_script_disables_the_telemetry_and_diagnostic_services():
    for svc in ("DiagTrack", "dmwappushservice", "WerSvc", "diagnosticshub.standardcollector.service"):
        assert svc in OPT


def test_script_sets_the_telemetry_policies():
    for needle in ("Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry", "DoNotShowFeedbackNotifications",
                   "AdvertisingInfo", "DisabledByGroupPolicy", "SQMClient", "CEIPEnable"):
        assert needle in OPT


def test_script_turns_off_copilot_and_recall_and_removes_the_packages():
    for needle in ("TurnOffWindowsCopilot", "DisableAIDataAnalysis", "Recall", "*Copilot*", "HubsSidebarEnabled"):
        assert needle in OPT
    assert "Remove-AppxPackage" in OPT and "Remove-AppxProvisionedPackage" in OPT


def test_script_removes_consumer_bloat_widgets_and_onedrive_sync():
    for needle in ("AllowNewsAndInterests", "DisableWindowsConsumerFeatures", "DisableFileSyncNGSC", "BingNews", "Xbox"):
        assert needle in OPT


def test_script_keeps_security_updates_and_defender_untouched():
    assert not re.search(r"(WinDefend|wuauserv|Windows Defender|DisableAntiSpyware)", OPT.split("#")[0] + "".join(
        ln for ln in OPT.splitlines() if not ln.lstrip().startswith("#")))


def test_script_supports_whatif_and_logs_what_it_changes():
    assert "SupportsShouldPrompt" not in OPT
    assert "[CmdletBinding(SupportsShouldProcess" in OPT and "ShouldProcess(" in OPT
    assert "Write-Log" in OPT and "LogPath" in OPT
    assert "#Requires -RunAsAdministrator" in OPT


def test_script_is_idempotent_by_checking_the_current_value_first():
    assert "Get-ItemProperty" in OPT and "UNCHANGED" in OPT and "CHANGED" in OPT


def test_join_script_asks_for_credentials_and_has_no_password_literal():
    assert "Get-Credential" in JOIN
    assert not re.search(r"(?i)password\s*=\s*['\"][^'\"]+['\"]", JOIN) and "ConvertTo-SecureString" not in JOIN


def test_join_script_trusts_the_lab_ca_and_uses_the_domain_controller_for_dns():
    assert "Import-Certificate" in JOIN and "LocalMachine\\Root" in JOIN
    assert "Set-DnsClientServerAddress" in JOIN and "Add-Computer" in JOIN


def test_join_script_defaults_match_the_inventory():
    text = (LAB / "inventory/group_vars/all.yml").read_text()
    domain = re.search(r"^lab_domain: (\S+)", text, re.M).group(1)
    dc_ip = re.search(r"samba-dc01: \{.*?ip: ([0-9.]+)", text).group(1)
    assert f"'{domain}'" in JOIN and f"'{dc_ip}'" in JOIN


def test_readme_says_what_is_kept_and_what_is_removed():
    read
