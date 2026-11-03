# Air Travel & Indian Railways - Artwork & Design Guide

## Overview

This document outlines the artwork and visual design specifications for two new major sections in the India's Journey dashboard: **Air Travel & Civil Aviation** and **Indian Railways**.

Both sections follow the established design patterns in the dashboard while incorporating India-specific imagery and official branding elements.

---

## Section 1: Air Travel & Civil Aviation

### Main Group Artwork
**File:** `air-travel.svg`
**Theme:** India's aviation connectivity and flight network
**Design Elements:**
- **Central Icon:** Stylized aircraft silhouette in flight (ascending/climbing angle)
- **Color Palette:** Saffron (#ff9933) as primary accent with sky blue (#58a6ff)
- **Background:** Simplified outline map of India showing major aviation hubs (Delhi, Mumbai, Bangalore, Hyderabad, Chennai)
- **Symbolism:**
  - Commercial jet representing civil aviation growth
  - Network nodes at major airports (connected with lines showing air routes)
  - Rising arrow/trajectory suggesting growth in passenger numbers
  - Stack of flight route lines showing multiple corridors

**Dimensions:** 256x256px (scalable SVG)
**Style:** Minimalist, flat design consistent with existing dashboard artwork

### Subgroups Artwork

#### 1. Passenger Traffic & Market Growth
**File:** `air-passengers-growth.svg`
**Design:** 
- Silhouettes of diverse passengers boarding an aircraft
- Multiple passengers representing volume and growth
- Upward trajectory in background
- Color: #58a6ff (sky blue)

#### 2. Air Cargo & Exports
**File:** `air-cargo-freight.svg`
**Design:**
- Cargo containers and packages
- Aircraft in profile showing cargo door
- High-value goods (pharmaceuticals, electronics symbols)
- Color: #ff7b72 (cargo red)

#### 3. Domestic Aviation
**File:** `air-domestic-routes.svg`
**Design:**
- India map with connecting lines between major metros (Mumbai, Delhi, Bangalore, Hyderabad, Kolkata, Chennai)
- Domestic flight symbol (smaller than international aircraft)
- Regional distribution patterns
- Color: #ff9933 (saffron)

#### 4. International Aviation
**File:** `air-international-routes.svg`
**Design:**
- Globe/Earth showing India's position
- International flight routes connecting to major global hubs (Dubai, Singapore, London, USA, Europe)
- Larger aircraft symbol
- Color: #3fb950 (emerald)

#### 5. Airport Infrastructure & Capacity
**File:** `airport-infrastructure.svg`
**Design:**
- Airport terminal building with multiple gates
- Runway capacity visualization
- Passenger throughput indicators (moving people symbols)
- Color: #bc8cff (purple)

---

## Section 2: Indian Railways

### Main Group Artwork
**File:** `indian-railways.svg`
**Theme:** India's vast rail network and heritage connectivity
**Design Elements:**
- **Central Icon:** Stylized locomotive (front view, heritage + modern blend)
- **Color Palette:** Dark teal (#39c5bb) with saffron (#ff9933) accent rails
- **Background:** Simplified India railway network map showing:
  - Major rail corridors
  - North-South and East-West connectivity
  - Regional railway zones indicated by subtle color coding
- **Symbolism:**
  - Locomotive representing India's rail transport backbone
  - Rail tracks extending across the nation
  - Multiple train lines showing network density
  - Historical and modern elements combined (heritage steam + modern electric locomotive)
  - Passengers visible (human element - social transport)

**Dimensions:** 256x256px (scalable SVG)
**Style:** Minimalist, flat design consistent with existing dashboard artwork

### Subgroups Artwork

#### 1. Network & Infrastructure
**File:** `railways-network-infrastructure.svg`
**Design:**
- Railway tracks and network lines
- Electrification progress shown as glowing overhead lines
- Multiple gauge types (broad gauge as primary line)
- Station symbols distributed across network
- Color: #ff9933 (saffron)

#### 2. Passenger Services
**File:** `railways-passengers-services.svg`
**Design:**
- Crowded suburban train with passengers hanging from doors (representing Mumbai local train culture)
- Mix of passenger classes (general, sleeper, AC coaches shown as different carriage types)
- Stations and platforms
- Color: #58a6ff (sky blue)

#### 3. Freight & Cargo Operations
**File:** `railways-freight-cargo.svg`
**Design:**
- Goods trains with open wagons carrying coal/ore
- Freight symbols (coal, iron ore, containers)
- Industrial backdrop (factories, ports)
- Container trains and modern boxcars
- Color: #3fb950 (emerald)

#### 4. Fleet & Locomotives
**File:** `railways-fleet-locomotives.svg`
**Design:**
- Variety of locomotives (electric, diesel, modern electric)
- Coaches (LHB modern coaches vs traditional ICF)
- Vande Bharat semi-high-speed train prominently featured
- Fleet comparison showing old and new
- Color: #ff7b72 (red/maroon - heritage railway color)

#### 5. Financial Performance
**File:** `railways-financial-performance.svg`
**Design:**
- Revenue streams visualization (freight, passengers, ancillary)
- Railway budget expansion (upward bar chart)
- Infrastructure capex symbol (construction crane, new lines)
- Currency/finance symbols
- Color: #f6c344 (gold)

#### 6. Safety & Quality
**File:** `railways-safety-quality.svg`
**Design:**
- Grade separation (bridge over level crossing, no collision)
- Safety helmet and checkmark
- Train on elevated line crossing road
- CCTV camera symbolizing surveillance
- Modern signalling tower
- Color: #e3b341 (safety orange-gold)

#### 7. Regional Networks & Development
**File:** `railways-regional-networks.svg`
**Design:**
- India map divided into regional zones (Northern, Southern, Eastern, Western, Central, etc.)
- Color-coded regions showing zone diversity
- Major city connectivity (regional hubs highlighted)
- New line projects indicated (dotted or highlighted routes)
- Color: #39c5bb (teal - showing geographic breadth)

---

## Design Specifications for All Artwork

### Technical Requirements
1. **Format:** SVG (Scalable Vector Graphics)
2. **Color Mode:** RGB or HSL (no CMYK)
3. **Resolution:** Designed for 256x256px display, scalable to any size
4. **File Size:** <50 KB per SVG

### Style Guidelines
1. **Consistency:**
   - Follow the existing dashboard's flat, minimalist design language
   - Use the official India tri-color as accents (Saffron #ff9933, White #ffffff, Green #3fb950)
   - Maintain visual hierarchy with primary and secondary elements

2. **Color Coding:**
   - Use color psychology for different sectors:
     - **Blue** (#58a6ff): Passenger/People focus
     - **Green** (#3fb950): Growth/Development
     - **Saffron** (#ff9933): Primary India identity
     - **Red** (#ff7b72): Energy/Cargo
     - **Purple** (#bc8cff): Infrastructure/Technology
     - **Teal** (#39c5bb): Regional/Distribution
     - **Gold** (#f6c344, #e3b341): Financial/Safety

3. **Icons and Symbols:**
   - Use simple, recognizable shapes
   - Avoid overly complex details
   - Ensure icons are understandable at small sizes (32x32px minimum)
   - Incorporate India-specific elements (e.g., ashoka chakra for railways, Indian geography)

4. **Typography:**
   - Avoid embedding text; let titles come from metadata
   - If needed, use clean sans-serif fonts (Helvetica, Inter, system fonts)

### Accessibility
1. **Color Contrast:** Ensure all icons have sufficient contrast (WCAG AA standard: 4.5:1 for text, 3:1 for graphics)
2. **Clarity:** Icons should be meaningful to colorblind users (not color-dependent alone)
3. **Simplicity:** Avoid overly intricate patterns that may cause visual confusion

---

## Integration with Dashboard

### Catalog Entry Format
Both new groups will appear in the dashboard catalog (`data/catalog.json`) with:

```json
{
  "name": "Indian Railways",
  "order": 22,
  "title": "🚂 Indian Railways | World's 2nd Largest by Passengers",
  "description": "Rail transport network, passengers, freight operations, fleet modernization, financial performance, safety standards, and regional connectivity.",
  "badges": ["World's 2nd Largest by Passengers", "Infrastructure & Freight Backbone"],
  "art": "indian-railways.svg",
  "subgroups": [...]
}
```

### Artwork File Locations
- All SVG files should be placed in: `docs/assets/` or `frontend/public/assets/`
- Alternative theme variants (dark mode, high contrast) can be in subdirectories

### Display Context
- **Hero Banner:** Main artwork displayed prominently on group tile (200x200px)
- **Subgroup Icons:** Smaller variants or thematic icons (96x96px) for each subgroup
- **Favicon/Logo:** Simplified version (32x32px) for browser tabs and shortcuts

---

## Reference Images & Inspiration

### Air Travel
- Inspiration: Global aviation hubs (Singapore Changi, Dubai, Amsterdam), India's major airport designs
- Reference: DGCA logos, Ministry of Civil Aviation branding, airline liveries (IndiGo, Air India)
- Imagery: Aircraft silhouettes, flight paths, airport terminals, cargo containers

### Indian Railways
- Inspiration: Indian Railways heritage logos, regional zone emblems, heritage train designs
- Reference: BR classification locos (WAG-7, WAP-5), Vande Bharat design, British-era railway infrastructure
- Imagery: Locomotives (steam, diesel, electric), tracks, level crossings, stations, signals, regional maps

---

## Notes for Design Team

1. **Consistency with Existing Artwork:** Review existing subgroup icons in `docs/assets/` to match the established visual language (e.g., `macro-skyline.svg`, `factory-floor.svg`, `stock-market.svg`)

2. **Responsive Design:** Ensure artwork looks clear when scaled down to 64x64px and up to 512x512px

3. **Branding Elements:** 
   - Indian Railways can incorporate the official Railway Board logo as an Easter egg or corner accent
   - Air Travel can feature the Airports Authority of India (AAI) emblem

4. **Cultural Sensitivity:** 
   - Use inclusive imagery (diverse passengers, workers)
   - Avoid stereotypes; focus on modernity and progress
   - Incorporate Indic script elements subtly if culturally appropriate

5. **Dark Mode Support:** Ensure SVG artwork has appropriate fill colors that work on both light and dark backgrounds
   - Consider providing `<style>` tags in SVG for dynamic color switching
   - Or provide separate light/dark variants

---

## Delivery Checklist

- [ ] Main group artwork (2 files): `air-travel.svg`, `indian-railways.svg`
- [ ] Subgroup artwork (13 files total):
  - [ ] Air Travel: 5 subgroup icons
  - [ ] Indian Railways: 7 subgroup icons
- [ ] Dark mode variants (optional but recommended): 15 files
- [ ] High-contrast variants (optional): 15 files
- [ ] SVG optimization (minify without breaking): all files <50 KB each
- [ ] Accessibility audit: color contrast, clarity at small sizes
- [ ] Integration testing: verify icons render correctly in catalog view
- [ ] Documentation: this design guide

---

## File Naming Convention

```
{section}-{subgroup-or-feature}.svg

Examples:
- air-travel.svg (main group)
- air-passengers-growth.svg (subgroup)
- air-cargo-freight.svg (subgroup)
- indian-railways.svg (main group)
- railways-network-infrastructure.svg (subgroup)
- railways-passengers-services.svg (subgroup)
```

---

## Approval & Versioning

**Version:** 1.0 (Initial Design Specification)
**Date:** November 3, 2026
**Status:** Ready for Implementation
**Review:** To be completed by design team and integrated into main dashboard branch
