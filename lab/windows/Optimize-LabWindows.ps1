<#
.SYNOPSIS
    Turn a fresh Windows 11 install into a lean lab client: disables telemetry, diagnostics, Copilot,
    Recall and consumer bloat. Idempotent (safe to run again) and logs every change it makes.

.DESCRIPTION
    This is one of the lab's "unverified" components: it has been reviewed, but never run against a real
    Windows 11 install in this environment (see docs/design/lab-build-design.md). Run it with -WhatIf first.

.EXAMPLE
    Optimize-LabWindows.ps1 -WhatIf
    Optimize-LabWindows.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$LogPath = "$env:ProgramData\lab\optimize-windows.log"
)

New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null
Start-Transcript -Path $LogPath -Append | Out-Null

function Set-LabRegistryValue {
    param([string]$Path, [string]$Name, $Value, [string]$Type = 'DWord')
    if ($PSCmdlet.ShouldProcess("$Path\$Name", "Set to $Value")) {
        New-Item -Path $Path -Force -ErrorAction SilentlyContinue | Out-Null
        $existing = Get-ItemProperty -Path $Path -Name $Name -ErrorAction SilentlyContinue
        if ($existing -and $existing.$Name -eq $Value) {
            Write-Output "already set: $Path\$Name = $Value"
        } else {
            New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType $Type -Force | Out-Null
            Write-Output "set: $Path\$Name = $Value"
        }
    }
}

function Stop-LabService {
    param([string]$Name)
    if ($PSCmdlet.ShouldProcess($Name, "Disable service")) {
        $svc = Get-Service -Name $Name -ErrorAction SilentlyContinue
        if ($null -eq $svc) { Write-Output "not present: $Name"; return }
        Stop-Service -Name $Name -Force -ErrorAction SilentlyContinue
        Set-Service -Name $Name -StartupType Disabled
        Write-Output "disabled: $Name"
    }
}

Write-Output '--- Telemetry and diagnostics ---'
# DiagTrack (Connected User Experiences and Telemetry) and dmwappushservice (device management WAP push)
# are the two services that carry most diagnostic data off the machine.
Stop-LabService -Name 'DiagTrack'
Stop-LabService -Name 'dmwappushservice'

# AllowTelemetry: 0 is the lowest setting most editions accept (Enterprise/Education allow "Security",
# which this value maps to; Pro cannot go lower than "Basic" and silently clamps it).
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' -Name 'AllowTelemetry' -Value 0
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' -Name 'DoNotShowFeedbackNotifications' -Value 1
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent' -Name 'DisableWindowsConsumerFeatures' -Value 1
Set-LabRegistryValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo' -Name 'AllowAdvertisingID' -Value 0

Write-Output '--- Copilot and Recall ---'
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot' -Name 'TurnOffWindowsCopilot' -Value 1
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' -Name 'DisableAIDataAnalysis' -Value 1
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' -Name 'AllowRecallEnablement' -Value 0

foreach ($pattern in @('*Copilot*', '*Microsoft.Windows.Ai.Copilot*')) {
    $packages = Get-AppxPackage -AllUsers -Name $pattern -ErrorAction SilentlyContinue
    foreach ($pkg in $packages) {
        if ($PSCmdlet.ShouldProcess($pkg.Name, 'Remove-AppxPackage')) {
            Remove-AppxPackage -Package $pkg.PackageFullName -AllUsers -ErrorAction SilentlyContinue
            Write-Output "removed package: $($pkg.Name)"
        }
    }
}

Write-Output '--- Widgets and consumer features ---'
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Dsh' -Name 'AllowNewsAndInterests' -Value 0
Set-LabRegistryValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Explorer' -Name 'TaskbarDa' -Value 0

Write-Output '--- OneDrive sync client ---'
$oneDriveSetup = "$env:SystemRoot\SysWOW64\OneDriveSetup.exe"
if (Test-Path $oneDriveSetup) {
    if ($PSCmdlet.ShouldProcess('OneDrive', 'Uninstall sync client')) {
        Stop-Process -Name OneDrive -Force -ErrorAction SilentlyContinue
        Start-Process -FilePath $oneDriveSetup -ArgumentList '/uninstall' -Wait
        Write-Output 'OneDrive sync client uninstalled'
    }
} else {
    Write-Output 'already absent: OneDrive sync client'
}

Write-Output "Done. Log: $LogPath"
Stop-Transcript | Out-Null
