[CmdletBinding()]
param(
  [string]$InstallDir = $(Join-Path ($(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" })) "skills\cli-model-switcher"),
  [string]$Repo = "YuxuanSun123/cli-model-switcher",
  [string]$Branch = "main",
  [ValidateSet("auto", "powershell", "cmd", "unix", "bash", "zsh", "fish")]
  [string]$Shell = "auto",
  [string]$Recipes = "opencode-openrouter,local-ollama",
  [string]$Active = "opencode-openrouter",
  [switch]$Full,
  [switch]$NoInstall,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Get-PythonCommand {
  if ($env:AI_CLI_SWITCHER_PYTHON) {
    return [pscustomobject]@{ Command = $env:AI_CLI_SWITCHER_PYTHON; Args = @() }
  }
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return [pscustomobject]@{ Command = "py"; Args = @("-3.12") }
  }
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return [pscustomobject]@{ Command = "python"; Args = @() }
  }
  if (Get-Command python3 -ErrorAction SilentlyContinue) {
    return [pscustomobject]@{ Command = "python3"; Args = @() }
  }
  throw "Python 3 was not found. Install Python 3 or set AI_CLI_SWITCHER_PYTHON."
}

$Python = Get-PythonCommand

function Invoke-Python {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
  & $Python.Command @($Python.Args) @Args
  if ($LASTEXITCODE -ne 0) {
    throw "Python command failed with exit code $LASTEXITCODE"
  }
}

function Invoke-Setup {
  param([string]$Root, [switch]$AsDryRun)
  $Helper = Join-Path $Root "scripts\cli_model_switcher.py"
  if (-not (Test-Path -LiteralPath $Helper)) {
    throw "Missing helper script: $Helper"
  }

  $SetupArgs = @($Helper, "setup")
  if ($Full) {
    $SetupArgs += "--full"
  } else {
    $SetupArgs += @("--wizard", "--yes", "--recipes", $Recipes, "--active", $Active)
  }
  $SetupArgs += @("--shell", $Shell)
  if ($NoInstall) {
    $SetupArgs += "--no-install"
  }
  if ($AsDryRun) {
    $SetupArgs += "--dry-run"
  }
  Invoke-Python @SetupArgs
}

function Install-FromArchive {
  $Temp = Join-Path ([IO.Path]::GetTempPath()) ("cli-model-switcher-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Path $Temp | Out-Null
  try {
    $Zip = Join-Path $Temp "source.zip"
    $Url = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Zip
    Expand-Archive -LiteralPath $Zip -DestinationPath $Temp -Force
    $Expanded = Get-ChildItem -LiteralPath $Temp -Directory | Where-Object { $_.Name -ne "." } | Select-Object -First 1
    if (-not $Expanded) {
      throw "Downloaded archive did not contain a source directory."
    }
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Copy-Item -Path (Join-Path $Expanded.FullName "*") -Destination $InstallDir -Recurse -Force
  } finally {
    if (Test-Path -LiteralPath $Temp) {
      Remove-Item -LiteralPath $Temp -Recurse -Force
    }
  }
}

function Install-OrUpdateRepo {
  $GitDir = Join-Path $InstallDir ".git"
  $ExistingHelper = Join-Path $InstallDir "scripts\cli_model_switcher.py"

  if (Test-Path -LiteralPath $GitDir) {
    git -C $InstallDir fetch origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }
    git -C $InstallDir checkout $Branch
    if ($LASTEXITCODE -ne 0) { throw "git checkout failed" }
    git -C $InstallDir pull --ff-only origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "git pull failed" }
    return
  }

  if (Test-Path -LiteralPath $ExistingHelper) {
    Write-Host "Using existing installation at $InstallDir"
    return
  }

  if ((Test-Path -LiteralPath $InstallDir) -and (Get-ChildItem -LiteralPath $InstallDir -Force | Select-Object -First 1)) {
    throw "Install directory is not empty and is not a CLI Model Switcher checkout: $InstallDir"
  }

  if (Get-Command git -ErrorAction SilentlyContinue) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $InstallDir) -Force | Out-Null
    git clone --depth 1 --branch $Branch "https://github.com/$Repo.git" $InstallDir
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
    return
  }

  Install-FromArchive
}

Write-Host "CLI Model Switcher installer"
Write-Host "Repository: $Repo"
Write-Host "Branch: $Branch"
Write-Host "Install directory: $InstallDir"
Write-Host "Shell: $Shell"
Write-Host "Python: $($Python.Command) $($Python.Args -join ' ')"

if ($DryRun) {
  Write-Host "Dry run: would clone/update and run setup."
  $LocalHelper = Join-Path $PSScriptRoot "scripts\cli_model_switcher.py"
  if (Test-Path -LiteralPath $LocalHelper) {
    Invoke-Setup -Root $PSScriptRoot -AsDryRun
  } else {
    Write-Host "Dry run skipped setup execution because the helper script is not next to install.ps1."
  }
  exit 0
}

Install-OrUpdateRepo
Invoke-Setup -Root $InstallDir

Write-Host ""
Write-Host "Installed CLI Model Switcher."
Write-Host "Open a new terminal or reload the shell profile printed above, then run:"
Write-Host "  ayatori about"
Write-Host "  ayatori status"
Write-Host "  ai-status"
Write-Host "  ai-doctor --fix"
Write-Host ""
Write-Host "In each project where you want agent-side switching, run:"
Write-Host "  ai-agent install all"
