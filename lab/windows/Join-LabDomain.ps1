<#
.SYNOPSIS
    Trust the lab's certificate authority, then join this Windows client to the lab domain.

.DESCRIPTION
    Run after Optimize-LabWindows.ps1. Prompts for domain administrator credentials interactively
    (Get-Credential): the password is never a script argument or a literal in this file.

.PARAMETER RootCaPath
    Path to the lab root CA certificate (lab-root-ca.crt), for example on a share or a USB drive.

.EXAMPLE
    Join-LabDomain.ps1 -RootCaPath 'C:\lab\lab-root-ca.crt' -DomainName 'lab.internal'
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$RootCaPath,
    [string]$DomainName = 'lab.internal'
)

if ($PSCmdlet.ShouldProcess($RootCaPath, 'Import as a trusted root certificate')) {
    Import-Certificate -FilePath $RootCaPath -CertStoreLocation 'Cert:\LocalMachine\Root' | Out-Null
    Write-Output "trusted: $RootCaPath (lab-root-ca)"
}

$credential = Get-Credential -Message "Domain administrator for $DomainName"

if ($PSCmdlet.ShouldProcess($DomainName, 'Add-Computer')) {
    Add-Computer -DomainName $DomainName -Credential $credential -Restart -Force
}
