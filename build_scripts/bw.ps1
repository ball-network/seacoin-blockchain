# $env:path should contain a path to editbin.exe and signtool.exe

$ErrorActionPreference = "Stop"

$env:SEA_INSTALLER_VERSION = '2.0.0'
if (-not (Test-Path env:SEA_INSTALLER_VERSION)) {
  $env:SEA_INSTALLER_VERSION = '0.0.0'
  Write-Output "WARNING: No environment variable SEA_INSTALLER_VERSION set. Using 0.0.0"
}
Write-Output "SeaCoin Version is: $env:SEA_INSTALLER_VERSION"
Write-Output "   ---"

# Write-Output "   ---"
# Write-Output "Use pyinstaller to create sea .exe's"
# Write-Output "   ---"
# $SPEC_FILE = (python -c 'import sea; print(sea.PYINSTALLER_SPEC_PATH)') -join "`n"
# pyinstaller --log-level INFO $SPEC_FILE

# Write-Output "   ---"
# Write-Output "Creating a directory of licenses from pip and npm packages"
# Write-Output "   ---"
# bash ./build_win_license_dir.sh

# Write-Output "   ---"
# Write-Output "Copy sea executables to seacoin-blockchain-gui\"
# Write-Output "   ---"
# Copy-Item "dist\daemon" -Destination "..\seacoin-blockchain-gui\packages\gui\" -Recurse

Write-Output "   ---"
Write-Output "Setup npm packager"
Write-Output "   ---"
Set-Location -Path ".\npm_windows" -PassThru
npm ci
$Env:Path = $(npm root) + "\.bin;" + $Env:Path

Set-Location -Path "..\..\" -PassThru

Write-Output "   ---"
Write-Output "Prepare Electron packager"
Write-Output "   ---"
$Env:NODE_OPTIONS = "--max-old-space-size=3000"

# Change to the GUI directory
Set-Location -Path "seacoin-blockchain-gui\packages\gui" -PassThru

Write-Output "   ---"
Write-Output "Increase the stack for sea command for (sea plots create) chiapos limitations"
# editbin.exe needs to be in the path
editbin.exe /STACK:8000000 daemon\sea.exe
Write-Output "   ---"

$packageVersion = "$env:SEA_INSTALLER_VERSION"
$packageName = "SeaCoin-$packageVersion"


Write-Output "   ---"
Write-Output "electron-builder create package directory"
electron-builder build --win --x64 --config.productName="SeaCoin" --dir
Get-ChildItem dist\win-unpacked\resources
Write-Output "   ---"

If ($env:HAS_SIGNING_SECRET) {
   Write-Output "   ---"
   Write-Output "Sign all EXEs"
   Get-ChildItem ".\dist\win-unpacked" -Recurse | Where-Object { $_.Extension -eq ".exe" } | ForEach-Object {
      $exePath = $_.FullName
      Write-Output "Signing $exePath"
      signtool.exe sign /sha1 $env:SM_CODE_SIGNING_CERT_SHA1_HASH /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 $exePath
      Write-Output "Verify signature"
      signtool.exe verify /v /pa $exePath
  }
}    Else    {
   Write-Output "Skipping verify signatures - no authorization to install certificates"
}

Write-Output "   ---"
Write-Output "electron-builder create installer"
electron-builder build --win --x64 --config.productName="SeaCoin" --pd ".\dist\win-unpacked"
Write-Output "   ---"

If ($env:HAS_SIGNING_SECRET) {
   Write-Output "   ---"
   Write-Output "Sign Final Installer App"
   signtool.exe sign /sha1 $env:SM_CODE_SIGNING_CERT_SHA1_HASH /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 .\dist\SeaCoinSetup-$packageVersion.exe
   Write-Output "   ---"
   Write-Output "Verify signature"
   Write-Output "   ---"
   signtool.exe verify /v /pa .\dist\SeaCoinSetup-$packageVersion.exe
}   Else    {
   Write-Output "Skipping verify signatures - no authorization to install certificates"
}

Write-Output "   ---"
Write-Output "Moving final installers to expected location"
Write-Output "   ---"
Copy-Item ".\dist\win-unpacked" -Destination "$env:GITHUB_WORKSPACE\seacoin-blockchain-gui\SeaCoin-win32-x64" -Recurse
mkdir "$env:GITHUB_WORKSPACE\seacoin-blockchain-gui\release-builds\windows-installer" -ea 0
Copy-Item ".\dist\SeaCoinSetup-$packageVersion.exe" -Destination "$env:GITHUB_WORKSPACE\seacoin-blockchain-gui\release-builds\windows-installer"

Write-Output "   ---"
Write-Output "Windows Installer complete"
Write-Output "   ---"
