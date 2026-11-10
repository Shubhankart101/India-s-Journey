# India in Maps

State and Union Territory choropleths are rendered by the shared React application in both Django and static builds (`frontend/src/components/IndiaMap.jsx` and `IndiaMap.css`). The map data and supporting geographic assets are served from the same generated catalogue and public assets in either mode.

## Where maps come from

Every dashboard series with State/UT values can be rendered as a map; derived maps are calculated from dashboard series and identify their source indicators. Lower-court NJDG series with annual observations support period selection. The map layer does not fetch a separate external data source.

## Interactions and themes

Maps support hover details, keyboard navigation, ranked lists, search, period selection and shareable state. Colours use shared theme tokens, so all ten display modes apply in both Django and static builds. The [home page](../README.md#explore-live) also features a compact India map; its asset path is built from the app base URL so it works on GitHub Pages.

## Artwork

The map builder writes artwork to `frontend/public/art/`; Vite copies those assets into the static `docs/` build. Rebuild the static site with `npm.cmd --prefix frontend run build:static` after updating source data or artwork. See [Architecture](ARCHITECTURE.md), [Pipelines](PIPELINES.md) and [Deployment](DEPLOYMENT.md) for the shared build and hosting flow.