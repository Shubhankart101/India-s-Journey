# Release 42: Under-Budget AI, Google/Microsoft OAuth, Data Pipelines & Azure Cloud Architecture

**Release Date**: November 19, 2026  
**Milestone**: v2.1.0  
**Target Environments**: Azure App Service Linux B1 Web App (`https://indias-journey-m5ag64.azurewebsites.net/`) and GitHub Pages Static Mirror (`https://shubhankart101.github.io/India-s-Journey/`)

---

## 1. Executive Summary

This major release introduces privacy-first **Google & Microsoft OAuth authentication**, an in-memory **Under-Budget AI Engine** (Semantic Vector Search, Recommender, Macroeconomic Inflection Synthesizer, and Compare Cross-Correlation Engine), automated **Data Collection Pipelines** for national indices, and a modular **Terraform Cloud Architecture** configured under a strict **Rs. 12,500 INR/month** Azure budget cap.

All capabilities function with a **₹0 / $0 required cloud budget baseline** using pre-computed in-memory embeddings and deterministic statistical algorithms, while providing seamless opt-in hooks for managed Azure resources.

---

## 2. What's New

### A. Google & Microsoft OAuth 2.0 Authentication
* **Dedicated Sign-In Interface ([`/login`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/AuthPage.jsx))**:
  - Branded Google (4-color icon) and Microsoft (4-tile window logo) single-click authentication.
  - Zero password storage, zero credential leaks: relies on OAuth 2.0 PKCE and Django CSRF protection.
  - Authenticated user profile view with initials avatar, display name, email, and clean sign-out.
* **Header Auth Integration ([`Layout.jsx`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/components/Layout.jsx))**:
  - Dynamic user status pill in the top header (`[ 🔑 Sign in ]` / `[ 👤 {FirstName} ]`).
* **Session Endpoints ([`views.py`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/webapp/indicators/views.py))**:
  - `GET /api/auth/me/` (session user state).
  - `GET /api/auth/providers/` (active identity providers).
  - `POST /api/auth/logout/` (session termination).
  - `GET /api/auth/csrf/` (CSRF cookie issuance).

---

### B. Under-Budget AI & Intelligent Analytics Engine
Every AI feature runs locally in-memory on the existing container with **₹0 required cloud spend**:

1. **Semantic Vector Search (`/api/ai/search/`)**:
   - Natural language indicator search across 3,082 verified public catalog items.
   - Pre-computed 256-dimensional embeddings matrix (`data/catalog_embeddings.json`, 3MB RAM).
   - Sub-5ms cosine similarity inference with offline token-vectorizer fallback.
2. **Cross-Domain Vector Indicator Recommender (`/api/ai/recommend/<key>/`)**:
   - In-memory vector cosine similarity finding top 4–5 related indicators across different categories in <15ms.
   - Renders interactive indicator recommendation pills with match percentages on [Indicator.jsx](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/Indicator.jsx).
3. **Macroeconomic Inflection & Policy Synthesizer (`/api/ai/insights/<key>/`)**:
   - Generates 3 executive takeaways:
     - Growth trajectory (CAGR, baseline delta, historical peak & trough).
     - Historical milestone correlation (1991 reforms, 1998 sanctions, 2008 GFC, 2016 demonetization, 2017 GST, 2020 COVID shock, 2022 energy shocks).
     - Methodological caveats (e.g. MoSPI 2011-12 base-year revision, delimitation boundaries).
4. **Compare View Cross-Correlation & Decoupling Engine (`/api/ai/compare-insights/`)**:
   - Computes pairwise Pearson correlation coefficients ($r$) on aligned multi-series.
   - Categorizes co-movement strength (*Strong positive co-movement*, *Moderate*, *Decoupled*, or *Inverse trade-off*).
   - Detects historical decoupling shocks (divergent directional movements against macro shocks).
   - Renders an executive synthesis workbench on [Compare.jsx](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/frontend/src/pages/Compare.jsx).

---

### C. Automated Data Collection Pipelines & Index Snapshots
Four new automated pipelines expand continuous data collection across national indices:

