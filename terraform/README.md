# 🇮🇳 India's Journey — Terraform Azure Infrastructure

This directory contains the production-ready Terraform Infrastructure-as-Code for deploying **India's Journey** onto Microsoft Azure with minimal resource consumption.

## Budget & Cost Efficiency
- **Plan**: Azure Linux App Service Plan `B1` (1 vCPU, 1.75 GB RAM)
- **Monthly Cost**: **~₹1,100 / month (~$13 USD)**
- **Monthly Budget**: **₹12,500 / month** (Leaves > ₹11,400 / month in savings)
- **Built-in Budget Alert**: Automatically alerts your email when spend hits 80% (₹10,000) and 100% (₹12,500).

---

## Prerequisites
1. [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) (>= 1.5.0)
2. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) (`az login`)

---

## Deployment Instructions

### 1. Authenticate with Azure
```bash
az login
```

### 2. Initialize Terraform
```bash
cd terraform
terraform init
```

### 3. Review Plan
```bash
terraform plan
```

### 4. Apply Configuration
```bash
terraform apply
```

Upon completion, Terraform will output the live URL:
```
Outputs:
web_app_url = "https://indias-journey-abc123.azurewebsites.net"
estimated_monthly_cost = "Approx. Rs. 1,100 / month (~$13 USD)"
monthly_budget_ceiling = "Rs. 12500 / month"
```

---

## Destroying Resources (Tear Down)
To completely delete all created resources and stop any Azure charges:
```bash
terraform destroy
```
