# India in Maps, display themes and contact links

- **Commit:** [`9e65ede`](https://github.com/Shubhankart101/India-s-Journey/commit/9e65ede799453b1e3092470c8653d8f1ff4fba4a)
- **Date:** 2026-11-05

## What it delivered

- **India in Maps** group: every statistic on the dashboard that is reported by State/UT is also drawn as a map of India. That gives 134 maps in 10 subgroups, one subgroup per source group: State Performance, Judiciary, Payments, Elections, Public Health, Social, Environment, Air Travel, Water Transport and Railways. Statistics with several series get one map per series. State-wise trend lines are mapped at their latest reported value. On both the static site and the web app, cards show a compact map. The full view adds hover and keyboard readouts, a colour scale and a Map/Bar switch.
- **Boundaries:** the DataMeet States layer (Survey of India outline, CC BY 2.5 IN), simplified to a 75 KB outline by `scripts/build_india_maps.py`. The same derivation (`docs/india-maps.js`) runs on the static site and in `scripts/export_catalog.mjs`, so both sites show the same maps.
- **Art:** 26 new retro map scenes, one for the group and one per source group, with spinning sunbursts, ripples and drifting waves. All motion stops under reduced-motion settings.
- **Display themes:** Light, Dark, Newspaper and Pamphlet, chosen from a segmented switch in the top-right corner of the static site, the React app and the Django pages. The choice is shared across all three. Charts and maps change colour with the theme, and background artwork stays visible in every theme.
- **Contact:** LinkedIn and GitHub buttons next to the theme switch.
- **Fix:** repairs double-encoded characters ("Â·", "â€º") on the published static pages and adds a regression test for them.
- **Tests:** 250 Python tests (new map, name-parity and encoding suites), 117 Django tests and 85 frontend tests.

Previous: [Water, Logistics, expanded air and rail data, interactive charts](./31-aeb4153-water-logistics-and-interactive-charts.md)
