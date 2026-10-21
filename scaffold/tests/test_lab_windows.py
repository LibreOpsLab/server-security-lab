"""String-level checks of the Windows PowerShell scripts: no PowerShell interpreter is available here,
so these pin what the script text must contain rather than executing it. See docs/design/lab-build-design.md
("Testing here versus on the lab")."""

from pathlib import Path

LAB = Path(__file__).parents[2] / "lab"
OPTIMIZE = (LAB / "windows" / "Optimize-LabWindows.ps1").read_text()
JOIN = (LAB / "windows" / "Join-LabDomain.ps1").read_text()


def test_script_disables_diagtrack_and_dmwappushservice():
    for svc in ("DiagTrack", "dmwappushservice"):
        assert f"Stop-LabService -Name '{svc}'" in OPTIMIZE
    assert "Stop-Service -Name $Name" in OPTIMIZE and "StartupType Disabled" in OPTIMIZE


def test_script_sets_telemetry_diagnostics_and_feedback_policies():
    for key in ("AllowTelemetry", "DoNotShowFeedbackNotifications", "AllowAdvertisingID"):
        assert key in OPTIMIZE


def test_script_sets_copilot_and_recall_policies_and_removes_the_packages():
    for key in ("TurnOffWindowsCopilot", "DisableAIDataAnalysis"):
        assert key in OPTIMIZE
    assert "'*Copilot*'" in OPTIMIZE and "Get-AppxPackage -AllUsers -Name $pattern" in OPTIMIZE
    assert "Remove-AppxPackage" in OPTIMIZE


def test_script_disables_widgets_and_removes_onedrive_sync():
    assert "AllowNewsAndInterests" in OPTIMIZE or "TaskbarDa" in OPTIMIZE
    assert "OneDriveSetup.exe" in OPTIMIZE and "/uninstall" in OPTIMIZE


def test_supports_whatif_and_logs_every_change():
    assert "SupportsShouldProcess" in OPTIMIZE and "$PSCmdlet.ShouldProcess" in OPTIMIZE
    assert "Start-Transcript" in OPTIMIZE or "Add-Content" in OPTIMIZE


def test_script_is_idempotent_about_what_it_reports():
    assert "already" in OPTIMIZE.lower() or "-ErrorAction SilentlyContinue" in OPTIMIZE


def test_join_script_prompts_for_credentials_rather_than_taking_a_literal_password():
    assert "Get-Credential" in JOIN and "ConvertTo-SecureString" not in JOIN.replace("-AsPlainText", "")
    assert "Add-Computer" in JOIN and "-DomainName" in JOIN


def test_join_script_trusts_the_lab_ca():
    assert "Import-Certificate" in JOIN and "Root" in JOIN and "lab-root-ca" in JOIN


def test_join_script_supports_whatif():
    assert "SupportsShouldProcess" in JOIN
