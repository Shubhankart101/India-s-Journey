<#
.SYNOPSIS
    Turnkey Azure Deployment Script for India's Journey (PowerShell).
    Optimized for Linux B1 Plan (~Rs. 1,100/month, well within the Rs. 12,500 budget).

.EXAMPLE
    .\scripts\azure-deploy.ps1 -ResourceGroup "rg-indiasjourney" -Location "centralindia"
#>
param(
    [string]$ResourceGroup = "rg-indiasjourney",
    [string]$Location = "centralindia",
    [string]$AppName = "indias-journey-$((Get-Random -Minimum 1000 -Maximum 9999))",
    [string]$PlanName = "asp-indiasjourney-b1",
    [string]$Sku = "B1"
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " India's Journey: Deploying to Microsoft Azure (Lowest Resource Plan)" -ForegroundColor Cyan
Write-Host " Target Resource Group : $ResourceGroup"
Write-Host " Location               : $Location"
Write-Host " App Name               : $AppName"
Write-Host " App Service Plan SKU   : $Sku (~Rs. 1,100 / month)"
Write-Host " Monthly Budget Ceiling : Rs. 12,500"
Write-Host "======================================================================"

# 1. Verify Azure CLI login
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "Connected to Azure Subscription: $($account.id)" -ForegroundColor Green
} catch {
    Write-Host "Not signed in to Azure CLI. Please run: az login" -ForegroundColor Red
    exit 1
}

# 2. Create Resource Group
Write-Host "Creating Resource Group '$ResourceGroup'..."
az group create --name $ResourceGroup --location $Location --output table

# 3. Create App Service Plan (Linux B1)
Write-Host "Creating App Service Plan '$PlanName' (Linux $Sku)..."
az appservice plan create `
    --name $PlanName `
    --resource-group $ResourceGroup `
    --location $Location `
    --is-linux `
    --sku $Sku `
    --output table

# 4. Generate high-entropy Django Secret Key
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

# 5. Create Web App
Write-Host "Creating Web App '$AppName'..."
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan $PlanName `
    --deployment-local-git `
    --output table

# 6. Configure Application Settings
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

# 7. Configure Health Check Path
Write-Host "Enabling health check at /api/health/..."
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --generic-configurations '{\"healthCheckPath\": \"/api/health/\"}' `
    --output table

$appUrl = "https://${AppName}.azurewebsites.net"
Write-Host "======================================================================" -ForegroundColor Green
Write-Host " Deployment Configuration Complete!" -ForegroundColor Green
Write-Host " App URL: $appUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Deploy your container or code:"
Write-Host "  Option A (Container): az webapp config container set --name $AppName --resource-group $ResourceGroup --docker-custom-image-name <your-image>"
Write-Host "  Option B (GitHub Actions): Download publish profile via: az webapp deployment list-publishing-profiles --name $AppName --resource-group $ResourceGroup --xml"
Write-Host "======================================================================" -ForegroundColor Green
