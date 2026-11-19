# 🇮🇳 India's Journey — Release v2.1.0

**Under-Budget AI Engine, Google & Microsoft OAuth, Continuous Index Pipelines & Azure Cloud Architecture**

---

## 🌟 Highlights of Release v2.1.0

### 1. Privacy-First Authentication (Google & Microsoft Identity)
- Single-click **"Continue with Google"** and **"Continue with Microsoft (Outlook/365)"** OAuth 2.0 flow.
- Accessible directly at route [`/login`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/AuthPage.jsx) and through header user status pills.
- Protected against CSRF with session cookies and zero stored passwords.

### 2. Under-Budget AI & Intelligent Analytics Engine (₹0 Required Baseline)
- **Semantic Vector Search (`/api/ai/search/`)**: Natural language discovery across all 3,082 verified public catalog indicators with offline token-vectorizer fallback.
- **Cross-Domain Vector Indicator Recommender (`/api/ai/recommend/<key>/`)**: Evaluates cosine similarity in RAM in <15ms to recommend contextually related series on [Indicator.jsx](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/Indicator.jsx).
- **Macroeconomic Inflection & Policy Synthesizer (`/api/ai/insights/<key>/`)**: Computes CAGR, peak/trough benchmarks, and correlates inflections with 1991, 1998, 2008, 2016, 2017, 2020, and 2022 milestones.
- **Compare View Cross-Series Correlation Engine (`/api/ai/compare-insights/`)**: Calculates Pearson correlation ($r$) and highlights historical decoupling shocks on [Compare.jsx](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/Compare.jsx).

### 3. Continuous Data Collection Pipelines
- **Infrastructure & Energy Pipeline**: Tracks CEA generation, solar/wind capacity additions, and NHAI highway completion (`collect_energy_and_infrastructure.py`).
- **DPI & Payments Pipeline**: Synthesizes NPCI UPI transaction volumes/values, FASTag toll collections, and RBI-DPI progression (`collect_dpi_and_payments.py`).
- **Market & Commodity Benchmark Pipeline**: Gathers BSE SENSEX, NSE Nifty 50, RBI USD/INR exchange rates, and crude oil prices (`collect_market_and_commodity_indices.py`).
- **Azure Storage Archival Sync**: Automates cloud archival to Azure Blob Storage under budget (`sync_data_to_azure_storage.py`).

### 4. Modular Azure Cloud Architecture (Terraform)
- **App Service Linux B1 Plan**: Low-cost production baseline (~Rs. 1,100/mo).
- **Optional Modules**: PostgreSQL Flexible Server B1ms (~Rs. 800/mo), Azure Cache for Redis C0 (~Rs. 1,200/mo), Azure OpenAI Cognitive Services S0, and Azure Storage Account Cool tier (~Rs. 60/mo).
- **Budget Ceiling**: Strictly enforced via Azure Consumption Budget at **Rs. 12,500 INR/month** with automated email alerts at 80% and 100%.

### 5. Static Site & GitHub Pages Parity
- Full client-side JavaScript execution of AI recommendations, search, and Pearson correlation in static mode (`docs/`).
- Verified with 145 Django backend tests and 149 Vitest frontend tests.

---

*Target Repository*: [Shubhankart101/India-s-Journey](https://github.com/Shubhankart101/India-s-Journey)  
*Azure Production Deployment*: [indias-journey-m5ag64.azurewebsites.net](https://indias-journey-m5ag64.azurewebsites.net/)  
*Static Production Deployment*: [shubhankart101.github.io/India-s-Journey](https://shubhankart101.github.io/India-s-Journey/)
