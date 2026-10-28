<#
.SYNOPSIS
    Prepares a Windows lab workstation for nested virtualisation (Proxmox VE inside VMware Workstation),
    checks that the preparation has held, and can put the machine back as it was.

.DESCRIPTION
    VMware Workstation can only expose VT-x/EPT to a guest hypervisor (Proxmox) when Windows is not using
    the processor's virtualisation features itself. This script switches off the Windows features that do:
    Hyper-V and its helper features, virtualization-based security (VBS), Memory Integrity (HVCI) and
    Credential Guard.

    These features protect the machine. Turning them off is a deliberate trade-off for a lab workstation.
    Use -Mode Restore to undo it, especially if the computer is used for other work.

    Modes
      Check    Read-only. Reports the current state and whether nested virtualisation is ready. This is the
               "is it still off?" check for the start of each class. Exit code 0 = ready, 2 = not ready.
      Disable  Saves the current state, switches the features off, and asks you to restart.
               -UnlockFirmware additionally schedules Microsoft's SecConfig.efi for a one-time boot to
               remove a firmware-backed VBS lock.
      Restore  Puts back what Disable changed, using the saved state. Restart afterwards.

    The saved state is a small JSON file (default C:\ProgramData\LabHostPrep\state.json). It is written once,
    by the first Disable run, so running Disable twice never overwrites the original settings.

.PARAMETER Mode
    Check (default), Disable or Restore.

.PARAMETER StatePath
    Where the original settings are saved.

.PARAMETER Force
    Skip the confirmation prompt in Disable and Restore modes.

.PARAMETER UnlockFirmware
    With -Mode Disable, schedule Microsoft's SecConfig.efi for a one-time boot to remove a firmware-backed
    VBS/Credential Guard lock. Requires UEFI, physical access at restart, and may trigger BitLocker recovery.

.EXAMPLE
    .\Set-NestedVirtualisation.ps1
    Reports the current state. Changes nothing.

.EXAMPLE
    .\Set-NestedVirtualisation.ps1 -Mode Disable -WhatIf
    Shows what Disable would change without changing anything.

.EXAMPLE
    .\Set-NestedVirtualisation.ps1 -Mode Disable
    Prepares the workstation. Restart, then run the script again with no parameters to verify.

.EXAMPLE
    .\Set-NestedVirtualisation.ps1 -Mode Disable -UnlockFirmware
    Also schedules a one-time firmware unlock. Have the BitLocker recovery key available and confirm the
    prompt shown before Windows starts.

.NOTES
    Run from an elevated PowerShell (Run as administrator). Works on Windows PowerShell 5.1 and PowerShell 7.
    Confirmed working on a lab PC in the October 2026 spike (nested Proxmox runs, KVM available).
    Group Policy or Intune can switch these settings back on; Check mode reports when a policy is set.
#>
#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Check', 'Disable', 'Restore')]
    [string]$Mode = 'Check',

    [string]$StatePath = (Join-Path $env:ProgramData 'LabHostPrep\state.json'),

    [switch]$Force,

    [switch]$UnlockFirmware
)

$ErrorActionPreference = 'Stop'
if ($UnlockFirmware -and $Mode -ne 'Disable') {
    throw '-UnlockFirmware can only be used with -Mode Disable.'
}

# --- What the script manages ------------------------------------------------------------------------

# Windows optional features that use the hypervisor. WSL 2, Docker Desktop and Windows Sandbox all depend
# on these, so they stop working while the features are off.
$FeatureNames = @(
    'Microsoft-Hyper-V-All',
    'HypervisorPlatform',
    'VirtualMachinePlatform',
    'Containers-DisposableClientVM',     # Windows Sandbox
    'Windows-Defender-ApplicationGuard'  # retired in newer Windows builds; skipped when absent
)

# Boot settings (bcdedit) that start the hypervisor and the secure kernel.
$BootValues = @('hypervisorlaunchtype', 'vsmlaunchtype')

# Registry values that turn on VBS, Memory Integrity and Credential Guard.
$RegistryValues = @(
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard'; Name = 'EnableVirtualizationBasedSecurity' },
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard'; Name = 'RequirePlatformSecurityFeatures' },
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard'; Name = 'HypervisorEnforcedCodeIntegrity' },
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity'; Name = 'Enabled' },
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa'; Name = 'LsaCfgFlags' }
)

