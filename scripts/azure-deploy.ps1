<#
.SYNOPSIS
    Turnkey Azure Deployment Script for India's Journey (PowerShell).
    Supports Terraform (default) and Azure CLI roll out modes.
    Optimized for Linux B1 Plan (~Rs. 1,100/month, well within the Rs. 12,500 budget).

.EXAMPLE
    .\scripts\azure-deploy.ps1 -Mode "terraform"
    .\scripts\azure-deploy.ps1 -Mode "cli" -ResourceGroup "rg-indiasjourney"
#>
param(
    [ValidateSet("terraform", "cli")]
    [string]$Mode = "terraform",
    [string]$ResourceGroup = "rg-indiasjourney",
    [string]$Location = "centralindia",
    [string]$AppName = "indias-journey-$((Get-Random -Minimum 1000 -Maximum 9999))",
    [string]$Sku = "B1"
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 🇮🇳 India's Journey: Azure Cloud Roll Out" -ForegroundColor Cyan
Write-Host " Deployment Mode        : $Mode"
Write-Host " Target Resource Group  : $ResourceGroup"
Write-Host " Location                : $Location"
Write-Host " Compute Plan SKU        : Linux $Sku (1 vCPU, 1.75 GB RAM, ~Rs. 1,100 / mo)"
Write-Host " Monthly Budget Ceiling  : Rs. 12,500 (with automated email alerts)"
Write-Host "======================================================================"

# 1. Verify Azure CLI login
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✓ Connected to Azure Subscription: $($account.id)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Not signed in to Azure CLI. Please run: az login" -ForegroundColor Red
    exit 1
}

# 2. Terraform Deployment Mode
if ($Mode -eq "terraform") {
    $tf = Get-Command terraform -ErrorAction SilentlyContinue
    if (-not $tf) {
        Write-Host "⚠️ Terraform not found on PATH. Falling back to Azure CLI deployment..." -ForegroundColor Yellow
        $Mode = "cli"
    } else {
        Write-Host "Provisioning infrastructure via Terraform..." -ForegroundColor Cyan
        $tfDir = Join-Path $PSScriptRoot "..\terraform"
        Push-Location $tfDir
        try {
            terraform init
            terraform apply -auto-approve `
                -var="resource_group_name=$ResourceGroup" `
                -var="location=$Location" `
                -var="app_name_prefix=indias-journey" `
                -var="sku_name=$Sku" `
                -var="monthly_budget_inr=12500"
            Write-Host "======================================================================" -ForegroundColor Green
            Write-Host "🎉 Terraform Deployment Complete!" -ForegroundColor Green
            terraform output
            Write-Host "======================================================================" -ForegroundColor Green
        } finally {
            Pop-Location
        }
        exit 0
    }
}

# 3. CLI Deployment Mode
Write-Host "Creating Resource Group '$ResourceGroup'..."
az group create --name $ResourceGroup --location $Location --output table

$planName = "asp-indiasjourney-b1"
Write-Host "Creating App Service Plan '$planName' (Linux $Sku)..."
az appservice plan create `
    --name $planName `
    --resource-group $ResourceGroup `
    --location $Location `
    --is-linux `
    --sku $Sku `
    --output table

$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

Write-Host "Creating Web App '$AppName'..."
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan $planName `
    --deployment-local-git `
    --output table

Write-Host "Configuring environment variables and persistent storage..."
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        WEBSITES_PORT=8000 `
        PORT=8000 `
        DJANGO_DEBUG=false `
        DJANGO_SECRET_KEY=$secretKey `
        WEB_CONCURRENCY=2 `
        GUNICORN_THREADS=2 `
        DJANGO_SQLITE_PATH=/home/data/db.sqlite3 `
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=true `
        DJANGO_LOG_LEVEL=INFO `
    --output table

Write-Host "Enabling health check at /api/health/..."
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --generic-configurations '{\"healthCheckPath\": \"/api/health/\"}' `
    --output table

$appUrl = "https://${AppName}.azurewebsites.net"
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "🎉 Azure CLI Roll Out Complete!" -ForegroundColor Green
Write-Host "App URL: $appUrl" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Green