1. **Infrastructure & Renewable Energy Pipeline ([`scripts/collect_energy_and_infrastructure.py`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/scripts/collect_energy_and_infrastructure.py))**:
   - Central Electricity Authority (CEA) power generation (thermal, hydro, renewable).
   - MNRE solar and wind installed capacity milestones (GW).
   - Peak electricity demand met (Grid-India).
   - MoRTH/NHAI highway construction pace (km/day).
   - Workflow: `.github/workflows/infrastructure-energy-update.yml` (Bi-monthly on 1st & 15th).
2. **Digital Public Infrastructure (DPI) & Payments Pipeline ([`scripts/collect_dpi_and_payments.py`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/scripts/collect_dpi_and_payments.py))**:
   - NPCI UPI annual transaction volumes (billions) and values (lakh crore INR).
   - NETC FASTag toll collection progression.
   - RBI Digital Payments Index (RBI-DPI) milestone trajectory.
   - Workflow: `.github/workflows/dpi-payments-update.yml` (Monthly on 2nd).
3. **Market & Commodity Benchmark Pipeline ([`scripts/collect_market_and_commodity_indices.py`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/scripts/collect_market_and_commodity_indices.py))**:
   - BSE SENSEX and NSE Nifty 50 milestones.
   - RBI Reference USD/INR exchange rates.
   - Indian Basket Crude Oil prices (PPAC / MoPNG).
   - Workflow: `.github/workflows/market-indices-update.yml` (Weekdays 02:15 UTC).
4. **Azure Storage Dataset Sync Pipeline ([`scripts/sync_data_to_azure_storage.py`](file:///c:/Users/Dell/OneDrive/Desktop/Assignment/India-s-Journey/scripts/sync_data_to_azure_storage.py))**:
   - Automatically synchronizes all core catalog datasets, embeddings, and snapshots into Azure Blob Storage.
   - Workflow: `.github/workflows/azure-data-sync.yml` (Weekly on Sundays).

---

### D. Modular Terraform Infrastructure Under Budget
The Terraform configuration in `terraform/` provisions a resilient cloud environment on Microsoft Azure:

* **App Service Linux B1 Plan**: ~Rs. 1,100/mo baseline running the containerized Django + React application.
* **Module `postgresql`**: Optional Azure Database for PostgreSQL Flexible Server (`B_Standard_B1ms` burstable, 32 GB storage ~Rs. 800/mo).
* **Module `redis`**: Optional Azure Cache for Redis (`Basic C0` with TLS 1.2 ~Rs. 1,200/mo).
* **Module `azure_openai`**: Optional Azure Cognitive Services (`S0` pay-as-you-go text embeddings).
* **Module `storage`**: Optional Azure Storage Account (`Standard LRS Cool` tier ~Rs. 60/mo) with Blob Containers `datasets` and `pipeline-backups`.
* **Module `budget`**: Azure Consumption Budget enforcement capping resource group spend at **Rs. 12,500 INR/month** with automated email alerts at 80% and 100%.

---

### E. Static Hosting Parity (GitHub Pages)
* All AI endpoints (`/api/ai/search/`, `/api/ai/recommend/`, `/api/ai/insights/`, `/api/ai/compare-insights/`) include robust client-side fallbacks in `frontend/src/api.js`.
* When deployed on GitHub Pages (`docs/`), the application executes vector recommendations and Pearson correlation calculations directly in JavaScript without requiring an active backend server.
* Added `docs/login.html` and updated `docs/legacy-redirect.js` for seamless URL routing.

---

## 3. Verification & Test Metrics

- **Django Backend Test Suite**: **145 tests passed** (100% pass rate).
- **Frontend Vitest Test Suite**: **149 tests passed** across all 20 test files.
- **Static API Test Suite**: **5 Python tests passed** (`tests/test_static_api.py`).
- **Catalog Export Test**: **Passed** (`tests/test_catalog_export.py`).
- **Terraform Validation**: `terraform validate` succeeded (`Success! The configuration is valid.`).
