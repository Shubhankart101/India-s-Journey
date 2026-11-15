// Azure Bicep Template: India's Journey on Minimal-Cost Azure App Service (Linux B1)
// Budget: Fits within Rs. 1,100 - Rs. 2,200/month (well below Rs. 12,500/month budget)

@description('Name of the App Service plan')
param appServicePlanName string = 'asp-indiasjourney-b1'

@description('Name of the Azure Web App (must be globally unique)')
param webAppName string = 'indias-journey-${uniqueString(resourceGroup().id)}'

@description('Azure Region (centralindia = Pune, southindia = Chennai)')
param location string = 'centralindia'

@description('Pricing tier: B1 (1 vCPU, 1.75GB RAM ~Rs. 1,100/mo) or B2 (2 vCPU, 3.5GB RAM ~Rs. 2,200/mo)')
@allowed([
  'B1'
  'B2'
])
param skuName string = 'B1'

@description('Docker image URL (e.g. ghcr.io/username/indias-journey:latest or Azure Container Registry)')
param dockerImage string = 'mcr.microsoft.com/appsvc/staticsite:latest'

@secure()
@description('Django Secret Key (32+ random characters)')
param djangoSecretKey string = uniqueString(newGuid(), resourceGroup().id)

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: skuName
    tier: 'Basic'
    capacity: 1
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  kind: 'app,linux,container'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    reserved: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerImage}'
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      healthCheckPath: '/api/health/'
      appSettings: [
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
        {
          name: 'PORT'
          value: '8000'
        }
        {
          name: 'DJANGO_DEBUG'
          value: 'false'
        }
        {
          name: 'DJANGO_SECRET_KEY'
          value: djangoSecretKey
        }
        {
          name: 'WEB_CONCURRENCY'
          value: '2'
        }
        {
          name: 'GUNICORN_THREADS'
          value: '2'
        }
        {
          name: 'DJANGO_SQLITE_PATH'
          value: '/home/data/db.sqlite3'
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'true'
        }
        {
          name: 'DJANGO_LOG_LEVEL'
          value: 'INFO'
        }
      ]
    }
  }
}

output appUrl string = 'https://${webApp.properties.defaultHostName}'
output appName string = webApp.name
output planSku string = skuName
