# Release 41: Authentic Organic City Cartography Across All 16 Cities, De-Cluttered Journey Planner, and Widescreen Maximize Map Mode

## Executive Summary
This release resolves the visual box boundary artifacts, eliminates screen clutter on the cartographic metro atlas, expands the map canvas width, and brings authentic organic city-level cartography (waterways, rivers, arterial highways, ring roads, and Indian Railways trunks) to all 16 Indian metro cities, perfectly matching the high standard of Delhi NCR.

---

## Key Enhancements Delivered

### 1. Authentic Organic City Cartography for All 16 Cities (ODbL Vectors)
- **Eliminated Artificial Box Boundaries**: Removed the 4-point trapezoid municipal bounding box outline (`base.bd`) that previously gave non-Delhi cities an artificial geometric container appearance.
- **Organic Waterways & Shorelines**:
  - **Mumbai & Navi Mumbai**: Arabian Sea West Coast, Thane Creek, Mithi River, Mahim Bay, Powai & Tulsi Lakes, Panvel Creek, Kasadi River.
  - **Kolkata**: Meandering Hooghly River, East Kolkata Wetlands, Rabindra Sarobar, Subhas Sarobar.
  - **Bengaluru**: Ulsoor Lake, Sankey Tank, Bellandur Lake, Varthur Lake, Hebbal Lake, Madivala Lake, Agara Lake.
  - **Chennai**: Marina / Bay of Bengal Coastline, Cooum River, Adyar River, Buckingham Canal.
  - **Hyderabad**: Musi River, Hussain Sagar Lake, Osman Sagar, Himayat Sagar.
  - **Ahmedabad & Surat**: Sabarmati Riverfront, Tapi River, Dumas & Hazira Coastline, Gopi Talav.
  - **Pune & Kochi**: Mula-Mutha Confluence, Khadakwasla, Vembanad Backwaters, Periyar River, Kochi Port / Arabian Sea Harbour.
  - **Lucknow, Kanpur & Agra**: Gomti River loops, Ganga River waterfront at Kanpur, Yamuna River meandering around Taj Mahal and Agra Fort.
  - **Jaipur, Bhopal & Nagpur**: Jal Mahal Mansagar Lake, Dravyavati River, Bhopal Bhojtal (Upper Lake) & Lower Lake, Kahn River Indore, Nag River & Ambazari Lake.
- **Arterial Highway Blueprints**: Real ring roads, bypasses, expressways, and radials (Western Express Highway, Eastern Freeway, Outer Ring Roads, AB Road, VIP Roads).
- **Indian Railways Mainlines**: Western Railway, Central Railway, Southern Railway, Northern Railway, and Eastern Railway trunks grounding transit geography.

### 2. De-Cluttered Station Nodes & Outer Rings
- **Dynamic Zoom-Responsive Radii**: When viewing the whole network (`z < 1,200,000`), station node radii scale down smoothly from $4.8\text{px}$ to $2.0\text{px}$–$2.6\text{px}$ with a hairline $0.9\text{px}$ border.
- **Smart Interchange Rings**: Outer interchange rings are conditionally suppressed during wide-angle whole network view so dense downtown clusters (e.g. Connaught Place / Central Secretariat in Delhi) remain crisp and legible without turning into clotted black blobs. Outer rings cleanly emerge when zooming in or when hovering/selecting.
- **Strict Zero-Clutter Default**: Station names remain strictly hidden by default and appear exclusively upon hover, scroll, or station selection.

### 3. Streamlined "Plan a Journey" Card
- **Reduced Width & Visual Weight**: Shrunk the journey card from 320px down to 248px (~25% width reduction), with compact padding (8px–10px), condensed select inputs, and streamlined metric pills.
- **Zero-Overlap Tiered Layout**:
  - **Row 1 (`top: 12px`)**: Mode toggle (`Cartographic Terrain` / `Line Diagram`) and `⛶ Maximize Map` button.
  - **Row 2 (`top: 56px`)**: Layer filter pills on the left (`Whole Network`, `--- Under Construction`, `All Lines`) and Zoom controls on the right (`+ Zoom In`, `− Zoom Out`, `↺ Fit View`).
  - **Row 3 (`top: 96px`)**: Compact Journey Planner neatly docked along the right margin.
- **Collapsible Badge**: One-click minimize button (`−` / `+`) allows commuters to tuck the card into a sleek floating badge (`[ 🧭 PLAN A JOURNEY › ]`), granting 100% unobstructed view of the network.

### 4. Widescreen Map Container & Maximize Toggle
- **Wider Default Ratio**: Increased `.metro-workbench-grid` from `1.55fr / 1fr` to `2.2fr / 1fr`, dedicating ~70% of standard desktop width to the map.
- **1-Click Full Width Toggle (`⛶ Maximize Map`)**: Clicking the button toggles `.full-map-layout`, instantly expanding the map to a panoramic 100% full-width view with the station inspector and dossier gracefully wrapping underneath.

---

## Verification & Test Results
- **Frontend Vitest Suite**: 19 test files, 141 tests passing (100% pass rate).
- **Python Unit Test Suite**: 100 tests passing (100% pass rate).
- **Django Integration Suite**: 117 tests passing (100% pass rate).
- **Static Site Build**: Succeeded in 906ms (`docs/index.html` and assets generated).
