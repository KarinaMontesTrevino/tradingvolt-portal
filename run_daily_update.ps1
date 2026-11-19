# ==============================================================================
# TradingVolt Daily Market Intelligence - Automated Task Runner
# ==============================================================================
$ErrorActionPreference = "Stop"
Write-Host "[TRADINGVOLT] Sincronizando datos diarios de mercado y macro..." -ForegroundColor Cyan

$uvPath = "$HOME\.local\bin\uv.exe"
if (-not (Test-Path $uvPath)) {
    $uvPath = "uv"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

& $uvPath run --offline --with pandas --with matplotlib --with requests python "$scriptDir\daily_market_intelligence.py"

Write-Host "[TRADINGVOLT] Actualización diaria completada exitosamente." -ForegroundColor Green
