param([string]$GitPath = '', [switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$courseRoot = Split-Path -Parent $PSScriptRoot
$targetUrl = 'https://github.com/ml4vn/MachineLearning.git'
$gitOptions = @('-c', "safe.directory=$courseRoot", '-C', $courseRoot)

if (-not $GitPath) {
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCommand) { $GitPath = $gitCommand.Source }
}
if (-not $GitPath) {
    $bundledGit = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
    if (Test-Path -LiteralPath $bundledGit) { $GitPath = $bundledGit }
}
if (-not $GitPath -or -not (Test-Path -LiteralPath $GitPath)) {
    throw 'Install Git for Windows, or provide -GitPath with the path to git.exe.'
}

function Invoke-CourseGit {
    & $GitPath @gitOptions @args
    if ($LASTEXITCODE -ne 0) { throw "Git failed with exit code $LASTEXITCODE. See the message above." }
}

if (-not (Test-Path -LiteralPath (Join-Path $courseRoot '.git'))) {
    Invoke-CourseGit init -b main
}
$branch = [string](Invoke-CourseGit symbolic-ref --short HEAD)
if ($branch.Trim() -ne 'main') { throw 'Expected local branch main. Review branch history before publishing.' }
$remoteNames = @(Invoke-CourseGit remote)
if ($remoteNames -contains 'origin') {
    $remoteUrl = [string](Invoke-CourseGit remote get-url origin)
    if ($remoteUrl.Trim().TrimEnd('/') -notin @($targetUrl, 'https://github.com/ml4vn/MachineLearning')) {
        throw 'origin points to a different repository. Review it before publishing.'
    }
} else {
    Invoke-CourseGit remote add origin $targetUrl
}

$remoteRefs = @(Invoke-CourseGit ls-remote --heads --tags origin)
& $GitPath @gitOptions rev-parse --verify --quiet HEAD | Out-Null
$hasHead = $LASTEXITCODE -eq 0
if ($remoteRefs.Count -gt 0) {
    if (-not $hasHead) { throw 'Remote already contains commits. Clone/synchronize its history before adding these files.' }
    Invoke-CourseGit fetch origin main
    & $GitPath @gitOptions merge-base --is-ancestor origin/main HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Remote main is not an ancestor of local HEAD. Synchronize before publishing; do not force-push.' }
}

if ($CheckOnly) {
    Write-Host "Target: $targetUrl"
    Write-Host "Existing remote refs: $($remoteRefs.Count)"
    foreach ($field in @('user.name', 'user.email')) {
        $configuredValue = [string](& $GitPath @gitOptions config --get $field)
        Write-Host "$field configured: $(-not [string]::IsNullOrWhiteSpace($configuredValue))"
    }
    Write-Host 'Preflight complete. No commit or push performed.'
    exit 0
}

foreach ($field in @('user.name', 'user.email')) {
    $value = [string](& $GitPath @gitOptions config --get $field)
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = Read-Host "Enter your commit $field (stored only in this repository)"
        if ([string]::IsNullOrWhiteSpace($value)) { throw "$field is required. Nothing has been pushed." }
        Invoke-CourseGit config --local $field $value.Trim()
    }
}

Invoke-CourseGit add -- .
Invoke-CourseGit diff --cached --check
Invoke-CourseGit diff --cached --stat
& $GitPath @gitOptions diff --cached --quiet
$hasChanges = $LASTEXITCODE -eq 1
if ($LASTEXITCODE -gt 1) { throw 'Could not inspect staged changes.' }
if ($hasChanges) {
    Invoke-CourseGit commit -m 'Add ten pre-reading guides and Python machine learning labs'
}
if (-not $hasHead -and -not $hasChanges) { throw 'No files available to publish.' }
Invoke-CourseGit push -u origin main
Write-Host 'Published to https://github.com/ml4vn/MachineLearning'
Write-Host 'Next: check Actions and set the About description from docs/MO_TA_DU_AN.txt.'
