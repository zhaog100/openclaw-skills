# QMD Knowledge Search Tool

param(
    [Parameter(Mandatory=$true)]
    [string]$Query
)

$knowledgePath = "C:\Users\zhaog\.openclaw\workspace\knowledge"

Write-Host ""
Write-Host "Searching for: $Query" -ForegroundColor Cyan
Write-Host "=================================================="

$files = Get-ChildItem -Path $knowledgePath -Recurse -Filter "*.md"
$results = @()

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $matches = ([regex]::Matches($content, $Query, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase))
    
    if ($matches.Count -gt 0) {
        $relativePath = $file.FullName.Replace($knowledgePath, "").TrimStart('\')
        $results += [PSCustomObject]@{
            File = $relativePath
            Matches = $matches.Count
        }
    }
}

if ($results.Count -eq 0) {
    Write-Host ""
    Write-Host "No results found" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "Found $($results.Count) files:" -ForegroundColor Green
    Write-Host ""
    
    $results | Sort-Object Matches -Descending | ForEach-Object {
        Write-Host "  File: $($_.File)" -ForegroundColor Yellow
        Write-Host "  Matches: $($_.Matches)"
        Write-Host ""
    }
}

Write-Host "=================================================="
