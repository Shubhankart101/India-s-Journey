#!/usr/bin/env python3
"""
Full cartographic generator for all 17 Indian metro networks.
Writes frontend/src/data/metro/all_city_packs.js.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "frontend" / "src" / "data" / "metro" / "all_city_packs.js"

# Let's define the comprehensive dataset for all cities other than Delhi (which uses delhi_metro_pack.json)
CITIES = {
    "mumbai": {
        "name": "Mumbai Metro & Monorail",
        "hindi": "मुंबई मेट्रो",
        "base": {
            "water": [
                # Arabian Sea Coastline
                {"t": "river", "g": [[72.78, 18.90], [72.79, 18.96], [72.81, 19.05], [72.82, 19.12], [72.83, 19.20], [72.85, 19.28]]},
                # Mahim Creek & Mithi River
                {"t": "canal", "g": [[72.84, 19.04], [72.86, 19.06], [72.88, 19.07], [72.90, 19.09]]},
                # Thane Creek Basin
                {"t": "river", "g": [[72.95, 18.98], [72.97, 19.06], [72.99, 19.14], [72.98, 19.22]]},
            ],
            "roads": [
                # Western Express Highway (WEH)
                {"c": 3, "g": [[72.86, 19.26], [72.85, 19.19], [72.85, 19.12], [72.84, 19.04], [72.83, 18.98]]},
                # Eastern Express Highway (EEH)
                {"c": 3, "g": [[72.96, 19.20], [72.93, 19.12], [72.91, 19.05], [72.88, 19.00]]},
                # SV Road
                {"c": 2, "g": [[72.84, 19.24], [72.83, 19.16], [72.83, 19.09], [72.83, 19.05]]},
            ],
            "places": [
                {"n": "Bandra Kurla Complex (BKC)", "ll": [72.865, 19.065], "r": 5},
                {"n": "Chhatrapati Shivaji Maharaj Terminus", "ll": [72.835, 18.940], "r": 5},
                {"n": "Gateway of India", "ll": [72.834, 18.922], "r": 4},
                {"n": "Andheri West", "ll": [72.830, 19.119], "r": 4},
                {"n": "Sanjay Gandhi National Park", "ll": [72.910, 19.230], "r": 3},
            ]
        },
        "lines": [
            {
                "id": "mum-l1", "nm": "Line 1 (Blue Corridor: Versova - Ghatkopar)", "c": "#0284c7",
                "seq": ["Versova", "DN Nagar", "Azad Nagar", "Andheri", "Western Express Highway", "Chakala", "Airport Road", "Marol Naka", "Saki Naka", "Asalpha", "Jagruti Nagar", "Ghatkopar"]
            },
            {
                "id": "mum-l2a", "nm": "Line 2A (Yellow Line: Dahisar East - Andheri West)", "c": "#eab308",
                "seq": ["Dahisar East", "Anand Nagar", "Kandarpada", "Mandapeshwar", "Eksar", "Borivali West", "Pahadi Eksar", "Kandivali West", "Dahanukarwadi", "Valnai", "Malad West", "Lower Malad", "Pahadi Goregaon", "Goregaon West", "Oshiwara", "Lower Oshiwara", "Andheri West"]
            },
            {
                "id": "mum-l7", "nm": "Line 7 (Red Line: Dahisar East - Gundavali)", "c": "#ef4444",
                "seq": ["Dahisar East", "Ovaripada", "National Park", "Devipada", "Magathane", "Poisar", "Akurli", "Kurar", "Dindoshi", "Aarey", "Goregaon East", "Jogeshwari East", "Mogra", "Gundavali"]
            },
            {
                "id": "mum-l3", "nm": "Line 3 (Aqua Underground: Aarey - BKC - Cuffe Parade)", "c": "#06b6d4",
                "seq": ["Aarey JVLR", "SEEPZ", "MIDC", "Marol Naka", "CSMIA T2", "Sahar Road", "CSMIA T1", "Santacruz", "Vidyanagari", "BKC", "Dharavi", "Shitaladevi", "Dadar", "Siddhivinayak", "Worli", "Acharya Atre Chowk", "Science Museum", "Mahalaxmi", "Mumbai Central", "Grant Road", "Girgaon", "Kalbadevi", "CSMT", "Hutatma Chowk", "Churchgate", "Vidhan Bhavan", "Cuffe Parade"]
            }
        ],
        "stations": [
            # Line 1
            {"n": "Versova", "hindi": "वर्सोवा", "ll": [72.8197, 19.1311], "l": ["mum-l1"]},
            {"n": "DN Nagar", "hindi": "डी एन नगर", "ll": [72.8315, 19.1245], "l": ["mum-l1", "mum-l2a"], "interchange": True},
            {"n": "Azad Nagar", "hindi": "आज़ाद नगर", "ll": [72.8420, 19.1250], "l": ["mum-l1"]},
            {"n": "Andheri", "hindi": "अंधेरी", "ll": [72.8525, 19.1197], "l": ["mum-l1"], "interchange": True},
            {"n": "Western Express Highway", "hindi": "वेस्टर्न एक्सप्रेस हाईवे", "ll": [72.8580, 19.1150], "l": ["mum-l1", "mum-l7"], "interchange": True},
            {"n": "Chakala", "hindi": "चकला", "ll": [72.8640, 19.1120], "l": ["mum-l1"]},
            {"n": "Airport Road", "hindi": "एयरपोर्ट रोड", "ll": [72.8735, 19.1105], "l": ["mum-l1"]},
            {"n": "Marol Naka", "hindi": "मरोल नाका", "ll": [72.8820, 19.1090], "l": ["mum-l1", "mum-l3"], "interchange": True},
            {"n": "Saki Naka", "hindi": "साकी नाका", "ll": [72.8890, 19.1020], "l": ["mum-l1"]},
            {"n": "Asalpha", "hindi": "असाल्फा", "ll": [72.8980, 19.0950], "l": ["mum-l1"]},
            {"n": "Jagruti Nagar", "hindi": "जागृति नगर", "ll": [72.9050, 19.0920], "l": ["mum-l1"]},
            {"n": "Ghatkopar", "hindi": "घाटकोपर", "ll": [72.9125, 19.0880], "l": ["mum-l1"], "interchange": True},
            # Line 2A
            {"n": "Dahisar East", "hindi": "दहिसर पूर्व", "ll": [72.8620, 19.2570], "l": ["mum-l2a", "mum-l7"], "interchange": True},
            {"n": "Anand Nagar", "hindi": "आनंद नगर", "ll": [72.8560, 19.2520], "l": ["mum-l2a"]},
            {"n": "Kandarpada", "hindi": "कंदरपाड़ा", "ll": [72.8520, 19.2450], "l": ["mum-l2a"]},
            {"n": "Mandapeshwar", "hindi": "मंडपेश्वर", "ll": [72.8480, 19.2380], "l": ["mum-l2a"]},
            {"n": "Eksar", "hindi": "एकसर", "ll": [72.8440, 19.2300], "l": ["mum-l2a"]},
            {"n": "Borivali West", "hindi": "बोरीवली पश्चिम", "ll": [72.8400, 19.2220], "l": ["mum-l2a"]},
            {"n": "Pahadi Eksar", "hindi": "पहाड़ी एकसर", "ll": [72.8380, 19.2150], "l": ["mum-l2a"]},
            {"n": "Kandivali West", "hindi": "कांदिवली पश्चिम", "ll": [72.8360, 19.2080], "l": ["mum-l2a"]},
            {"n": "Dahanukarwadi", "hindi": "दहानुकरवाड़ी", "ll": [72.8340, 19.2000], "l": ["mum-l2a"]},
            {"n": "Valnai", "hindi": "वलनई", "ll": [72.8320, 19.1920], "l": ["mum-l2a"]},
            {"n": "Malad West", "hindi": "मालाड पश्चिम", "ll": [72.8310, 19.1840], "l": ["mum-l2a"]},
            {"n": "Lower Malad", "hindi": "लोअर मालाड", "ll": [72.8300, 19.1760], "l": ["mum-l2a"]},
            {"n": "Pahadi Goregaon", "hindi": "पहाड़ी गोरेगांव", "ll": [72.8290, 19.1680], "l": ["mum-l2a"]},
            {"n": "Goregaon West", "hindi": "गोरेगांव पश्चिम", "ll": [72.8280, 19.1600], "l": ["mum-l2a"]},
            {"n": "Oshiwara", "hindi": "ओशिवरा", "ll": [72.8270, 19.1500], "l": ["mum-l2a"]},
            {"n": "Lower Oshiwara", "hindi": "लोअर ओशिवरा", "ll": [72.8280, 19.1400], "l": ["mum-l2a"]},
            {"n": "Andheri West", "hindi": "अंधेरी पश्चिम", "ll": [72.8300, 19.1300], "l": ["mum-l2a", "mum-l1"], "interchange": True},
            # Line 7
            {"n": "Ovaripada", "hindi": "ओवरीपाड़ा", "ll": [72.8630, 19.2480], "l": ["mum-l7"]},
            {"n": "National Park", "hindi": "नेशनल पार्क", "ll": [72.8640, 19.2380], "l": ["mum-l7"]},
            {"n": "Devipada", "hindi": "देवीपाड़ा", "ll": [72.8645, 19.2280], "l": ["mum-l7"]},
            {"n": "Magathane", "hindi": "मागाठाणे", "ll": [72.8650, 19.2180], "l": ["mum-l7"]},
            {"n": "Poisar", "hindi": "पोईसर", "ll": [72.8640, 19.2080], "l": ["mum-l7"]},
            {"n": "Akurli", "hindi": "आकुर्ली", "ll": [72.8630, 19.1980], "l": ["mum-l7"]},
            {"n": "Kurar", "hindi": "कुरार", "ll": [72.8620, 19.1880], "l": ["mum-l7"]},
            {"n": "Dindoshi", "hindi": "दिंडोशी", "ll": [72.8610, 19.1780], "l": ["mum-l7"]},
            {"n": "Aarey", "hindi": "आरे", "ll": [72.8600, 19.1680], "l": ["mum-l7"]},
            {"n": "Goregaon East", "hindi": "गोरेगांव पूर्व", "ll": [72.8590, 19.1580], "l": ["mum-l7"]},
            {"n": "Jogeshwari East", "hindi": "जोगेश्वरी पूर्व", "ll": [72.8580, 19.1450], "l": ["mum-l7"]},
            {"n": "Mogra", "hindi": "मोगरा", "ll": [72.8570, 19.1320], "l": ["mum-l7"]},
            {"n": "Gundavali", "hindi": "गुंदवली", "ll": [72.8580, 19.1170], "l": ["mum-l7", "mum-l1"], "interchange": True},
            # Line 3 (Aqua)
            {"n": "Aarey JVLR", "hindi": "आरे जेवीएलआर", "ll": [72.8750, 19.1390], "l": ["mum-l3"]},
            {"n": "SEEPZ", "hindi": "सीप्ज़", "ll": [72.8780, 19.1290], "l": ["mum-l3"]},
            {"n": "MIDC", "hindi": "एमआईडीसी", "ll": [72.8800, 19.1190], "l": ["mum-l3"]},
            {"n": "CSMIA T2", "hindi": "सीएसएमआईए टी2 एयरपोर्ट", "ll": [72.8740, 19.0980], "l": ["mum-l3"]},
            {"n": "Sahar Road", "hindi": "सहार रोड", "ll": [72.8680, 19.0960], "l": ["mum-l3"]},
            {"n": "CSMIA T1", "hindi": "सीएसएमआईए टी1", "ll": [72.8540, 19.0900], "l": ["mum-l3"]},
            {"n": "Santacruz", "hindi": "सांताक्रूज़", "ll": [72.8460, 19.0820], "l": ["mum-l3"]},
            {"n": "Vidyanagari", "hindi": "विद्यानगरी", "ll": [72.8550, 19.0730], "l": ["mum-l3"]},
            {"n": "BKC", "hindi": "बीकेसी (बांद्रा कुर्ला कॉम्प्लेक्स)", "ll": [72.8650, 19.0650], "l": ["mum-l3"], "interchange": True},
            {"n": "Dharavi", "hindi": "धारावी", "ll": [72.8550, 19.0480], "l": ["mum-l3"]},
            {"n": "Shitaladevi", "hindi": "शीतलादेवी", "ll": [72.8450, 19.0350], "l": ["mum-l3"]},
            {"n": "Dadar", "hindi": "दादर", "ll": [72.8410, 19.0190], "l": ["mum-l3"], "interchange": True},
            {"n": "Siddhivinayak", "hindi": "सिद्धिविनायक", "ll": [72.8320, 19.0160], "l": ["mum-l3"]},
            {"n": "Worli", "hindi": "वर्ली", "ll": [72.8220, 19.0080], "l": ["mum-l3"]},
            {"n": "Acharya Atre Chowk", "hindi": "आचार्य अत्रे चौक", "ll": [72.8180, 18.9980], "l": ["mum-l3"]},
            {"n": "Science Museum", "hindi": "साइंस म्यूजियम", "ll": [72.8200, 18.9880], "l": ["mum-l3"]},
            {"n": "Mahalaxmi", "hindi": "महालक्ष्मी", "ll": [72.8220, 18.9810], "l": ["mum-l3"]},
            {"n": "Mumbai Central", "hindi": "मुंबई सेंट्रल", "ll": [72.8190, 18.9710], "l": ["mum-l3"], "interchange": True},
            {"n": "Grant Road", "hindi": "ग्रांट रोड", "ll": [72.8160, 18.9630], "l": ["mum-l3"]},
            {"n": "Girgaon", "hindi": "गिरगांव", "ll": [72.8180, 18.9550], "l": ["mum-l3"]},
            {"n": "Kalbadevi", "hindi": "कालबादेवी", "ll": [72.8250, 18.9480], "l": ["mum-l3"]},
            {"n": "CSMT", "hindi": "सीएसएमटी", "ll": [72.8350, 18.9400], "l": ["mum-l3"], "interchange": True},
            {"n": "Hutatma Chowk", "hindi": "हुतात्मा चौक (फ्लोरा फाउंटेन)", "ll": [72.8320, 18.9320], "l": ["mum-l3"]},
            {"n": "Churchgate", "hindi": "चर्चगेट", "ll": [72.8280, 18.9350], "l": ["mum-l3"], "interchange": True},
            {"n": "Vidhan Bhavan", "hindi": "विधान भवन", "ll": [72.8250, 18.9270], "l": ["mum-l3"]},
            {"n": "Cuffe Parade", "hindi": "कफ परेड", "ll": [72.8190, 18.9150], "l": ["mum-l3"]},
        ],
        "links": [
            ["Andheri", "Western Express Highway"],
            ["Gundavali", "Western Express Highway"],
            ["DN Nagar", "Andheri West"],
        ]
    },
    "bengaluru": {
        "name": "Bengaluru Namma Metro",
        "hindi": "ನಮ್ಮ ಮೆಟ್ರೋ ಬೆಂಗಳೂರು",
        "base": {
            "water": [
                {"t": "river", "g": [[77.61, 12.98], [77.63, 12.97], [77.65, 12.96]]}, # Ulsoor Lake
                {"t": "river", "g": [[77.66, 12.93], [77.68, 12.92], [77.70, 12.93]]}, # Bellandur Lake
                {"t": "canal", "g": [[77.57, 13.01], [77.58, 13.02], [77.59, 13.04]]}, # Sankey Tank
            ],
            "roads": [
                {"c": 3, "g": [[77.49, 12.95], [77.55, 12.89], [77.64, 12.91], [77.69, 12.96], [77.65, 13.04], [77.55, 13.04], [77.49, 12.95]]}, # Outer Ring Road
                {"c": 3, "g": [[77.60, 12.97], [77.62, 12.92], [77.65, 12.87], [77.68, 12.81]]}, # Hosur Road
                {"c": 2, "g": [[77.59, 12.97], [77.59, 13.05], [77.60, 13.12]]}, # Bellary Road
            ],
            "places": [
                {"n": "Vidhana Soudha", "ll": [77.590, 12.979], "r": 5},
                {"n": "Majestic (KSR Railway)", "ll": [77.572, 12.977], "r": 5},
                {"n": "MG Road", "ll": [77.607, 12.975], "r": 4},
                {"n": "Whitefield IT Hub", "ll": [77.750, 12.970], "r": 4},
                {"n": "Electronic City", "ll": [77.675, 12.845], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "blr-purple", "nm": "Purple Line (Whitefield Kadugodi - Challaghatta)", "c": "#9333ea",
                "seq": ["Whitefield (Kadugodi)", "Hopefarm Channasandra", "Kadugodi Tree Park", "Pattandur Agrahara", "Sri Sathya Sai Hospital", "Nallurhalli", "Kundalahalli", "Seetharampalya", "Hoodi", "Garudacharpalya", "Singayyanapalya", "KR Puram", "Benniganahalli", "Baiyappanahalli", "Swami Vivekananda Road", "Indiranagar", "Halasuru", "Trinity", "MG Road", "Cubbon Park", "Dr. BR Ambedkar Vidhana Soudha", "Sir M Visveshwaraya Central College", "Nadaprabhu Kempegowda Majestic", "KSR City Railway Station", "Magadi Road", "Hosahalli", "Vijayanagar", "Attiguppe", "Deepanjali Nagar", "Mysuru Road", "Pantharapalya", "Rajarajeshwari Nagar", "Jnanabharathi", "Pattanagere", "Kengeri Bus Terminal", "Kengeri", "Challaghatta"]
            },
            {
                "id": "blr-green", "nm": "Green Line (Madavara - Silk Institute)", "c": "#16a34a",
                "seq": ["Madavara (BIEC)", "Chikkabidarakallu", "Manjunathanagar", "Nagasandra", "Dasarahalli", "Jalahalli", "Peenya Industry", "Peenya", "Goraguntepalya", "Yeshwanthpur", "Sandal Soap Factory", "Mahalakshmi", "Rajajinagar", "Mahakavi Kuvempu Road", "Sampige Road", "Nadaprabhu Kempegowda Majestic", "Chickpete", "Krishna Rajendra Market", "National College", "Lalbagh", "South End Circle", "Jayanagar", "RV Road", "Banashankari", "JP Nagar", "Yelachenahalli", "Konanakunte Cross", "Doddakallasandra", "Vajrahalli", "Thalaghattapura", "Silk Institute"]
            },
            {
                "id": "blr-yellow", "nm": "Yellow Line (RV Road - Bommasandra)", "c": "#eab308",
                "seq": ["RV Road", "Ragigudda", "Jayadeva Hospital", "BTM Layout", "Central Silk Board", "Bommanahalli", "Hongasandra", "Kudlu Gate", "Singasandra", "Hosa Road", "Beratena Agrahara", "Electronic City", "Infosys Foundation", "Huskur Road", "Hebbagodi", "Bommasandra"]
            }
        ],
        "stations": [
            # Purple Line Key Stations
            {"n": "Whitefield (Kadugodi)", "hindi": "व्हाइटफील्ड", "ll": [77.7600, 12.9960], "l": ["blr-purple"]},
            {"n": "Hopefarm Channasandra", "hindi": "होपफार्म", "ll": [77.7500, 12.9860], "l": ["blr-purple"]},
            {"n": "Kadugodi Tree Park", "hindi": "काडुगोडी ट्री पार्क", "ll": [77.7400, 12.9850], "l": ["blr-purple"]},
            {"n": "Pattandur Agrahara", "hindi": "पट्टंदूर अग्रहारा", "ll": [77.7300, 12.9840], "l": ["blr-purple"]},
            {"n": "Sri Sathya Sai Hospital", "hindi": "सत्य साईं अस्पताल", "ll": [77.7200, 12.9830], "l": ["blr-purple"]},
            {"n": "Nallurhalli", "hindi": "नल्लूरहल्ली", "ll": [77.7100, 12.9820], "l": ["blr-purple"]},
            {"n": "Kundalahalli", "hindi": "कुंडलहल्ली", "ll": [77.7000, 12.9820], "l": ["blr-purple"]},
            {"n": "Seetharampalya", "hindi": "सीतारामपाल्या", "ll": [77.6900, 12.9850], "l": ["blr-purple"]},
            {"n": "Hoodi", "hindi": "हूडी", "ll": [77.6800, 12.9890], "l": ["blr-purple"]},
            {"n": "Garudacharpalya", "hindi": "गरुड़ाचारपाल्या", "ll": [77.6750, 12.9930], "l": ["blr-purple"]},
            {"n": "Singayyanapalya", "hindi": "सिंगय्यनापाल्या", "ll": [77.6700, 12.9950], "l": ["blr-purple"]},
            {"n": "KR Puram", "hindi": "केआर पुरम", "ll": [77.6650, 12.9980], "l": ["blr-purple"], "interchange": True},
            {"n": "Benniganahalli", "hindi": "बेन्निगनहल्ली", "ll": [77.6580, 12.9940], "l": ["blr-purple"]},
            {"n": "Baiyappanahalli", "hindi": "बैयप्पनहल्ली", "ll": [77.6520, 12.9910], "l": ["blr-purple"]},
            {"n": "Swami Vivekananda Road", "hindi": "स्वामी विवेकानंद रोड", "ll": [77.6430, 12.9860], "l": ["blr-purple"]},
            {"n": "Indiranagar", "hindi": "इंदिरानगर", "ll": [77.6380, 12.9780], "l": ["blr-purple"]},
            {"n": "Halasuru", "hindi": "हलसूरु", "ll": [77.6270, 12.9760], "l": ["blr-purple"]},
            {"n": "Trinity", "hindi": "ट्रिनिटी", "ll": [77.6180, 12.9730], "l": ["blr-purple"]},
            {"n": "MG Road", "hindi": "एमजी रोड", "ll": [77.6070, 12.9750], "l": ["blr-purple"], "interchange": True},
            {"n": "Cubbon Park", "hindi": "कब्बन पार्क", "ll": [77.5980, 12.9800], "l": ["blr-purple"]},
            {"n": "Dr. BR Ambedkar Vidhana Soudha", "hindi": "विधान सौध", "ll": [77.5910, 12.9790], "l": ["blr-purple"]},
            {"n": "Sir M Visveshwaraya Central College", "hindi": "विश्वेश्वरय्या सेंट्रल कॉलेज", "ll": [77.5830, 12.9760], "l": ["blr-purple"]},
            {"n": "Nadaprabhu Kempegowda Majestic", "hindi": "केम्पेगौड़ा मैजेस्टिक", "ll": [77.5720, 12.9770], "l": ["blr-purple", "blr-green"], "interchange": True},
            {"n": "KSR City Railway Station", "hindi": "केएसआर रेलवे स्टेशन", "ll": [77.5680, 12.9750], "l": ["blr-purple"]},
            {"n": "Magadi Road", "hindi": "मागडी रोड", "ll": [77.5550, 12.9730], "l": ["blr-purple"]},
            {"n": "Hosahalli", "hindi": "होसहल्ली", "ll": [77.5450, 12.9720], "l": ["blr-purple"]},
            {"n": "Vijayanagar", "hindi": "विजयनगर", "ll": [77.5370, 12.9700], "l": ["blr-purple"]},
            {"n": "Attiguppe", "hindi": "अत्तिगुप्पे", "ll": [77.5280, 12.9640], "l": ["blr-purple"]},
            {"n": "Deepanjali Nagar", "hindi": "दीपांजलि नगर", "ll": [77.5220, 12.9570], "l": ["blr-purple"]},
            {"n": "Mysuru Road", "hindi": "मैसूरु रोड", "ll": [77.5180, 12.9480], "l": ["blr-purple"]},
            {"n": "Pantharapalya", "hindi": "पंथरपाल्या", "ll": [77.5120, 12.9400], "l": ["blr-purple"]},
            {"n": "Rajarajeshwari Nagar", "hindi": "राजारामेश्वरी नगर", "ll": [77.5050, 12.9320], "l": ["blr-purple"]},
            {"n": "Jnanabharathi", "hindi": "ज्ञानभारती (बीयू)", "ll": [77.4980, 12.9250], "l": ["blr-purple"]},
            {"n": "Pattanagere", "hindi": "पट्टणगेरे", "ll": [77.4920, 12.9180], "l": ["blr-purple"]},
            {"n": "Kengeri Bus Terminal", "hindi": "केंगेरी बस टर्मिनल", "ll": [77.4850, 12.9120], "l": ["blr-purple"]},
            {"n": "Kengeri", "hindi": "केंगेरी", "ll": [77.4780, 12.9060], "l": ["blr-purple"]},
            {"n": "Challaghatta", "hindi": "चल्लाघट्टा", "ll": [77.4690, 12.8980], "l": ["blr-purple"]},
            # Green Line
            {"n": "Madavara (BIEC)", "hindi": "मादवार (बीआईईसी)", "ll": [77.4780, 13.0650], "l": ["blr-green"]},
            {"n": "Chikkabidarakallu", "hindi": "चिक्कबिदारकल्लु", "ll": [77.4850, 13.0550], "l": ["blr-green"]},
            {"n": "Manjunathanagar", "hindi": "मंजुनाथनगर", "ll": [77.4920, 13.0450], "l": ["blr-green"]},
            {"n": "Nagasandra", "hindi": "नागसंद्रा", "ll": [77.5000, 13.0380], "l": ["blr-green"]},
            {"n": "Dasarahalli", "hindi": "दासरहल्ली", "ll": [77.5080, 13.0300], "l": ["blr-green"]},
            {"n": "Jalahalli", "hindi": "जालहल्ली", "ll": [77.5150, 13.0220], "l": ["blr-green"]},
            {"n": "Peenya Industry", "hindi": "पीन्या इंडस्ट्री", "ll": [77.5220, 13.0180], "l": ["blr-green"]},
            {"n": "Peenya", "hindi": "पीन्या", "ll": [77.5280, 13.0120], "l": ["blr-green"]},
            {"n": "Goraguntepalya", "hindi": "गोरगुंटेपाल्या", "ll": [77.5350, 13.0080], "l": ["blr-green"]},
            {"n": "Yeshwanthpur", "hindi": "यशवंतपुर", "ll": [77.5450, 13.0040], "l": ["blr-green"], "interchange": True},
            {"n": "Sandal Soap Factory", "hindi": "सैंडल सोप फैक्ट्री", "ll": [77.5520, 12.9980], "l": ["blr-green"]},
            {"n": "Mahalakshmi", "hindi": "महालक्ष्मी", "ll": [77.5560, 12.9920], "l": ["blr-green"]},
            {"n": "Rajajinagar", "hindi": "राजाजीनगर", "ll": [77.5600, 12.9880], "l": ["blr-green"]},
            {"n": "Mahakavi Kuvempu Road", "hindi": "कुवेम्पु रोड", "ll": [77.5630, 12.9830], "l": ["blr-green"]},
            {"n": "Sampige Road", "hindi": "संपिगे रोड", "ll": [77.5670, 12.9800], "l": ["blr-green"]},
            {"n": "Chickpete", "hindi": "चिक्कपेटा", "ll": [77.5750, 12.9710], "l": ["blr-green"]},
            {"n": "Krishna Rajendra Market", "hindi": "केआर मार्केट", "ll": [77.5770, 12.9640], "l": ["blr-green"]},
            {"n": "National College", "hindi": "नेशनल कॉलेज", "ll": [77.5760, 12.9550], "l": ["blr-green"]},
            {"n": "Lalbagh", "hindi": "लालबाग", "ll": [77.5780, 12.9460], "l": ["blr-green"]},
            {"n": "South End Circle", "hindi": "साउथ एंड सर्कल", "ll": [77.5800, 12.9380], "l": ["blr-green"]},
            {"n": "Jayanagar", "hindi": "जयनगर", "ll": [77.5820, 12.9300], "l": ["blr-green"]},
            {"n": "RV Road", "hindi": "आरवी रोड (राष्ट्रीय विद्यालय)", "ll": [77.5830, 12.9220], "l": ["blr-green", "blr-yellow"], "interchange": True},
            {"n": "Banashankari", "hindi": "बनशंकरी", "ll": [77.5730, 12.9150], "l": ["blr-green"]},
            {"n": "JP Nagar", "hindi": "जेपी नगर", "ll": [77.5680, 12.9080], "l": ["blr-green"]},
            {"n": "Yelachenahalli", "hindi": "यलाचेनहल्ली", "ll": [77.5650, 12.8980], "l": ["blr-green"]},
            {"n": "Konanakunte Cross", "hindi": "कोणनकुंटे क्रॉस", "ll": [77.5600, 12.8880], "l": ["blr-green"]},
            {"n": "Doddakallasandra", "hindi": "दोड्डकल्लासांद्रा", "ll": [77.5550, 12.8790], "l": ["blr-green"]},
            {"n": "Vajrahalli", "hindi": "वज्रहल्ली", "ll": [77.5480, 12.8700], "l": ["blr-green"]},
            {"n": "Thalaghattapura", "hindi": "थलघट्टपुरा", "ll": [77.5400, 12.8620], "l": ["blr-green"]},
            {"n": "Silk Institute", "hindi": "सिल्क इंस्टीट्यूट", "ll": [77.5320, 12.8540], "l": ["blr-green"]},
            # Yellow Line
            {"n": "Ragigudda", "hindi": "रागिगुड्डा", "ll": [77.5920, 12.9160], "l": ["blr-yellow"]},
            {"n": "Jayadeva Hospital", "hindi": "जयदेव अस्पताल", "ll": [77.6020, 12.9180], "l": ["blr-yellow"], "interchange": True},
            {"n": "BTM Layout", "hindi": "बीटीएम लेआउट", "ll": [77.6120, 12.9160], "l": ["blr-yellow"]},
            {"n": "Central Silk Board", "hindi": "सेंट्रल सिल्क बोर्ड", "ll": [77.6250, 12.9170], "l": ["blr-yellow"], "interchange": True},
            {"n": "Bommanahalli", "hindi": "बोम्मनहल्ली", "ll": [77.6320, 12.9050], "l": ["blr-yellow"]},
            {"n": "Hongasandra", "hindi": "होंगासांद्रा", "ll": [77.6380, 12.8950], "l": ["blr-yellow"]},
            {"n": "Kudlu Gate", "hindi": "कुडलू गेट", "ll": [77.6450, 12.8850], "l": ["blr-yellow"]},
            {"n": "Singasandra", "hindi": "सिंगासांद्रा", "ll": [77.6520, 12.8750], "l": ["blr-yellow"]},
            {"n": "Hosa Road", "hindi": "होसा रोड", "ll": [77.6580, 12.8650], "l": ["blr-yellow"]},
            {"n": "Beratena Agrahara", "hindi": "बेरातेना अग्रहारा", "ll": [77.6650, 12.8550], "l": ["blr-yellow"]},
            {"n": "Electronic City", "hindi": "इलेक्ट्रॉनिक सिटी", "ll": [77.6720, 12.8450], "l": ["blr-yellow"]},
            {"n": "Infosys Foundation", "hindi": "इन्फोसिस फाउंडेशन", "ll": [77.6780, 12.8350], "l": ["blr-yellow"]},
            {"n": "Huskur Road", "hindi": "हुस्कूर रोड", "ll": [77.6850, 12.8250], "l": ["blr-yellow"]},
            {"n": "Hebbagodi", "hindi": "हेब्बागोडी", "ll": [77.6920, 12.8150], "l": ["blr-yellow"]},
            {"n": "Bommasandra", "hindi": "बोम्मासांद्रा", "ll": [77.6980, 12.8050], "l": ["blr-yellow"]},
        ],
        "links": []
    },
    "kolkata": {
        "name": "Kolkata Metro (India's First Metro & Underwater Tunnel)",
        "hindi": "कोलकाता मेट्रो",
        "base": {
            "water": [
                # River Hooghly (running N-S through Kolkata and Howrah)
                {"t": "river", "g": [[88.35, 22.65], [88.36, 22.60], [88.34, 22.58], [88.33, 22.55], [88.32, 22.50], [88.31, 22.45]]},
                # Circular Canal
                {"t": "canal", "g": [[88.37, 22.60], [88.39, 22.58], [88.40, 22.54]]},
            ],
            "roads": [
                # Eastern Metropolitan (EM) Bypass
                {"c": 3, "g": [[88.40, 22.60], [88.40, 22.54], [88.39, 22.48], [88.38, 22.44]]},
                # AJC Bose Road / Howrah Bridge Connectors
                {"c": 3, "g": [[88.34, 22.58], [88.35, 22.54], [88.35, 22.51]]},
            ],
            "places": [
                {"n": "Howrah Railway Station", "ll": [88.342, 22.583], "r": 5},
                {"n": "Victoria Memorial", "ll": [88.342, 22.544], "r": 5},
                {"n": "Esplanade Central", "ll": [88.352, 22.565], "r": 5},
                {"n": "Salt Lake Sector V", "ll": [88.432, 22.570], "r": 4},
                {"n": "Dakshineswar Temple", "ll": [88.358, 22.653], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "kol-l1", "nm": "Blue Line (Line 1: Dakshineswar - Kavi Subhash)", "c": "#2563eb",
                "seq": ["Dakshineswar", "Baranagar", "Noapara", "Dum Dum", "Belgachia", "Shyambazar", "Shovabazar", "Girish Park", "MG Road Kolkata", "Central Kolkata", "Chandni Chowk Kolkata", "Esplanade", "Park Street", "Maidan", "Netaji Bhavan", "Jatin Das Park", "Kalighat", "Rabindra Sarobar", "Mahanayak Uttam Kumar", "Netaji", "Masterda Surya Sen", "Gitanjali", "Kavi Nazrul", "Shahid Khudiram", "Kavi Subhash"]
            },
            {
                "id": "kol-l2", "nm": "Green Line (Line 2 Underwater East-West: Howrah Maidan - Sector V)", "c": "#16a34a",
                "seq": ["Howrah Maidan", "Howrah Railway Station", "Mahakaran", "Esplanade", "Sealdah", "Phoolbagan", "Salt Lake Stadium", "Bengal Chemical", "City Centre", "Central Park", "Karunamoyee", "Salt Lake Sector V"]
            },
            {
                "id": "kol-l3", "nm": "Purple Line (Line 3: Joka - Majerhat)", "c": "#7c3aed",
                "seq": ["Joka", "Thakurpukur", "Sakherbazar", "Behala Chowrasta", "Behala Bazar", "Taratala", "Majerhat"]
            },
            {
                "id": "kol-l6", "nm": "Orange Line (Line 6: Kavi Subhash - Hemanta Mukhopadhyay)", "c": "#ea580c",
                "seq": ["Kavi Subhash", "Satyajit Ray", "Jyotirindra Nandy", "Kavi Sukanta", "Hemanta Mukhopadhyay"]
            }
        ],
        "stations": [
            # Line 1 (Blue)
            {"n": "Dakshineswar", "hindi": "दक्षिणेश्वर", "ll": [88.3580, 22.6530], "l": ["kol-l1"]},
            {"n": "Baranagar", "hindi": "बरानगर", "ll": [88.3680, 22.6410], "l": ["kol-l1"]},
            {"n": "Noapara", "hindi": "नोआपाड़ा", "ll": [88.3800, 22.6320], "l": ["kol-l1"]},
            {"n": "Dum Dum", "hindi": "दम दम", "ll": [88.3920, 22.6220], "l": ["kol-l1"], "interchange": True},
            {"n": "Belgachia", "hindi": "बेलगछिया", "ll": [88.3880, 22.6070], "l": ["kol-l1"]},
            {"n": "Shyambazar", "hindi": "श्यामबाजार", "ll": [88.3730, 22.6010], "l": ["kol-l1"]},
            {"n": "Shovabazar", "hindi": "शोभाबाजार", "ll": [88.3660, 22.5930], "l": ["kol-l1"]},
            {"n": "Girish Park", "hindi": "गिरीश पार्क", "ll": [88.3610, 22.5840], "l": ["kol-l1"]},
            {"n": "MG Road Kolkata", "hindi": "एमजी रोड कोलकाता", "ll": [88.3580, 22.5760], "l": ["kol-l1"]},
            {"n": "Central Kolkata", "hindi": "सेंट्रल", "ll": [88.3550, 22.5710], "l": ["kol-l1"]},
            {"n": "Chandni Chowk Kolkata", "hindi": "चांदनी चौक", "ll": [88.3530, 22.5680], "l": ["kol-l1"]},
            {"n": "Esplanade", "hindi": "एस्प्लेनेड", "ll": [88.3520, 22.5640], "l": ["kol-l1", "kol-l2"], "interchange": True},
            {"n": "Park Street", "hindi": "पार्क स्ट्रीट", "ll": [88.3500, 22.5530], "l": ["kol-l1"]},
            {"n": "Maidan", "hindi": "मैदान", "ll": [88.3480, 22.5450], "l": ["kol-l1"]},
            {"n": "Netaji Bhavan", "hindi": "नेताजी भवन", "ll": [88.3460, 22.5350], "l": ["kol-l1"]},
            {"n": "Jatin Das Park", "hindi": "जतिन दास पार्क", "ll": [88.3450, 22.5250], "l": ["kol-l1"]},
            {"n": "Kalighat", "hindi": "कालीघाट", "ll": [88.3440, 22.5160], "l": ["kol-l1"]},
            {"n": "Rabindra Sarobar", "hindi": "रवींद्र सरोवर", "ll": [88.3450, 22.5070], "l": ["kol-l1"]},
            {"n": "Mahanayak Uttam Kumar", "hindi": "महान्यायक उत्तम कुमार (टॉलीगंज)", "ll": [88.3460, 22.4960], "l": ["kol-l1"]},
            {"n": "Netaji", "hindi": "नेताजी", "ll": [88.3500, 22.4850], "l": ["kol-l1"]},
            {"n": "Masterda Surya Sen", "hindi": "मास्टरदा सूर्य सेन", "ll": [88.3550, 22.4760], "l": ["kol-l1"]},
            {"n": "Gitanjali", "hindi": "गीतांजलि", "ll": [88.3620, 22.4660], "l": ["kol-l1"]},
            {"n": "Kavi Nazrul", "hindi": "कवि नजरुल", "ll": [88.3720, 22.4570], "l": ["kol-l1"]},
            {"n": "Shahid Khudiram", "hindi": "शहीद खुदीराम", "ll": [88.3830, 22.4490], "l": ["kol-l1"]},
            {"n": "Kavi Subhash", "hindi": "कवि सुभाष (न्यू गरिया)", "ll": [88.3950, 22.4420], "l": ["kol-l1", "kol-l6"], "interchange": True},
            # Line 2 (Green Underwater)
            {"n": "Howrah Maidan", "hindi": "हावड़ा मैदान", "ll": [88.3280, 22.5850], "l": ["kol-l2"]},
            {"n": "Howrah Railway Station", "hindi": "हावड़ा रेलवे स्टेशन (अंडरवॉटर)", "ll": [88.3410, 22.5830], "l": ["kol-l2"], "interchange": True},
            {"n": "Mahakaran", "hindi": "महाकरण (राइटर्स बिल्डिंग)", "ll": [88.3490, 22.5720], "l": ["kol-l2"]},
            {"n": "Sealdah", "hindi": "सियालदह", "ll": [88.3710, 22.5670], "l": ["kol-l2"], "interchange": True},
            {"n": "Phoolbagan", "hindi": "फूलबागान", "ll": [88.3900, 22.5710], "l": ["kol-l2"]},
            {"n": "Salt Lake Stadium", "hindi": "सॉल्ट लेक स्टेडियम", "ll": [88.4020, 22.5720], "l": ["kol-l2"]},
            {"n": "Bengal Chemical", "hindi": "बंगाल केमिकल", "ll": [88.4090, 22.5730], "l": ["kol-l2"]},
            {"n": "City Centre", "hindi": "सिटी सेंटर", "ll": [88.4140, 22.5740], "l": ["kol-l2"]},
            {"n": "Central Park", "hindi": "सेंट्रल पार्क", "ll": [88.4190, 22.5750], "l": ["kol-l2"]},
            {"n": "Karunamoyee", "hindi": "करुणामयी", "ll": [88.4230, 22.5730], "l": ["kol-l2"]},
            {"n": "Salt Lake Sector V", "hindi": "सॉल्ट लेक सेक्टर 5", "ll": [88.4320, 22.5700], "l": ["kol-l2"]},
            # Line 3 (Purple)
            {"n": "Joka", "hindi": "जोका", "ll": [88.3050, 22.4430], "l": ["kol-l3"]},
            {"n": "Thakurpukur", "hindi": "ठाकुरपुकुर", "ll": [88.3120, 22.4550], "l": ["kol-l3"]},
            {"n": "Sakherbazar", "hindi": "सखेरबाजार", "ll": [88.3170, 22.4680], "l": ["kol-l3"]},
            {"n": "Behala Chowrasta", "hindi": "बेहाला चौरास्ता", "ll": [88.3220, 22.4820], "l": ["kol-l3"]},
            {"n": "Behala Bazar", "hindi": "बेहाला बाजार", "ll": [88.3250, 22.4950], "l": ["kol-l3"]},
            {"n": "Taratala", "hindi": "तारातला", "ll": [88.3270, 22.5080], "l": ["kol-l3"]},
            {"n": "Majerhat", "hindi": "माझेरहाट", "ll": [88.3300, 22.5180], "l": ["kol-l3"], "interchange": True},
            # Line 6 (Orange)
            {"n": "Satyajit Ray", "hindi": "सत्यजीत रे", "ll": [88.3980, 22.4600], "l": ["kol-l6"]},
            {"n": "Jyotirindra Nandy", "hindi": "ज्योतिरिंद्र नंदी", "ll": [88.4010, 22.4780], "l": ["kol-l6"]},
            {"n": "Kavi Sukanta", "hindi": "कवि सुकांत", "ll": [88.4030, 22.4960], "l": ["kol-l6"]},
            {"n": "Hemanta Mukhopadhyay", "hindi": "हेमंत मुखोपाध्याय (रूबी)", "ll": [88.4020, 22.5140], "l": ["kol-l6"]},
        ],
        "links": []
    },
    "chennai": {
        "name": "Chennai Metro (CMRL)",
        "hindi": "சென்னை மெட்ரோ",
        "base": {
            "water": [
                {"t": "river", "g": [[80.30, 13.15], [80.29, 13.08], [80.28, 13.01], [80.26, 12.95]]}, # Bay of Bengal Coast
                {"t": "canal", "g": [[80.22, 13.08], [80.25, 13.07], [80.28, 13.06]]}, # Cooum River
                {"t": "canal", "g": [[80.18, 13.01], [80.22, 13.01], [80.26, 13.01]]}, # Adyar River
            ],
            "roads": [
                {"c": 3, "g": [[80.27, 13.08], [80.25, 13.04], [80.21, 13.00], [80.17, 12.97]]}, # Anna Salai / GST Road
                {"c": 3, "g": [[80.20, 13.10], [80.21, 13.04], [80.20, 12.99]]}, # Inner Ring Road
            ],
            "places": [
                {"n": "Chennai Central (MGR)", "ll": [80.275, 13.082], "r": 5},
                {"n": "Chennai International Airport", "ll": [80.165, 12.980], "r": 5},
                {"n": "Marina Beach", "ll": [80.282, 13.055], "r": 4},
                {"n": "Alandur Hub", "ll": [80.201, 13.004], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "chn-blue", "nm": "Blue Line (Line 1: Wimco Nagar - Airport)", "c": "#2563eb",
                "seq": ["Wimco Nagar", "Tiruvottriyur", "Tollgate", "Washermanpet", "High Court Chennai", "Chennai Central", "Government Estate", "LIC Chennai", "Thousand Lights", "AG-DMS", "Teynampet", "Nandanam", "Saidapet", "Little Mount", "Guindy", "Alandur", "Meenambakkam", "Chennai International Airport"]
            },
            {
                "id": "chn-green", "nm": "Green Line (Line 2: Chennai Central - St. Thomas Mount)", "c": "#16a34a",
                "seq": ["Chennai Central", "Egmore", "Nehru Park", "Kilpauk Medical College", "Pachaiyappa's College", "Shenoy Nagar", "Anna Nagar East", "Anna Nagar Tower", "Thirumangalam", "Koyambedu", "CMBT", "Arumbakkam", "Vadapalani", "Ashok Nagar", "Ekkattuthangal", "Alandur", "St. Thomas Mount"]
            }
        ],
        "stations": [
            {"n": "Wimco Nagar", "hindi": "विमको नगर", "ll": [80.3010, 13.1680], "l": ["chn-blue"]},
            {"n": "Tiruvottriyur", "hindi": "तिरुवोट्टियूर", "ll": [80.2980, 13.1550], "l": ["chn-blue"]},
            {"n": "Tollgate", "hindi": "टोलगेट", "ll": [80.2940, 13.1360], "l": ["chn-blue"]},
            {"n": "Washermanpet", "hindi": "वॉशरमैनपेट", "ll": [80.2880, 13.1110], "l": ["chn-blue"]},
            {"n": "High Court Chennai", "hindi": "हाई कोर्ट", "ll": [80.2860, 13.0900], "l": ["chn-blue"]},
            {"n": "Chennai Central", "hindi": "चेन्नई सेंट्रल", "ll": [80.2750, 13.0820], "l": ["chn-blue", "chn-green"], "interchange": True},
            {"n": "Government Estate", "hindi": "गवर्नमेंट एस्टेट", "ll": [80.2730, 13.0690], "l": ["chn-blue"]},
            {"n": "LIC Chennai", "hindi": "एलआईसी", "ll": [80.2660, 13.0620], "l": ["chn-blue"]},
            {"n": "Thousand Lights", "hindi": "थाउजेंड लाइट्स", "ll": [80.2550, 13.0560], "l": ["chn-blue"]},
            {"n": "AG-DMS", "hindi": "एजी-डीएमएस", "ll": [80.2480, 13.0450], "l": ["chn-blue"]},
            {"n": "Teynampet", "hindi": "तेनामपेट", "ll": [80.2450, 13.0380], "l": ["chn-blue"]},
            {"n": "Nandanam", "hindi": "नंदनम", "ll": [80.2390, 13.0290], "l": ["chn-blue"]},
            {"n": "Saidapet", "hindi": "सैदापेट", "ll": [80.2280, 13.0220], "l": ["chn-blue"]},
            {"n": "Little Mount", "hindi": "लिटिल माउंट", "ll": [80.2210, 13.0160], "l": ["chn-blue"]},
            {"n": "Guindy", "hindi": "गिंडी", "ll": [80.2130, 13.0080], "l": ["chn-blue"], "interchange": True},
            {"n": "Alandur", "hindi": "अलंदूर", "ll": [80.2010, 13.0040], "l": ["chn-blue", "chn-green"], "interchange": True},
            {"n": "Meenambakkam", "hindi": "मीनम्बाक्कम", "ll": [80.1820, 12.9890], "l": ["chn-blue"]},
            {"n": "Chennai International Airport", "hindi": "चेन्नई एयरपोर्ट", "ll": [80.1650, 12.9800], "l": ["chn-blue"]},
            # Green Line
            {"n": "Egmore", "hindi": "एग्मोर", "ll": [80.2610, 13.0780], "l": ["chn-green"], "interchange": True},
            {"n": "Nehru Park", "hindi": "नेहरू पार्क", "ll": [80.2520, 13.0780], "l": ["chn-green"]},
            {"n": "Kilpauk Medical College", "hindi": "किल्पॉक मेडिकल कॉलेज", "ll": [80.2420, 13.0780], "l": ["chn-green"]},
            {"n": "Pachaiyappa's College", "hindi": "पचयप्पा कॉलेज", "ll": [80.2330, 13.0770], "l": ["chn-green"]},
            {"n": "Shenoy Nagar", "hindi": "शेनॉय नगर", "ll": [80.2250, 13.0780], "l": ["chn-green"]},
            {"n": "Anna Nagar East", "hindi": "अन्ना नगर ईस्ट", "ll": [80.2180, 13.0840], "l": ["chn-green"]},
            {"n": "Anna Nagar Tower", "hindi": "अन्ना नगर टॉवर", "ll": [80.2120, 13.0850], "l": ["chn-green"]},
            {"n": "Thirumangalam", "hindi": "थिरुमंगलम", "ll": [80.1990, 13.0850], "l": ["chn-green"]},
            {"n": "Koyambedu", "hindi": "कोयम्बेडु", "ll": [80.1950, 13.0740], "l": ["chn-green"]},
            {"n": "CMBT", "hindi": "सीएमबीटी बस टर्मिनल", "ll": [80.2030, 13.0670], "l": ["chn-green"]},
            {"n": "Arumbakkam", "hindi": "अरुम्बाक्कम", "ll": [80.2080, 13.0610], "l": ["chn-green"]},
            {"n": "Vadapalani", "hindi": "वडापलानी", "ll": [80.2110, 13.0510], "l": ["chn-green"]},
            {"n": "Ashok Nagar", "hindi": "अशोक नगर", "ll": [80.2120, 13.0360], "l": ["chn-green"]},
            {"n": "Ekkattuthangal", "hindi": "एक्काट्टुथांगल", "ll": [80.2050, 13.0200], "l": ["chn-green"]},
            {"n": "St. Thomas Mount", "hindi": "सेंट थॉमस माउंट", "ll": [80.1980, 12.9950], "l": ["chn-green"], "interchange": True},
        ],
        "links": []
    },
    "hyderabad": {
        "name": "Hyderabad Metro (HMRL)",
        "hindi": "హైదరాబాద్ మెట్రో",
        "base": {
            "water": [
                {"t": "river", "g": [[78.43, 17.37], [78.48, 17.36], [78.53, 17.38], [78.58, 17.37]]}, # Musi River
                {"t": "river", "g": [[78.46, 17.42], [78.48, 17.43], [78.47, 17.44]]}, # Hussain Sagar
            ],
            "roads": [
                {"c": 3, "g": [[78.41, 17.44], [78.47, 17.42], [78.51, 17.44], [78.55, 17.40]]}, # Inner Ring / NH 65
            ],
            "places": [
                {"n": "Charminar", "ll": [78.474, 17.361], "r": 5},
                {"n": "Hitec City Cyber Towers", "ll": [78.375, 17.450], "r": 5},
                {"n": "Ameerpet Junction", "ll": [78.448, 17.437], "r": 5},
                {"n": "Secunderabad Junction", "ll": [78.503, 17.434], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "hyd-red", "nm": "Red Line (Corridor 1: Miyapur - LB Nagar)", "c": "#dc2626",
                "seq": ["Miyapur", "JNTU College", "KPHB Colony", "Kukatpally", "Bharat Nagar", "Erragadda", "ESI Hospital", "Ameerpet", "Punjagutta", "Irrum Manzil", "Khairatabad", "Lakdi-ka-pul", "Assembly", "Nampally", "Gandhi Bhavan", "MGBS", "Malakpet", "Dilsukhnagar", "Chaitanyapuri", "Victoria Memorial", "LB Nagar"]
            },
            {
                "id": "hyd-blue", "nm": "Blue Line (Corridor 2: Nagole - Raidurg)", "c": "#2563eb",
                "seq": ["Nagole", "Uppal", "Stadium", "NGRI", "Habsiguda", "Tarnaka", "Mettuguda", "Secunderabad East", "Parade Ground", "Paradise", "Begumpet", "Ameerpet", "Madhura Nagar", "Yusufguda", "Jubilee Hills Checkpost", "Peddamma Gudi", "Madhapur", "Durgam Cheruvu", "Hitec City", "Raidurg"]
            },
            {
                "id": "hyd-green", "nm": "Green Line (Corridor 3: JBS - MGBS)", "c": "#16a34a",
                "seq": ["JBS Parade Ground", "Secunderabad West", "Gandhi Hospital", "Musheerabad", "RTC X Roads", "Chikkadpally", "Narayanguda", "Sultan Bazaar", "MGBS"]
            }
        ],
        "stations": [
            # Red Line
            {"n": "Miyapur", "hindi": "मियापुर", "ll": [78.3610, 17.4960], "l": ["hyd-red"]},
            {"n": "JNTU College", "hindi": "जेएनटीयू कॉलेज", "ll": [78.3880, 17.4940], "l": ["hyd-red"]},
            {"n": "KPHB Colony", "hindi": "केपीएचबी कॉलोनी", "ll": [78.4010, 17.4920], "l": ["hyd-red"]},
            {"n": "Kukatpally", "hindi": "कूकटपल्ली", "ll": [78.4110, 17.4870], "l": ["hyd-red"]},
            {"n": "Bharat Nagar", "hindi": "भारत नगर", "ll": [78.4230, 17.4660], "l": ["hyd-red"]},
            {"n": "Erragadda", "hindi": "एर्रागड्डा", "ll": [78.4320, 17.4580], "l": ["hyd-red"]},
            {"n": "ESI Hospital", "hindi": "ईएसआई अस्पताल", "ll": [78.4410, 17.4470], "l": ["hyd-red"]},
            {"n": "Ameerpet", "hindi": "अमीरपेट (सेंट्रल इंटरचेंज)", "ll": [78.4480, 17.4370], "l": ["hyd-red", "hyd-blue"], "interchange": True},
            {"n": "Punjagutta", "hindi": "पंजागुट्टा", "ll": [78.4520, 17.4260], "l": ["hyd-red"]},
            {"n": "Irrum Manzil", "hindi": "इर्रम मंजिल", "ll": [78.4560, 17.4180], "l": ["hyd-red"]},
            {"n": "Khairatabad", "hindi": "खैराताबाद", "ll": [78.4610, 17.4110], "l": ["hyd-red"]},
            {"n": "Lakdi-ka-pul", "hindi": "लकड़ी का पुल", "ll": [78.4650, 17.4040], "l": ["hyd-red"]},
            {"n": "Assembly", "hindi": "असेंबली", "ll": [78.4680, 17.3970], "l": ["hyd-red"]},
            {"n": "Nampally", "hindi": "नामपल्ली रेलवे स्टेशन", "ll": [78.4710, 17.3910], "l": ["hyd-red"]},
            {"n": "Gandhi Bhavan", "hindi": "गांधी भवन", "ll": [78.4740, 17.3850], "l": ["hyd-red"]},
            {"n": "MGBS", "hindi": "एमजीबीएस बस स्टेशन", "ll": [78.4820, 17.3780], "l": ["hyd-red", "hyd-green"], "interchange": True},
            {"n": "Malakpet", "hindi": "मलकपेट", "ll": [78.4960, 17.3740], "l": ["hyd-red"]},
            {"n": "Dilsukhnagar", "hindi": "दिलसुखनगर", "ll": [78.5250, 17.3680], "l": ["hyd-red"]},
            {"n": "Chaitanyapuri", "hindi": "चैतन्यपुरी", "ll": [78.5370, 17.3640], "l": ["hyd-red"]},
            {"n": "Victoria Memorial", "hindi": "विक्टोरिया मेमोरियल", "ll": [78.5460, 17.3590], "l": ["hyd-red"]},
            {"n": "LB Nagar", "hindi": "एलबी नगर", "ll": [78.5530, 17.3520], "l": ["hyd-red"]},
            # Blue Line
            {"n": "Raidurg", "hindi": "रायदुर्ग", "ll": [78.3750, 17.4420], "l": ["hyd-blue"]},
            {"n": "Hitec City", "hindi": "हाईटेक सिटी", "ll": [78.3840, 17.4460], "l": ["hyd-blue"]},
            {"n": "Durgam Cheruvu", "hindi": "दुर्गम चेरुवू", "ll": [78.3910, 17.4440], "l": ["hyd-blue"]},
            {"n": "Madhapur", "hindi": "माधापुर", "ll": [78.3980, 17.4410], "l": ["hyd-blue"]},
            {"n": "Peddamma Gudi", "hindi": "पेद्दम्मा गुड़ी", "ll": [78.4110, 17.4350], "l": ["hyd-blue"]},
            {"n": "Jubilee Hills Checkpost", "hindi": "जुबली हिल्स चेकपोस्ट", "ll": [78.4180, 17.4320], "l": ["hyd-blue"]},
            {"n": "Yusufguda", "hindi": "यूसुफगुड़ा", "ll": [78.4310, 17.4370], "l": ["hyd-blue"]},
            {"n": "Madhura Nagar", "hindi": "मधुरा नगर", "ll": [78.4390, 17.4380], "l": ["hyd-blue"]},
            {"n": "Begumpet", "hindi": "बेगमपेट", "ll": [78.4620, 17.4390], "l": ["hyd-blue"]},
            {"n": "Paradise", "hindi": "पैराडाइज", "ll": [78.4870, 17.4410], "l": ["hyd-blue"]},
            {"n": "Parade Ground", "hindi": "परेड ग्राउंड", "ll": [78.4980, 17.4440], "l": ["hyd-blue", "hyd-green"], "interchange": True},
            {"n": "Secunderabad East", "hindi": "सिकंदराबाद ईस्ट", "ll": [78.5040, 17.4350], "l": ["hyd-blue"]},
            {"n": "Mettuguda", "hindi": "मेट्टुगुड़ा", "ll": [78.5170, 17.4310], "l": ["hyd-blue"]},
            {"n": "Tarnaka", "hindi": "तारनाका", "ll": [78.5300, 17.4280], "l": ["hyd-blue"]},
            {"n": "Habsiguda", "hindi": "हब्सीगुड़ा", "ll": [78.5450, 17.4180], "l": ["hyd-blue"]},
            {"n": "NGRI", "hindi": "एनजीआरआई", "ll": [78.5530, 17.4110], "l": ["hyd-blue"]},
            {"n": "Stadium", "hindi": "स्टेडियम (उप्पल)", "ll": [78.5600, 17.4040], "l": ["hyd-blue"]},
            {"n": "Uppal", "hindi": "उप्पल", "ll": [78.5680, 17.3990], "l": ["hyd-blue"]},
            {"n": "Nagole", "hindi": "नागोले", "ll": [78.5770, 17.3870], "l": ["hyd-blue"]},
            # Green Line
            {"n": "JBS Parade Ground", "hindi": "जेबीएस परेड ग्राउंड", "ll": [78.4980, 17.4510], "l": ["hyd-green"]},
            {"n": "Secunderabad West", "hindi": "सिकंदराबाद वेस्ट", "ll": [78.5020, 17.4380], "l": ["hyd-green"]},
            {"n": "Gandhi Hospital", "hindi": "गांधी अस्पताल", "ll": [78.5070, 17.4240], "l": ["hyd-green"]},
            {"n": "Musheerabad", "hindi": "मुशीराबाद", "ll": [78.5080, 17.4150], "l": ["hyd-green"]},
            {"n": "RTC X Roads", "hindi": "आरटीसी क्रॉस रोड्स", "ll": [78.5050, 17.4040], "l": ["hyd-green"]},
            {"n": "Chikkadpally", "hindi": "चिक्कड़पल्ली", "ll": [78.5010, 17.3970], "l": ["hyd-green"]},
            {"n": "Narayanguda", "hindi": "नारायणगुड़ा", "ll": [78.4960, 17.3910], "l": ["hyd-green"]},
            {"n": "Sultan Bazaar", "hindi": "सुल्तान बाजार", "ll": [78.4890, 17.3840], "l": ["hyd-green"]},
        ],
        "links": []
    },
    "kochi": {
        "name": "Kochi Metro & Water Metro (KMRL)",
        "hindi": "കൊച്ചി മെട്രോ",
        "base": {
            "water": [
                {"t": "river", "g": [[76.24, 10.08], [76.28, 10.05], [76.32, 10.04]]}, # Periyar River
                {"t": "river", "g": [[76.26, 9.98], [76.27, 9.95], [76.30, 9.93]]}, # Vembanad Backwaters
            ],
            "roads": [
                {"c": 3, "g": [[76.34, 10.11], [76.31, 10.04], [76.30, 9.99], [76.33, 9.95]]}, # NH 544
            ],
            "places": [
                {"n": "High Court Water Terminal", "ll": [76.273, 9.984], "r": 5},
                {"n": "Aluva Riverfront", "ll": [76.353, 10.110], "r": 4},
                {"n": "JLN Stadium Kaloor", "ll": [76.299, 9.998], "r": 4},
                {"n": "Tripunithura Heritage Palace", "ll": [76.350, 9.950], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "koc-blue", "nm": "Blue Line (Line 1: Aluva - Tripunithura)", "c": "#0284c7",
                "seq": ["Aluva", "Pulinchodu", "Companypady", "Ambattukavu", "Muttom", "Kalamassery", "Cochin University (CUSAT)", "Pathadipalam", "Edapally", "Changampuzha Park", "Palarivattom", "JLN Stadium", "Kaloor", "Lissie", "MG Road Kochi", "Maharaja's College", "Ernakulam South", "Kadavanthra", "Elamkulam", "Vyttila", "Thykoodam", "Petta", "Vadakkekotta", "SN Junction", "Tripunithura"]
            }
        ],
        "stations": [
            {"n": "Aluva", "hindi": "अलुवा", "ll": [76.3530, 10.1100], "l": ["koc-blue"], "interchange": True},
            {"n": "Pulinchodu", "hindi": "पुलिंचोडु", "ll": [76.3450, 10.1000], "l": ["koc-blue"]},
            {"n": "Companypady", "hindi": "कंपनीपडी", "ll": [76.3390, 10.0880], "l": ["koc-blue"]},
            {"n": "Ambattukavu", "hindi": "अम्बट्टुकावु", "ll": [76.3320, 10.0780], "l": ["koc-blue"]},
            {"n": "Muttom", "hindi": "मुट्टम", "ll": [76.3260, 10.0680], "l": ["koc-blue"]},
            {"n": "Kalamassery", "hindi": "कलमस्सेरी", "ll": [76.3210, 10.0550], "l": ["koc-blue"]},
            {"n": "Cochin University (CUSAT)", "hindi": "कोचीन यूनिवर्सिटी", "ll": [76.3160, 10.0450], "l": ["koc-blue"]},
            {"n": "Pathadipalam", "hindi": "पथाडीपालम", "ll": [76.3120, 10.0350], "l": ["koc-blue"]},
            {"n": "Edapally", "hindi": "एडापल्ली (लुलु मॉल)", "ll": [76.3080, 10.0240], "l": ["koc-blue"], "interchange": True},
            {"n": "Changampuzha Park", "hindi": "चंगम्पुझा पार्क", "ll": [76.3050, 10.0150], "l": ["koc-blue"]},
            {"n": "Palarivattom", "hindi": "पलारिवट्टम", "ll": [76.3020, 10.0060], "l": ["koc-blue"]},
            {"n": "JLN Stadium", "hindi": "जवाहरलाल नेहरू स्टेडियम", "ll": [76.2990, 9.9980], "l": ["koc-blue"]},
            {"n": "Kaloor", "hindi": "कलूर", "ll": [76.2950, 9.9900], "l": ["koc-blue"]},
            {"n": "Lissie", "hindi": "लिस्सी", "ll": [76.2900, 9.9850], "l": ["koc-blue"]},
            {"n": "MG Road Kochi", "hindi": "एमजी रोड कोच्चि", "ll": [76.2840, 9.9800], "l": ["koc-blue"]},
            {"n": "Maharaja's College", "hindi": "महाराजा कॉलेज", "ll": [76.2850, 9.9720], "l": ["koc-blue"]},
            {"n": "Ernakulam South", "hindi": "एर्नाकुलम साउथ जंक्शन", "ll": [76.2890, 9.9670], "l": ["koc-blue"], "interchange": True},
            {"n": "Kadavanthra", "hindi": "कडवन्थरा", "ll": [76.2980, 9.9650], "l": ["koc-blue"]},
            {"n": "Elamkulam", "hindi": "एलमकुलम", "ll": [76.3080, 9.9640], "l": ["koc-blue"]},
            {"n": "Vyttila", "hindi": "वायटिला मोबिलिटी हब", "ll": [76.3200, 9.9650], "l": ["koc-blue"], "interchange": True},
            {"n": "Thykoodam", "hindi": "थाइकुडम", "ll": [76.3260, 9.9610], "l": ["koc-blue"]},
            {"n": "Petta", "hindi": "पेट्टा", "ll": [76.3320, 9.9570], "l": ["koc-blue"]},
            {"n": "Vadakkekotta", "hindi": "वडक्केकोट्टा", "ll": [76.3400, 9.9540], "l": ["koc-blue"]},
            {"n": "SN Junction", "hindi": "एसएन जंक्शन", "ll": [76.3450, 9.9520], "l": ["koc-blue"]},
            {"n": "Tripunithura", "hindi": "त्रिपुनिथुरा रेलवे स्टेशन", "ll": [76.3500, 9.9500], "l": ["koc-blue"], "interchange": True},
        ],
        "links": []
    },
    "ahmedabad": {
        "name": "Ahmedabad & Gandhinagar Metro (GMRC)",
        "hindi": "અમદાવાદ મેટ્રો",
        "base": {
            "water": [
                # River Sabarmati (flowing north to south through Ahmedabad)
                {"t": "river", "g": [[72.58, 23.12], [72.59, 23.07], [72.58, 23.03], [72.57, 22.98]]},
            ],
            "roads": [
                {"c": 3, "g": [[72.51, 23.10], [72.51, 23.04], [72.50, 22.98]]}, # SG Highway
                {"c": 3, "g": [[72.56, 23.08], [72.56, 23.02], [72.57, 22.97]]}, # Ashram Road
            ],
            "places": [
                {"n": "Sabarmati Ashram", "ll": [72.580, 23.060], "r": 5},
                {"n": "Narendra Modi Stadium Motera", "ll": [72.597, 23.092], "r": 5},
                {"n": "Kalupur Railway Station", "ll": [72.602, 23.022], "r": 4},
                {"n": "Old High Court Central", "ll": [72.568, 23.038], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "ahm-blue", "nm": "Blue Line (East-West: Thaltej Gam - Vastral Gam)", "c": "#2563eb",
                "seq": ["Thaltej Gam", "Thaltej", "Doordarshan Kendra", "Gurukul Road", "Gujarat University", "Commerce Six Road", "Stadium Ahmedabad", "Old High Court", "Sabarmati Riverfront", "Shahpur", "Gheekanta", "Kalupur Railway Station", "Kankaria East", "Apparel Park", "Amraiwadi", "Rabari Colony", "Vastral", "Vastral Gam"]
            },
            {
                "id": "ahm-red", "nm": "Red Line (North-South: Motera Stadium - APMC)", "c": "#dc2626",
                "seq": ["Motera Stadium", "Sabarmati", "AEC", "Ranip", "Vadaj", "Vijay Nagar", "Usmanpura", "Old High Court", "Gandhigram", "Paldi", "Shreyas", "Rajiv Nagar", "Jivraj Park", "APMC"]
            }
        ],
        "stations": [
            # Blue Line
            {"n": "Thaltej Gam", "hindi": "थलतेज गाम", "ll": [72.5050, 23.0520], "l": ["ahm-blue"]},
            {"n": "Thaltej", "hindi": "थलतेज", "ll": [72.5180, 23.0500], "l": ["ahm-blue"]},
            {"n": "Doordarshan Kendra", "hindi": "दूरदर्शन केंद्र", "ll": [72.5280, 23.0480], "l": ["ahm-blue"]},
            {"n": "Gurukul Road", "hindi": "गुरुकुल रोड", "ll": [72.5370, 23.0450], "l": ["ahm-blue"]},
            {"n": "Gujarat University", "hindi": "गुजरात यूनिवर्सिटी", "ll": [72.5480, 23.0410], "l": ["ahm-blue"]},
            {"n": "Commerce Six Road", "hindi": "कॉमर्स सिक्स रोड", "ll": [72.5560, 23.0390], "l": ["ahm-blue"]},
            {"n": "Stadium Ahmedabad", "hindi": "सरदार पटेल स्टेडियम", "ll": [72.5620, 23.0380], "l": ["ahm-blue"]},
            {"n": "Old High Court", "hindi": "ओल्ड हाई कोर्ट (सेंट्रल इंटरचेंज)", "ll": [72.5680, 23.0380], "l": ["ahm-blue", "ahm-red"], "interchange": True},
            {"n": "Sabarmati Riverfront", "hindi": "साबरमती रिवरफ्रंट", "ll": [72.5760, 23.0350], "l": ["ahm-blue"]},
            {"n": "Shahpur", "hindi": "शाहपुर", "ll": [72.5830, 23.0330], "l": ["ahm-blue"]},
            {"n": "Gheekanta", "hindi": "घीकांटा", "ll": [72.5920, 23.0280], "l": ["ahm-blue"]},
            {"n": "Kalupur Railway Station", "hindi": "कालूपुर अहमदाबाद रेलवे स्टेशन", "ll": [72.6020, 23.0220], "l": ["ahm-blue"], "interchange": True},
            {"n": "Kankaria East", "hindi": "कांकरिया ईस्ट", "ll": [72.6100, 23.0150], "l": ["ahm-blue"]},
            {"n": "Apparel Park", "hindi": "अपेरल पार्क", "ll": [72.6200, 23.0100], "l": ["ahm-blue"]},
            {"n": "Amraiwadi", "hindi": "अमराईवाड़ी", "ll": [72.6300, 23.0070], "l": ["ahm-blue"]},
            {"n": "Rabari Colony", "hindi": "रबारी कॉलोनी", "ll": [72.6410, 23.0050], "l": ["ahm-blue"]},
            {"n": "Vastral", "hindi": "वस्त्राल", "ll": [72.6520, 23.0030], "l": ["ahm-blue"]},
            {"n": "Vastral Gam", "hindi": "वस्त्राल गाम", "ll": [72.6650, 23.0010], "l": ["ahm-blue"]},
            # Red Line
            {"n": "Motera Stadium", "hindi": "नरेंद्र मोदी स्टेडियम मोटेरा", "ll": [72.5970, 23.0920], "l": ["ahm-red"]},
            {"n": "Sabarmati", "hindi": "साबरमती रेलवे स्टेशन", "ll": [72.5900, 23.0820], "l": ["ahm-red"], "interchange": True},
            {"n": "AEC", "hindi": "एईसी", "ll": [72.5840, 23.0730], "l": ["ahm-red"]},
            {"n": "Ranip", "hindi": "रानीप बस टर्मिनल", "ll": [72.5790, 23.0640], "l": ["ahm-red"]},
            {"n": "Vadaj", "hindi": "वाडज", "ll": [72.5740, 23.0560], "l": ["ahm-red"]},
            {"n": "Vijay Nagar", "hindi": "विजय नगर", "ll": [72.5710, 23.0480], "l": ["ahm-red"]},
            {"n": "Usmanpura", "hindi": "उस्मानपुरा", "ll": [72.5690, 23.0420], "l": ["ahm-red"]},
            {"n": "Gandhigram", "hindi": "गांधीग्राम", "ll": [72.5670, 23.0290], "l": ["ahm-red"]},
            {"n": "Paldi", "hindi": "पालडी", "ll": [72.5650, 23.0180], "l": ["ahm-red"]},
            {"n": "Shreyas", "hindi": "श्रेयस", "ll": [72.5620, 23.0080], "l": ["ahm-red"]},
            {"n": "Rajiv Nagar", "hindi": "राजीव नगर", "ll": [72.5580, 22.9990], "l": ["ahm-red"]},
            {"n": "Jivraj Park", "hindi": "जीवराज पार्क", "ll": [72.5540, 22.9910], "l": ["ahm-red"]},
            {"n": "APMC", "hindi": "एपीएमसी मार्केट", "ll": [72.5500, 22.9820], "l": ["ahm-red"]},
        ],
        "links": []
    },
    "pune": {
        "name": "Pune Metro (Maha Metro)",
        "hindi": "पुणे मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[73.78, 18.59], [73.83, 18.56], [73.87, 18.53]]}, # Mula River
                {"t": "river", "g": [[73.80, 18.51], [73.84, 18.52], [73.87, 18.53], [73.92, 18.54]]}, # Mutha River & Sangam
            ],
            "roads": [
                {"c": 3, "g": [[73.82, 18.63], [73.84, 18.58], [73.85, 18.52], [73.86, 18.49]]}, # Old Mumbai-Pune / Swargate
                {"c": 3, "g": [[73.80, 18.50], [73.85, 18.52], [73.91, 18.55]]}, # Karve Road to Nagar Road
            ],
            "places": [
                {"n": "Shaniwar Wada", "ll": [73.855, 18.519], "r": 5},
                {"n": "Civil Court Underground Hub", "ll": [73.856, 18.527], "r": 5},
                {"n": "Pune Junction Railway", "ll": [73.873, 18.528], "r": 5},
                {"n": "PCMC Civic Center", "ll": [73.820, 18.627], "r": 4},
                {"n": "Swargate Multimodal Hub", "ll": [73.858, 18.501], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "pun-purple", "nm": "Purple Line (Line 1: PCMC - Swargate)", "c": "#7c3aed",
                "seq": ["PCMC", "Sant Tukaram Nagar", "Bhosari", "Kasarwadi", "Phugewadi", "Dapodi", "Bopodi", "Khadki", "Range Hill", "Shivajinagar", "Civil Court", "Budhwar Peth", "Mandai", "Swargate"]
            },
            {
                "id": "pun-aqua", "nm": "Aqua Line (Line 2: Vanaz - Ramwadi)", "c": "#06b6d4",
                "seq": ["Vanaz", "Anand Nagar Pune", "Ideal Colony", "Nal Stop", "Garware College", "Deccan Gymkhana", "Chhatrapati Sambhaji Udyan", "PMC", "Civil Court", "Mangalwar Peth", "Pune Railway Station", "Ruby Hall Clinic", "Bund Garden", "Yerawada", "Kalyani Nagar", "Ramwadi"]
            }
        ],
        "stations": [
            # Purple Line
            {"n": "PCMC", "hindi": "पिंपरी चिंचवड (पीसीएमसी)", "ll": [73.8200, 18.6270], "l": ["pun-purple"]},
            {"n": "Sant Tukaram Nagar", "hindi": "संत तुकाराम नगर", "ll": [73.8240, 18.6180], "l": ["pun-purple"]},
            {"n": "Bhosari", "hindi": "भोसरी (नाशिक फाटा)", "ll": [73.8290, 18.6070], "l": ["pun-purple"]},
            {"n": "Kasarwadi", "hindi": "कासारवाडी", "ll": [73.8320, 18.5980], "l": ["pun-purple"]},
            {"n": "Phugewadi", "hindi": "फुगेवाडी", "ll": [73.8350, 18.5880], "l": ["pun-purple"]},
            {"n": "Dapodi", "hindi": "दापोडी", "ll": [73.8380, 18.5780], "l": ["pun-purple"]},
            {"n": "Bopodi", "hindi": "बोपोडी", "ll": [73.8410, 18.5680], "l": ["pun-purple"]},
            {"n": "Khadki", "hindi": "खड़की", "ll": [73.8450, 18.5580], "l": ["pun-purple"]},
            {"n": "Range Hill", "hindi": "रेंज हिल", "ll": [73.8480, 18.5470], "l": ["pun-purple"]},
            {"n": "Shivajinagar", "hindi": "शिवाजीनगर रेलवे स्टेशन", "ll": [73.8520, 18.5340], "l": ["pun-purple"], "interchange": True},
            {"n": "Civil Court", "hindi": "सिविल कोर्ट (पुणे सेंट्रल हब)", "ll": [73.8560, 18.5270], "l": ["pun-purple", "pun-aqua"], "interchange": True},
            {"n": "Budhwar Peth", "hindi": "बुधवार पेठ", "ll": [73.8570, 18.5170], "l": ["pun-purple"]},
            {"n": "Mandai", "hindi": "मंडई", "ll": [73.8575, 18.5090], "l": ["pun-purple"]},
            {"n": "Swargate", "hindi": "स्वारगेट मल्टीमॉडल हब", "ll": [73.8580, 18.5010], "l": ["pun-purple"], "interchange": True},
            # Aqua Line
            {"n": "Vanaz", "hindi": "वनाझ", "ll": [73.7990, 18.5020], "l": ["pun-aqua"]},
            {"n": "Anand Nagar Pune", "hindi": "आनंद नगर पुणे", "ll": [73.8080, 18.5040], "l": ["pun-aqua"]},
            {"n": "Ideal Colony", "hindi": "आइडियल कॉलोनी", "ll": [73.8180, 18.5070], "l": ["pun-aqua"]},
            {"n": "Nal Stop", "hindi": "नल स्टॉप", "ll": [73.8290, 18.5100], "l": ["pun-aqua"]},
            {"n": "Garware College", "hindi": "गरवारे कॉलेज", "ll": [73.8370, 18.5130], "l": ["pun-aqua"]},
            {"n": "Deccan Gymkhana", "hindi": "डेक्कन जिमखाना", "ll": [73.8440, 18.5170], "l": ["pun-aqua"]},
            {"n": "Chhatrapati Sambhaji Udyan", "hindi": "छत्रपती संभाजी उद्यान", "ll": [73.8490, 18.5210], "l": ["pun-aqua"]},
            {"n": "PMC", "hindi": "पीएमसी (पुणे महानगरपालिका)", "ll": [73.8530, 18.5240], "l": ["pun-aqua"]},
            {"n": "Mangalwar Peth", "hindi": "मंगळवार पेठ", "ll": [73.8640, 18.5280], "l": ["pun-aqua"]},
            {"n": "Pune Railway Station", "hindi": "पुणे रेलवे स्टेशन", "ll": [73.8730, 18.5280], "l": ["pun-aqua"], "interchange": True},
            {"n": "Ruby Hall Clinic", "hindi": "रूबी हॉल क्लिनिक", "ll": [73.8820, 18.5300], "l": ["pun-aqua"]},
            {"n": "Bund Garden", "hindi": "बंड गार्डन", "ll": [73.8900, 18.5340], "l": ["pun-aqua"]},
            {"n": "Yerawada", "hindi": "यरवडा", "ll": [73.8990, 18.5420], "l": ["pun-aqua"]},
            {"n": "Kalyani Nagar", "hindi": "कल्याणी नगर", "ll": [73.9080, 18.5480], "l": ["pun-aqua"]},
            {"n": "Ramwadi", "hindi": "रामवाडी", "ll": [73.9180, 18.5530], "l": ["pun-aqua"]},
        ],
        "links": []
    },
    "lucknow": {
        "name": "Lucknow Metro (UPMRC)",
        "hindi": "लखनऊ मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[80.88, 26.88], [80.93, 26.86], [80.96, 26.84], [80.99, 26.82]]}, # Gomti River
            ],
            "roads": [
                {"c": 3, "g": [[80.88, 26.76], [80.92, 26.83], [80.94, 26.87], [80.98, 26.89]]}, # Kanpur Road - Faizabad Road
            ],
            "places": [
                {"n": "Chaudhary Charan Singh Airport", "ll": [80.883, 26.765], "r": 5},
                {"n": "Charbagh Heritage Railway", "ll": [80.922, 26.832], "r": 5},
                {"n": "Hazratganj Cultural Heart", "ll": [80.945, 26.852], "r": 4},
                {"n": "Bara Imambara", "ll": [80.912, 26.869], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "lko-red", "nm": "Red Line (North-South: CCS Airport - Munshi Pulia)", "c": "#dc2626",
                "seq": ["CCS Airport", "Amausi", "Transport Nagar LKO", "Krishna Nagar", "Singar Nagar", "Alambagh", "Alambagh Bus Station", "Mawaiya", "Durgapuri", "Charbagh", "Hussainganj", "Sachivalaya", "Hazratganj", "KD Singh Babu Stadium", "Vishwavidyalaya LKO", "IT Chauraha", "Badshahnagar", "Mahanagar", "Dandiya", "Indiranagar LKO", "Munshi Pulia"]
            }
        ],
        "stations": [
            {"n": "CCS Airport", "hindi": "चौधरी चरण सिंह एयरपोर्ट", "ll": [80.8830, 26.7650], "l": ["lko-red"]},
            {"n": "Amausi", "hindi": "अमौसी", "ll": [80.8890, 26.7780], "l": ["lko-red"]},
            {"n": "Transport Nagar LKO", "hindi": "ट्रांसपोर्ट नगर", "ll": [80.8950, 26.7900], "l": ["lko-red"]},
            {"n": "Krishna Nagar", "hindi": "कृष्णा नगर", "ll": [80.9010, 26.8010], "l": ["lko-red"]},
            {"n": "Singar Nagar", "hindi": "सिंगार नगर", "ll": [80.9060, 26.8100], "l": ["lko-red"]},
            {"n": "Alambagh", "hindi": "आलमबाग", "ll": [80.9110, 26.8180], "l": ["lko-red"]},
            {"n": "Alambagh Bus Station", "hindi": "आलमबाग बस स्टेशन", "ll": [80.9150, 26.8230], "l": ["lko-red"]},
            {"n": "Mawaiya", "hindi": "मवैया", "ll": [80.9180, 26.8270], "l": ["lko-red"]},
            {"n": "Durgapuri", "hindi": "दुर्गापुरी", "ll": [80.9200, 26.8300], "l": ["lko-red"]},
            {"n": "Charbagh", "hindi": "चारबाग रेलवे स्टेशन", "ll": [80.9220, 26.8320], "l": ["lko-red"], "interchange": True},
            {"n": "Hussainganj", "hindi": "हुसैनगंज", "ll": [80.9310, 26.8400], "l": ["lko-red"]},
            {"n": "Sachivalaya", "hindi": "सचिवालय (विधान सभा)", "ll": [80.9380, 26.8460], "l": ["lko-red"]},
            {"n": "Hazratganj", "hindi": "हजरतगंज", "ll": [80.9450, 26.8520], "l": ["lko-red"]},
            {"n": "KD Singh Babu Stadium", "hindi": "केडी सिंह बाबू स्टेडियम", "ll": [80.9420, 26.8590], "l": ["lko-red"]},
            {"n": "Vishwavidyalaya LKO", "hindi": "लखनऊ विश्वविद्यालय", "ll": [80.9380, 26.8680], "l": ["lko-red"]},
            {"n": "IT Chauraha", "hindi": "आईटी चौराहा", "ll": [80.9410, 26.8750], "l": ["lko-red"]},
            {"n": "Badshahnagar", "hindi": "बादशाहनगर रेलवे स्टेशन", "ll": [80.9520, 26.8770], "l": ["lko-red"], "interchange": True},
            {"n": "Mahanagar", "hindi": "महानगर", "ll": [80.9630, 26.8790], "l": ["lko-red"]},
            {"n": "Dandiya", "hindi": "डांडिया", "ll": [80.9730, 26.8820], "l": ["lko-red"]},
            {"n": "Indiranagar LKO", "hindi": "इंदिरानगर", "ll": [80.9830, 26.8840], "l": ["lko-red"]},
            {"n": "Munshi Pulia", "hindi": "मुंशी पुलिया", "ll": [80.9920, 26.8870], "l": ["lko-red"]},
        ],
        "links": []
    },
    "kanpur": {
        "name": "Kanpur Metro (UPMRC)",
        "hindi": "कानपुर मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[80.25, 26.54], [80.32, 26.50], [80.38, 26.47]]}, # Ganga River
            ],
            "roads": [
                {"c": 3, "g": [[80.23, 26.51], [80.30, 26.49], [80.36, 26.46], [80.35, 26.42]]}, # Grand Trunk (GT) Road
            ],
            "places": [
                {"n": "IIT Kanpur Premier Tech Institute", "ll": [80.232, 26.512], "r": 5},
                {"n": "Kanpur Central Terminal", "ll": [80.352, 26.454], "r": 5},
                {"n": "Motijheel Civic Core", "ll": [80.312, 26.481], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "knp-orange", "nm": "Orange Line (Line 1: IIT Kanpur - Naubasta)", "c": "#ea580c",
                "seq": ["IIT Kanpur", "Kalyanpur", "SPM Hospital", "CSJM University", "Gurudev Chauraha", "Geeta Nagar", "Rawatpur", "LLR Hospital", "Moti Jheel", "Chunniganj", "Naveen Market", "Bada Chauraha", "Nayaganj", "Kanpur Central", "Jhakarkati Bus Terminal", "Transport Nagar KNP", "Baradevi", "Kidwai Nagar", "Vasant Vihar", "Baudh Nagar", "Naubasta"]
            }
        ],
        "stations": [
            {"n": "IIT Kanpur", "hindi": "आईआईटी कानपुर", "ll": [80.2320, 26.5120], "l": ["knp-orange"]},
            {"n": "Kalyanpur", "hindi": "कल्याणपुर", "ll": [80.2450, 26.5080], "l": ["knp-orange"]},
            {"n": "SPM Hospital", "hindi": "एसपीएम अस्पताल", "ll": [80.2580, 26.5040], "l": ["knp-orange"]},
            {"n": "CSJM University", "hindi": "सीएसजेएम कानपुर यूनिवर्सिटी", "ll": [80.2700, 26.5000], "l": ["knp-orange"]},
            {"n": "Gurudev Chauraha", "hindi": "गुरुदेव चौराहा", "ll": [80.2820, 26.4950], "l": ["knp-orange"]},
            {"n": "Geeta Nagar", "hindi": "गीता नगर", "ll": [80.2930, 26.4900], "l": ["knp-orange"]},
            {"n": "Rawatpur", "hindi": "रावतपुर रेलवे स्टेशन", "ll": [80.3020, 26.4860], "l": ["knp-orange"], "interchange": True},
            {"n": "LLR Hospital", "hindi": "एलएलआर हैलट अस्पताल", "ll": [80.3070, 26.4840], "l": ["knp-orange"]},
            {"n": "Moti Jheel", "hindi": "मोती झील", "ll": [80.3120, 26.4810], "l": ["knp-orange"]},
            {"n": "Chunniganj", "hindi": "चुन्नीगंज", "ll": [80.3250, 26.4750], "l": ["knp-orange"]},
            {"n": "Naveen Market", "hindi": "नवीन मार्केट", "ll": [80.3340, 26.4700], "l": ["knp-orange"]},
            {"n": "Bada Chauraha", "hindi": "बड़ा चौराहा", "ll": [80.3420, 26.4650], "l": ["knp-orange"]},
            {"n": "Nayaganj", "hindi": "नयागंज", "ll": [80.3480, 26.4590], "l": ["knp-orange"]},
            {"n": "Kanpur Central", "hindi": "कानपुर सेंट्रल रेलवे स्टेशन", "ll": [80.3520, 26.4540], "l": ["knp-orange"], "interchange": True},
            {"n": "Jhakarkati Bus Terminal", "hindi": "झकरकटी बस टर्मिनल", "ll": [80.3540, 26.4460], "l": ["knp-orange"]},
            {"n": "Transport Nagar KNP", "hindi": "ट्रांसपोर्ट नगर कानपुर", "ll": [80.3550, 26.4380], "l": ["knp-orange"]},
            {"n": "Baradevi", "hindi": "बारादेवी", "ll": [80.3540, 26.4300], "l": ["knp-orange"]},
            {"n": "Kidwai Nagar", "hindi": "किदवई नगर", "ll": [80.3520, 26.4220], "l": ["knp-orange"]},
            {"n": "Vasant Vihar", "hindi": "वसंत विहार", "ll": [80.3500, 26.4150], "l": ["knp-orange"]},
            {"n": "Baudh Nagar", "hindi": "बौद्ध नगर", "ll": [80.3480, 26.4080], "l": ["knp-orange"]},
            {"n": "Naubasta", "hindi": "नौबस्ता", "ll": [80.3450, 26.4010], "l": ["knp-orange"]},
        ],
        "links": []
    },
    "agra": {
        "name": "Agra Metro (UPMRC)",
        "hindi": "आगरा मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[77.98, 27.22], [78.02, 27.19], [78.06, 27.17]]}, # Yamuna River
            ],
            "roads": [
                {"c": 3, "g": [[78.06, 27.15], [78.04, 27.16], [78.01, 27.18], [77.97, 27.21]]}, # Fatehabad Road - MG Road
            ],
            "places": [
                {"n": "Taj Mahal UNESCO Wonder", "ll": [78.042, 27.175], "r": 5},
                {"n": "Agra Fort World Heritage", "ll": [78.021, 27.179], "r": 5},
                {"n": "Mankameshwar Ancient Temple", "ll": [78.015, 27.185], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "agr-yellow", "nm": "Yellow Line (Taj East Gate - Sikandra)", "c": "#eab308",
                "seq": ["Taj East Gate", "Captain Shubham Gupta", "Taj Mahal", "Agra Fort", "Jama Masjid Agra", "SN Medical College", "Agra College", "Raja Ki Mandi", "RBS College", "Sikandra"]
            }
        ],
        "stations": [
            {"n": "Taj East Gate", "hindi": "ताज ईस्ट गेट", "ll": [78.0620, 27.1620], "l": ["agr-yellow"]},
            {"n": "Captain Shubham Gupta", "hindi": "कैप्टन शुभम गुप्ता (फतेहाबाद रोड)", "ll": [78.0500, 27.1650], "l": ["agr-yellow"]},
            {"n": "Taj Mahal", "hindi": "ताज महल स्टेशन", "ll": [78.0400, 27.1710], "l": ["agr-yellow"]},
            {"n": "Agra Fort", "hindi": "आगरा फोर्ट", "ll": [78.0240, 27.1780], "l": ["agr-yellow"], "interchange": True},
            {"n": "Jama Masjid Agra", "hindi": "जामा मस्जिद (मनकामेश्वर)", "ll": [78.0160, 27.1840], "l": ["agr-yellow"]},
            {"n": "SN Medical College", "hindi": "एसएन मेडिकल कॉलेज", "ll": [78.0080, 27.1880], "l": ["agr-yellow"]},
            {"n": "Agra College", "hindi": "आगरा कॉलेज", "ll": [78.0010, 27.1920], "l": ["agr-yellow"]},
            {"n": "Raja Ki Mandi", "hindi": "राजा की मंडी रेलवे स्टेशन", "ll": [77.9920, 27.1990], "l": ["agr-yellow"], "interchange": True},
            {"n": "RBS College", "hindi": "आरबीएस कॉलेज", "ll": [77.9820, 27.2060], "l": ["agr-yellow"]},
            {"n": "Sikandra", "hindi": "सिकंदरा (अकबर का मकबरा)", "ll": [77.9540, 27.2210], "l": ["agr-yellow"]},
        ],
        "links": []
    },
    "jaipur": {
        "name": "Jaipur Metro (JMRC)",
        "hindi": "जयपुर मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[75.76, 26.86], [75.78, 26.89], [75.80, 26.93]]}, # Dravyavati River
            ],
            "roads": [
                {"c": 3, "g": [[75.74, 26.88], [75.78, 26.91], [75.82, 26.92]]}, # Ajmer Road - MI Road
            ],
            "places": [
                {"n": "Hawa Mahal & City Palace", "ll": [75.826, 26.924], "r": 5},
                {"n": "Jaipur Junction Railway", "ll": [75.789, 26.920], "r": 5},
                {"n": "Albert Hall Museum", "ll": [75.819, 26.911], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "jai-pink", "nm": "Pink Line (Phase 1: Mansarovar - Badi Chaupar)", "c": "#ec4899",
                "seq": ["Mansarovar", "New Aatish Market", "Vivek Vihar", "Shyam Nagar", "Ram Nagar", "Civil Lines Jaipur", "Railway Station Jaipur", "Sindhi Camp", "Chandpole", "Chhoti Chaupar", "Badi Chaupar"]
            }
        ],
        "stations": [
            {"n": "Mansarovar", "hindi": "मानसरोवर", "ll": [75.7520, 26.8790], "l": ["jai-pink"]},
            {"n": "New Aatish Market", "hindi": "न्यू आतिश मार्केट", "ll": [75.7610, 26.8860], "l": ["jai-pink"]},
            {"n": "Vivek Vihar", "hindi": "विवेक विहार", "ll": [75.7680, 26.8930], "l": ["jai-pink"]},
            {"n": "Shyam Nagar", "hindi": "श्याम नगर", "ll": [75.7720, 26.8990], "l": ["jai-pink"]},
            {"n": "Ram Nagar", "hindi": "राम नगर", "ll": [75.7760, 26.9060], "l": ["jai-pink"]},
            {"n": "Civil Lines Jaipur", "hindi": "सिविल लाइंस", "ll": [75.7810, 26.9120], "l": ["jai-pink"]},
            {"n": "Railway Station Jaipur", "hindi": "जयपुर रेलवे स्टेशन", "ll": [75.7890, 26.9200], "l": ["jai-pink"], "interchange": True},
            {"n": "Sindhi Camp", "hindi": "सिंधी कैंप बस टर्मिनल", "ll": [75.7980, 26.9230], "l": ["jai-pink"], "interchange": True},
            {"n": "Chandpole", "hindi": "चांदपोल (हेरिटेज गेट)", "ll": [75.8110, 26.9240], "l": ["jai-pink"]},
            {"n": "Chhoti Chaupar", "hindi": "छोटी चौपड़", "ll": [75.8200, 26.9240], "l": ["jai-pink"]},
            {"n": "Badi Chaupar", "hindi": "बड़ी चौपड़ (हवा महल)", "ll": [75.8280, 26.9240], "l": ["jai-pink"]},
        ],
        "links": []
    },
    "nagpur": {
        "name": "Nagpur Metro (Maha Metro)",
        "hindi": "नागपूर मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[79.03, 21.14], [79.08, 21.13], [79.12, 21.14]]}, # Nag River
            ],
            "roads": [
                {"c": 3, "g": [[79.07, 21.05], [79.08, 21.12], [79.08, 21.19]]}, # Wardha Road (N-S)
                {"c": 3, "g": [[79.01, 21.13], [79.08, 21.14], [79.15, 21.15]]}, # Central Avenue (E-W)
            ],
            "places": [
                {"n": "Zero Mile Stone Freedom Park", "ll": [79.082, 21.148], "r": 5},
                {"n": "Sitabuldi Interchange Atrium", "ll": [79.084, 21.146], "r": 5},
                {"n": "Deekshabhoomi Sacred Monument", "ll": [79.068, 21.128], "r": 5},
            ]
        },
        "lines": [
            {
                "id": "nag-orange", "nm": "Orange Line (North-South: Automotive Square - Khapri)", "c": "#ea580c",
                "seq": ["Automotive Square", "Nari Road", "Indora Square", "Kadvi Chowk", "GaddiGodam Square", "Kasturchand Park", "Zero Mile Freedom Park", "Sitabuldi Nagpur", "Congress Nagar", "Rahate Colony", "Ajni Square", "Chhatrapati Square", "Jaiprakash Nagar", "Ujjwal Nagar", "Airport Nagpur", "Airport South", "New Airport", "Khapri"]
            },
            {
                "id": "nag-aqua", "nm": "Aqua Line (East-West: Prajapati Nagar - Lokmanya Nagar)", "c": "#06b6d4",
                "seq": ["Prajapati Nagar", "Vaishno Devi Square", "Ambedkar Square", "Telephone Exchange", "Chittar Oli Square", "Agrasen Square", "Dosar Vaisya Square", "Nagpur Railway Station", "Cotton Market", "Sitabuldi Nagpur", "Jhansi Rani Square", "Institute of Engineers", "Shankar Nagar Square", "LAD Square", "Dharampeth College", "Subhash Nagar Nagpur", "Rachana Ring Road", "Vasudev Nagar", "Bansi Nagar", "Lokmanya Nagar"]
            }
        ],
        "stations": [
            # Orange Line
            {"n": "Automotive Square", "hindi": "ऑटोमोटिव चौक", "ll": [79.0860, 21.1960], "l": ["nag-orange"]},
            {"n": "Nari Road", "hindi": "नारी रोड", "ll": [79.0860, 21.1870], "l": ["nag-orange"]},
            {"n": "Indora Square", "hindi": "इंदोरा चौक", "ll": [79.0850, 21.1780], "l": ["nag-orange"]},
            {"n": "Kadvi Chowk", "hindi": "कड़वी चौक", "ll": [79.0850, 21.1690], "l": ["nag-orange"]},
            {"n": "GaddiGodam Square", "hindi": "गड्डीगोदाम चौक", "ll": [79.0840, 21.1600], "l": ["nag-orange"]},
            {"n": "Kasturchand Park", "hindi": "कस्तूरचंद पार्क", "ll": [79.0830, 21.1540], "l": ["nag-orange"]},
            {"n": "Zero Mile Freedom Park", "hindi": "जीरो माइल फ्रीडम पार्क", "ll": [79.0820, 21.1480], "l": ["nag-orange"]},
            {"n": "Sitabuldi Nagpur", "hindi": "सीताबर्डी (सेंट्रल इंटरचेंज)", "ll": [79.0840, 21.1460], "l": ["nag-orange", "nag-aqua"], "interchange": True},
            {"n": "Congress Nagar", "hindi": "कांग्रेस नगर", "ll": [79.0820, 21.1370], "l": ["nag-orange"]},
            {"n": "Rahate Colony", "hindi": "राहाटे कॉलोनी", "ll": [79.0800, 21.1290], "l": ["nag-orange"]},
            {"n": "Ajni Square", "hindi": "अजनी चौक", "ll": [79.0780, 21.1200], "l": ["nag-orange"], "interchange": True},
            {"n": "Chhatrapati Square", "hindi": "छत्रपती चौक", "ll": [79.0760, 21.1110], "l": ["nag-orange"]},
            {"n": "Jaiprakash Nagar", "hindi": "जयप्रकाश नगर", "ll": [79.0740, 21.1020], "l": ["nag-orange"]},
            {"n": "Ujjwal Nagar", "hindi": "उज्ज्वल नगर", "ll": [79.0720, 21.0930], "l": ["nag-orange"]},
            {"n": "Airport Nagpur", "hindi": "नागपुर एयरपोर्ट", "ll": [79.0700, 21.0840], "l": ["nag-orange"]},
            {"n": "Airport South", "hindi": "एयरपोर्ट साउथ", "ll": [79.0680, 21.0740], "l": ["nag-orange"]},
            {"n": "New Airport", "hindi": "न्यू एयरपोर्ट", "ll": [79.0660, 21.0640], "l": ["nag-orange"]},
            {"n": "Khapri", "hindi": "खापरी", "ll": [79.0640, 21.0540], "l": ["nag-orange"]},
            # Aqua Line
            {"n": "Prajapati Nagar", "hindi": "प्रजापति नगर", "ll": [79.1550, 21.1520], "l": ["nag-aqua"]},
            {"n": "Vaishno Devi Square", "hindi": "वैष्णो देवी चौक", "ll": [79.1450, 21.1510], "l": ["nag-aqua"]},
            {"n": "Ambedkar Square", "hindi": "आंबेडकर चौक", "ll": [79.1350, 21.1500], "l": ["nag-aqua"]},
            {"n": "Telephone Exchange", "hindi": "टेलीफोन एक्सचेंज", "ll": [79.1250, 21.1490], "l": ["nag-aqua"]},
            {"n": "Chittar Oli Square", "hindi": "चित्तार ओली चौक", "ll": [79.1150, 21.1480], "l": ["nag-aqua"]},
            {"n": "Agrasen Square", "hindi": "अग्रसेन चौक", "ll": [79.1050, 21.1470], "l": ["nag-aqua"]},
            {"n": "Dosar Vaisya Square", "hindi": "दोसर वैश्य चौक", "ll": [79.0960, 21.1460], "l": ["nag-aqua"]},
            {"n": "Nagpur Railway Station", "hindi": "नागपुर रेलवे स्टेशन", "ll": [79.0900, 21.1460], "l": ["nag-aqua"], "interchange": True},
            {"n": "Cotton Market", "hindi": "कॉटन मार्केट", "ll": [79.0870, 21.1460], "l": ["nag-aqua"]},
            {"n": "Jhansi Rani Square", "hindi": "झांसी रानी चौक", "ll": [79.0760, 21.1440], "l": ["nag-aqua"]},
            {"n": "Institute of Engineers", "hindi": "इंस्टीट्यूट ऑफ इंजीनियर्स", "ll": [79.0680, 21.1420], "l": ["nag-aqua"]},
            {"n": "Shankar Nagar Square", "hindi": "शंकर नगर चौक", "ll": [79.0590, 21.1400], "l": ["nag-aqua"]},
            {"n": "LAD Square", "hindi": "एलएडी चौक", "ll": [79.0510, 21.1380], "l": ["nag-aqua"]},
            {"n": "Dharampeth College", "hindi": "धरमपेठ कॉलेज", "ll": [79.0430, 21.1360], "l": ["nag-aqua"]},
            {"n": "Subhash Nagar Nagpur", "hindi": "सुभाष नगर", "ll": [79.0350, 21.1340], "l": ["nag-aqua"]},
            {"n": "Rachana Ring Road", "hindi": "रचना रिंग रोड", "ll": [79.0270, 21.1320], "l": ["nag-aqua"]},
            {"n": "Vasudev Nagar", "hindi": "वासुदेव नगर", "ll": [79.0190, 21.1300], "l": ["nag-aqua"]},
            {"n": "Bansi Nagar", "hindi": "बंसी नगर", "ll": [79.0110, 21.1280], "l": ["nag-aqua"]},
            {"n": "Lokmanya Nagar", "hindi": "लोकमान्य नगर", "ll": [79.0030, 21.1260], "l": ["nag-aqua"]},
        ],
        "links": []
    },
    "noida": {
        "name": "Noida & Greater Noida Metro (NMRC Aqua Line)",
        "hindi": "नोएडा मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[77.37, 28.60], [77.41, 28.53], [77.45, 28.45], [77.48, 28.38]]}, # Hindon River
            ],
            "roads": [
                {"c": 3, "g": [[77.36, 28.57], [77.42, 28.50], [77.48, 28.45], [77.53, 28.43]]}, # Noida-Gr Noida Expressway
            ],
            "places": [
                {"n": "Pari Chowk Landmark", "ll": [77.502, 28.463], "r": 5},
                {"n": "Knowledge Park Higher Education Hub", "ll": [77.485, 28.466], "r": 4},
                {"n": "NSEZ Export Processing Zone", "ll": [77.404, 28.532], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "noi-aqua", "nm": "Aqua Line (Noida Sector 51 - Depot Greater Noida)", "c": "#06b6d4",
                "seq": ["Noida Sector 51", "Sector 50", "Sector 76", "Sector 101", "Sector 81", "NSEZ", "Sector 83", "Sector 137", "Sector 142", "Sector 143", "Sector 144", "Sector 145", "Sector 146", "Sector 147", "Sector 148", "Knowledge Park II", "Pari Chowk", "Alpha 1", "Delta 1", "GNIDA Office", "Depot Greater Noida"]
            }
        ],
        "stations": [
            {"n": "Noida Sector 51", "hindi": "नोएडा सेक्टर 51", "ll": [77.3680, 28.5780], "l": ["noi-aqua"], "interchange": True},
            {"n": "Sector 50", "hindi": "सेक्टर 50", "ll": [77.3730, 28.5710], "l": ["noi-aqua"]},
            {"n": "Sector 76", "hindi": "सेक्टर 76", "ll": [77.3800, 28.5620], "l": ["noi-aqua"]},
            {"n": "Sector 101", "hindi": "सेक्टर 101", "ll": [77.3870, 28.5520], "l": ["noi-aqua"]},
            {"n": "Sector 81", "hindi": "सेक्टर 81", "ll": [77.3940, 28.5420], "l": ["noi-aqua"]},
            {"n": "NSEZ", "hindi": "एनएसईजेड स्पेशल इकोनॉमिक जोन", "ll": [77.4040, 28.5320], "l": ["noi-aqua"]},
            {"n": "Sector 83", "hindi": "सेक्टर 83", "ll": [77.4110, 28.5220], "l": ["noi-aqua"]},
            {"n": "Sector 137", "hindi": "सेक्टर 137", "ll": [77.4200, 28.5120], "l": ["noi-aqua"]},
            {"n": "Sector 142", "hindi": "सेक्टर 142", "ll": [77.4280, 28.5020], "l": ["noi-aqua"]},
            {"n": "Sector 143", "hindi": "सेक्टर 143", "ll": [77.4360, 28.4940], "l": ["noi-aqua"]},
            {"n": "Sector 144", "hindi": "सेक्टर 144", "ll": [77.4440, 28.4870], "l": ["noi-aqua"]},
            {"n": "Sector 145", "hindi": "सेक्टर 145", "ll": [77.4520, 28.4810], "l": ["noi-aqua"]},
            {"n": "Sector 146", "hindi": "सेक्टर 146", "ll": [77.4610, 28.4750], "l": ["noi-aqua"]},
            {"n": "Sector 147", "hindi": "सेक्टर 147", "ll": [77.4700, 28.4700], "l": ["noi-aqua"]},
            {"n": "Sector 148", "hindi": "सेक्टर 148", "ll": [77.4780, 28.4670], "l": ["noi-aqua"]},
            {"n": "Knowledge Park II", "hindi": "नॉलेज पार्क 2", "ll": [77.4850, 28.4660], "l": ["noi-aqua"]},
            {"n": "Pari Chowk", "hindi": "परी चौक ग्रेटर नोएडा", "ll": [77.5020, 28.4630], "l": ["noi-aqua"], "interchange": True},
            {"n": "Alpha 1", "hindi": "अल्फा 1", "ll": [77.5120, 28.4600], "l": ["noi-aqua"]},
            {"n": "Delta 1", "hindi": "डेल्टा 1", "ll": [77.5200, 28.4520], "l": ["noi-aqua"]},
            {"n": "GNIDA Office", "hindi": "ग्रेनो प्राधिकरण कार्यालय", "ll": [77.5250, 28.4440], "l": ["noi-aqua"]},
            {"n": "Depot Greater Noida", "hindi": "डिपो ग्रेटर नोएडा", "ll": [77.5270, 28.4350], "l": ["noi-aqua"]},
        ],
        "links": []
    },
    "navi-mumbai": {
        "name": "Navi Mumbai Metro (CIDCO Line 1)",
        "hindi": "नवी मुंबई मेट्रो",
        "base": {
            "water": [
                {"t": "river", "g": [[73.01, 19.01], [73.03, 19.04], [73.05, 19.06]]}, # Panvel Creek
            ],
            "roads": [
                {"c": 3, "g": [[73.03, 19.02], [73.06, 19.05], [73.09, 19.08]]}, # Sion-Panvel Highway
            ],
            "places": [
                {"n": "CBD Belapur Financial Hub", "ll": [73.038, 19.018], "r": 5},
                {"n": "Central Park Kharghar", "ll": [73.066, 19.052], "r": 4},
                {"n": "Utsav Chowk Kharghar", "ll": [73.054, 19.038], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "nm-l1", "nm": "Line 1 (CBD Belapur - Pendhar)", "c": "#0284c7",
                "seq": ["Belapur Terminal", "Sector 7 Belapur", "CIDCO Science Park", "Utsav Chowk", "Sector 11 Kharghar", "Sector 14 Kharghar", "Central Park Kharghar", "Pethpada", "Sector 34 Kharghar", "Panchanand", "Pendhar"]
            }
        ],
        "stations": [
            {"n": "Belapur Terminal", "hindi": "सीबीडी बेलापुर टर्मिनल", "ll": [73.0380, 19.0180], "l": ["nm-l1"], "interchange": True},
            {"n": "Sector 7 Belapur", "hindi": "सेक्टर 7 बेलापुर", "ll": [73.0420, 19.0230], "l": ["nm-l1"]},
            {"n": "CIDCO Science Park", "hindi": "सिडको साइंस पार्क", "ll": [73.0470, 19.0300], "l": ["nm-l1"]},
            {"n": "Utsav Chowk", "hindi": "उत्सव चौक", "ll": [73.0540, 19.0380], "l": ["nm-l1"]},
            {"n": "Sector 11 Kharghar", "hindi": "सेक्टर 11 खारघर", "ll": [73.0580, 19.0430], "l": ["nm-l1"]},
            {"n": "Sector 14 Kharghar", "hindi": "सेक्टर 14 खारघर", "ll": [73.0620, 19.0480], "l": ["nm-l1"]},
            {"n": "Central Park Kharghar", "hindi": "सेंट्रल पार्क खारघर", "ll": [73.0660, 19.0520], "l": ["nm-l1"]},
            {"n": "Pethpada", "hindi": "पेठपाड़ा", "ll": [73.0720, 19.0580], "l": ["nm-l1"]},
            {"n": "Sector 34 Kharghar", "hindi": "सेक्टर 34 खारघर", "ll": [73.0780, 19.0640], "l": ["nm-l1"]},
            {"n": "Panchanand", "hindi": "पंचानंद", "ll": [73.0840, 19.0700], "l": ["nm-l1"]},
            {"n": "Pendhar", "hindi": "पेंधर", "ll": [73.0910, 20.0760], "l": ["nm-l1"]},
        ],
        "links": []
    },
    "bhopal-indore": {
        "name": "Madhya Pradesh Metro (Bhopal & Indore - MPMRCL)",
        "hindi": "मध्य प्रदेश मेट्रो (भोपाल एवं इंदौर)",
        "base": {
            "water": [
                {"t": "river", "g": [[77.34, 23.25], [77.39, 23.24], [77.42, 23.23]]}, # Upper Lake Bhopal
                {"t": "river", "g": [[75.84, 22.70], [75.86, 22.73], [75.87, 22.76]]}, # Khan River Indore
            ],
            "roads": [
                {"c": 3, "g": [[77.40, 23.28], [77.43, 23.23], [77.45, 23.19]]}, # Hoshangabad Road Bhopal
                {"c": 3, "g": [[75.81, 22.72], [75.86, 22.72], [75.90, 22.74]]}, # AB Road Indore
            ],
            "places": [
                {"n": "AIIMS Bhopal Medical Complex", "ll": [77.456, 23.204], "r": 5},
                {"n": "Rani Kamlapati Station (World Class)", "ll": [77.441, 23.220], "r": 5},
                {"n": "Rajwada Historic Royal Palace Indore", "ll": [75.856, 22.718], "r": 5},
                {"n": "Indore Super Corridor", "ll": [75.820, 22.750], "r": 4},
            ]
        },
        "lines": [
            {
                "id": "bhp-orange", "nm": "Bhopal Orange Line (Karond - AIIMS Bhopal)", "c": "#ea580c",
                "seq": ["Karond", "Bhopal Railway Station", "Nadra Bus Stand", "Subhash Nagar Bhopal", "Kendriya Vidyalaya Bhopal", "DB City Mall", "MP Nagar Zone 1", "Rani Kamlapati", "Alkapuri Bhopal", "AIIMS Bhopal"]
            },
            {
                "id": "ind-yellow", "nm": "Indore Yellow Line (Indore Ring: Railway Station - Airport - Palasia)", "c": "#eab308",
                "seq": ["Indore Railway Station", "Rajwada", "Bada Ganpati", "Airport Indore", "Gandhi Nagar Indore", "Super Corridor 3", "Super Corridor 1", "MR 10 Road", "Vijay Nagar Indore", "Bengali Square", "Palasia"]
            }
        ],
        "stations": [
            # Bhopal Orange Line
            {"n": "Karond", "hindi": "करोंद चौराहा", "ll": [77.3980, 23.3050], "l": ["bhp-orange"]},
            {"n": "Bhopal Railway Station", "hindi": "भोपाल जंक्शन रेलवे स्टेशन", "ll": [77.4110, 23.2680], "l": ["bhp-orange"], "interchange": True},
            {"n": "Nadra Bus Stand", "hindi": "नादरा बस स्टैंड", "ll": [77.4150, 23.2610], "l": ["bhp-orange"]},
            {"n": "Subhash Nagar Bhopal", "hindi": "सुभाष नगर", "ll": [77.4250, 23.2480], "l": ["bhp-orange"]},
            {"n": "Kendriya Vidyalaya Bhopal", "hindi": "केंद्रीय विद्यालय", "ll": [77.4310, 23.2410], "l": ["bhp-orange"]},
            {"n": "DB City Mall", "hindi": "डीबी सिटी मॉल", "ll": [77.4350, 23.2350], "l": ["bhp-orange"]},
            {"n": "MP Nagar Zone 1", "hindi": "एमपी नगर जोन 1", "ll": [77.4380, 23.2280], "l": ["bhp-orange"]},
            {"n": "Rani Kamlapati", "hindi": "रानी कमलापति (हबीबगंज)", "ll": [77.4410, 23.2200], "l": ["bhp-orange"], "interchange": True},
            {"n": "Alkapuri Bhopal", "hindi": "अलकापुरी", "ll": [77.4490, 23.2110], "l": ["bhp-orange"]},
            {"n": "AIIMS Bhopal", "hindi": "एम्स भोपाल", "ll": [77.4560, 23.2040], "l": ["bhp-orange"]},
            # Indore Yellow Line
            {"n": "Indore Railway Station", "hindi": "इंदौर जंक्शन रेलवे स्टेशन", "ll": [75.8670, 22.7160], "l": ["ind-yellow"], "interchange": True},
            {"n": "Rajwada", "hindi": "राजवाड़ा पैलेस", "ll": [75.8560, 22.7180], "l": ["ind-yellow"]},
            {"n": "Bada Ganpati", "hindi": "बड़ा गणपति", "ll": [75.8450, 22.7210], "l": ["ind-yellow"]},
            {"n": "Airport Indore", "hindi": "देवी अहिल्याबाई होल्कर एयरपोर्ट", "ll": [75.8050, 22.7240], "l": ["ind-yellow"]},
            {"n": "Gandhi Nagar Indore", "hindi": "गांधी नगर", "ll": [75.8080, 22.7410], "l": ["ind-yellow"]},
            {"n": "Super Corridor 3", "hindi": "सुपर कॉरिडोर 3", "ll": [75.8190, 22.7530], "l": ["ind-yellow"]},
            {"n": "Super Corridor 1", "hindi": "सुपर कॉरिडोर 1", "ll": [75.8320, 22.7620], "l": ["ind-yellow"]},
            {"n": "MR 10 Road", "hindi": "एमआर 10 रोड", "ll": [75.8520, 22.7660], "l": ["ind-yellow"]},
            {"n": "Vijay Nagar Indore", "hindi": "विजय नगर", "ll": [75.8850, 22.7540], "l": ["ind-yellow"]},
            {"n": "Bengali Square", "hindi": "बंगाली चौराहा", "ll": [75.9010, 22.7280], "l": ["ind-yellow"]},
            {"n": "Palasia", "hindi": "पलासिया", "ll": [75.8850, 22.7210], "l": ["ind-yellow"]},
        ],
        "links": []
    }
}

# Generate segments automatically from station sequences
for cid, city in CITIES.items():
    st_dict = {s["n"]: s for s in city["stations"]}
    for line in city["lines"]:
        seg = []
        for sname in line.get("seq", []):
            if sname in st_dict:
                seg.append(st_dict[sname]["ll"])
        line["segs"] = [seg] if len(seg) > 1 else []

# Now write out all_city_packs.js
code = '''// All 17 Indian Metro Networks: Authentic Cartographic Packs & Station Coordinates
// Sources: OpenStreetMap (ODbL), DMRC influence zones, KMRCL underwater Hooghly alignment,
// MMRDA, BMRCL, CMRL, HMRL, KMRL, GMRC, Maha Metro, UPMRC, JMRC, NMRC, CIDCO, MPMRCL.

import packDataDelhi from './delhi_metro_pack.json';

export const px = l => (l + 180) / 360;
export const py = l => {
  const s = Math.sin((l * Math.PI) / 180);
  return 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI);
};

const R2 = Math.PI / 180;
export function kmDist(a, b) {
  if (!a || !b || !a.ll || !b.ll) return 1.5;
  const dx = (b.ll[0] - a.ll[0]) * Math.cos(((a.ll[1] + b.ll[1]) / 2) * R2) * 111.32;
  const dy = (b.ll[1] - a.ll[1]) * 110.57;
  return Math.hypot(dx, dy);
}

export const projSegs = g => {
  const o = new Array(g.length);
  for (let i = 0; i < g.length; i++) o[i] = [px(g[i][0]), py(g[i][1])];
  return o;
};

export function preparePack(raw) {
  const lines = (raw.lines || []).map(l => ({
    ...l,
    P: (l.segs || []).map(projSegs),
  }));

  const stations = (raw.stations || []).map(s => ({
    ...s,
    P: [px(s.ll[0]), py(s.ll[1])],
    ix: s.l?.length > 1 || !!(raw.branchIx && raw.branchIx[s.n]) || !!s.interchange,
  }));

  const future = (raw.future || []).map(f => ({
    ...f,
    PZ: projSegs(f.zone || []),
    st: (f.st || []).map(s => ({ ...s, P: [px(s.ll[0]), py(s.ll[1])] })),
  }));

  const base = {
    bd: (raw.base?.bd || []).map(b => ({ ...b, P: (b.r || []).map(projSegs) })),
    water: (raw.base?.water || []).map(w => ({ ...w, P: projSegs(w.g || []) })),
    roads: (raw.base?.roads || []).map(r => ({ ...r, P: projSegs(r.g || []) })),
    rail: (raw.base?.rail || []).map(r => ({ ...r, P: projSegs(r.g || []) })),
    places: (raw.base?.places || []).map(p => ({ ...p, P: [px(p.ll[0]), py(p.ll[1])] })),
  };

  const lmap = Object.fromEntries(lines.map(l => [l.id, l]));
  const smap = Object.fromEntries(stations.map(s => [s.n, s]));
  const adj = {};

  function addEdge(a, b, line) {
    if (!smap[a] || !smap[b] || a === b) return;
    const d = kmDist(smap[a], smap[b]);
    (adj[a] = adj[a] || []).push({ to: b, line, km: d });
    (adj[b] = adj[b] || []).push({ to: a, line, km: d });
  }

  for (const l of lines) {
    for (const br of [l.seq, l.branch]) {
      if (br && Array.isArray(br)) {
        for (let i = 1; i < br.length; i++) addEdge(br[i - 1], br[i], l.id);
      }
    }
  }

  for (const p of (raw.links || [])) {
    addEdge(p[0], p[1], null);
  }

  return { raw, lines, stations, future, base, lmap, smap, adj };
}

export const CITY_RAW_DATA = ''' + json.dumps(CITIES, indent=2) + ''';

export const PREPARED_PACKS = {
  'delhi-ncr': preparePack(packDataDelhi),
};

for (const [cid, raw] of Object.entries(CITY_RAW_DATA)) {
  PREPARED_PACKS[cid] = preparePack(raw);
}

export function getCityPack(cityId) {
  return PREPARED_PACKS[cityId] || PREPARED_PACKS['delhi-ncr'];
}
'''

OUT_FILE.write_text(code, encoding="utf-8")
print(f"Generated {OUT_FILE} with {len(CITIES) + 1} city packs successfully!")
