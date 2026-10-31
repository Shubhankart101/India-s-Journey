---
title: India's Journey
emoji: 🇮🇳
colorFrom: yellow
colorTo: green
sdk: docker
app_port: 8000
pinned: false
short_description: India data dashboard - Django REST API + React
---

# India's Journey

An interactive India data dashboard: 900+ official indicators across the economy, industry, mining, banking, State/UT performance, health, social, defence, crime, elections and tourism, with a Django REST API, Swagger UI and a React front end.

- API docs: `/api/docs/`
- Health check: `/api/health/`
- Backup static dashboard: https://shubhankart101.github.io/India-s-Journey/
- Source: https://github.com/Shubhankart101/India-s-Journey

Google/Microsoft sign-in only works on the direct `*.hf.space` URL (open it via **⋮ → Embed this Space → Direct URL**), not inside the huggingface.co frame.

This Space is deployed by `scripts/deploy_hf_space.py` from the GitHub repository. User accounts and saved charts are kept in SQLite under `/tmp`, so they reset whenever the Space restarts; the dashboards are re-imported on every start.
