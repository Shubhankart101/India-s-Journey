#!/usr/bin/env python3
"""
Generate bespoke animated vector SVGs for all subgroups and new groups.
Places generated SVGs in both frontend/public/art/ and docs/art/.
"""

import os

SVG_DEFS = {
    "ancient-empires.svg": {
        "title": "Ancient Empires of India",
        "subtitle": "600 BCE – 850 CE • SUBREGIONAL HEGEMONY",
        "sky1": "#2c1810", "sky2": "#8c481e", "accent": "#facc15",
        "shapes": """
        <!-- Ancient Citadel & Ashoka Pillar Silhouette -->
        <g transform="translate(600, 360)">
          <!-- Grand Ashoka Pillar -->
          <rect x="-12" y="-180" width="24" height="260" rx="3" fill="#e2d8be"/>
          <path d="M -24 -180 L 24 -180 L 16 -195 L -16 -195 Z" fill="#d4a72c"/>
          <!-- Lion Capital -->
          <circle cx="0" cy="-210" r="18" fill="#d4a72c"/>
          <path d="M -8 -200 Q -18 -215 0 -228 Q 18 -215 8 -200 Z" fill="#facc15"/>
          <!-- 24-spoke Ashoka Chakra wheel -->
          <circle cx="0" cy="-160" r="16" fill="none" stroke="#1d4ed8" stroke-width="2.5" class="rot-slow"/>
          <!-- Fortified Mauryan / Gupta battlements -->
          <path d="M -350 80 L -350 -40 L -310 -40 L -310 -20 L -270 -20 L -270 -40 L -230 -40 L -230 80 Z" fill="#3a1e14" opacity="0.8"/>
          <path d="M 230 80 L 230 -40 L 270 -40 L 270 -20 L 310 -20 L 310 -40 L 350 -40 L 350 80 Z" fill="#3a1e14" opacity="0.8"/>
        </g>
        """
    },
    "mahajanapadas.svg": {
        "title": "16 Mahajanapadas & Republics",
        "subtitle": "SECOND URBANISATION • 600 BCE",
        "sky1": "#1e1b4b", "sky2": "#6366f1", "accent": "#eab308",
        "shapes": """
        <!-- Ancient Mudbrick Walls of Rajagriha / Vaishali Assembly -->
        <g transform="translate(600, 380)">
          <!-- Cyclopean Wall of Rajgir -->
          <path d="M -450 60 Q -200 -20 0 10 Q 250 -30 450 60 L 450 140 L -450 140 Z" fill="#2e1065"/>
          <!-- Democratic Santhagara Assembly Hall -->
          <polygon points="-80,-40 0,-100 80,-40" fill="#eab308" opacity="0.9"/>
          <rect x="-70" y="-40" width="140" height="80" fill="#4338ca"/>
          <!-- Pillars of Assembly -->
          <rect x="-55" y="-30" width="10" height="70" fill="#e0e7ff"/>
          <rect x="-20" y="-30" width="10" height="70" fill="#e0e7ff"/>
          <rect x="15" y="-30" width="10" height="70" fill="#e0e7ff"/>
          <rect x="50" y="-30" width="10" height="70" fill="#e0e7ff"/>
        </g>
        """
    },
    "magadha-nanda.svg": {
        "title": "Magadha Empire & The Nandas",
        "subtitle": "EKACHHATRA UNIFICATION • 544–322 BCE",
        "sky1": "#2e1065", "sky2": "#b45309", "accent": "#fbbf24",
        "shapes": """
        <!-- Imperial War Elephants & Pataliputra Citadel -->
        <g transform="translate(600, 370)">
          <!-- Elephant silhouette with golden howdah -->
          <circle cx="0" cy="-20" r="65" fill="#1e1b4b"/>
          <circle cx="-55" cy="-45" r="40" fill="#1e1b4b"/>
          <!-- Trunk -->
          <path d="M -85 -45 Q -110 -20 -95 10 Q -90 15 -85 5 Q -95 -10 -75 -25 Z" fill="#1e1b4b"/>
          <!-- Tusks -->
          <path d="M -70 -25 Q -95 -20 -90 -40 Q -85 -30 -65 -25 Z" fill="#fef08a"/>
          <!-- Legs -->
          <rect x="-45" y="25" width="22" height="65" rx="4" fill="#1e1b4b"/>
          <rect x="-10" y="25" width="22" height="65" rx="4" fill="#1e1b4b"/>
          <rect x="25" y="25" width="22" height="65" rx="4" fill="#1e1b4b"/>
          <!-- Royal Howdah & Chhatra (Imperial Umbrella) -->
          <rect x="-25" y="-75" width="50" height="35" rx="4" fill="#f59e0b"/>
          <path d="M -40 -105 Q 0 -135 40 -105 Z" fill="#facc15"/>
          <line x1="0" y1="-105" x2="0" y2="-75" stroke="#facc15" stroke-width="3"/>
        </g>
        """
    },
    "alexander-campaign.svg": {
        "title": "Alexander's Campaign & Hydaspes",
        "subtitle": "MACEDONIAN LIMITS • 327–325 BCE",
        "sky1": "#082f49", "sky2": "#0284c7", "accent": "#38bdf8",
        "shapes": """
        <!-- Greek Phalanx Sarissas & Macedonian Helmet over the Jhelum -->
        <g transform="translate(600, 360)">
          <!-- Corinthian / Boeotian helmet crest -->
          <path d="M -40 -30 Q 0 -100 40 -30 Q 30 20 -40 -30 Z" fill="#38bdf8" opacity="0.9"/>
          <path d="M -30 -115 Q 0 -145 30 -115 L 25 -95 Q 0 -125 -25 -95 Z" fill="#ef4444"/>
          <!-- Slanted 18-foot Sarissa pikes -->
          <line x1="-300" y1="120" x2="100" y2="-180" stroke="#94a3b8" stroke-width="3" opacity="0.7"/>
          <line x1="-280" y1="130" x2="120" y2="-170" stroke="#94a3b8" stroke-width="3" opacity="0.7"/>
          <line x1="-260" y1="140" x2="140" y2="-160" stroke="#94a3b8" stroke-width="3" opacity="0.7"/>
          <!-- River Waves of Hydaspes -->
          <path d="M -500 120 Q -250 80 0 120 Q 250 160 500 120 L 500 180 L -500 180 Z" fill="#0369a1" opacity="0.6"/>
        </g>
        """
    },
    "maurya-empire.svg": {
        "title": "Mauryan Pan-Indian Empire",
        "subtitle": "ASHOKA & DHAMMAVIJAYA • 322–185 BCE",
        "sky1": "#3b0764", "sky2": "#86198f", "accent": "#facc15",
        "shapes": """
        <!-- Sanchi Stupa Gateway (Torana) & Ashoka Edicts -->
        <g transform="translate(600, 370)">
          <!-- Great Stupa Dome -->
          <path d="M -160 80 A 160 160 0 0 1 160 80 Z" fill="#581c87"/>
          <!-- Harmika & Chhatravali umbrella spire -->
          <rect x="-24" y="-95" width="48" height="20" fill="#a855f7"/>
          <circle cx="0" cy="-125" r="30" fill="#facc15" opacity="0.8"/>
          <circle cx="0" cy="-145" r="22" fill="#facc15" opacity="0.9"/>
          <circle cx="0" cy="-160" r="14" fill="#fde047"/>
          <!-- Ornate Torana Gateway -->
          <rect x="-190" y="-40" width="16" height="130" fill="#facc15"/>
          <rect x="174" y="-40" width="16" height="130" fill="#facc15"/>
          <rect x="-210" y="-30" width="420" height="12" rx="4" fill="#fde047"/>
          <rect x="-200" y="-12" width="400" height="10" rx="4" fill="#fde047"/>
        </g>
        """
    },
    "indo-greek.svg": {
        "title": "Indo-Greek & Shunga Dynasties",
        "subtitle": "MILINDA & HELIODORUS PILLAR • 185 BCE–10 CE",
        "sky1": "#0c4a6e", "sky2": "#0284c7", "accent": "#38bdf8",
        "shapes": """
        <!-- Heliodorus Garuda Pillar with Greek Coin Medallion -->
        <g transform="translate(600, 360)">
          <!-- Fluted Octagonal Heliodorus Pillar -->
          <rect x="-14" y="-140" width="28" height="230" fill="#bae6fd"/>
          <polygon points="-24,-140 24,-140 18,-155 -18,-155" fill="#38bdf8"/>
          <!-- Garuda Capital -->
          <circle cx="0" cy="-175" r="16" fill="#38bdf8"/>
          <!-- Bilingual Greek-Brahmi Coin Silhouette -->
          <circle cx="220" cy="-60" r="60" fill="none" stroke="#facc15" stroke-width="4"/>
          <circle cx="220" cy="-60" r="54" fill="#075985"/>
          <text x="220" y="-55" fill="#fef08a" font-size="12" font-family="sans-serif" font-weight="800" text-anchor="middle">ΒΑΣΙΛΕΩΣ</text>
          <text x="220" y="-35" fill="#fef08a" font-size="12" font-family="sans-serif" font-weight="800" text-anchor="middle">ΜΕΝΑΝΔΡΟΥ</text>
        </g>
        """
    },
    "satavahana-empire.svg": {
        "title": "Satavahana Deccan Empire",
        "subtitle": "TRI-SAMUDRA-TOYA • 2ND C. BCE–220 CE",
        "sky1": "#064e3b", "sky2": "#059669", "accent": "#34d399",
        "shapes": """
        <!-- Two-Masted Satavahana Ocean Vessel & Amaravati Relief -->
        <g transform="translate(600, 370)">
          <!-- Ship Hull with Anchor -->
          <path d="M -180 30 Q -100 80 0 80 Q 100 80 180 30 L 150 0 L -150 0 Z" fill="#047857"/>
          <!-- Two Masts & Rigging -->
          <line x1="-60" y1="0" x2="-60" y2="-130" stroke="#fef08a" stroke-width="4"/>
          <line x1="60" y1="0" x2="60" y2="-130" stroke="#fef08a" stroke-width="4"/>
          <!-- Billowing Square Sails -->
          <rect x="-105" y="-115" width="90" height="70" rx="4" fill="#a7f3d0" opacity="0.85"/>
          <rect x="15" y="-115" width="90" height="70" rx="4" fill="#a7f3d0" opacity="0.85"/>
          <!-- Rolling ocean waves -->
          <path d="M -450 70 Q -250 40 0 70 Q 250 100 450 70 L 450 140 L -450 140 Z" fill="#065f46"/>
        </g>
        """
    },
    "kushan-empire.svg": {
        "title": "Kushan Silk Road Empire",
        "subtitle": "KANISHKA & GANDHARA • 30–375 CE",
        "sky1": "#450a0a", "sky2": "#b91c1c", "accent": "#f87171",
        "shapes": """
        <!-- Gandhara Standing Buddha & Kanishka Casket Spire -->
        <g transform="translate(600, 360)">
          <!-- Halo & Meditating Buddha silhouette -->
          <circle cx="0" cy="-70" r="95" fill="none" stroke="#fca5a5" stroke-width="3" opacity="0.7"/>
          <circle cx="0" cy="-70" r="88" fill="#7f1d1d" opacity="0.6"/>
          <circle cx="0" cy="-90" r="28" fill="#fecaca"/>
          <path d="M -45 50 Q -35 -40 0 -50 Q 35 -40 45 50 Z" fill="#991b1b"/>
          <!-- Silk Road Mountain Passes (Hindu Kush) -->
          <polygon points="-450,120 -280,-40 -120,120" fill="#262626" opacity="0.9"/>
          <polygon points="120,120 280,-40 450,120" fill="#262626" opacity="0.9"/>
        </g>
        """
    },
    "gupta-empire.svg": {
        "title": "Gupta Empire: Classical Golden Age",
        "subtitle": "SAMUDRAGUPTA & VIKRAMADITYA • 319–550 CE",
        "sky1": "#422006", "sky2": "#ca8a04", "accent": "#facc15",
        "shapes": """
        <!-- Golden Dinara Coin, Iron Pillar & Temple Shikhara -->
        <g transform="translate(600, 360)">
          <!-- Iron Pillar of Delhi (Mehrauli) -->
          <rect x="-10" y="-170" width="20" height="250" rx="3" fill="#3f3f46"/>
          <polygon points="-18,-170 18,-170 12,-185 -12,-185" fill="#71717a"/>
          <!-- Classical Nagara Shikhara Temple (Deogarh Dashavatara) -->
          <path d="M -220 80 L -220 -30 Q -180 -120 -150 -140 Q -120 -120 -80 -30 L -80 80 Z" fill="#854d0e"/>
          <circle cx="-150" cy="-145" r="8" fill="#facc15"/>
          <!-- Gold Coin (Archer Type of Chandragupta II) -->
          <circle cx="170" cy="-50" r="65" fill="#facc15" stroke="#ca8a04" stroke-width="4"/>
          <circle cx="170" cy="-50" r="58" fill="#eab308"/>
          <circle cx="170" cy="-50" r="14" fill="#a16207"/>
        </g>
        """
    },
    "harsha-empire.svg": {
        "title": "Vardhana Empire of Harsha",
        "subtitle": "KANNAUJ CONGREGATION • 606–647 CE",
        "sky1": "#431407", "sky2": "#ea580c", "accent": "#fb923c",
        "shapes": """
        <!-- Grand Kannauj Assembly Pavilion & Xuanzang's Manuscripts -->
        <g transform="translate(600, 360)">
          <!-- Tiered Wooden Imperial Pavilion -->
          <polygon points="-120,-30 0,-110 120,-30" fill="#ea580c"/>
          <polygon points="-150,20 0,-40 150,20" fill="#c2410c"/>
          <rect x="-90" y="20" width="180" height="70" fill="#7c2d12"/>
          <!-- Banner Streamers -->
          <line x1="0" y1="-110" x2="0" y2="-160" stroke="#fbbf24" stroke-width="3"/>
          <polygon points="0,-160 50,-145 0,-130" fill="#facc15"/>
        </g>
        """
    },
    "southern-dynasties.svg": {
        "title": "Classical Southern Dynasties",
        "subtitle": "CHOLA, CHERA, PANDYA & PALLAVA • 300 BCE–850 CE",
        "sky1": "#134e4a", "sky2": "#0d9488", "accent": "#2dd4bf",
        "shapes": """
        <!-- Shore Temple of Mamallapuram & Chola Tiger Flag -->
        <g transform="translate(600, 360)">
          <!-- Shore Temple Vimana Pyramid -->
          <polygon points="-60,-120 0,-160 60,-120" fill="#2dd4bf"/>
          <rect x="-70" y="-120" width="140" height="50" fill="#0f766e"/>
          <rect x="-90" y="-70" width="180" height="60" fill="#115e59"/>
          <rect x="-110" y="-10" width="220" height="80" fill="#134e4a"/>
          <!-- Ocean Breakers of the Coromandel Coast -->
          <path d="M -450 80 Q -200 40 0 80 Q 200 120 450 80 L 450 150 L -450 150 Z" fill="#042f2e"/>
        </g>
        """
    },
    "ivc-excavations.svg": {
        "title": "Indus Valley Excavation Atlas",
        "subtitle": "49 CATALOGED SITES • 3300–1300 BCE",
        "sky1": "#1c1917", "sky2": "#78350f", "accent": "#f59e0b",
        "shapes": """
        <!-- Great Bath of Mohenjo-daro & Citadel Wall -->
        <g transform="translate(600, 370)">
          <!-- Brick Citadel Mound -->
          <path d="M -300 80 L -250 -20 L 250 -20 L 300 80 Z" fill="#451a03"/>
          <!-- Great Bath basin steps -->
          <rect x="-140" y="-10" width="280" height="70" fill="#0c4a6e" stroke="#b45309" stroke-width="6"/>
          <rect x="-110" y="5" width="220" height="40" fill="#0284c7" opacity="0.75"/>
          <!-- Steps leading down to water -->
          <rect x="-40" y="-10" width="80" height="6" fill="#fde68a"/>
          <rect x="-30" y="-4" width="60" height="6" fill="#fde68a"/>
          <rect x="-20" y="2" width="40" height="6" fill="#fde68a"/>
        </g>
        """
    },
    "ivc-architecture.svg": {
        "title": "Indus Civil Engineering & Citadels",
        "subtitle": "DRAINAGE, GRANARIES & DOCKYARDS",
        "sky1": "#1c1917", "sky2": "#854d0e", "accent": "#facc15",
        "shapes": """
        <!-- Granary pillars & covered brick drains -->
        <g transform="translate(600, 360)">
          <!-- Baked brick granary blocks -->
          <rect x="-180" y="-50" width="70" height="100" fill="#78350f" rx="3"/>
          <rect x="-90" y="-50" width="70" height="100" fill="#78350f" rx="3"/>
          <rect x="20" y="-50" width="70" height="100" fill="#78350f" rx="3"/>
          <rect x="110" y="-50" width="70" height="100" fill="#78350f" rx="3"/>
          <!-- Covered Corbelled Arch Drain -->
          <path d="M -350 70 L 350 70 L 350 110 L -350 110 Z" fill="#292524"/>
          <path d="M -40 70 L 0 40 L 40 70 Z" fill="#b45309"/>
        </g>
        """
    },
    "savings-investment.svg": {
        "title": "Savings, Investment & Media",
        "subtitle": "CAPITAL FORMATION & HOUSEHOLD ASSETS",
        "sky1": "#064e3b", "sky2": "#047857", "accent": "#34d399",
        "shapes": """
        <!-- Investment growth chart & mutual fund vault -->
        <g transform="translate(600, 360)">
          <!-- Glowing upward trajectory curve -->
          <path d="M -300 80 Q -100 40 0 -30 T 300 -120" fill="none" stroke="#34d399" stroke-width="5" class="draw" pathLength="1000"/>
          <circle cx="300" cy="-120" r="10" fill="#facc15" class="ping"/>
          <!-- Rupee symbol medallion -->
          <circle cx="-160" cy="-40" r="50" fill="#065f46" stroke="#34d399" stroke-width="3"/>
          <text x="-160" y="-20" fill="#fef08a" font-size="52" font-family="sans-serif" font-weight="900" text-anchor="middle">₹</text>
        </g>
        """
    },
    "union-receipts.svg": {
        "title": "Union Budget & Receipts",
        "subtitle": "TAXATION, CAPITAL & FISCAL DEFICIT",
        "sky1": "#1e1b4b", "sky2": "#4338ca", "accent": "#a5b4fc",
        "shapes": """
        <!-- Parliament North Block & Budget Ledger -->
        <g transform="translate(600, 360)">
          <!-- North Block Sandstone Arcade -->
          <rect x="-240" y="-30" width="480" height="90" fill="#312e81" rx="4"/>
          <path d="M -60 -30 Q 0 -110 60 -30 Z" fill="#e0e7ff"/>
          <!-- Pillars -->
          <rect x="-180" y="-10" width="14" height="70" fill="#c7d2fe"/>
          <rect x="-120" y="-10" width="14" height="70" fill="#c7d2fe"/>
          <rect x="106" y="-10" width="14" height="70" fill="#c7d2fe"/>
          <rect x="166" y="-10" width="14" height="70" fill="#c7d2fe"/>
        </g>
        """
    },
    "borrowing-debt.svg": {
        "title": "How India Borrows & Debt",
        "subtitle": "SOVEREIGN BONDS & FISCAL DISCIPLINE",
        "sky1": "#18181b", "sky2": "#3f3f46", "accent": "#fbbf24",
        "shapes": """
        <!-- Sovereign Bond & Reserve Bank Vault -->
        <g transform="translate(600, 360)">
          <!-- Vault Door -->
          <circle cx="0" cy="0" r="90" fill="#27272a" stroke="#fbbf24" stroke-width="4"/>
          <circle cx="0" cy="0" r="70" fill="#18181b" stroke="#71717a" stroke-width="2"/>
          <circle cx="0" cy="0" r="25" fill="#fbbf24" class="rot"/>
        </g>
        """
    },
    "state-fiscal-welfare.svg": {
        "title": "State Fiscal Explorer & Welfare",
        "subtitle": "DIRECT BENEFIT TRANSFER & SOCIAL SPEND",
        "sky1": "#0c4a6e", "sky2": "#0284c7", "accent": "#38bdf8",
        "shapes": """
        <!-- DBT Network & State Welfare Map -->
        <g transform="translate(600, 360)">
          <!-- India map outline wireframe -->
          <path d="M -100 -90 L 0 -130 L 70 -80 L 50 40 L 0 90 L -50 30 Z" fill="none" stroke="#38bdf8" stroke-width="3" stroke-dasharray="4,4"/>
          <!-- Radiating digital welfare pulses -->
          <circle cx="0" cy="-20" r="30" fill="none" stroke="#facc15" stroke-width="2" class="ping"/>
        </g>
        """
    },
    "hockey-india.svg": {
        "title": "Indian Hockey: Legacy of Gold",
        "subtitle": "OLYMPIC GLORY & PRO LEAGUE",
        "sky1": "#064e3b", "sky2": "#047857", "accent": "#facc15",
        "shapes": """
        <!-- Crossed Hockey Sticks & Gold Medals -->
        <g transform="translate(600, 360)">
          <!-- Curved Hockey Stick 1 -->
          <path d="M -120 70 Q -40 20 100 -120 Q 115 -130 125 -115 Q 110 -90 60 -50 L -70 80 Q -100 100 -130 90 Q -150 70 -120 70 Z" fill="#facc15"/>
          <!-- Curved Hockey Stick 2 -->
          <path d="M 120 70 Q 40 20 -100 -120 Q -115 -130 -125 -115 Q -110 -90 -60 -50 L 70 80 Q 100 100 130 90 Q 150 70 120 70 Z" fill="#fbbf24"/>
          <!-- Ball -->
          <circle cx="0" cy="75" r="14" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        </g>
        """
    },
    "football-india.svg": {
        "title": "Indian Football & Leagues",
        "subtitle": "ISL, I-LEAGUE & ASIAN CHALLENGES",
        "sky1": "#1e1b4b", "sky2": "#312e81", "accent": "#38bdf8",
        "shapes": """
        <!-- Football Goalnet & Geodesic Soccer Ball -->
        <g transform="translate(600, 360)">
          <!-- Goal frame -->
          <path d="M -220 80 L -220 -80 L 220 -80 L 220 80" fill="none" stroke="#ffffff" stroke-width="8"/>
          <!-- Ball in mid-air -->
          <circle cx="60" cy="-20" r="35" fill="#f8fafc" stroke="#000" stroke-width="2"/>
          <polygon points="60,-35 48,-25 52,-10 68,-10 72,-25" fill="#0f172a"/>
        </g>
        """
    },
    "supreme-civil.svg": {
        "title": "Supreme Court: Civil Docket",
        "subtitle": "CONSTITUTIONAL & APPELLATE BENCHES",
        "sky1": "#18181b", "sky2": "#27272a", "accent": "#d4a72c",
        "shapes": """
        <!-- Scales of Justice & Supreme Court Facade -->
        <g transform="translate(600, 360)">
          <!-- Supreme Court central dome -->
          <path d="M -80 -40 Q 0 -130 80 -40 Z" fill="#d4a72c" opacity="0.9"/>
          <!-- Balance Scales -->
          <line x1="-140" y1="20" x2="140" y2="20" stroke="#fef08a" stroke-width="4"/>
          <line x1="0" y1="-20" x2="0" y2="70" stroke="#fef08a" stroke-width="4"/>
          <!-- Left pan -->
          <path d="M -170 60 Q -140 80 -110 60 Z" fill="#facc15"/>
          <!-- Right pan -->
          <path d="M 110 60 Q 140 80 170 60 Z" fill="#facc15"/>
        </g>
        """
    },
    "supreme-criminal.svg": {
        "title": "Supreme Court: Criminal Appeals",
        "subtitle": "SPECIAL LEAVE & CAPITAL CASES",
        "sky1": "#3f1a1a", "sky2": "#7f1d1d", "accent": "#f87171",
        "shapes": """
        <!-- Judicial Gavel & Law Corpus -->
        <g transform="translate(600, 360)">
          <!-- Gavel handle and head -->
          <rect x="-80" y="-40" width="160" height="45" rx="6" fill="#991b1b" stroke="#fca5a5" stroke-width="3"/>
          <rect x="-10" y="5" width="20" height="90" fill="#7f1d1d"/>
          <!-- Brass striking block -->
          <rect x="-90" y="80" width="180" height="20" rx="3" fill="#facc15"/>
        </g>
        """
    },
    "metro-atlas.svg": {
        "title": "Indian Metro Networks & Transit Atlas",
        "subtitle": "17 CITIES • 1,042 KM ACTIVE TRANSIT • DIJKSTRA ROUTING",
        "sky1": "#0a1128", "sky2": "#1e1b4b", "accent": "#38bdf8",
        "shapes": """
        <!-- Distant City Skyline Silhouettes with Twinkling Windows -->
        <g opacity="0.35">
          <rect x="80" y="160" width="48" height="200" fill="#0f172a"/>
          <rect x="140" y="120" width="60" height="240" fill="#1e1b4b"/>
          <line x1="170" y1="70" x2="170" y2="120" stroke="#38bdf8" stroke-width="2"/>
          <circle cx="170" cy="70" r="3" fill="#ef4444" class="tw"/>
          <rect x="220" y="190" width="55" height="170" fill="#0f172a"/>
          <rect x="290" y="140" width="70" height="220" fill="#1e293b"/>
          <rect x="380" y="210" width="50" height="150" fill="#0f172a"/>
          <g fill="#fef08a" opacity="0.6" class="tw">
            <rect x="150" y="140" width="6" height="8" rx="1"/>
            <rect x="165" y="140" width="6" height="8" rx="1"/>
            <rect x="180" y="140" width="6" height="8" rx="1"/>
            <rect x="150" y="160" width="6" height="8" rx="1"/>
            <rect x="180" y="160" width="6" height="8" rx="1"/>
            <rect x="150" y="180" width="6" height="8" rx="1"/>
            <rect x="165" y="180" width="6" height="8" rx="1"/>
            <rect x="305" y="160" width="8" height="8" rx="1"/>
            <rect x="325" y="160" width="8" height="8" rx="1"/>
            <rect x="305" y="185" width="8" height="8" rx="1"/>
            <rect x="345" y="185" width="8" height="8" rx="1"/>
          </g>
          <rect x="820" y="180" width="60" height="180" fill="#0f172a"/>
          <rect x="900" y="110" width="75" height="250" fill="#1e1b4b"/>
          <line x1="937" y1="50" x2="937" y2="110" stroke="#a855f7" stroke-width="2"/>
          <circle cx="937" cy="50" r="3" fill="#ef4444" class="tw"/>
          <rect x="990" y="170" width="65" height="190" fill="#0f172a"/>
          <rect x="1070" y="130" width="55" height="230" fill="#1e293b"/>
          <g fill="#38bdf8" opacity="0.6" class="tw">
            <rect x="915" y="130" width="8" height="8" rx="1"/>
            <rect x="935" y="130" width="8" height="8" rx="1"/>
            <rect x="955" y="130" width="8" height="8" rx="1"/>
            <rect x="915" y="155" width="8" height="8" rx="1"/>
            <rect x="955" y="155" width="8" height="8" rx="1"/>
            <rect x="1005" y="190" width="6" height="6" rx="1"/>
            <rect x="1025" y="190" width="6" height="6" rx="1"/>
          </g>
        </g>

        <!-- Dynamic Glowing Metro Route Schematic Overlay -->
        <g opacity="0.6">
          <path d="M 50 180 C 250 160 400 240 650 180 S 1000 220 1150 150" fill="none" stroke="#d946ef" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 8" class="draw"/>
          <path d="M 300 50 L 300 180 L 450 290 L 450 450" fill="none" stroke="#eab308" stroke-width="4.5" stroke-linecap="round"/>
          <path d="M 80 340 L 380 340 L 580 200 L 1120 200" fill="none" stroke="#0284c7" stroke-width="4" stroke-linecap="round"/>
          <path d="M 150 120 L 500 120 L 750 320 L 1050 320" fill="none" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>

          <g transform="translate(580, 200)">
            <circle cx="0" cy="0" r="16" fill="none" stroke="#38bdf8" stroke-width="2" class="ping"/>
            <circle cx="0" cy="0" r="9" fill="#0f172a" stroke="#ffffff" stroke-width="3" class="pulse"/>
          </g>
          <g transform="translate(450, 290)">
            <circle cx="0" cy="0" r="14" fill="none" stroke="#eab308" stroke-width="2" class="ping"/>
            <circle cx="0" cy="0" r="8" fill="#0f172a" stroke="#ffffff" stroke-width="3" class="pulse"/>
          </g>
          <g transform="translate(750, 320)">
            <circle cx="0" cy="0" r="8" fill="#0f172a" stroke="#ffffff" stroke-width="2.5"/>
          </g>
          <g transform="translate(300, 180)">
            <circle cx="0" cy="0" r="8" fill="#0f172a" stroke="#ffffff" stroke-width="2.5"/>
          </g>
        </g>

        <!-- Heavy Concrete Metro Viaduct Piers & Deck -->
        <g>
          <g fill="#1e293b" stroke="#334155" stroke-width="1.5">
            <path d="M 120 280 L 140 280 L 145 440 L 115 440 Z"/>
            <polygon points="105,270 155,270 145,285 115,285" fill="#334155"/>
            <path d="M 370 280 L 390 280 L 395 440 L 365 440 Z"/>
            <polygon points="355,270 405,270 395,285 365,285" fill="#334155"/>
            <path d="M 620 280 L 640 280 L 645 440 L 615 440 Z"/>
            <polygon points="605,270 655,270 645,285 615,285" fill="#334155"/>
            <path d="M 870 280 L 890 280 L 895 440 L 865 440 Z"/>
            <polygon points="855,270 905,270 895,285 865,285" fill="#334155"/>
            <path d="M 1070 280 L 1090 280 L 1095 440 L 1065 440 Z"/>
            <polygon points="1055,270 1105,270 1095,285 1065,285" fill="#334155"/>
          </g>

          <path d="M -50 268 L 1250 268 L 1250 286 L -50 286 Z" fill="#334155"/>
          <path d="M -50 264 L 1250 264 L 1250 268 L -50 268 Z" fill="#475569"/>
          <path d="M -50 256 L 1250 256 L 1250 264 L -50 264 Z" fill="#1e293b"/>
          <line x1="-50" y1="254" x2="1250" y2="254" stroke="#64748b" stroke-width="3"/>
          <line x1="-50" y1="250" x2="1250" y2="250" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="8 6"/>

          <g stroke="#64748b" stroke-width="2">
            <line x1="130" y1="170" x2="130" y2="254"/>
            <line x1="130" y1="180" x2="165" y2="180"/>
            <line x1="130" y1="195" x2="165" y2="180"/>
            <line x1="380" y1="170" x2="380" y2="254"/>
            <line x1="380" y1="180" x2="415" y2="180"/>
            <line x1="380" y1="195" x2="415" y2="180"/>
            <line x1="630" y1="170" x2="630" y2="254"/>
            <line x1="630" y1="180" x2="665" y2="180"/>
            <line x1="630" y1="195" x2="665" y2="180"/>
            <line x1="880" y1="170" x2="880" y2="254"/>
            <line x1="880" y1="180" x2="915" y2="180"/>
            <line x1="880" y1="195" x2="915" y2="180"/>
            <line x1="1080" y1="170" x2="1080" y2="254"/>
            <line x1="1080" y1="180" x2="1115" y2="180"/>
            <line x1="1080" y1="195" x2="1115" y2="180"/>
          </g>
          <path d="M -50 180 L 1250 180" stroke="#38bdf8" stroke-width="1.5" opacity="0.8"/>
          <path d="M -50 172 Q 130 180 380 172 T 880 172 T 1250 172" fill="none" stroke="#94a3b8" stroke-width="1.2" opacity="0.6"/>
        </g>

        <!-- Sleek Modern Stainless Steel Metro Train -->
        <g transform="translate(420, 192)">
          <polygon points="410,38 720,10 720,68 410,48" fill="#fef08a" opacity="0.18"/>
          <polygon points="410,40 600,24 600,56 410,46" fill="#ffffff" opacity="0.25"/>

          <!-- Coach 1 (Trailing Coach) -->
          <rect x="-320" y="10" width="180" height="52" rx="4" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
          <rect x="-320" y="38" width="180" height="6" fill="#dc2626"/>
          <rect x="-320" y="45" width="180" height="3" fill="#0284c7"/>
          <g fill="#fef08a" opacity="0.85">
            <rect x="-305" y="18" width="30" height="16" rx="2"/>
            <rect x="-260" y="18" width="30" height="16" rx="2"/>
            <rect x="-215" y="18" width="30" height="16" rx="2"/>
            <rect x="-170" y="18" width="22" height="16" rx="2"/>
          </g>
          <rect x="-300" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="-290" cy="65" r="5" fill="#475569"/>
          <circle cx="-270" cy="65" r="5" fill="#475569"/>
          <rect x="-180" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="-170" cy="65" r="5" fill="#475569"/>
          <circle cx="-150" cy="65" r="5" fill="#475569"/>

          <!-- Gangway 1 -->
          <rect x="-140" y="14" width="12" height="46" fill="#1e293b"/>
          <line x1="-136" y1="14" x2="-136" y2="60" stroke="#475569" stroke-width="2"/>
          <line x1="-132" y1="14" x2="-132" y2="60" stroke="#475569" stroke-width="2"/>

          <!-- Coach 2 (Middle Coach with Pantograph) -->
          <rect x="-128" y="10" width="220" height="52" rx="4" fill="#e2e8f0" stroke="#334155" stroke-width="1.5"/>
          <rect x="-128" y="38" width="220" height="6" fill="#dc2626"/>
          <rect x="-128" y="45" width="220" height="3" fill="#0284c7"/>
          <g fill="#fef08a" opacity="0.85">
            <rect x="-115" y="18" width="32" height="16" rx="2"/>
            <rect x="-70" y="18" width="32" height="16" rx="2"/>
            <rect x="-25" y="18" width="32" height="16" rx="2"/>
            <rect x="20" y="18" width="32" height="16" rx="2"/>
            <rect x="65" y="18" width="20" height="16" rx="2"/>
          </g>
          <rect x="-95" y="4" width="45" height="6" rx="2" fill="#64748b"/>
          <rect x="30" y="4" width="45" height="6" rx="2" fill="#64748b"/>
          <g stroke="#94a3b8" stroke-width="2" fill="none">
            <line x1="-30" y1="10" x2="-10" y2="-6"/>
            <line x1="-10" y1="-6" x2="10" y2="-12"/>
            <line x1="10" y1="-12" x2="30" y2="-12"/>
            <circle cx="20" cy="-12" r="3" fill="#38bdf8" class="ping"/>
          </g>
          <rect x="-110" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="-100" cy="65" r="5" fill="#475569"/>
          <circle cx="-80" cy="65" r="5" fill="#475569"/>
          <rect x="40" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="50" cy="65" r="5" fill="#475569"/>
          <circle cx="70" cy="65" r="5" fill="#475569"/>

          <!-- Gangway 2 -->
          <rect x="92" y="14" width="12" height="46" fill="#1e293b"/>
          <line x1="96" y1="14" x2="96" y2="60" stroke="#475569" stroke-width="2"/>
          <line x1="100" y1="14" x2="100" y2="60" stroke="#475569" stroke-width="2"/>

          <!-- Coach 3 (Leading Cab Coach with Aerodynamic Nose) -->
          <path d="M 104 10 L 340 10 Q 380 12 400 28 Q 412 38 410 52 Q 408 62 390 62 L 104 62 Z" fill="#f1f5f9" stroke="#334155" stroke-width="1.5"/>
          <path d="M 104 38 L 350 38 Q 385 39 405 44 L 405 49 Q 385 44 350 44 L 104 44 Z" fill="#dc2626"/>
          <path d="M 104 45 L 350 45 Q 385 46 405 51 L 405 53 Q 385 48 350 48 L 104 48 Z" fill="#0284c7"/>
          <g fill="#fef08a" opacity="0.85">
            <rect x="118" y="18" width="32" height="16" rx="2"/>
            <rect x="165" y="18" width="32" height="16" rx="2"/>
            <rect x="210" y="18" width="32" height="16" rx="2"/>
            <rect x="255" y="18" width="32" height="16" rx="2"/>
            <rect x="300" y="18" width="24" height="16" rx="2"/>
          </g>
          <path d="M 345 15 L 382 17 Q 396 24 398 34 L 355 34 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="1.2"/>
          <ellipse cx="365" cy="28" rx="8" ry="3" fill="#38bdf8" opacity="0.8"/>
          <ellipse cx="406" cy="42" rx="4" ry="2.5" fill="#ffffff"/>
          <circle cx="406" cy="42" r="2" fill="#fef08a"/>
          <ellipse cx="404" cy="48" rx="4" ry="2.5" fill="#ffffff"/>
          <circle cx="404" cy="48" r="2" fill="#fef08a"/>
          <rect x="130" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="140" cy="65" r="5" fill="#475569"/>
          <circle cx="160" cy="65" r="5" fill="#475569"/>
          <rect x="300" y="60" width="40" height="8" rx="2" fill="#0f172a"/>
          <circle cx="310" cy="65" r="5" fill="#475569"/>
          <circle cx="330" cy="65" r="5" fill="#475569"/>
        </g>
        """
    },
    "metro-transit.svg": {
        "title": "Urban Rapid Transit & Subterranean Corridors",
        "subtitle": "UNDERGROUND SHIELD TUNNELS • HOOGHLY RIVER BORE • REGIONAL RAPID RAIL",
        "sky1": "#091e3a", "sky2": "#0f766e", "accent": "#2dd4bf",
        "shapes": """
        <!-- Subterranean Geological Strata & Underwater Trench -->
        <g opacity="0.5">
          <path d="M 0 120 Q 300 140 600 110 T 1200 130 L 1200 600 L 0 600 Z" fill="#0b1727"/>
          <path d="M 0 170 Q 400 190 750 160 T 1200 180 L 1200 600 L 0 600 Z" fill="#0f293d"/>
          <path d="M 0 70 Q 150 55 300 70 T 600 70 T 900 70 T 1200 70 L 1200 120 L 0 120 Z" fill="#0284c7" opacity="0.3"/>
          <path d="M 0 85 Q 200 75 400 85 T 800 85 T 1200 85" stroke="#38bdf8" stroke-width="1.5" fill="none" opacity="0.4" class="draw"/>
        </g>

        <!-- Giant Circular Concrete Shield Tunnel Portal (33m Subterranean Depth) -->
        <g transform="translate(600, 260)">
          <circle cx="0" cy="0" r="210" fill="#0a192f" stroke="#1e3a5f" stroke-width="16"/>
          <circle cx="0" cy="0" r="198" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-dasharray="14 10" class="rot-slow"/>
          <circle cx="0" cy="0" r="182" fill="#071322" stroke="#334155" stroke-width="10"/>

          <ellipse cx="0" cy="25" rx="125" ry="70" fill="#020b14"/>
          <path d="M -170 -15 Q -80 15 -25 22" fill="none" stroke="#22d3ee" stroke-width="3" opacity="0.75"/>
          <path d="M 170 -15 Q 80 15 25 22" fill="none" stroke="#22d3ee" stroke-width="3" opacity="0.75"/>
          <path d="M -160 30 Q -70 38 -15 38" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.7"/>
          <path d="M 160 30 Q 70 38 15 38" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.7"/>

          <polygon points="-140,140 140,140 70,50 -70,50" fill="#1e293b"/>
          <line x1="-105" y1="140" x2="-35" y2="50" stroke="#94a3b8" stroke-width="4"/>
          <line x1="105" y1="140" x2="35" y2="50" stroke="#94a3b8" stroke-width="4"/>
          <line x1="0" y1="140" x2="0" y2="50" stroke="#eab308" stroke-width="2.5" stroke-dasharray="10 6"/>

          <!-- High-Speed Aerodynamic Bullet Metro / RRTS Train emerging from Portal -->
          <path d="M -75 125 Q -80 45 -52 8 Q 0 -22 52 8 Q 80 45 75 125 Z" fill="#0f172a" stroke="#0284c7" stroke-width="3"/>
          <path d="M -66 115 Q -72 52 -44 18 Q 0 -8 44 18 Q 72 52 66 115 Z" fill="#f8fafc"/>
          <path d="M -54 70 Q 0 42 54 70 L 58 84 Q 0 58 -58 84 Z" fill="#0284c7"/>
          <path d="M -55 84 Q 0 58 55 84 L 57 93 Q 0 66 -57 93 Z" fill="#f97316"/>
          <path d="M -40 28 Q 0 12 40 28 L 35 48 Q 0 35 -35 48 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="1.8"/>
          <ellipse cx="0" cy="40" rx="18" ry="4" fill="#38bdf8" opacity="0.8"/>
          <circle cx="-48" cy="102" r="7" fill="#ffffff"/>
          <circle cx="-48" cy="102" r="4" fill="#38bdf8"/>
          <circle cx="48" cy="102" r="7" fill="#ffffff"/>
          <circle cx="48" cy="102" r="4" fill="#38bdf8"/>
          <polygon points="-48,102 -160,220 160,220 48,102" fill="#38bdf8" opacity="0.12"/>

          <g transform="translate(140, 35)">
            <rect x="-8" y="-25" width="16" height="42" rx="7" fill="#0f172a" stroke="#475569" stroke-width="2"/>
            <circle cx="0" cy="-14" r="4" fill="#1e293b"/>
            <circle cx="0" cy="-2" r="4" fill="#1e293b"/>
            <circle cx="0" cy="10" r="4" fill="#10b981" class="pulse"/>
          </g>
        </g>

        <!-- Transit Route Network & Topological Vectors in Skies -->
        <g opacity="0.55">
          <line x1="100" y1="200" x2="350" y2="380" stroke="#06b6d4" stroke-width="3" stroke-linecap="round"/>
          <circle cx="100" cy="200" r="7" fill="#082f49" stroke="#06b6d4" stroke-width="2.5"/>
          <circle cx="350" cy="380" r="9" fill="#082f49" stroke="#ffffff" stroke-width="3"/>
          <line x1="350" y1="380" x2="480" y2="440" stroke="#06b6d4" stroke-width="3"/>

          <line x1="850" y1="380" x2="1100" y2="200" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
          <circle cx="1100" cy="200" r="7" fill="#022c22" stroke="#10b981" stroke-width="2.5"/>
          <circle cx="850" cy="380" r="9" fill="#022c22" stroke="#ffffff" stroke-width="3"/>
          <line x1="720" y1="440" x2="850" y2="380" stroke="#10b981" stroke-width="3"/>
        </g>
        """
    }
}

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true">
<style>
.tw{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
.rot{{transform-box:view-box;transform-origin:0 0;animation:rot 16s linear infinite}}
.rot-slow{{transform-box:fill-box;transform-origin:center;animation:rot 40s linear infinite}}
@keyframes rot{{to{{transform:rotate(360deg)}}}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 5s ease-in-out infinite}}
@keyframes pulse{{50%{{transform:scale(1.08);opacity:.75}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 3.2s ease-out infinite}}
@keyframes ping{{from{{transform:scale(.35);opacity:.9}}to{{transform:scale(1.7);opacity:0}}}}
.draw{{stroke-dasharray:1000;animation:draw 7s ease-in-out infinite alternate}}
@keyframes draw{{from{{stroke-dashoffset:1000}}to{{stroke-dashoffset:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<g transform="scale(1.333333 1.5)">
  <defs>
    <linearGradient id="sky_{name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sky1}"/>
      <stop offset="100%" stop-color="{sky2}"/>
    </linearGradient>
    <linearGradient id="lower_{name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="50%" stop-color="#000000" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <!-- Foreground shapes & bespoke art on transparent background -->
  {shapes}
</g>
</svg>"""

def main():
    dirs = ['frontend/public/art', 'docs/art']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    count = 0
    for filename, conf in SVG_DEFS.items():
        clean_name = filename.replace('.svg', '').replace('-', '_')
        svg_content = TEMPLATE.format(
            name=clean_name,
            sky1=conf['sky1'],
            sky2=conf['sky2'],
            accent=conf['accent'],
            title=conf['title'],
            subtitle=conf['subtitle'],
            shapes=conf['shapes']
        )

        for d in dirs:
            fpath = os.path.join(d, filename)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        count += 1

    print(f"Generated {count} authentic animated vector SVGs in both frontend/public/art and docs/art.")

if __name__ == '__main__':
    main()
