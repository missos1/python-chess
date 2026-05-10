<#
.SYNOPSIS
Builds a Windows executable for the chess engine with PyInstaller, Nuitka, or both.

.EXAMPLE
.\build.ps1
.\build.ps1 -Tool Nuitka
.\build.ps1 -Tool Both -Clean
#>

param(
    [ValidateSet("PyInstaller", "Nuitka", "Both")]
    [string]$Tool = "PyInstaller",

    [switch]$Clean,

    [string]$OutputName = "python-chess"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EntryPoint = Join-Path $ScriptRoot "main.py"
$DistRoot = Join-Path $ScriptRoot "dist"
$BuildRoot = Join-Path $ScriptRoot "build"
$PyInstallerDist = Join-Path $DistRoot "pyinstaller"
$PyInstallerWork = Join-Path $BuildRoot "pyinstaller"
$NuitkaDist = Join-Path $DistRoot "nuitka"

# TWEAK: Fail fast if entry point is missing
if (-not (Test-Path -LiteralPath $EntryPoint)) {
    throw "Entry point script not found at: $EntryPoint"
}

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    # TWEAK: Prioritize 'python' over 'py' to respect active Conda environments
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python @Arguments
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @Arguments
    }
    else {
        throw "Python was not found on PATH. Install Python or add it to PATH before running this script."
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Build command failed with exit code $LASTEXITCODE."
    }
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Remove-PathIfExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Build-PyInstaller {
    Write-Host "Building with PyInstaller..."

    Ensure-Directory -Path $PyInstallerDist
    Ensure-Directory -Path $PyInstallerWork

    $Arguments = @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--console",
        "--onefile",
        "--name", $OutputName,
        "--distpath", $PyInstallerDist,
        "--workpath", $PyInstallerWork,
        "--specpath", $PyInstallerWork,
        "--collect-submodules", "data.classes.chess_bot",
        $EntryPoint
    )

    Invoke-PythonModule -Arguments $Arguments
    Write-Host "PyInstaller output: $PyInstallerDist"
}

function Build-Nuitka {
    Write-Host "Building with Nuitka..."

    Ensure-Directory -Path $NuitkaDist

    $Arguments = @(
        "-m", "nuitka",
        "--assume-yes-for-downloads",
        "--standalone",
        "--follow-imports",
        "--onefile",
        "--windows-console-mode=force",
        "--include-package=data.classes.chess_bot",
        "--remove-output",                   # TWEAK: Cleans up the heavy .build folders
        "--output-dir=$NuitkaDist",          # TWEAK: Use '=' syntax for strict Nuitka parsing
        "--output-filename=$OutputName",     # TWEAK: Use '=' syntax for strict Nuitka parsing
        $EntryPoint
    )

    Invoke-PythonModule -Arguments $Arguments
    Write-Host "Nuitka output: $NuitkaDist"
}

Push-Location $ScriptRoot
try {
    if ($Clean) {
        Remove-PathIfExists -Path $DistRoot
        Remove-PathIfExists -Path $BuildRoot
    }

    Ensure-Directory -Path $DistRoot
    Ensure-Directory -Path $BuildRoot

    switch ($Tool) {
        "PyInstaller" {
            Build-PyInstaller
        }
        "Nuitka" {
            Build-Nuitka
        }
        "Both" {
            Build-PyInstaller
            Build-Nuitka
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Build complete."