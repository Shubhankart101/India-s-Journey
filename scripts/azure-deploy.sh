#!/usr/bin/env bash
# ==============================================================================
# Turnkey Azure Deployment Script for India's Journey (Terraform / CLI)
# Budget Optimization: Configured for Linux B1 (~Rs. 1,100/month)
# Fits well inside your Rs. 12,500/month budget ceiling.
# ==============================================================================
set -euo pipefail

MODE="${1:-terraform}" # "terraform" (default) or "cli"
RESOURCE_GROUP="${2:-rg-indiasjourney}"
LOCATION="${3:-centralindia}"          # Central India (Pune) for lowest latency in India
APP_NAME="${4:-indias-journey-$RANDOM}"

echo "======================================================================"
echo "🇮🇳 India's Journey: Azure Cloud Roll Out"
echo "Deployment Mode        : ${MODE}"
echo "Target Resource Group  : ${RESOURCE_GROUP}"
echo "Location                : ${LOCATION}"
echo "Compute Plan SKU        : Linux B1 (1 vCPU, 1.75 GB RAM, ~Rs. 1,100 / mo)"
echo "Monthly Budget Ceiling  : Rs. 12,500 (with automated email alerts)"
echo "======================================================================"

# Verify Azure CLI login
if ! az account show > /dev/null 2>&1; then
  echo "⚠️ Not signed in to Azure CLI. Please run: az login"
  exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✓ Connected to Azure Subscription: ${SUBSCRIPTION_ID}"

if [ "${MODE}" = "terraform" ]; then
  if ! command -v terraform > /dev/null 2>&1; then
    echo "⚠️ Terraform is not installed on PATH. Falling back to Azure CLI deployment..."
    MODE="cli"
  else
    echo "Provisioning infrastructure via Terraform..."
    cd "$(dirname "$0")/../terraform"
    terraform init
    terraform apply -auto-approve \
      -var="resource_group_name=${RESOURCE_GROUP}" \
      -var="location=${LOCATION}" \
      -var="app_name_prefix=indias-journey" \
      -var="sku_name=B1" \
      -var="monthly_budget_inr=12500"
    echo "======================================================================"
    echo "🎉 Terraform Deployment Complete!"
    terraform output
    echo "======================================================================"
    exit 0
  fi
fi

# Fallback / CLI Deployment Mode
echo "Creating resource group '${RESOURCE_GROUP}' in '${LOCATION}'..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output table

PLAN_NAME="asp-indiasjourney-b1"
echo "Creating App Service Plan '${PLAN_NAME}' (Linux B1)..."
az appservice plan create \
  --name "${PLAN_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${LOCATION}" \
  --is-linux \
  --sku "B1" \
  --output table

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 36)

echo "Creating Web App '${APP_NAME}'..."
az webapp create \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --plan "${PLAN_NAME}" \
  --deployment-local-git \
  --output table

echo "Configuring environment variables and persistent storage..."
az webapp config appsettings set \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --settings \
    WEBSITES_PORT=8000 \
    PORT=8000 \
    DJANGO_DEBUG=false \
    DJANGO_SECRET_KEY="${SECRET_KEY}" \
    WEB_CONCURRENCY=2 \
    GUNICORN_THREADS=2 \
    DJANGO_SQLITE_PATH=/home/data/db.sqlite3 \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
    DJANGO_LOG_LEVEL=INFO \
  --output table

echo "Enabling health check at /api/health/..."
az webapp config set \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --generic-configurations '{"healthCheckPath": "/api/health/"}' \
  --output table

APP_URL="https://${APP_NAME}.azurewebsites.net"
echo "======================================================================"
echo "🎉 Azure CLI Roll Out Complete!"
echo "App URL: ${APP_URL}"
echo "======================================================================"
