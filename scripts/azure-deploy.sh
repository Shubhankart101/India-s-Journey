#!/usr/bin/env bash
# ==============================================================================
# Turnkey Azure Deployment Script for India's Journey
# Budget Optimization: Configured for Linux B1 (~Rs. 1,100/month)
# Fits well inside your Rs. 12,500/month budget ceiling.
# ==============================================================================
set -euo pipefail

RESOURCE_GROUP="${1:-rg-indiasjourney}"
LOCATION="${2:-centralindia}"          # Central India (Pune) for lowest latency in India
APP_NAME="${3:-indias-journey-$RANDOM}" # Globally unique web app name
PLAN_NAME="${4:-asp-indiasjourney-b1}"
SKU="B1"                               # Basic 1 vCPU, 1.75 GB RAM (~Rs. 1,100 / mo)

echo "======================================================================"
echo "🇮🇳 India's Journey: Deploying to Microsoft Azure (Lowest Resource Plan)"
echo "Target Resource Group : ${RESOURCE_GROUP}"
echo "Location               : ${LOCATION}"
echo "App Name               : ${APP_NAME}"
echo "App Service Plan SKU   : ${SKU} (~Rs. 1,100 / month)"
echo "Monthly Budget Ceiling : Rs. 12,500"
echo "======================================================================"

# 1. Verify Azure CLI sign-in
if ! az account show > /dev/null 2>&1; then
  echo "⚠️ Not signed in to Azure CLI. Please run: az login"
  exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✓ Connected to Azure Subscription: ${SUBSCRIPTION_ID}"

# 2. Create Resource Group
echo "Creating resource group '${RESOURCE_GROUP}' in '${LOCATION}'..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output table

# 3. Create App Service Plan (Linux B1)
echo "Creating App Service Plan '${PLAN_NAME}' (Linux ${SKU})..."
az appservice plan create \
  --name "${PLAN_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${LOCATION}" \
  --is-linux \
  --sku "${SKU}" \
  --output table

# 4. Generate a high-entropy Django Secret Key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 36)

# 5. Create Web App (Docker Container runtime)
echo "Creating Web App '${APP_NAME}'..."
az webapp create \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --plan "${PLAN_NAME}" \
  --deployment-local-git \
  --output table

# 6. Configure Application Settings
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

# 7. Configure Health Check
echo "Enabling health check at /api/health/..."
az webapp config set \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --generic-configurations '{"healthCheckPath": "/api/health/"}' \
  --output table

APP_URL="https://${APP_NAME}.azurewebsites.net"
echo "======================================================================"
echo "🎉 Deployment Configuration Complete!"
echo "App URL: ${APP_URL}"
echo ""
echo "Next step: Push your container image or code:"
echo "  Option A (Container): az webapp config container set --name ${APP_NAME} --resource-group ${RESOURCE_GROUP} --docker-custom-image-name <your-acr-or-dockerhub-image>"
echo "  Option B (GitHub Actions): Set up AZURE_WEBAPP_PUBLISH_PROFILE in GitHub Secrets"
echo "======================================================================"
