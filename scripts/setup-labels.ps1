$ErrorActionPreference = "Stop"

$repo = "schmitzCatz/home-assistant-nutrition"

$labels = @(
    @{ Name = "bug";              Color = "d73a4a"; Description = "Something isn't working" }
    @{ Name = "enhancement";      Color = "a2eeef"; Description = "New feature or improvement" }
    @{ Name = "documentation";    Color = "0075ca"; Description = "Documentation improvements" }

    @{ Name = "area:weight";      Color = "5319e7"; Description = "Weight management" }
    @{ Name = "area:energy";      Color = "5319e7"; Description = "Energy calculations" }
    @{ Name = "area:macros";      Color = "5319e7"; Description = "Macronutrient calculations" }
    @{ Name = "area:dashboard";   Color = "5319e7"; Description = "Lovelace dashboard" }
    @{ Name = "area:ci";          Color = "5319e7"; Description = "CI and automated testing" }

    @{ Name = "priority:high";    Color = "b60205"; Description = "High priority" }
    @{ Name = "priority:medium";  Color = "fbca04"; Description = "Medium priority" }
    @{ Name = "priority:low";     Color = "0e8a16"; Description = "Low priority" }
)

gh auth status

if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated."
}

foreach ($label in $labels) {
    Write-Host "Configuring label: $($label.Name)"

    gh label create $label.Name `
        --repo $repo `
        --color $label.Color `
        --description $label.Description `
        --force

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to configure label: $($label.Name)"
    }
}

Write-Host "All labels configured successfully." -ForegroundColor Green