# Policy locations that override the values above. Read-only: reported, never changed.
$PolicyValues = @(
    @{ Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard'; Name = 'EnableVirtualizationBasedSecurity' },
    @{ Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard'; Name = 'RequirePlatformSecurityFeatures' },
    @{ Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard'; Name = 'HypervisorEnforcedCodeIntegrity' },
    @{ Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard'; Name = 'LsaCfgFlags' }
)

# --- Helpers ----------------------------------------------------------------------------------------

function Write-Section([string]$Text) {
    Write-Host ''
    Write-Host "== $Text" -ForegroundColor Cyan
}

function Get-FeatureState([string]$Name) {
    # Returns 'Enabled', 'Disabled', 'EnablePending', 'DisablePending' or $null when the feature does not exist.
    try {
        (Get-WindowsOptionalFeature -Online -FeatureName $Name).State.ToString()
    }
    catch {
        $null
    }
}

function Get-BootValue([string]$Name) {
    $line = & bcdedit /enum '{current}' | Select-String -Pattern "^\s*$Name\s+(\S+)"
    if ($line) { $line.Matches[0].Groups[1].Value } else { $null }
}

function Set-BootValue([string]$Name, [string]$Value) {
    if ($null -eq $Value) { & bcdedit /deletevalue $Name | Out-Null }
    else { & bcdedit /set $Name $Value | Out-Null }
    if ($LASTEXITCODE -ne 0) {
        # Deleting a value that is already absent is fine; anything else is a real failure.
        if ($null -ne $Value) { throw "bcdedit could not set $Name to $Value (exit code $LASTEXITCODE)." }
    }
}

function Invoke-BcdEdit([string[]]$Arguments) {
    & bcdedit.exe @Arguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "bcdedit $($Arguments -join ' ') failed (exit code $LASTEXITCODE)."
    }
}

function Schedule-FirmwareUnlock {
    $secConfig = Join-Path $env:windir 'System32\SecConfig.efi'
    if (-not (Test-Path $secConfig -PathType Leaf)) {
        throw "Microsoft's firmware unlock tool was not found at $secConfig."
    }

    $usedLetters = @(Get-PSDrive -PSProvider FileSystem | ForEach-Object { $_.Name })
    $letter = @('Z', 'Y', 'X', 'W', 'V', 'U', 'T', 'S') |
        Where-Object { $_ -notin $usedLetters -and -not (Test-Path "${_}:\") } |
        Select-Object -First 1
    if (-not $letter) { throw 'No unused drive letter is available to mount the EFI System Partition.' }

    $drive = "${letter}:"
    $mounted = $false
    $entryCreated = $false
    $entryGuid = "{$([guid]::NewGuid().ToString())}"

    try {
        & mountvol.exe $drive /s | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw 'Could not mount the EFI System Partition. Firmware unlock requires a UEFI system.'
        }
        $mounted = $true

        $bootDirectory = Join-Path $drive 'EFI\Microsoft\Boot'
        if (-not (Test-Path $bootDirectory -PathType Container)) {
            New-Item -ItemType Directory -Path $bootDirectory -Force | Out-Null
        }
        Copy-Item -LiteralPath $secConfig -Destination (Join-Path $bootDirectory 'SecConfig.efi') -Force

        Invoke-BcdEdit @('/create', $entryGuid, '/d', 'LabHostPrep VBS firmware unlock', '/application', 'osloader')
        $entryCreated = $true
        Invoke-BcdEdit @('/set', $entryGuid, 'device', "partition=$drive")
        Invoke-BcdEdit @('/set', $entryGuid, 'path', '\EFI\Microsoft\Boot\SecConfig.efi')
        Invoke-BcdEdit @('/set', $entryGuid, 'loadoptions', 'DISABLE-LSA-ISO,DISABLE-VBS')
        Invoke-BcdEdit @('/set', '{bootmgr}', 'bootsequence', $entryGuid)
    }
    catch {
        if ($entryCreated) {
            try { Invoke-BcdEdit @('/delete', $entryGuid, '/cleanup') }
            catch { Write-Warning "Could not remove the incomplete firmware-unlock boot entry $entryGuid." }
        }
        throw
    }
    finally {
        if ($mounted) {
            & mountvol.exe $drive /d | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Could not unmount the EFI System Partition at $drive."
            }
        }
    }

    Write-Host 'Firmware unlock is scheduled for the next boot.' -ForegroundColor Yellow
    Write-Host 'At the pre-Windows prompt, physically confirm the change. If no prompt appears, do not assume the firmware lock was removed.' -ForegroundColor Yellow
}

function Get-RegValue($Item) {
    $p = Get-ItemProperty -Path $Item.Path -Name $Item.Name -ErrorAction SilentlyContinue
    if ($p) { $p.($Item.Name) } else { $null }
}

function Get-Snapshot {
    $features = [ordered]@{}
    foreach ($f in $FeatureNames) { $features[$f] = Get-FeatureState $f }

    $boot = [ordered]@{}
    foreach ($b in $BootValues) { $boot[$b] = Get-BootValue $b }

    $registry = [ordered]@{}
    foreach ($r in $RegistryValues) { $registry["$($r.Path)|$($r.Name)"] = Get-RegValue $r }

    [ordered]@{
        Saved    = (Get-Date).ToString('s')
        Computer = $env:COMPUTERNAME
        Features = $features
        Boot     = $boot
        Registry = $registry
    }
}

function Show-State {
    # Prints the current state and returns $true when nested virtualisation should work.
    $ready = $true

    Write-Section 'Windows features'
    foreach ($f in $FeatureNames) {
        $s = Get-FeatureState $f
        if ($null -eq $s) { Write-Host ('  {0,-36} not present on this Windows build' -f $f); continue }
        $bad = $s -in 'Enabled', 'EnablePending', 'DisablePending'
        if ($bad) { $ready = $false }
        Write-Host ('  {0,-36} {1}' -f $f, $s) -ForegroundColor $(if ($bad) { 'Yellow' } else { 'Green' })
    }

    Write-Section 'Boot settings (bcdedit)'
    foreach ($b in $BootValues) {
        $v = Get-BootValue $b
        $bad = $v -notin 'off', 'Off'
        if ($bad) { $ready = $false }
        Write-Host ('  {0,-36} {1}' -f $b, $(if ($v) { $v } else { '(not set)' })) -ForegroundColor $(if ($bad) { 'Yellow' } else { 'Green' })
    }

    Write-Section 'Registry settings'
    foreach ($r in $RegistryValues) {
        $v = Get-RegValue $r
        Write-Host ('  {0,-36} {1}' -f $r.Name, $(if ($null -ne $v) { $v } else { '(not set)' }))
    }

    Write-Section 'Policy overrides (read only)'
    $policySet = $false
    foreach ($r in $PolicyValues) {
        $v = Get-RegValue $r
        if ($null -ne $v) {
            $policySet = $true
            Write-Host ('  {0,-36} {1}  (set by policy)' -f $r.Name, $v) -ForegroundColor Yellow
        }
    }
    if (-not $policySet) { Write-Host '  None found.' }

    Write-Section 'What Windows is running right now'
    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
    $dg = Get-CimInstance -Namespace 'root\Microsoft\Windows\DeviceGuard' -ClassName Win32_DeviceGuard -ErrorAction SilentlyContinue

    $hv = [bool]$cs.HypervisorPresent
    Write-Host ('  {0,-36} {1}' -f 'Hypervisor running under Windows', $hv) -ForegroundColor $(if ($hv) { 'Yellow' } else { 'Green' })
    if ($hv) { $ready = $false }

    if ($dg) {
        $vbs = switch ([int]$dg.VirtualizationBasedSecurityStatus) { 0 { 'Off' } 1 { 'Enabled, not running' } 2 { 'Running' } default { 'Unknown' } }
        $svc = @($dg.SecurityServicesRunning) | ForEach-Object { switch ([int]$_) { 1 { 'Credential Guard' } 2 { 'Memory Integrity (HVCI)' } 3 { 'System Guard' } 4 { 'SMM Firmware Protection' } default { "Service $_" } } }
        Write-Host ('  {0,-36} {1}' -f 'Virtualization-based security', $vbs) -ForegroundColor $(if ([int]$dg.VirtualizationBasedSecurityStatus -eq 0) { 'Green' } else { 'Yellow' })
        Write-Host ('  {0,-36} {1}' -f 'Security services running', $(if ($svc) { $svc -join ', ' } else { 'none' })) -ForegroundColor $(if ($svc) { 'Yellow' } else { 'Green' })
        if ([int]$dg.VirtualizationBasedSecurityStatus -ne 0 -or $svc) { $ready = $false }
    }
    else {
        Write-Host '  Device Guard status could not be read.' -ForegroundColor Yellow
        $ready = $false
    }

    Write-Section 'Result'
    if ($ready) {
        Write-Host '  READY: Windows is not using the virtualisation features. Nested virtualisation can work.' -ForegroundColor Green
    }
    else {
        Write-Host '  NOT READY: something is still using the virtualisation features.' -ForegroundColor Yellow
        Write-Host '  If you have already run -Mode Disable and restarted, a policy, an update or a firmware lock has' -ForegroundColor Yellow
        Write-Host '  probably switched something back on. Tell your lecturer which line above is yellow.' -ForegroundColor Yellow
    }
    return $ready
}

function Confirm-Action([string]$Message) {
    if ($Force -or $WhatIfPreference) { return $true }
    Write-Host ''
    Write-Host $Message -ForegroundColor Yellow
    return ((Read-Host 'Type YES to continue') -ceq 'YES')
}

# --- Modes ------------------------------------------------------------------------------------------

switch ($Mode) {

    'Check' {
        Write-Host 'Nested virtualisation check (read only)' -ForegroundColor Cyan
        if (Show-State) { exit 0 } else { exit 2 }
    }

    'Disable' {
        Write-Host 'Prepare this workstation for nested virtualisation' -ForegroundColor Cyan
        $msg = @'
This switches OFF Hyper-V, Virtual Machine Platform, Windows Hypervisor Platform, Windows Sandbox,
virtualization-based security, Memory Integrity and Credential Guard. They protect this computer.
WSL 2 and Docker Desktop will stop working until you run this script with -Mode Restore.
Do this on a lab workstation only.
'@
        if (-not (Confirm-Action $msg)) { Write-Host 'Cancelled. Nothing was changed.'; exit 1 }
        if ($UnlockFirmware -and -not (Confirm-Action @'
This also schedules Microsoft's SecConfig.efi for a one-time boot to clear a firmware-backed VBS lock.
Have the BitLocker recovery key available. You must be present to confirm the change before Windows starts.
This firmware change is not reversed by -Mode Restore.
'@)) {
            Write-Host 'Cancelled. Nothing was changed.'; exit 1
        }

        # Save the original state once. A second run must not overwrite it with already-changed settings.
        if (Test-Path $StatePath) {
            Write-Host "Original settings already saved at $StatePath (kept)."
            $savedState = Get-Content -Path $StatePath -Raw | ConvertFrom-Json
            $snapshotUpdated = $false
            foreach ($r in $RegistryValues) {
                $key = "$($r.Path)|$($r.Name)"
                if ($savedState.Registry.PSObject.Properties.Name -notcontains $key) {
                    $savedState.Registry | Add-Member -MemberType NoteProperty -Name $key -Value (Get-RegValue $r)
                    $snapshotUpdated = $true
                }
            }
            if ($snapshotUpdated) {
                $savedState | ConvertTo-Json -Depth 5 | Set-Content -Path $StatePath -Encoding UTF8
                Write-Host 'Saved state updated with newly managed registry settings.'
            }
        }
        elseif ($PSCmdlet.ShouldProcess($StatePath, 'Save original settings')) {
            New-Item -ItemType Directory -Path (Split-Path $StatePath) -Force | Out-Null
            Get-Snapshot | ConvertTo-Json -Depth 5 | Set-Content -Path $StatePath -Encoding UTF8
            Write-Host "Original settings saved to $StatePath" -ForegroundColor Green
        }

        $problems = @()

        Write-Section 'Windows features'
        foreach ($f in $FeatureNames) {
            $s = Get-FeatureState $f
            if ($null -eq $s) { Write-Host "  $f : not present, skipped"; continue }
            if ($s -notin 'Enabled', 'EnablePending') { Write-Host "  $f : already off"; continue }
            if ($PSCmdlet.ShouldProcess($f, 'Disable Windows feature')) {
                try {
                    Disable-WindowsOptionalFeature -Online -FeatureName $f -NoRestart | Out-Null
                    Write-Host "  $f : disabled (restart needed)"
                }
                catch { $problems += "Could not disable $f : $($_.Exception.Message)" }
            }
        }

        Write-Section 'Boot settings'
        foreach ($b in $BootValues) {
            if ($PSCmdlet.ShouldProcess($b, 'bcdedit set off')) {
                try { Set-BootValue $b 'off'; Write-Host "  $b = off" }
                catch { $problems += $_.Exception.Message }
            }
        }

        Write-Section 'Registry settings'
        foreach ($r in $RegistryValues) {
            if ($PSCmdlet.ShouldProcess("$($r.Path)\$($r.Name)", 'Set to 0')) {
                try {
                    if (-not (Test-Path $r.Path)) { New-Item -Path $r.Path -Force | Out-Null }
                    Set-ItemProperty -Path $r.Path -Name $r.Name -Value 0 -Type DWord
                    Write-Host "  $($r.Name) = 0"
                }
                catch { $problems += "Could not set $($r.Name) : $($_.Exception.Message)" }
            }
        }

        if ($UnlockFirmware -and $PSCmdlet.ShouldProcess('UEFI boot sequence', 'Schedule one-time VBS firmware unlock')) {
            try { Schedule-FirmwareUnlock }
            catch { $problems += "Could not schedule firmware unlock: $($_.Exception.Message)" }
        }

        if ($problems) {
            Write-Section 'Problems'
            $problems | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            Write-Host '  Record these (screenshot) and tell your lecturer. Do not carry on to the Proxmox install.' -ForegroundColor Red
            exit 1
        }

        Write-Host ''
        Write-Host 'Done. RESTART the computer now, then run this script again with no parameters to verify.' -ForegroundColor Green
        if ($UnlockFirmware) {
            Write-Host 'At the pre-Windows prompt, physically confirm the firmware unlock before Windows starts.' -ForegroundColor Yellow
        }
        Write-Host "To undo: .\Set-NestedVirtualisation.ps1 -Mode Restore"
        exit 0
    }

    'Restore' {
        Write-Host 'Restore the settings saved before Disable' -ForegroundColor Cyan
        if (-not (Test-Path $StatePath)) {
            Write-Host "No saved state at $StatePath. Nothing to restore." -ForegroundColor Red
            exit 1
        }
        if (-not (Confirm-Action 'This puts back the virtualisation features and protections as they were before Disable.')) {
            Write-Host 'Cancelled. Nothing was changed.'; exit 1
        }
        $saved = Get-Content -Path $StatePath -Raw | ConvertFrom-Json
        $problems = @()

        Write-Section 'Windows features'
        foreach ($f in $FeatureNames) {
            $was = $saved.Features.$f
            if ($was -notin 'Enabled', 'EnablePending') { continue }
            if ((Get-FeatureState $f) -eq 'Enabled') { Write-Host "  $f : already on"; continue }
            if ($PSCmdlet.ShouldProcess($f, 'Enable Windows feature')) {
                try {
                    Enable-WindowsOptionalFeature -Online -FeatureName $f -All -NoRestart | Out-Null
                    Write-Host "  $f : enabled (restart needed)"
                }
                catch { $problems += "Could not enable $f : $($_.Exception.Message)" }
            }
        }

        Write-Section 'Boot settings'
        foreach ($b in $BootValues) {
            $was = $saved.Boot.$b
            if ($PSCmdlet.ShouldProcess($b, 'Restore bcdedit value')) {
                try { Set-BootValue $b $was; Write-Host "  $b = $(if ($was) { $was } else { '(removed)' })" }
                catch { $problems += $_.Exception.Message }
            }
        }

        Write-Section 'Registry settings'
        foreach ($r in $RegistryValues) {
            $was = $saved.Registry."$($r.Path)|$($r.Name)"
            if ($PSCmdlet.ShouldProcess("$($r.Path)\$($r.Name)", 'Restore registry value')) {
                try {
                    if ($null -eq $was) {
                        Remove-ItemProperty -Path $r.Path -Name $r.Name -ErrorAction SilentlyContinue
                        Write-Host "  $($r.Name) : removed (was not set)"
                    }
                    else {
                        Set-ItemProperty -Path $r.Path -Name $r.Name -Value ([int]$was) -Type DWord
                        Write-Host "  $($r.Name) = $was"
                    }
                }
                catch { $problems += "Could not restore $($r.Name) : $($_.Exception.Message)" }
            }
        }

        if ($problems) {
            $problems | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            exit 1
        }
        Write-Host ''
        Write-Host 'Restored. RESTART the computer to finish.' -ForegroundColor Green
        Write-Host "The saved state file was kept at $StatePath. Delete it if you want a fresh start next time."
        exit 0
    }
}
