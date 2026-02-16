param(
  [Parameter(Mandatory = $true)]
  [string]$File,
  [Parameter(Mandatory = $true)]
  [string]$StartDate
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $File)) {
  throw "File not found: $File"
}

python scripts/parse_excel.py $File $StartDate
