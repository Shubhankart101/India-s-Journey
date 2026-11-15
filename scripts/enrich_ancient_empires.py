"""
Enrich ancient-empires.json with comprehensive battles, locations, and milestones for all 10 empires.
"""
import json
import os

ENRICHMENTS = {
    "mahajanapadas": {
        "capitals": [
            {"name": "Rajagriha (Magadha)", "x": 854.2, "y": -250.0, "role": "Magadhan cyclopean citadel and original capital", "desc": "Mountain-ringed capital of Magadha fortified with cyclopean stone masonry."},
            {"name": "Vaishali (Vajji)", "x": 853.0, "y": -259.0, "role": "Metropolis of the Licchavi republic and Gana-sangha assembly", "desc": "Capital of the Vajji confederacy, governed by an elected assembly of 7,707 rajas."},
            {"name": "Shravasti (Kosala)", "x": 820.0, "y": -275.0, "role": "Capital of Kosala on the Rapti River", "desc": "Flourishing commercial and political center of King Prasenajit; site of Jetavana monastery."},
            {"name": "Kaushambi (Vatsa)", "x": 814.0, "y": -253.0, "role": "Yamuna river trade nexus ruled by King Udayana", "desc": "Key transit hub where northern and southern trade routes intersected along the Yamuna."},
            {"name": "Ujjayini (Avanti)", "x": 757.8, "y": -231.8, "role": "Western trade junction on the Dakshinapatha highway", "desc": "Seat of King Chanda Pradyota, controlling the cotton routes and lapis/carnelian trade."},
            {"name": "Taxila (Gandhara)", "x": 728.2, "y": -337.4, "role": "Foremost pan-Asian Vedic university and northern trade crossroad", "desc": "Intellectual capital of Uttarapatha where Panini, Chanakya, and Jivaka studied."},
            {"name": "Champa (Anga)", "x": 869.8, "y": -252.3, "role": "Oceanic trade emporium on the Ganga-Champa confluence", "desc": "Wealthy riverine port trading silk, gems, and spices with Suvarnabhumi."},
            {"name": "Varanasi (Kasi)", "x": 830.0, "y": -253.2, "role": "Sacred metropolis famed for cotton textiles and brassware", "desc": "Ancient spiritual and commercial capital annexed alternately by Kosala and Magadha."},
            {"name": "Mathura (Surasena)", "x": 776.8, "y": -275.0, "role": "Yamuna commercial crossroads and Yadava republican center", "desc": "Heartland of the Surasena kingdom on the junction of Uttarapatha and Dakshinapatha."},
            {"name": "Ahichchhatra (Panchala)", "x": 791.8, "y": -283.6, "role": "Fortified capital of Northern Panchala", "desc": "Monumental mud-brick rampart city guarding the Upper Gangetic plain."},
            {"name": "Indraprastha (Kuru)", "x": 772.3, "y": -286.6, "role": "Historic capital of the Kuru Mahajanapada", "desc": "Traditional epicenter of the Kuru realm near modern Delhi along the Yamuna."},
            {"name": "Viratanagara (Matsya)", "x": 761.8, "y": -274.5, "role": "Capital of the Matsya pastoral kingdom", "desc": "Rich cattle-breeding janapada south of the Kurus; modern Bairat."}
        ],
        "locations": [
            {"name": "Rajagriha (Magadha)", "type": "capital", "x": 854.2, "y": -250.0, "role": "Magadhan cyclopean citadel and original capital", "desc": "Mountain-ringed capital of Magadha fortified with cyclopean stone masonry."},
            {"name": "Vaishali (Vajji)", "type": "republic_assembly", "x": 853.0, "y": -259.0, "role": "Metropolis of the Licchavi republic and Gana-sangha assembly", "desc": "Capital of the Vajji confederacy, governed by an elected assembly of 7,707 rajas."},
            {"name": "Shravasti (Kosala)", "type": "capital", "x": 820.0, "y": -275.0, "role": "Capital of Kosala on the Rapti River", "desc": "Flourishing commercial and political center of King Prasenajit; site of Jetavana monastery."},
            {"name": "Kaushambi (Vatsa)", "type": "capital", "x": 814.0, "y": -253.0, "role": "Yamuna river trade nexus ruled by King Udayana", "desc": "Key transit hub where northern and southern trade routes intersected along the Yamuna."},
            {"name": "Ujjayini (Avanti)", "type": "capital", "x": 757.8, "y": -231.8, "role": "Western trade junction on the Dakshinapatha highway", "desc": "Seat of King Chanda Pradyota, controlling the cotton routes and lapis/carnelian trade."},
            {"name": "Taxila (Gandhara)", "type": "university", "x": 728.2, "y": -337.4, "role": "Foremost pan-Asian Vedic university and northern trade crossroad", "desc": "Intellectual capital of Uttarapatha where Panini, Chanakya, and Jivaka studied."},
            {"name": "Champa (Anga)", "type": "port", "x": 869.8, "y": -252.3, "role": "Oceanic trade emporium on the Ganga-Champa confluence", "desc": "Wealthy riverine port trading silk, gems, and spices with Suvarnabhumi."},
            {"name": "Varanasi (Kasi)", "type": "sacred_site", "x": 830.0, "y": -253.2, "role": "Sacred metropolis famed for cotton textiles and brassware", "desc": "Ancient spiritual and commercial capital annexed alternately by Kosala and Magadha."},
            {"name": "Mathura (Surasena)", "type": "capital", "x": 776.8, "y": -275.0, "role": "Yamuna commercial crossroads and Yadava republican center", "desc": "Heartland of the Surasena kingdom on the junction of Uttarapatha and Dakshinapatha."},
            {"name": "Ahichchhatra (Panchala)", "type": "citadel", "x": 791.8, "y": -283.6, "role": "Fortified capital of Northern Panchala", "desc": "Monumental mud-brick rampart city guarding the Upper Gangetic plain."},
            {"name": "Indraprastha (Kuru)", "type": "capital", "x": 772.3, "y": -286.6, "role": "Historic capital of the Kuru Mahajanapada", "desc": "Traditional epicenter of the Kuru realm near modern Delhi along the Yamuna."},
            {"name": "Viratanagara (Matsya)", "type": "citadel", "x": 761.8, "y": -274.5, "role": "Capital of the Matsya pastoral kingdom", "desc": "Rich cattle-breeding janapada south of the Kurus; modern Bairat."},
            {"name": "Kusinara (Malla)", "type": "republic_assembly", "x": 838.9, "y": -267.4, "role": "Capital of the Malla republic; Buddha's Parinirvana site", "desc": "Autonomous oligarchic gana-sangha renowned for martial arts and wrestling."},
            {"name": "Potali / Bodhan (Assaka)", "type": "provincial_seat", "x": 778.8, "y": -186.7, "role": "Sole southern Mahajanapada along the Godavari river", "desc": "Southern outpost of the 16 realms, pioneering early iron and copper metallurgical trade."},
            {"name": "Pushkalavati (Gandhara)", "type": "citadel", "x": 716.8, "y": -341.6, "role": "Western Gandharan capital on the Swat-Kabul river confluence", "desc": "Renowned lotus city and citadel excavated at the Bala Hisar mound near Charsadda."},
            {"name": "Mithila (Videha)", "type": "republic_assembly", "x": 859.0, "y": -261.0, "role": "Ancient intellectual republic noted for Vedic philosophical conferences", "desc": "Famed for the royal court of Janaka and early philosophical assemblies recorded in the Upanishads."}
        ],
        "battles": [
            {
                "name": "Magadha–Vajji War",
                "year": "c. 484 – 468 BCE",
                "coords": {"x": 853.0, "y": -259.0},
                "parties": "Ajatashatru of Magadha vs. Licchavi / Vajji Confederacy",
                "summary": "Ajatashatru deployed two groundbreaking military innovations: the Mahashilakantaka (heavy stone siege catapult) and the Rathamusala (chariot with revolving scythe blades). Ended the independence of Vaishali.",
                "source": "Buddhist Digha Nikaya & Jaina Bhagavati Sutra"
            },
            {
                "name": "Magadha–Kosala War of Kasi",
                "year": "c. 490 BCE",
                "coords": {"x": 825.0, "y": -260.0},
                "parties": "Prasenajit of Kosala vs. Ajatashatru of Magadha",
                "summary": "Protracted war over the revenues of Kasi; Prasenajit captured Ajatashatru but released him and concluded a matrimonial treaty, ceding Kasi permanently to Magadha.",
                "source": "Samyutta Nikaya, Kosala Samyutta"
            },
            {
                "name": "Annexation of Anga",
                "year": "c. 535 BCE",
                "coords": {"x": 869.8, "y": -252.3},
                "parties": "Bimbisara of Magadha vs. Brahmadatta of Anga",
                "summary": "Bimbisara stormed the port-capital of Champa, slaying King Brahmadatta and installing crown prince Ajatashatru as viceroy, opening Magadhan commerce to the sea.",
                "source": "Mahavagga & Jaina Harivamsha Purana"
            },
            {
                "name": "Avanti–Vatsa Border Wars",
                "year": "c. 500 BCE",
                "coords": {"x": 785.0, "y": -242.0},
                "parties": "Chanda Pradyota of Avanti vs. Udayana of Vatsa",
                "summary": "Pradyota ambushed King Udayana using a mechanical decoy blue elephant; resolved through the romantic marriage of Udayana and Vasavadatta.",
                "source": "Bhasa's Svapnavasavadatta & Kathasaritsagara"
            },
            {
                "name": "Siege of Viratanagara",
                "year": "c. 550 BCE",
                "coords": {"x": 761.8, "y": -274.5},
                "parties": "Kuru-Trigarta Confederation vs. Matsya Kingdom",
                "summary": "Susharma of Trigarta and the Kuru forces raided Matsya territory to capture cattle herds, repelled by Matsya cavalry and allied warriors.",
                "source": "Mahabharata, Virata Parva"
            },
            {
                "name": "Dispute of the Rohini River",
                "year": "c. 520 BCE",
                "coords": {"x": 833.0, "y": -274.0},
                "parties": "Shakya Republic vs. Koliya Republic",
                "summary": "Severe drought triggered armed mobilization along the Rohini irrigation bund; averted without bloodshed through the personal arbitration of Gautama Buddha.",
                "source": "Jataka Attakatha, Kunala Jataka"
            }
        ],
        "events": [
            {"year": "c. 600 BCE", "title": "Crystallisation of the 16 Mahajanapadas across Northern and Central India", "desc": "Transition from tribal chiefdoms (janas) to territorial polities (janapadas) with minted punch-marked coins."},
            {"year": "c. 563 BCE", "title": "Birth of Gautama Buddha in the Shakya Republic at Lumbini", "desc": "Siddhartha Gautama born to Chief Shuddhodana in the oligarchic republic of Kapilavastu."},
            {"year": "c. 544 BCE", "title": "Bimbisara ascends the throne of Magadha; builds Rajagriha cyclopean walls", "desc": "Founding of the Haryanka dynasty and beginning of Magadha's 200-year drive for Indian supremacy."},
            {"year": "c. 540 BCE", "title": "Vardhamana Mahavira propagates Jainism across Magadha, Anga, and Videha", "desc": "24th Tirthankara establishes the four-fold sangha and revitalizes Jaina doctrine."},
            {"year": "c. 492 BCE", "title": "Ajatashatru seizes power in Magadha; launches 16-year campaign against Vajji", "desc": "Fortifies Pataligram at the Ganga-Son confluence to launch riverine warfare against the Licchavis."},
            {"year": "c. 483 BCE", "title": "Mahaparinirvana of Gautama Buddha at Kusinara; First Buddhist Council", "desc": "500 Arhats assemble at the Sattapanni Cave in Rajagriha to recite the Dhamma and Vinaya."},
            {"year": "c. 468 BCE", "title": "Vaishali falls to Magadhan siege engines; annexation of the Vajji Confederacy", "desc": "Ajatashatru integrates the Ganatantras into the centralized bureaucratic Magadhan realm."},
            {"year": "c. 413 BCE", "title": "Shishunaga overthrows Haryankas; destroys the 150-year Pradyota dynasty of Avanti", "desc": "Annexation of Ujjayini establishes Magadha as the undisputed master of Northern and Central India."}
        ]
    },
    "magadha-nanda": {
        "capitals": [
            {"name": "Pataliputra", "x": 851.4, "y": -256.1, "role": "Permanent imperial capital at the Ganga-Son confluence", "desc": "Founded by King Udayin; transformed into a fortified riverine metropolis of 64 gates."},
            {"name": "Rajagriha / Girivraja", "x": 854.2, "y": -250.0, "role": "Original mountain-ringed fortress capital of Bimbisara", "desc": "Protected by 40 km of cyclopean stone walls across five hills."},
            {"name": "Vaishali", "x": 853.0, "y": -259.0, "role": "Kalashoka's secondary imperial capital and Buddhist council venue", "desc": "Former Licchavi metropolis serving as northern administrative headquarters under the Shishunagas."},
            {"name": "Ujjayini", "x": 757.8, "y": -231.8, "role": "Western viceregal headquarters following conquest of Avanti", "desc": "Commanding maritime and overland routes linking North India to Arabian Sea ports."}
        ],
        "locations": [
            {"name": "Pataliputra", "type": "capital", "x": 851.4, "y": -256.1, "role": "Permanent imperial capital at the Ganga-Son confluence", "desc": "Founded by King Udayin; transformed into a fortified riverine metropolis of 64 gates."},
            {"name": "Rajagriha / Girivraja", "type": "capital", "x": 854.2, "y": -250.0, "role": "Original mountain-ringed fortress capital of Bimbisara", "desc": "Protected by 40 km of cyclopean stone walls across five hills."},
            {"name": "Vaishali", "type": "republic_assembly", "x": 853.0, "y": -259.0, "role": "Kalashoka's secondary imperial capital and Buddhist council venue", "desc": "Former Licchavi metropolis serving as northern administrative headquarters under the Shishunagas."},
            {"name": "Ujjayini", "type": "provincial_seat", "x": 757.8, "y": -231.8, "role": "Western viceregal headquarters following conquest of Avanti", "desc": "Commanding maritime and overland routes linking North India to Arabian Sea ports."},
            {"name": "Champa", "type": "port", "x": 869.8, "y": -252.3, "role": "Eastern riverine port city of Anga", "desc": "Major shipbuilding and merchant hub trading along the Bay of Bengal."},
            {"name": "Kashi (Varanasi)", "type": "sacred_site", "x": 830.0, "y": -253.2, "role": "Textile, ivory, and metallurgical hub on the holy Ganga", "desc": "Magadhan provincial center producing celebrated Kasika silks and iron weapons."},
            {"name": "Kaushambi", "type": "citadel", "x": 814.0, "y": -253.0, "role": "Fortified river gateway to the Doab", "desc": "Enclosed by monumental baked-brick ramparts with revetments and moats."},
            {"name": "Tosali (Kalinga)", "type": "citadel", "x": 858.3, "y": -202.6, "role": "Kalinga imperial fortress annexed by Mahapadma Nanda", "desc": "Site of the canal excavated by King Nanda mentioned in the Hathigumpha inscription."},
            {"name": "Tamralipti", "type": "port", "x": 879.2, "y": -223.0, "role": "Gangetic Delta oceanic port", "desc": "Terminal maritime nexus for ships sailing to Southeast Asia and Sri Lanka."},
            {"name": "Mathura", "type": "provincial_seat", "x": 776.8, "y": -275.0, "role": "Northern administrative outpost on the Yamuna", "desc": "Strategic river port connecting the Magadhan heartland to Gandhara."},
            {"name": "Ayodhya", "type": "citadel", "x": 822.0, "y": -268.0, "role": "Kosalan provincial center on the Saryu River", "desc": "Integrated into the Nanda empire following the absorption of Kosala."},
            {"name": "Shravasti", "type": "provincial_seat", "x": 820.0, "y": -275.0, "role": "Northern commercial city on the Rapti", "desc": "Maintained as a wealthy provincial governorship under Shishunaga and Nanda rule."}
        ],
        "battles": [
            {
                "name": "Siege of Vaishali",
                "year": "c. 468 BCE",
                "coords": {"x": 853.0, "y": -259.0},
                "parties": "Ajatashatru of Magadha vs. Licchavi Confederacy",
                "summary": "16-year siege concluded when Magadhan engineers deployed stone-hurling catapults (Mahashilakantaka) and scythed chariots (Rathamusala), permanently extinguishing Licchavi independence.",
                "source": "Uvasagadasao & Buddhist Atthakatha"
            },
            {
                "name": "Conquest of Avanti",
                "year": "c. 410 BCE",
                "coords": {"x": 757.8, "y": -231.8},
                "parties": "Shishunaga of Magadha vs. Avanti Pradyotas",
                "summary": "Shishunaga smashed the military power of Avanti, capturing Ujjayini and bringing western India under Magadhan suzerainty.",
                "source": "Puranic Dynastic Lists & Mahavamsa"
            },
            {
                "name": "Nanda Conquest of Kalinga",
                "year": "c. 340 BCE",
                "coords": {"x": 858.3, "y": -202.6},
                "parties": "Mahapadma Nanda vs. Kings of Kalinga",
                "summary": "Mahapadma Nanda invaded Kalinga, carried away the venerated Jina idol (Kalinga Jina) as an imperial trophy, and engineered the 300-year Tanasuliya canal.",
                "source": "Hathigumpha Inscription of Kharavela, Line 6"
            },
            {
                "name": "Mahapadma Nanda's Digvijaya",
                "year": "c. 345 BCE",
                "coords": {"x": 790.0, "y": -270.0},
                "parties": "Mahapadma Nanda vs. Panchalas, Kashis, Kurus, and Ikshvakus",
                "summary": "Systematic subjugation of old Aryan Kshatriya dynasties across northern India, earning Mahapadma the title Sarva-Kshatrantaka ('Destroyer of all Kshatriyas').",
                "source": "Vishnu Purana & Matsya Purana"
            },
            {
                "name": "Overthrow of the Shishunagas",
                "year": "c. 345 BCE",
                "coords": {"x": 851.4, "y": -256.1},
                "parties": "Mahapadma Nanda vs. Kalashoka's Successors",
                "summary": "Mahapadma seized power at Pataliputra, executing the ten sons of Kalashoka and inaugurating the Nanda dynasty's centralized imperial state.",
                "source": "Bana's Harshacharita & Curtius Rufus"
            },
            {
                "name": "Deterrence at the Beas / Hyphasis",
                "year": "326 BCE",
                "coords": {"x": 753.0, "y": -317.0},
                "parties": "Nanda Imperial Army vs. Alexander's Macedonians",
                "summary": "Intelligence of Dhana Nanda's 200,000 infantry, 20,000 cavalry, 2,000 chariots, and 4,000 trained war elephants provoked an army mutiny, forcing Alexander to abandon his march.",
                "source": "Plutarch, Life of Alexander & Diodorus Siculus XVII.93"
            }
        ],
        "events": [
            {"year": "c. 544 BCE", "title": "Bimbisara founds Haryanka Dynasty in Magadha", "desc": "Constructs capital at Rajagriha and initiates central fiscal administration."},
            {"year": "c. 460 BCE", "title": "King Udayin establishes Pataliputra as the permanent imperial capital", "desc": "Erects a stone fortress at the strategic convergence of the Ganga, Son, and Gandak rivers."},
            {"year": "c. 413 BCE", "title": "Shishunaga ascends the throne; permanently annexes the kingdom of Avanti", "desc": "Eliminates Magadha's greatest geopolitical rival and shifts royal residence temporarily to Vaishali."},
            {"year": "c. 383 BCE", "title": "Second Buddhist Council convened at Vaishali under King Kalashoka", "desc": "700 monks assemble to resolve the Ten Points dispute, leading to the first major schism (Mahasamghika)."},
            {"year": "c. 345 BCE", "title": "Mahapadma Nanda founds the Nanda Empire; proclaims himself 'Ekarat'", "desc": "Creates the first trans-regional standing army with state monopolies over mines, salt, and forests."},
            {"year": "c. 330 BCE", "title": "Dhana Nanda amasses monumental imperial treasury and 4,000 war elephants", "desc": "Standardizes imperial measures (Nandapakani) and collects immense revenue recorded by classical writers."},
            {"year": "c. 326 BCE", "title": "Nanda military deployment halts Alexander the Great at the Beas River", "desc": "Macedonian troops refuse to face Magadhan elephant corps; Alexander turns southward down the Indus."},
            {"year": "c. 322 BCE", "title": "Chandragupta Maurya and Chanakya overthrow the Nanda Dynasty", "desc": "Decisive siege of Pataliputra inaugurates the Mauryan Empire."}
        ]
    },
    "alexander-campaign": {
        "capitals": [
            {"name": "Pella (Macedonia)", "x": 225.2, "y": -407.6, "role": "Macedonian royal birthplace of Alexander and expedition base", "desc": "Argead dynastic capital where Aristotle tutored Alexander."},
            {"name": "Alexandria (Egypt)", "x": 299.2, "y": -312.0, "role": "Mediterranean metropolis founded 331 BCE; tomb of Alexander", "desc": "Imperial seaport and cultural capital designed by architect Dinocrates."},
            {"name": "Babylon (Mesopotamia)", "x": 444.2, "y": -325.4, "role": "Administrative capital of Alexander's world empire", "desc": "Seat of imperial government where Alexander received embassies and died in June 323 BCE."},
            {"name": "Taxila (Punjab)", "x": 728.2, "y": -337.4, "role": "Indian headquarters and base for the Punjab expedition", "desc": "King Ambhi surrendered his kingdom, providing 5,000 Indian troops and 30 war elephants."}
        ],
        "locations": [
            {"name": "Pella (Macedonia)", "type": "capital", "x": 225.2, "y": -407.6, "role": "Macedonian royal birthplace of Alexander and expedition base", "desc": "Argead dynastic capital where Aristotle tutored Alexander."},
            {"name": "Alexandria (Egypt)", "type": "capital", "x": 299.2, "y": -312.0, "role": "Mediterranean metropolis founded 331 BCE; tomb of Alexander", "desc": "Imperial seaport and cultural capital designed by architect Dinocrates."},
            {"name": "Babylon (Mesopotamia)", "type": "capital", "x": 444.2, "y": -325.4, "role": "Administrative capital of Alexander's world empire", "desc": "Seat of imperial government where Alexander received embassies and died in June 323 BCE."},
            {"name": "Taxila (Punjab)", "type": "university", "x": 728.2, "y": -337.4, "role": "Indian headquarters and base for the Punjab expedition", "desc": "King Ambhi surrendered his kingdom, providing 5,000 Indian troops and 30 war elephants."},
            {"name": "Persepolis (Persia)", "type": "citadel", "x": 528.9, "y": -299.3, "role": "Achaemenid ceremonial capital; burned by Alexander", "desc": "Grand palaces of Darius and Xerxes looted and burned in May 330 BCE."},
            {"name": "Susa (Elam)", "type": "citadel", "x": 482.4, "y": -322.0, "role": "Persian administrative palace; site of the mass Susa Weddings", "desc": "Alexander married Stateira and wed 80 Macedonian officers to noble Persian women."},
            {"name": "Bactra / Zariaspa", "type": "citadel", "x": 669.0, "y": -367.5, "role": "Northern Silk Road fortress in Central Asia", "desc": "Base for Sogdian campaigns; venue of Alexander's marriage to Roxana."},
            {"name": "Maracanda (Samarkand)", "type": "citadel", "x": 669.6, "y": -396.5, "role": "Sogdian capital garrisoned by Macedonian troops", "desc": "Site of the tragic drunken quarrel where Alexander killed Cleitus the Black."},
            {"name": "Alexandria the Furthest (Khujand)", "type": "citadel", "x": 696.0, "y": -403.0, "role": "Northeastern frontier fortress on the Syr Darya (Jaxartes)", "desc": "Built in 17 days to deter Scythian and Saka horse-archers."},
            {"name": "Alexandria in the Caucasus (Bagram)", "type": "provincial_seat", "x": 692.7, "y": -349.8, "role": "Hindu Kush operational base near Kabul", "desc": "Founded 329 BCE at the foot of the Hindu Kush to control mountain passes."},
            {"name": "Alexandria Nicaea (Jhelum)", "type": "citadel", "x": 737.0, "y": -329.0, "role": "Victory city founded after the Battle of the Hydaspes", "desc": "Built on the eastern bank of the Jhelum to commemorate the defeat of Porus."},
            {"name": "Alexandria Bucephala", "type": "citadel", "x": 736.0, "y": -328.5, "role": "City founded in memory of Alexander's war-horse Bucephalus", "desc": "Erected on the western bank of the Jhelum where Bucephalus died of battle wounds."},
            {"name": "Alexandria on the Indus (Uch)", "type": "port", "x": 710.5, "y": -292.3, "role": "Naval base at the convergence of the Punjab rivers with the Indus", "desc": "Extensive dockyards built by Craterus and Hephaestion for 1,000 river vessels."},
            {"name": "Pattala (Indus Delta)", "type": "port", "x": 683.0, "y": -248.0, "role": "Terminal ocean harbor on the Arabian Sea", "desc": "Launchpad for Nearchus' fleet expedition sailing across the Indian Ocean to the Persian Gulf."}
        ],
        "battles": [
            {
                "name": "Battle of the Granicus",
                "year": "May 334 BCE",
                "coords": {"x": 272.5, "y": -402.0},
                "parties": "Alexander III vs. Persian Satraps & Greek Mercenaries",
                "summary": "First major victory in Asia Minor. Alexander personally led the Companion Cavalry charge across the river, shattering Persian satrapal lines.",
                "source": "Arrian, Anabasis of Alexander I.12–16"
            },
            {
                "name": "Battle of Issus",
                "year": "November 333 BCE",
                "coords": {"x": 362.0, "y": -368.0},
                "parties": "Alexander III vs. Darius III of Persia",
                "summary": "Tactical masterpiece in a narrow coastal corridor along the Pinarus river; Darius fled leaving his royal family, chariot, and bow behind.",
                "source": "Callisthenes & Arrian II.7–11"
            },
            {
                "name": "Siege of Tyre",
                "year": "Jan – Jul 332 BCE",
                "coords": {"x": 352.1, "y": -332.7},
                "parties": "Alexander III vs. Tyrian Fleet and Citadel",
                "summary": "Seven-month siege in which Macedonians constructed a kilometer-long causeway from the mainland to storm the Phoenician island fortress.",
                "source": "Diodorus Siculus XVII.40–46"
            },
            {
                "name": "Battle of Gaugamela",
                "year": "October 331 BCE",
                "coords": {"x": 435.0, "y": -363.0},
                "parties": "Alexander III vs. Darius III of Persia",
                "summary": "Decisive battle of world antiquity. Alexander exploited a fatal gap in the Persian line with an oblique cavalry charge, destroying Achaemenid imperial power.",
                "source": "Arrian, Anabasis III.7–15"
            },
            {
                "name": "Battle of the Persian Gate",
                "year": "January 330 BCE",
                "coords": {"x": 518.0, "y": -305.0},
                "parties": "Alexander III vs. Satrap Ariobarzanes",
                "summary": "Ariobarzanes held the narrow Zagros mountain pass in Persia's 'Thermopylae' until Alexander outflanked the defenders via mountain goat paths.",
                "source": "Arrian III.18 & Curtius Rufus V.3–4"
            },
            {
                "name": "Siege of the Sogdian Rock",
                "year": "Spring 327 BCE",
                "coords": {"x": 668.5, "y": -385.0},
                "parties": "Alexander III vs. Oxyartes and Sogdian Barons",
                "summary": "300 elite Macedonian mountaineers climbed sheer icy precipices with iron tent-pegs at night, forcing Oxyartes' garrison to surrender without a fight.",
                "source": "Arrian IV.18–19"
            },
            {
                "name": "Siege of Aornos Rock",
                "year": "April 326 BCE",
                "coords": {"x": 728.0, "y": -347.0},
                "parties": "Alexander III vs. Aspasioi and Assakenoi Warriors",
                "summary": "Alexander conquered the legendary precipitous mountain stronghold above the Indus gorge that even Heracles was said to have failed to take.",
                "source": "Sir Aurel Stein & Arrian IV.28–30"
            },
            {
                "name": "Battle of the Hydaspes",
                "year": "May 326 BCE",
                "coords": {"x": 737.0, "y": -329.0},
                "parties": "Alexander III vs. King Porus (Paurava Kingdom)",
                "summary": "Epic night river crossing in a tropical monsoon storm. Alexander outmaneuvered Porus' 200 war elephants; Porus fought heroically until captured.",
                "source": "Arrian V.8–19 & Plutarch, Life of Alexander 60"
            },
            {
                "name": "Siege of Multan (Mallian Campaign)",
                "year": "Nov 326 BCE",
                "coords": {"x": 715.0, "y": -302.0},
                "parties": "Alexander III vs. Mallian Republic (Malavas)",
                "summary": "Frustrated by the siege pace, Alexander climbed the ramparts alone; his ladder broke and he was shot through the lung by a 3-cubit Indian arrow before rescue.",
                "source": "Arrian VI.9–11"
            },
            {
                "name": "Mutiny at the Hyphasis / Beas River",
                "year": "July 326 BCE",
                "coords": {"x": 753.0, "y": -317.0},
                "parties": "Macedonian Veterans vs. Alexander's Ambition",
                "summary": "Exhausted after marching 20,000 km, Coenus and the army refused to cross the Beas to confront the 4,000 elephants of the Nanda Empire. Alexander built 12 altars and turned south.",
                "source": "Arrian V.25–29 & Curtius IX.2–3"
            }
        ],
        "events": [
            {"year": "334 BCE", "title": "Alexander crosses the Hellespont into Asia", "desc": "Mobilizes 32,000 infantry and 5,100 cavalry to overthrow the Persian Empire."},
            {"year": "332 BCE", "title": "Conquest of Egypt; Foundation of Alexandria", "desc": "Visits the Oracle of Ammon at Siwa Oasis; proclaimed son of Zeus-Ammon."},
            {"year": "331 BCE", "title": "Triumph at Gaugamela; Proclaimed King of Asia", "desc": "Overthrow of the Achaemenid Empire; entry into Babylon and Susa."},
            {"year": "330 BCE", "title": "Persepolis burned; Pursuit of Bessus into Central Asia", "desc": "Death of Darius III; adoption of Persian royal ceremonial and diadem."},
            {"year": "327 BCE", "title": "Invasion of the Indian Subcontinent through the Khyber and Swat", "desc": "Captures the mountain fortresses of Massaga, Bazira, and Aornos."},
            {"year": "326 BCE", "title": "Battle of the Hydaspes; Army Mutiny at the Beas River", "desc": "Defeat of Porus along the Jhelum; soldiers refuse to advance into the Gangetic valley."},
            {"year": "325 BCE", "title": "Descent of the Indus; Brutal march through the Gedrosian Desert", "desc": "Nearchus leads the fleet along the coast; Alexander loses thousands in the Makran sands."},
            {"year": "323 BCE", "title": "Death of Alexander the Great in Babylon at age 32", "desc": "His empire is divided among his marshals (Diadochi), sparking the Hellenistic Era."}
        ]
    },
    "maurya-empire": {
        "capitals": [
            {"name": "Pataliputra", "x": 851.4, "y": -256.1, "role": "Imperial seat of the Mauryas; city of 64 gates and 570 towers", "desc": "Monumental wooden and stone-pillared palatial capital described by Megasthenes."},
            {"name": "Taxila (Uttarapatha)", "x": 728.2, "y": -337.4, "role": "Northern viceroyalty headquarters; Pan-Asian academy", "desc": "Governed by crown princes including Ashoka; nexus of Silk Road and Uttarapatha trade."},
            {"name": "Ujjayini (Avantiratha)", "x": 757.8, "y": -231.8, "role": "Western viceroyalty headquarters on international highway", "desc": "Governed by Ashoka as viceroy; center of astronomical study and western trade."},
            {"name": "Tosali (Kalinga)", "x": 858.3, "y": -202.6, "role": "Eastern viceroyalty following the Kalinga War", "desc": "Seat of the Kumara (royal prince) and site of Ashoka's Separate Rock Edicts at Dhauli."},
            {"name": "Suvarnagiri (Dakshinapatha)", "x": 772.0, "y": -155.0, "role": "Southern viceroyalty in Karnataka", "desc": "Headquarters of the southern province managing royal gold mines (Hatti gold belt)."}
        ],
        "locations": [
            {"name": "Pataliputra", "type": "capital", "x": 851.4, "y": -256.1, "role": "Imperial seat of the Mauryas; city of 64 gates and 570 towers", "desc": "Monumental wooden and stone-pillared palatial capital described by Megasthenes."},
            {"name": "Taxila (Uttarapatha)", "type": "university", "x": 728.2, "y": -337.4, "role": "Northern viceroyalty headquarters; Pan-Asian academy", "desc": "Governed by crown princes including Ashoka; nexus of Silk Road and Uttarapatha trade."},
            {"name": "Ujjayini (Avantiratha)", "type": "provincial_seat", "x": 757.8, "y": -231.8, "role": "Western viceroyalty headquarters on international highway", "desc": "Governed by Ashoka as viceroy; center of astronomical study and western trade."},
            {"name": "Tosali (Dhauli / Kalinga)", "type": "citadel", "x": 858.3, "y": -202.6, "role": "Eastern viceroyalty following the Kalinga War", "desc": "Seat of the Kumara (royal prince) and site of Ashoka's Separate Rock Edicts at Dhauli."},
            {"name": "Suvarnagiri (Dakshinapatha)", "type": "provincial_seat", "x": 772.0, "y": -155.0, "role": "Southern viceroyalty in Karnataka", "desc": "Headquarters of the southern province managing royal gold mines (Hatti gold belt)."},
            {"name": "Alexandropolis / Kandahar", "type": "citadel", "x": 657.2, "y": -316.2, "role": "Northwestern bilingual Ashokan rock edict site", "desc": "Greek and Aramaic bilingual inscriptions by Ashoka commanding piety and vegetarianism."},
            {"name": "Girnar (Junagadh)", "type": "citadel", "x": 706.0, "y": -215.2, "role": "Western provincial fortress and Sudarshana Lake dam", "desc": "Engineered under Chandragupta by governor Pushyagupta and canalized under Ashoka by Tushaspha."},
            {"name": "Sannati", "type": "sacred_site", "x": 769.2, "y": -168.3, "role": "Major Karnataka stupa complex with inscribed Ashokan portrait", "desc": "Only known sculpted portrait inscribed 'Raya Asoko' discovered at Kanaganahalli."},
            {"name": "Sopara (Shurparaka)", "type": "port", "x": 728.2, "y": -194.2, "role": "Chief Mauryan port on the Arabian Sea", "desc": "Site of Ashoka's Major Rock Edicts VIII and IX engraved on basalt blocks."},
            {"name": "Tamralipti", "type": "port", "x": 879.2, "y": -223.0, "role": "Eastern oceanic emporium on the Bay of Bengal", "desc": "Port from which Princess Sanghamitta embarked carrying a sapling of the Bodhi tree to Sri Lanka."},
            {"name": "Sarnath (Isipatana)", "type": "sacred_site", "x": 830.2, "y": -253.8, "role": "Site of the Lion Capital of Ashoka (National Emblem of India)", "desc": "Erected by Ashoka to commemorate Buddha's First Sermon (Dharmachakrapravartana)."},
            {"name": "Lumbini (Rummindei)", "type": "sacred_site", "x": 832.8, "y": -274.8, "role": "Birthplace of Gautama Buddha", "desc": "Ashoka's pillar inscription recording royal tax exemption ('lummini-game ubalike kate')."},
            {"name": "Brahmagiri", "type": "sacred_site", "x": 768.1, "y": -148.1, "role": "Southern Karnataka Minor Rock Edict site", "desc": "Engraved by royal scribe Chapada in both Brahmi and Kharosthi scripts."},
            {"name": "Maski", "type": "sacred_site", "x": 766.6, "y": -159.6, "role": "Edict confirming Ashoka's personal name", "desc": "Famous Minor Rock Edict directly naming 'Devanampriya Asoka' discovered in 1915."},
            {"name": "Shravanabelagola", "type": "sacred_site", "x": 764.8, "y": -128.5, "role": "Chandragupta Maurya's ascetic retirement sanctuary", "desc": "Chandragiri hill where Emperor Chandragupta undertook the Jain rite of Sallekhana with Bhadrabahu."}
        ],
        "battles": [
            {
                "name": "Overthrow of the Nanda Empire",
                "year": "c. 322 BCE",
                "coords": {"x": 851.4, "y": -256.1},
                "parties": "Chandragupta Maurya & Chanakya vs. Dhana Nanda",
                "summary": "Chandragupta assembled a mixed army of northwestern tribes, Greek mercenaries, and mountain allies to encircle and conquer Pataliputra, executing Dhana Nanda.",
                "source": "Mudrarakshasa of Vishakhadatta & Mahavamsatika"
            },
            {
                "name": "Mauryan–Seleucid War",
                "year": "c. 305 – 303 BCE",
                "coords": {"x": 695.0, "y": -310.0},
                "parties": "Chandragupta Maurya vs. Seleucus I Nicator",
                "summary": "Seleucus crossed the Indus seeking to reclaim Alexander's conquests; Chandragupta repulsed the invasion. By treaty, Seleucus ceded Arachosia, Gedrosia, Paropamisadae, and Aria in exchange for 500 war elephants.",
                "source": "Appian, Syriaca 55 & Strabo XV.2.9"
            },
            {
                "name": "The Kalinga War",
                "year": "c. 261 BCE",
                "coords": {"x": 858.4, "y": -201.9},
                "parties": "Emperor Ashoka vs. Republican Kalinga",
                "summary": "Cataclysmic conflict along the Daya River. Over 100,000 Kalingans slain and 150,000 exiled. Witnessing the carnage prompted Ashoka's profound moral awakening and conversion to non-violence (Ahimsa).",
                "source": "Ashoka Major Rock Edict XIII (Kalsi, Shahbazgarhi, Girnar)"
            },
            {
                "name": "Bindusara's Deccan Campaign",
                "year": "c. 300 – 290 BCE",
                "coords": {"x": 765.0, "y": -160.0},
                "parties": "Emperor Bindusara vs. Southern Peninsular Kingdoms",
                "summary": "Bindusara (known to Greeks as Amitrochates, 'Slayer of Foes') marched across peninsular India, subjugating sixteen chiefdoms between the Arabian Sea and Bay of Bengal.",
                "source": "Taranatha's History of Buddhism & Mamulanar (Akananuru 251)"
            },
            {
                "name": "Suppression of the Taxila Rebellion",
                "year": "c. 275 BCE",
                "coords": {"x": 728.2, "y": -337.4},
                "parties": "Crown Prince Ashoka vs. Corrupt Provincial Governors",
                "summary": "Citizens of Taxila rebelled against oppressive imperial ministers; Bindusara dispatched Prince Ashoka, who peacefully resolved the grievances without violence.",
                "source": "Ashokavadana, Divyavadana XXVI"
            },
            {
                "name": "Assassination of Brihadratha",
                "year": "185 BCE",
                "coords": {"x": 851.4, "y": -256.1},
                "parties": "Pushyamitra Shunga vs. Emperor Brihadratha",
                "summary": "Mauryan Commander-in-Chief Pushyamitra Shunga killed the last Mauryan ruler Brihadratha during an imperial military inspection, founding the Shunga Dynasty.",
                "source": "Bana's Harshacharita & Puranic Chronology"
            }
        ],
        "events": [
            {"year": "322 BCE", "title": "Chandragupta Maurya founds the Mauryan Empire with Chanakya's guidance", "desc": "Establishes unified pan-Indian administration based on the principles of the Arthashastra."},
            {"year": "305 BCE", "title": "Mauryan-Seleucid Peace Treaty; Megasthenes arrives at Pataliputra", "desc": "Seleucus I establishes marital alliance and dispatches Megasthenes, who authors the Indika."},
            {"year": "297 BCE", "title": "Chandragupta abdicates; migrates to Shravanabelagola for Sallekhana", "desc": "Bindusara crowned second Mauryan emperor; continues patronizing Ajivika ascetics."},
            {"year": "268 BCE", "title": "Formal consecration of Ashoka the Great at Pataliputra", "desc": "Ashoka consolidates the empire after a succession contest following Bindusara's death."},
            {"year": "261 BCE", "title": "The Kalinga War; Ashoka renounces military conquest for Dhammavijaya", "desc": "Adopts Buddhism, abolishes royal hunting, and orders imperial rock edicts across the subcontinent."},
            {"year": "c. 250 BCE", "title": "Third Buddhist Council convened at Pataliputra under Moggaliputta Tissa", "desc": "Purification of the Sangha and compilation of the Kathavatthu (Abhidhamma Pitaka)."},
            {"year": "c. 240 BCE", "title": "Ashoka dispatches Buddhist missions across Asia and the Mediterranean", "desc": "Mahinda and Sanghamitta travel to Sri Lanka; envoys sent to Antiochus II, Ptolemy II, and Antigonus."},
            {"year": "232 BCE", "title": "Death of Ashoka; empire partitioned between Dasaratha and Kunala", "desc": "Gradual weakening of imperial central authority over distant provinces."},
            {"year": "185 BCE", "title": "Fall of the Mauryan Empire; Pushyamitra Shunga assumes power", "desc": "Mauryan dynasty concludes after 137 years of pan-Indian hegemony."}
        ]
    },
    "indo-greek-shunga": {
        "capitals": [
            {"name": "Vidisha (Besnagar)", "x": 778.0, "y": -235.3, "role": "Primary Shunga imperial capital and cultural center", "desc": "Seat of Crown Prince Agnimitra; site of the Heliodorus Garuda pillar."},
            {"name": "Pataliputra", "x": 851.4, "y": -256.1, "role": "Eastern Shunga imperial seat", "desc": "Retained as imperial capital by Pushyamitra Shunga following the Mauryan overthrow."},
            {"name": "Sagala (Sialkot)", "x": 745.3, "y": -325.0, "role": "Indo-Greek capital of King Menander I (Milinda)", "desc": "Cosmopolitan Greco-Indian city celebrated for parks, moats, and Buddhist stupas in Milinda Panha."},
            {"name": "Pushkalavati (Charsadda)", "x": 716.8, "y": -341.6, "role": "Western Indo-Greek mint and fortified administrative center", "desc": "Center of Hellenistic minting and Gandharan stone craft."}
        ],
        "locations": [
            {"name": "Vidisha (Besnagar)", "type": "capital", "x": 778.0, "y": -235.3, "role": "Primary Shunga imperial capital and cultural center", "desc": "Seat of Crown Prince Agnimitra; site of the Heliodorus Garuda pillar."},
            {"name": "Pataliputra", "type": "capital", "x": 851.4, "y": -256.1, "role": "Eastern Shunga imperial seat", "desc": "Retained as imperial capital by Pushyamitra Shunga following the Mauryan overthrow."},
            {"name": "Sagala (Sialkot)", "type": "capital", "x": 745.3, "y": -325.0, "role": "Indo-Greek capital of King Menander I (Milinda)", "desc": "Cosmopolitan Greco-Indian city celebrated for parks, moats, and Buddhist stupas in Milinda Panha."},
            {"name": "Pushkalavati (Charsadda)", "type": "capital", "x": 716.8, "y": -341.6, "role": "Western Indo-Greek mint and fortified administrative center", "desc": "Center of Hellenistic minting and Gandharan stone craft."},
            {"name": "Taxila (Sirkap)", "type": "university", "x": 728.2, "y": -337.4, "role": "Indo-Greek planned city built on Hippodamian grid", "desc": "Sirkap urban phase featuring Greco-Bactrian temples, stupas, and bilingual coin mints."},
            {"name": "Mathura", "type": "citadel", "x": 776.8, "y": -275.0, "role": "Easternmost Indo-Greek outpost and Shunga artistic center", "desc": "Contested commercial hub where Indo-Greek drachms circulated alongside Shunga sculptures."},
            {"name": "Ayodhya (Saketa)", "type": "citadel", "x": 822.0, "y": -268.0, "role": "Kosalan stronghold besieged by Greeks", "desc": "Site of the Dhanadeva-Ayodhya inscription documenting Pushyamitra's two Ashvamedhas."},
            {"name": "Bharhut", "type": "sacred_site", "x": 808.0, "y": -245.0, "role": "Famous Shunga-period Buddhist gateway and torana", "desc": "Masterpiece of early Indian narrative stone relief sculpture inscribed 'Suganam Raje'."},
            {"name": "Sanchi", "type": "sacred_site", "x": 777.4, "y": -234.8, "role": "Great Stupa enlarged with stone railings under the Shungas", "desc": "Stone balustrade and toranas constructed during Shunga and Satavahana patronage."},
            {"name": "Alexandria in Arachosia (Kandahar)", "type": "provincial_seat", "x": 657.2, "y": -316.2, "role": "Indo-Greek western frontier stronghold", "desc": "Greco-Bactrian military hub connecting Arachosia to the Indus basin."},
            {"name": "Demetrias in Sind", "type": "port", "x": 685.0, "y": -250.0, "role": "Indo-Greek maritime harbor on the Indus mouth", "desc": "Founded by Demetrius I to control Indian Ocean trade routes."},
            {"name": "Kaushambi", "type": "provincial_seat", "x": 814.0, "y": -253.0, "role": "Shunga administrative center on the Yamuna", "desc": "Excavations revealed extensive Shunga brick fortifications, seals, and terracotta plaques."}
        ],
        "battles": [
            {
                "name": "Battle of the Sindhu River",
                "year": "c. 175 BCE",
                "coords": {"x": 715.0, "y": -320.0},
                "parties": "Prince Vasumitra (Shunga) vs. Indo-Greek Yavana Cavalry",
                "summary": "Pushyamitra's grandson Vasumitra guarded the imperial sacrificial horse on the banks of the Sindhu, repelling Greek cavalry in a fierce engagement.",
                "source": "Kalidasa's Malavikagnimitram, Act V"
            },
            {
                "name": "Indo-Greek Siege of Saketa (Ayodhya)",
                "year": "c. 165 BCE",
                "coords": {"x": 822.0, "y": -268.0},
                "parties": "Indo-Greek King (Demetrius / Menander) vs. Shunga Garrison",
                "summary": "Yavana armies advanced deep into the Gangetic heartland, laying siege to Saketa and Mathura as recorded by the grammarian Patanjali.",
                "source": "Patanjali's Mahabhasya on Panini III.2.111"
            },
            {
                "name": "Greco-Bactrian March on Pataliputra",
                "year": "c. 160 BCE",
                "coords": {"x": 851.4, "y": -256.1},
                "parties": "Menander I of Sagala vs. Shunga Imperial Forces",
                "summary": "Menander's allied vanguard reached the mud-brick fortifications of Pataliputra before civil conflicts in Bactria forced the Greeks to retreat.",
                "source": "Yuga Purana & Strabo XI.11.1"
            },
            {
                "name": "Menander's Conquest of Mathura",
                "year": "c. 155 BCE",
                "coords": {"x": 776.8, "y": -275.0},
                "parties": "Menander I vs. Surasena Chieftains",
                "summary": "Indo-Greek annexation of the upper Yamuna valley, leaving hoards of Menander's silver drachms across the Mathura region.",
                "source": "Archaeological Survey of India Coin Hoards"
            },
            {
                "name": "Shunga–Vidarbha War",
                "year": "c. 180 BCE",
                "coords": {"x": 785.0, "y": -212.0},
                "parties": "Crown Prince Agnimitra vs. King Yajnasena of Vidarbha",
                "summary": "Agnimitra's general Virasena crossed the Narmada and defeated Yajnasena, partitioning Vidarbha between two cousin-rulers subject to Shunga suzerainty.",
                "source": "Kalidasa's Malavikagnimitram"
            },
            {
                "name": "Defense of Pushyamitra's Ashvamedha",
                "year": "c. 170 BCE",
                "coords": {"x": 775.0, "y": -280.0},
                "parties": "Imperial Shunga Army vs. Regional Insurgents",
                "summary": "Pushyamitra successfully concludes his second Ashvamedha sacrifice, reaffirming Vedic imperial rituals across northern India.",
                "source": "Ayodhya Inscription of Dhanadeva"
            }
        ],
        "events": [
            {"year": "185 BCE", "title": "Pushyamitra Shunga establishes the Shunga Dynasty at Pataliputra", "desc": "Restores Vedic horse sacrifice (Ashvamedha) and patronizes arts and architecture."},
            {"year": "c. 180 BCE", "title": "Demetrius I crosses Hindu Kush; founds the Indo-Greek Kingdom", "desc": "Captures Punjab and Gandhara, establishing bilingual Greek-Kharosthi coinage."},
            {"year": "c. 165–130 BCE", "title": "Golden age of Indo-Greek culture under King Menander I (Milinda)", "desc": "Conversations on Buddhist philosophy with Nagasena compiled as the Milinda Panha."},
            {"year": "c. 150 BCE", "title": "Sage Patanjali writes the Mahabhasya grammar treatise at Vidisha", "desc": "Documents contemporaneous Indo-Greek incursions into Saketa and Madhyamika."},
            {"year": "c. 113 BCE", "title": "Heliodorus, Greek ambassador from Taxila, erects Garuda Pillar at Vidisha", "desc": "Inscribed in Brahmi Prakrit declaring himself a Bhagavata (devotee of Vishnu-Vasudeva)."},
            {"year": "c. 73 BCE", "title": "Vasudeva Kanva overthrows Devabhuti, the last Shunga monarch", "desc": "Founding of the Kanva Dynasty in Magadha."},
            {"year": "c. 10 CE", "title": "Indo-Scythians (Sakas) extinguish the last Indo-Greek realms in Punjab", "desc": "King Strato II defeated by the Northern Satraps under Rajuvula."}
        ]
    },
    "satavahana-empire": {
        "capitals": [
            {"name": "Pratishthana (Paithan)", "x": 753.8, "y": -194.8, "role": "First imperial capital on the Godavari in Maharashtra", "desc": "Ancient textile and commercial center celebrated in the Periplus of the Erythraean Sea."},
            {"name": "Amaravati / Dharanikota", "x": 803.6, "y": -165.7, "role": "Eastern maritime capital on the Krishna River", "desc": "Magnificent Buddhist religious and artistic center; site of the Great Amaravati Stupa."},
            {"name": "Junnar", "x": 738.8, "y": -192.1, "role": "Early western stronghold near Naneghat pass", "desc": "Surrounded by over 200 rock-cut caves and Buddhist viharas."}
        ],
        "locations": [
            {"name": "Pratishthana (Paithan)", "type": "capital", "x": 753.8, "y": -194.8, "role": "First imperial capital on the Godavari in Maharashtra", "desc": "Ancient textile and commercial center celebrated in the Periplus of the Erythraean Sea."},
            {"name": "Amaravati / Dharanikota", "type": "capital", "x": 803.6, "y": -165.7, "role": "Eastern maritime capital on the Krishna River", "desc": "Magnificent Buddhist religious and artistic center; site of the Great Amaravati Stupa."},
            {"name": "Junnar", "type": "citadel", "x": 738.8, "y": -192.1, "role": "Early western stronghold near Naneghat pass", "desc": "Surrounded by over 200 rock-cut caves and Buddhist viharas."},
            {"name": "Naneghat Pass", "type": "sacred_site", "x": 736.8, "y": -192.9, "role": "Strategic mountain toll pass and royal inscription sanctuary", "desc": "Queen Nayanika's Brahmi inscription recording Satakarni I's Vedic sacrifices and gifts."},
            {"name": "Karle (Karli)", "type": "sacred_site", "x": 735.2, "y": -187.8, "role": "Greatest rock-cut Chaitya hall in ancient India", "desc": "Grand wooden-ribbed rock architecture patronized by merchants and Satavahana kings."},
            {"name": "Sopara (Shurparaka)", "type": "port", "x": 728.2, "y": -194.2, "role": "Major western port conducting maritime trade with Roman Egypt", "desc": "Ancient port excavated with Roman amphorae and Ashokan rock edicts."},
            {"name": "Barygaza (Bharuch)", "type": "port", "x": 729.8, "y": -217.0, "role": "Narmada estuary port described in the Periplus", "desc": "Gateway for Roman gold, wine, and Italian glassware exchanged for Indian silk and pepper."},
            {"name": "Arikamedu (Podouke)", "type": "port", "x": 798.3, "y": -119.0, "role": "Indo-Roman trading station on the Coromandel coast", "desc": "Excavated with Arretine ware, Roman glass, rouletted pottery, and dyeing vats."},
            {"name": "Nagarjunakonda", "type": "university", "x": 792.9, "y": -165.2, "role": "Major Buddhist university and monastery on the Krishna", "desc": "Associated with philosopher Acharya Nagarjuna and patronized by Ikshvaku queens."},
            {"name": "Banavasi", "type": "citadel", "x": 750.1, "y": -145.4, "role": "Southern Satavahana administrative stronghold in North Canara", "desc": "Later became the capital of the Kadamba dynasty."},
            {"name": "Nashik (Pandavleni)", "type": "sacred_site", "x": 737.9, "y": -200.0, "role": "Rock-cut monastic complex and royal eulogy site", "desc": "Cave 3 contains Queen Gautami Balashri's famous prasasti celebrating Gautamiputra."},
            {"name": "Kanheri", "type": "university", "x": 729.1, "y": -192.1, "role": "Foremost coastal Buddhist monastery near Mumbai", "desc": "109 rock-cut caves functioning as an educational and monastic center for 1,000 years."},
            {"name": "Ghantasala", "type": "port", "x": 808.8, "y": -161.5, "role": "Eastern port mentioned by Ptolemy as Kontakossyla", "desc": "Active maritime trade center carrying Buddhist pilgrims and spices to Sri Lanka."}
        ],
        "battles": [
            {
                "name": "Battle of Govardhana (Nashik)",
                "year": "124 CE",
                "coords": {"x": 737.9, "y": -200.0},
                "parties": "Gautamiputra Satakarni vs. Nahapana (Western Kshatrapas)",
                "summary": "Gautamiputra routed the Kshaharata satrap Nahapana, restriking thousands of his silver coins at the Jogalthambi hoard and liberating western Maharashtra.",
                "source": "Nashik Cave Inscription No. 2 & Jogalthambi Coin Hoard"
            },
            {
                "name": "Destruction of the Kshaharatas",
                "year": "c. 125 CE",
                "coords": {"x": 738.8, "y": -192.1},
                "parties": "Gautamiputra Satakarni vs. Kshaharata Remnants",
                "summary": "Total extermination of the Kshaharata dynasty ('Kshaharata-vamsa-nirvaseshakara'), re-establishing Satavahana control over Konkan, Gujarat, and Malwa.",
                "source": "Gautami Balashri Prasasti (Nashik Cave 3)"
            },
            {
                "name": "Wars with Rudradaman I",
                "year": "c. 150 CE",
                "coords": {"x": 715.0, "y": -225.0},
                "parties": "Vashishtiputra Satakarni vs. Mahakshatrapa Rudradaman",
                "summary": "Rudradaman defeated the Satavahana king twice in open field battle, but spared his life due to non-distant marital relationship, retaking Saurashtra and Aparanta.",
                "source": "Junagadh Rock Inscription of Rudradaman, Lines 11–12"
            },
            {
                "name": "Early Expansion into Malwa",
                "year": "c. 110 BCE",
                "coords": {"x": 757.8, "y": -231.8},
                "parties": "Satakarni I vs. Shunga Regional Governors",
                "summary": "Satakarni I crossed the Narmada and conquered western Malwa, minting coins at Ujjayini and celebrating two Ashvamedhas.",
                "source": "Naneghat Inscription & Ujjain Coinage"
            },
            {
                "name": "Subjugation of the Kanvas",
                "year": "c. 30 BCE",
                "coords": {"x": 778.0, "y": -235.3},
                "parties": "Satavahana Forces vs. King Susarman (Kanva)",
                "summary": "Satavahana armies advanced into central India, slaying Susarman and annexing Vidisha and eastern territories.",
                "source": "Puranic Dynastic Accounts"
            },
            {
                "name": "Naval Defense of the Western Seaboard",
                "year": "c. 180 CE",
                "coords": {"x": 728.0, "y": -185.0},
                "parties": "Yajna Sri Satakarni vs. Arab and Scythian Pirates",
                "summary": "Maritime patrols secured the Indian Ocean trade lanes, commemorated on Yajna Sri Satakarni's famous ship-type lead and silver coins.",
                "source": "Ship-Type Coin Corpus & Periplus of the Erythraean Sea"
            }
        ],
        "events": [
            {"year": "c. 100 BCE", "title": "King Simuka founds the Satavahana Dynasty in the Deccan", "desc": "Unifies Maharashtra and Andhra regions after the disintegration of Mauryan rule."},
            {"year": "c. 70 BCE", "title": "Satakarni I performs two Ashvamedhas and Rajasuya sacrifices", "desc": "Queen Nayanika records royal conquests and enormous dakshina gifts at Naneghat pass."},
            {"year": "c. 106–130 CE", "title": "Reign of Gautamiputra Satakarni; zenith of Satavahana power", "desc": "Titles himself 'Tri-Samudra-Toya-Pita-Vahana' (Whose steeds drank the waters of three oceans)."},
            {"year": "c. 130–159 CE", "title": "Reign of Vashishtiputra Pulumavi; shifts capital to Dharanikota (Amaravati)", "desc": "Consolidates eastern Deccan and expands oceanic commerce with Rome and Southeast Asia."},
            {"year": "c. 170–199 CE", "title": "Reign of Yajna Sri Satakarni; mints ship-type coins", "desc": "Demonstrates Satavahana naval supremacy across the Bay of Bengal and Arabian Sea."},
            {"year": "c. 225 CE", "title": "Decline of the Satavahana Empire into regional successor dynasties", "desc": "Power passes to Ikshvakus in Andhra, Abhiras in Maharashtra, and Kadambas/Pallavas in the south."}
        ]
    },
    "kushan-empire": {
        "capitals": [
            {"name": "Purushapura (Peshawar)", "x": 715.8, "y": -340.1, "role": "Winter imperial capital; site of Kanishka's Great Stupa", "desc": "Foremost Buddhist metropolis featuring Kanishka's 400-foot multi-tiered wooden stupa."},
            {"name": "Mathura", "x": 776.8, "y": -275.0, "role": "Southern imperial capital and center of Indian art", "desc": "Cradle of the Mathura school of mottled red sandstone Buddhist, Jaina, and Brahmanical art."},
            {"name": "Begram / Kapisa", "x": 692.7, "y": -349.8, "role": "Summer mountain capital in the Hindu Kush foothills", "desc": "Site of the spectacular Begram Treasure containing Chinese lacquer, Roman glassware, and Indian ivories."},
            {"name": "Bactra / Balkh", "x": 669.0, "y": -367.5, "role": "Ancestral Northern capital and Silk Road crossroads", "desc": "Ancient mother of cities where Kushan emperors minted Greek-inscribed gold dinars."}
        ],
        "locations": [
            {"name": "Purushapura (Peshawar)", "type": "capital", "x": 715.8, "y": -340.1, "role": "Winter imperial capital; site of Kanishka's Great Stupa", "desc": "Foremost Buddhist metropolis featuring Kanishka's 400-foot multi-tiered wooden stupa."},
            {"name": "Mathura", "type": "capital", "x": 776.8, "y": -275.0, "role": "Southern imperial capital and center of Indian art", "desc": "Cradle of the Mathura school of mottled red sandstone Buddhist, Jaina, and Brahmanical art."},
            {"name": "Begram / Kapisa", "type": "capital", "x": 692.7, "y": -349.8, "role": "Summer mountain capital in the Hindu Kush foothills", "desc": "Site of the spectacular Begram Treasure containing Chinese lacquer, Roman glassware, and Indian ivories."},
            {"name": "Bactra / Balkh", "type": "capital", "x": 669.0, "y": -367.5, "role": "Ancestral Northern capital and Silk Road crossroads", "desc": "Ancient mother of cities where Kushan emperors minted Greek-inscribed gold dinars."},
            {"name": "Taxila (Sirkap / Jaulian)", "type": "university", "x": 728.2, "y": -337.4, "role": "Gandharan university and monastic center", "desc": "Site of Dharmarajika and Jaulian monasteries renowned for Greco-Buddhist stucco sculptures."},
            {"name": "Rabatak", "type": "citadel", "x": 686.0, "y": -361.0, "role": "Sanctuary of Kanishka's famous royal genealogy inscription", "desc": "23-line Bactrian inscription discovered in 1993 detailing Kanishka's reign and cities."},
            {"name": "Surkh Kotal", "type": "sacred_site", "x": 687.5, "y": -360.5, "role": "Grand dynastic fire-temple of Kanishka the Victorious", "desc": "Monumental terraced sanctuary featuring colossal royal statues and Greek-script Bactrian texts."},
            {"name": "Kunduz", "type": "provincial_seat", "x": 688.0, "y": -367.0, "role": "Oxus river valley commercial hub", "desc": "Strategic crossing point connecting Bactria to the Pamir trading networks."},
            {"name": "Harwan / Kundalvana (Kashmir)", "type": "sacred_site", "x": 749.0, "y": -341.5, "role": "Site of the Fourth Buddhist Council under Kanishka", "desc": "Monastery where 500 scholars under Vasumitra compiled the Mahavibhasha canon engraved on copper sheets."},
            {"name": "Sarnath (Varanasi)", "type": "sacred_site", "x": 830.2, "y": -253.8, "role": "Easternmost documented Kushan administrative umbrella", "desc": "Colossal red sandstone Bodhisattva dedicated by Friar Bala in Year 3 of Kanishka."},
            {"name": "Termez", "type": "citadel", "x": 672.8, "y": -372.2, "role": "Major Buddhist monastic citadel on the northern Oxus", "desc": "Kara Tepe and Fayaz Tepe rock-cut monasteries with Gandharan wall paintings."},
            {"name": "Kausambi", "type": "provincial_seat", "x": 814.0, "y": -253.0, "role": "Eastern Gangetic outpost under Kushan governors", "desc": "Inscriptions of Kanishka and Huvishka found on monolithic pillars and stone images."}
        ],
        "battles": [
            {
                "name": "Kushan Campaign in the Tarim Basin",
                "year": "c. 90 CE",
                "coords": {"x": 759.9, "y": -394.7},
                "parties": "Kushan Viceroy Xie vs. Han General Ban Chao",
                "summary": "70,000 Kushan cavalry crossed the Pamir passes to enforce a royal marriage proposal with the Han court; Ban Chao used scorched-earth tactics to force a negotiated withdrawal.",
                "source": "Book of the Later Han (Hou Hanshu), Chapter 77"
            },
            {
                "name": "Conquest of Gandhara & Punjab",
                "year": "c. 60 CE",
                "coords": {"x": 728.2, "y": -337.4},
                "parties": "Kujula Kadphises vs. Indo-Parthian Kingdom",
                "summary": "Kujula Kadphises swept down from Kabul, capturing Taxila and Pushkalavati from the Indo-Parthians under Gondophares.",
                "source": "Rabatak Inscription & Taxila Silver Scrolls"
            },
            {
                "name": "Kanishka's Eastern Gangetic Campaign",
                "year": "c. 130 CE",
                "coords": {"x": 851.4, "y": -256.1},
                "parties": "Emperor Kanishka I vs. Kings of Saketa and Pataliputra",
                "summary": "Kanishka marched deep into Magadha, imposing tribute on Pataliputra and escorting the celebrated Buddhist philosopher Ashvaghosha to his court.",
                "source": "Kumaralata's Kalpanamanditika & Tibetan Buddhist Annals"
            },
            {
                "name": "Kanishka's Western Parthian Frontier War",
                "year": "c. 135 CE",
                "coords": {"x": 622.0, "y": -376.0},
                "parties": "Kushan Imperial Army vs. Arsacid Parthians",
                "summary": "Kushan forces secured Margiana (Merv) on the western marches, cementing undisputed control over the overland Silk Road trade arteries.",
                "source": "Coins of Kanishka with Oado & Bactrian Texts"
            },
            {
                "name": "Sasanian Invasion of Bactria",
                "year": "c. 240 CE",
                "coords": {"x": 669.0, "y": -367.5},
                "parties": "Shapur I of Sasanian Empire vs. Kushan King Vasudeva II",
                "summary": "Sasanian emperor Shapur I conquered Bactria and Peshawar, reducing western Kushan territories into the Kushano-Sasanian (Kushanshah) vassal province.",
                "source": "Naqsh-e Rostam Inscription of Shapur I"
            },
            {
                "name": "Battle of the Oxus Frontier",
                "year": "c. 200 CE",
                "coords": {"x": 672.0, "y": -372.0},
                "parties": "Vasudeva I vs. Steppe Nomads",
                "summary": "Kushan garrisons along the Oxus river beat back early Chionite and Hunnic tribal incursions, defending the fertile oasis cities of Bactria.",
                "source": "Numismatic Evidence of Vasudeva I"
            }
        ],
        "events": [
            {"year": "c. 30 CE", "title": "Kujula Kadphises unifies the five Yuezhi yabghus and founds the Kushan Empire", "desc": "Crosses the Hindu Kush, absorbing Kabul, Gandhara, and the upper Indus basin."},
            {"year": "c. 90–110 CE", "title": "Vima Kadphises introduces the gold dinar coinage based on the Roman standard", "desc": "Vast gold coin hoards reflect lucrative trade with the Roman Empire via maritime and Silk Road networks."},
            {"year": "127 CE", "title": "Accession of Kanishka the Great; declaration of the Kanishka Era", "desc": "Adopts the Iranian Bactrian language for official inscriptions, replacing Greek on coins."},
            {"year": "c. 140 CE", "title": "Fourth Buddhist Council convened at Kundalvana (Kashmir)", "desc": "Codification of the Mahayana Mahavibhasha commentaries; rise of Sanskrit as the Buddhist canonical tongue."},
            {"year": "c. 150 CE", "title": "Construction of the colossal Kanishka Stupa in Peshawar", "desc": "Over 400 feet high, praised by Faxian and Xuanzang as the tallest architectural marvel in Asia."},
            {"year": "c. 190–230 CE", "title": "Reign of Vasudeva I; cultural Indianization of Kushan royal imagery", "desc": "Coins feature Lord Shiva with trident and Nandi bull; adoption of Classical Indian courtly traditions."},
            {"year": "c. 240–270 CE", "title": "Sasanian conquests split the Kushan Empire into eastern and western realms", "desc": "Western provinces yield to Kushano-Sasanian princes; eastern domains continue around Mathura and Punjab."},
            {"year": "375 CE", "title": "Kidarite Huns and the rising Gupta Empire absorb the remaining Kushan principalities", "desc": "Conclusion of over three centuries of Kushan syncretic civilization."}
        ]
    },
    "gupta-empire": {
        "capitals": [
            {"name": "Pataliputra", "x": 851.4, "y": -256.1, "role": "Imperial seat of the Guptas in Magadha", "desc": "Sprawling capital celebrated by Chinese traveler Faxian for its lavish charitable hospitals and monasteries."},
            {"name": "Ujjayini", "x": 757.8, "y": -231.8, "role": "Second imperial capital under Chandragupta II Vikramaditya", "desc": "Cultural capital where the Nine Jewels (Navaratnas) including poet-dramatist Kalidasa assembled."},
            {"name": "Ayodhya", "x": 822.0, "y": -268.0, "role": "Early royal residence and minting center", "desc": "Prominent administrative seat on the Saryu River celebrated in Gupta literary tradition."}
        ],
        "locations": [
            {"name": "Pataliputra", "type": "capital", "x": 851.4, "y": -256.1, "role": "Imperial seat of the Guptas in Magadha", "desc": "Sprawling capital celebrated by Chinese traveler Faxian for its lavish charitable hospitals and monasteries."},
            {"name": "Ujjayini", "type": "capital", "x": 757.8, "y": -231.8, "role": "Second imperial capital under Chandragupta II Vikramaditya", "desc": "Cultural capital where the Nine Jewels (Navaratnas) including poet-dramatist Kalidasa assembled."},
            {"name": "Prayaga (Allahabad)", "type": "sacred_site", "x": 818.5, "y": -254.4, "role": "Confluence of Ganga-Yamuna; site of Harishena's Allahabad Pillar Inscription", "desc": "Monolithic Ashokan pillar engraved with Harishena's 33-line Sanskrit prasasti of Samudragupta's conquests."},
            {"name": "Nalanda", "type": "university", "x": 854.4, "y": -251.3, "role": "Pan-Asian residential university founded by Kumaragupta I", "desc": "Premier international center of learning housing over 10,000 scholars from across Asia."},
            {"name": "Vidisha / Udayagiri", "type": "sacred_site", "x": 778.0, "y": -235.3, "role": "Malwa administrative center and cave sanctuary", "desc": "Udayagiri Cave 5 features the monumental rock-cut Varaha rescuing the Earth Goddess, commissioned under Chandragupta II."},
            {"name": "Eran (Airikina)", "type": "citadel", "x": 782.0, "y": -241.0, "role": "Military base of Samudragupta and Bhanugupta", "desc": "Famous for the colossal Varaha statue, Janardana temple, and the 510 CE Goparaja Sati pillar."},
            {"name": "Mathura", "type": "provincial_seat", "x": 776.8, "y": -275.0, "role": "Center of Classical Gupta sculpture and religious harmony", "desc": "Created the serene standing Buddha statues with wet-drapery folds that defined classical Asian iconography."},
            {"name": "Tamralipti", "type": "port", "x": 879.2, "y": -223.0, "role": "Foremost eastern seaport trading with Southeast Asia and China", "desc": "Where Faxian spent two years copying Buddhist sutras before embarking for Sri Lanka."},
            {"name": "Valabhi", "type": "provincial_seat", "x": 718.7, "y": -218.8, "role": "Western administrative center in Saurashtra under the Maitrakas", "desc": "Renowned for higher learning, Buddhist viharas, and the codification of the Jaina canonical agamas."},
            {"name": "Bhitari", "type": "citadel", "x": 832.0, "y": -256.0, "role": "Royal pillar inscription documenting Skandagupta's defense against Hunas", "desc": "Skandagupta's red sandstone monolithic pillar recounting his sleepless battle against the barbarian hordes."},
            {"name": "Deogarh (Dashavatara Temple)", "type": "sacred_site", "x": 782.5, "y": -245.4, "role": "Masterpiece of Gupta panchayatana temple architecture", "desc": "Classic 6th-century stone temple featuring the reclining Sheshashayi Vishnu sculpture on the Betwa river."},
            {"name": "Kanchipuram", "type": "citadel", "x": 797.0, "y": -128.3, "role": "Southernmost point reached in Samudragupta's Digvijaya", "desc": "King Vishnugopa of Kanchi was defeated and restored as a tributary ally."}
        ],
        "battles": [
            {
                "name": "Samudragupta's Aryavarta Campaign",
                "year": "c. 350 CE",
                "coords": {"x": 790.0, "y": -270.0},
                "parties": "Samudragupta vs. 9 Northern Kings (Nagasena, Achyuta, Rudradeva)",
                "summary": "Total uprooting ('prasabhoddharana') of nine northern monarchs across the Ganga-Yamuna plain, annexing their realms directly into the Gupta imperial domain.",
                "source": "Allahabad Pillar Inscription of Samudragupta, Line 21"
            },
            {
                "name": "Samudragupta's Southern Expedition (Dakshinapatha)",
                "year": "c. 360 CE",
                "coords": {"x": 798.0, "y": -128.0},
                "parties": "Samudragupta vs. 12 Southern Kings (Vishnugopa of Kanchi, Hastivarman of Vengi)",
                "summary": "Epic 3,000-mile military expedition defeating twelve southern rulers down to Tamil Nadu, liberating them as tributary vassals (Grahana-Moksha-Anugraha).",
                "source": "Allahabad Pillar Inscription, Lines 19–20"
            },
            {
                "name": "Conquest of the Western Kshatrapas",
                "year": "c. 395 CE",
                "coords": {"x": 757.8, "y": -231.8},
                "parties": "Chandragupta II Vikramaditya vs. Rudrasimha III",
                "summary": "Chandragupta II marched into Gujarat and Malwa, slaying the last Western Kshatrapa ruler Rudrasimha III and annexing Arabian Sea ports.",
                "source": "Udayagiri Cave Inscriptions & Silver Coinage of Chandragupta II"
            },
            {
                "name": "Battle of Bhitari (Skandagupta vs. Hunas)",
                "year": "455 CE",
                "coords": {"x": 832.0, "y": -256.0},
                "parties": "Crown Prince Skandagupta vs. White Huns (Hephthalites)",
                "summary": "Skandagupta smashed the first catastrophic White Hun invasion along the northern marches, saving Indian classical civilization while the Roman Empire fell to the Huns in Europe.",
                "source": "Bhitari Stone Pillar Inscription of Skandagupta"
            },
            {
                "name": "Skandagupta's Pushyamitra War",
                "year": "c. 450 CE",
                "coords": {"x": 770.0, "y": -220.0},
                "parties": "Skandagupta vs. Pushyamitra Confederacy",
                "summary": "Skandagupta spent nights sleeping on the bare ground restoring the destabilized fortunes of the Gupta imperial family following Kumaragupta's death.",
                "source": "Bhitari Inscription, Verses 4–5"
            },
            {
                "name": "Battle of Eran (Bhanugupta vs. Toramana)",
                "year": "510 CE",
                "coords": {"x": 782.0, "y": -241.0},
                "parties": "Gupta King Bhanugupta & Goparaja vs. Toramana the Huna",
                "summary": "Violent collision in central India. General Goparaja fell heroically in battle; his wife committed Sati on his funeral pyre, commemorated in the Eran stone pillar.",
                "source": "Eran Stone Pillar Inscription of Bhanugupta, 510 CE"
            },
            {
                "name": "Battle of Sondani",
                "year": "528 CE",
                "coords": {"x": 751.0, "y": -240.5},
                "parties": "Yashodharman of Malwa & Narasimhagupta Baladitya vs. Mihirakula",
                "summary": "Decisive victory shattering the Alchon Hun invasion. The cruel tyrant Mihirakula bowed his head before Yashodharman, breaking Hun power in India forever.",
                "source": "Mandasor Pillar Inscription of Yashodharman & Xuanzang's Records"
            }
        ],
        "events": [
            {"year": "320 CE", "title": "Chandragupta I marries Licchavi princess Kumaradevi; founds the Gupta Era", "desc": "Assumes the imperial title Maharajadhiraja, minting the famous king-and-queen gold coins."},
            {"year": "335–375 CE", "title": "Reign of Samudragupta ('The Indian Napoleon'); performs Ashvamedha", "desc": "Unifies India through military genius; excels as poet (Kaviraja) and veena player."},
            {"year": "375–415 CE", "title": "Reign of Chandragupta II Vikramaditya; Golden Age of Indian literature", "desc": "Kalidasa composes Shakuntala and Meghaduta; Faxian visits peaceful, prosperous cities."},
            {"year": "415–455 CE", "title": "Reign of Kumaragupta I; establishes Nalanda Mahavihara University", "desc": "Celebrates 40 years of peace and prosperity, performing two Ashvamedha horse sacrifices."},
            {"year": "455–467 CE", "title": "Reign of Skandagupta; repulses the Huna invasions and repairs Sudarshana Dam", "desc": "Restores stability to the empire; Junagadh inscription records hydraulic engineering triumphs."},
            {"year": "c. 510–528 CE", "title": "Alchon Hun invasion under Toramana and Mihirakula", "desc": "Destruction of Buddhist monasteries across Gandhara and Punjab."},
            {"year": "528 CE", "title": "Battle of Sondani: Yashodharman and Baladitya crush Mihirakula", "desc": "Liberation of northern India from Hunnic tyranny."},
            {"year": "c. 550 CE", "title": "Disintegration of the imperial Gupta state into regional kingdoms", "desc": "Rise of the Maukharis of Kannauj, Pushyabhutis of Thanesar, and Maitrakas of Valabhi."}
        ]
    },
    "harsha-empire": {
        "capitals": [
            {"name": "Kannauj (Kanyakubja)", "x": 799.2, "y": -270.6, "role": "Imperial seat of Emperor Harsha; glorious metropolis of the Ganga", "desc": "Multi-walled city with hundreds of Buddhist monasteries and Hindu temples described by Xuanzang."},
            {"name": "Thanesar (Sthanishvara)", "x": 768.2, "y": -299.8, "role": "Ancestral Vardhana dynastic capital in Kurukshetra", "desc": "Seat of King Prabhakaravardhana and birthplace of Harsha along the sacred Saraswati river."}
        ],
        "locations": [
            {"name": "Kannauj (Kanyakubja)", "type": "capital", "x": 799.2, "y": -270.6, "role": "Imperial seat of Emperor Harsha; glorious metropolis of the Ganga", "desc": "Multi-walled city with hundreds of Buddhist monasteries and Hindu temples described by Xuanzang."},
            {"name": "Thanesar (Sthanishvara)", "type": "capital", "x": 768.2, "y": -299.8, "role": "Ancestral Vardhana dynastic capital in Kurukshetra", "desc": "Seat of King Prabhakaravardhana and birthplace of Harsha along the sacred Saraswati river."},
            {"name": "Prayag (Allahabad)", "type": "sacred_site", "x": 818.5, "y": -254.4, "role": "Site of Harsha's quinquennial Maha Moksha Parishad", "desc": "Where Harsha held his 75-day festival distributing all royal wealth and personal jewelry to monks and the poor."},
            {"name": "Nalanda Mahavihara", "type": "university", "x": 854.4, "y": -251.3, "role": "Buddhist international university endowed with 100 villages by Harsha", "desc": "Xuanzang studied Yogachara doctrine here under Abbot Shilabhadra for five years."},
            {"name": "Valabhi", "type": "provincial_seat", "x": 718.7, "y": -218.8, "role": "Maitraka western capital subordinated through dynastic alliance", "desc": "King Dhruvasena II married Harsha's daughter and attended the grand Kannauj assembly."},
            {"name": "Varanasi", "type": "sacred_site", "x": 830.0, "y": -253.2, "role": "Spiritual center on the Ganga visited by Harsha and Xuanzang", "desc": "Described by Xuanzang as having 30 Buddhist monasteries and 100 Deva temples with a 100-foot copper statue of Shiva."},
            {"name": "Mathura", "type": "provincial_seat", "x": 776.8, "y": -275.0, "role": "Major religious center along the Yamuna in Harsha's realm", "desc": "Flourishing Buddhist stupas and five grand monasteries along the river banks."},
            {"name": "Kamarupa (Pragjyotishpura)", "type": "provincial_seat", "x": 917.4, "y": -261.8, "role": "Allied kingdom of King Bhaskaravarman in Assam", "desc": "Allied with Harsha to defeat Shashanka of Gauda; escorted Xuanzang to the Kannauj court."},
            {"name": "Kongoda (Ganjam)", "type": "citadel", "x": 850.5, "y": -193.8, "role": "Coastal Orissan realm subdued in Harsha's last campaign", "desc": "Annexed by Harsha in 643 CE, extending his sovereignty to the Chilika Lake."},
            {"name": "Ahichchhatra", "type": "citadel", "x": 791.8, "y": -283.6, "role": "Major fortified city in the central province of Harsha", "desc": "Excavated with monumental terraced temples and Harsha-era seals."},
            {"name": "Shravasti", "type": "provincial_seat", "x": 820.0, "y": -275.0, "role": "Historical Kosalan city visited by Xuanzang", "desc": "Though partially ruined, Jetavana monastery remained an active pilgrimage sanctuary."},
            {"name": "Tamralipti", "type": "port", "x": 879.2, "y": -223.0, "role": "Eastern seaport connecting Harsha's empire to Southeast Asia and China", "desc": "Visited by Chinese pilgrim Daoxuan and maritime merchants carrying Buddhist texts."}
        ],
        "battles": [
            {
                "name": "Battle of the Narmada River",
                "year": "c. 618–619 CE",
                "coords": {"x": 765.0, "y": -218.0},
                "parties": "Harsha (Lord of the North) vs. Pulakeshin II Chalukya (Lord of the South)",
                "summary": "Clash of the Titans. Harsha led his vast northern host with thousands of elephants to the Narmada; Pulakeshin's disciplined Deccan army repelled the invasion, establishing the river as the permanent imperial boundary.",
                "source": "Aihole Inscription of Pulakeshin II, Verse 23 & Xuanzang's Records"
            },
            {
                "name": "Harsha's War with Shashanka of Gauda",
                "year": "c. 606–619 CE",
                "coords": {"x": 880.0, "y": -240.0},
                "parties": "Harsha & Bhaskaravarman vs. Shashanka of Gauda (Bengal)",
                "summary": "Harsha swore vengeance for the treacherous murder of his brother Rajyavardhana; allied with Kamarupa, he waged protracted campaigns, eventually annexing Bengal after Shashanka's death.",
                "source": "Bana's Harshacharita & Buddhist Manjushri-Mula-Kalpa"
            },
            {
                "name": "Subjugation of Vallabhi",
                "year": "c. 625 CE",
                "coords": {"x": 720.0, "y": -220.0},
                "parties": "Harsha vs. Dhruvasena II (Maitrakas of Gujarat)",
                "summary": "Harsha invaded Saurashtra, defeating Dhruvasena II; with the mediation of Dadda II of Broach, Dhruvasena submitted, married Harsha's daughter, and became a premier feudatory.",
                "source": "Nausari Copper Plates & Xuanzang's Travelogue"
            },
            {
                "name": "Conquest of Kongoda (Odisha)",
                "year": "642–643 CE",
                "coords": {"x": 850.0, "y": -195.0},
                "parties": "Harsha vs. Sailodbhava Rulers of Kongoda",
                "summary": "Harsha's final military campaign, subduing the coastal kingdom of Kongoda along the Bay of Bengal and distributing the revenues among scholars and monks.",
                "source": "Life of Hiuen-Tsiang by Huili"
            },
            {
                "name": "Rescue of Rajyashri in the Vindhyas",
                "year": "606 CE",
                "coords": {"x": 785.0, "y": -240.0},
                "parties": "Harsha & Buddhist Monk Divakaramitra vs. Jungle Hostilities",
                "summary": "Following the assassination of King Grahavarman of Kannauj, Harsha tracked his widowed sister Rajyashri into the Vindhya forests, rescuing her as she was about to mount a funeral pyre.",
                "source": "Bana's Harshacharita, Chapter VIII"
            },
            {
                "name": "Campaign against the Hunas of Punjab",
                "year": "605 CE",
                "coords": {"x": 768.2, "y": -299.8},
                "parties": "Crown Prince Rajyavardhana & Harsha vs. Huna Invaders",
                "summary": "King Prabhakaravardhana dispatched his sons to the Himalayan foothills, where Rajyavardhana smashed the Huna horsemen while Harsha hunted in the rear forests.",
                "source": "Bana's Harshacharita, Chapter V"
            }
        ],
        "events": [
            {"year": "606 CE", "title": "Harsha ascends the throne at age 16; unifies Thanesar and Kannauj", "desc": "Combines the Vardhana and Maukhari kingdoms following the murder of his brother Rajyavardhana."},
            {"year": "618 CE", "title": "Battle of the Narmada against Pulakeshin II Chalukya", "desc": "Pulakeshin halts Harsha's advance; formal treaty confirms the Narmada as the border of North and South India."},
            {"year": "629 CE", "title": "Chinese pilgrim Xuanzang begins his 16-year journey across India", "desc": "Travels through the Silk Road, reaches Kannauj, and becomes an honored guest of Emperor Harsha."},
            {"year": "636 CE", "title": "Harsha authors classic Sanskrit dramas Ratnavali, Priyadarsika, and Nagananda", "desc": "Renowned as a patron of literature and an accomplished royal playwright and calligrapher."},
            {"year": "643 CE", "title": "Grand Kannauj Religious Assembly and Maha Moksha Parishad at Prayag", "desc": "Assembly attended by 20 tributary kings, 4,000 Buddhist monks, and thousands of Jaina and Brahmanical scholars."},
            {"year": "647 CE", "title": "Death of Emperor Harsha without an heir; end of the Vardhana Empire", "desc": "Minister Arjuna seizes power; conflict with Chinese envoy Wang Xuance marks the collapse of Kannauj's hegemony."}
        ]
    },
    "classical-southern-dynasties": {
        "capitals": [
            {"name": "Thanjavur", "x": 791.3, "y": -107.8, "role": "Imperial Chola capital; site of Rajaraja's Brihadisvara Temple", "desc": "Granary of Tamilakam and administrative seat of the Middle Chola Empire."},
            {"name": "Gangaikonda Cholapuram", "x": 794.5, "y": -112.0, "role": "New imperial capital built by Rajendra Chola I after victorious northern march", "desc": "Founded 1025 CE with the vast Cholaganga irrigation reservoir ('Liquid Pillar of Victory')."},
            {"name": "Madurai", "x": 781.2, "y": -99.2, "role": "Ancient Pandya capital on the Vaigai river", "desc": "Sacred center of the three legendary Tamil Sangam literary assemblies and the Meenakshi temple."},
            {"name": "Kanchipuram", "x": 797.0, "y": -128.3, "role": "Grand Pallava capital and educational center (Ghatika)", "desc": "City of a thousand temples; capital of Mahendravarman I and Narasimhavarman I."},
            {"name": "Vatapi (Badami)", "x": 756.8, "y": -159.2, "role": "Rock-cut cliff capital of the Early Western Chalukyas", "desc": "Seat of Pulakeshin II surrounded by red sandstone cliff temples and Lake Agastya."},
            {"name": "Manyakheta (Malkhed)", "x": 771.5, "y": -171.8, "role": "Imperial capital of the Rashtrakuta Empire", "desc": "Founded by Amoghavarsha I; celebrated by Arab merchant Sulaiman as one of the four great empires of the world."}
        ],
        "locations": [
            {"name": "Thanjavur", "type": "capital", "x": 791.3, "y": -107.8, "role": "Imperial Chola capital; site of Rajaraja's Brihadisvara Temple", "desc": "Granary of Tamilakam and administrative seat of the Middle Chola Empire."},
            {"name": "Gangaikonda Cholapuram", "type": "capital", "x": 794.5, "y": -112.0, "role": "New imperial capital built by Rajendra Chola I after victorious northern march", "desc": "Founded 1025 CE with the vast Cholaganga irrigation reservoir ('Liquid Pillar of Victory')."},
            {"name": "Madurai", "type": "capital", "x": 781.2, "y": -99.2, "role": "Ancient Pandya capital on the Vaigai river", "desc": "Sacred center of the three legendary Tamil Sangam literary assemblies and the Meenakshi temple."},
            {"name": "Kanchipuram", "type": "capital", "x": 797.0, "y": -128.3, "role": "Grand Pallava capital and educational center (Ghatika)", "desc": "City of a thousand temples; capital of Mahendravarman I and Narasimhavarman I."},
            {"name": "Mamallapuram", "type": "port", "x": 801.9, "y": -126.2, "role": "Pallava royal seaport with monolithic rock-cut rathas and Shore Temple", "desc": "Emporium of Pallava maritime trade with Southeast Asia and China."},
            {"name": "Muziris (Kodungallur)", "type": "port", "x": 762.0, "y": -102.0, "role": "Foremost Chera international port on the Malabar Coast", "desc": "Where Roman ships brought gold and wine to exchange for Malabar black pepper and beryl."},
            {"name": "Korkai", "type": "port", "x": 780.8, "y": -86.5, "role": "Ancient Pandya pearl-fishery port at the mouth of the Thamirabarani", "desc": "Celebrated in Sangam poems and Greco-Roman texts for the world's finest sea pearls."},
            {"name": "Uraiyur (Tiruchirappalli)", "type": "citadel", "x": 786.8, "y": -108.3, "role": "Early Sangam Chola capital noted for fine handloom textiles", "desc": "Ancient fortress capital of Karikala Chola on the southern bank of the Kaveri."},
            {"name": "Puhar / Kaveripattinam", "type": "port", "x": 798.5, "y": -111.5, "role": "Fabled Sangam Chola seaport emporium celebrated in Silappadikaram", "desc": "Cosmopolitan harbor with foreign merchant colonies, lighthouses, and dockyards."},
            {"name": "Vatapi (Badami)", "type": "citadel", "x": 756.8, "y": -159.2, "role": "Rock-cut cliff capital of the Early Western Chalukyas", "desc": "Seat of Pulakeshin II surrounded by red sandstone cliff temples and Lake Agastya."},
            {"name": "Manyakheta (Malkhed)", "type": "citadel", "x": 771.5, "y": -171.8, "role": "Imperial capital of the Rashtrakuta Empire", "desc": "Founded by Amoghavarsha I; celebrated by Arab merchant Sulaiman as one of the four great empires of the world."},
            {"name": "Vengi", "type": "citadel", "x": 811.0, "y": -168.0, "role": "Capital of the Eastern Chalukyas; contested Chola-Chalukya buffer", "desc": "Strategic territory linking the Tamil heartland to Odisha and Bengal."},
            {"name": "Anuradhapura (Sri Lanka)", "type": "citadel", "x": 804.0, "y": -83.5, "role": "Ancient Sinhala capital conquered by Rajaraja Chola I", "desc": "Incorporated into the Chola Empire as the province of Mummudi-Chola-Mandalam in 993 CE."}
        ],
        "battles": [
            {
                "name": "Battle of Venni",
                "year": "c. 130 CE",
                "coords": {"x": 791.3, "y": -107.8},
                "parties": "Karikala Chola vs. Chera & Pandya Confederacy",
                "summary": "Young Karikala decisively defeated the combined armies of the Chera king, Pandya king, and eleven Velir chieftains; the wounded Chera king committed ritual suicide (Vadakkiruthal).",
                "source": "Purananuru 65, 66 & Pattinappalai"
            },
            {
                "name": "Battle of Vatapi",
                "year": "642 CE",
                "coords": {"x": 756.8, "y": -159.2},
                "parties": "Narasimhavarman I Pallava vs. Pulakeshin II Chalukya",
                "summary": "Pallava General Paranjothi stormed and burned the Chalukya cliff fortress of Vatapi; Pulakeshin II fell in defense of his capital, and Narasimhavarman assumed the title Vatapikonda.",
                "source": "Kuram Copper Plates & Mahavamsa"
            },
            {
                "name": "Battle of Sri Purambiyam",
                "year": "879 CE",
                "coords": {"x": 793.0, "y": -109.8},
                "parties": "Aparajita Pallava & Aditya I Chola vs. Varagunavarman II Pandya",
                "summary": "Decisive three-way collision near Kumbakonam. Ganga king Prithvipati I died heroically; Pandya invasion shattered, sparking the resurrection of the Imperial Chola dynasty.",
                "source": "Udayendiram Copper Plates & Tillaisthanam Inscription"
            },
            {
                "name": "Battle of Takkolam",
                "year": "949 CE",
                "coords": {"x": 796.5, "y": -130.0},
                "parties": "Krishna III (Rashtrakuta) & Butuga II vs. Rajaditya Chola",
                "summary": "Rashtrakuta allied army invaded the northern Chola territory; Ganga feudatory Butuga shot Crown Prince Rajaditya with a poisoned arrow atop his royal war elephant.",
                "source": "Atakur Inscription & Karhad Copper Plates"
            },
            {
                "name": "Battle of Koppam",
                "year": "1054 CE",
                "coords": {"x": 760.0, "y": -153.0},
                "parties": "Rajadhiraja & Rajendra II Chola vs. Someshvara I Chalukya",
                "summary": "Emperor Rajadhiraja was mortally wounded on his elephant; his younger brother Rajendra II rallied the retreating Cholas, crowned himself on the active battlefield, and routed the Western Chalukyas.",
                "source": "Manimangalam Inscription of Rajendra Chola II"
            },
            {
                "name": "Battle of Kudal-Sangamam",
                "year": "1062 CE",
                "coords": {"x": 763.5, "y": -162.0},
                "parties": "Virarajendra Chola vs. Someshvara I (Western Chalukyas)",
                "summary": "Fought at the confluence of the Krishna and Tungabhadra rivers. Virarajendra routed Someshvara's sons and generals, erecting a pillar of victory at the confluence.",
                "source": "Kanyakumari Inscription of Virarajendra"
            },
            {
                "name": "Chola Naval Conquest of Anuradhapura",
                "year": "993 CE",
                "coords": {"x": 804.0, "y": -83.5},
                "parties": "Rajaraja Chola I vs. King Mahinda V of Sri Lanka",
                "summary": "Rajaraja dispatched an armada across the Palk Strait, sacked the ancient capital of Anuradhapura, and established Polonnaruwa as the Chola provincial capital.",
                "source": "Thanjavur Brihadisvara Inscriptions & Mahavamsa LV"
            },
            {
                "name": "Chola Expedition to the Ganga",
                "year": "1023 CE",
                "coords": {"x": 880.0, "y": -230.0},
                "parties": "Rajendra Chola I vs. Mahipala I (Pala Empire of Bengal)",
                "summary": "Chola expeditionary force marched north through Odisha to the banks of the sacred Ganga, defeating Pala king Mahipala and carrying holy water to consecrate Gangaikonda Cholapuram.",
                "source": "Tirumalai Rock Inscription of Rajendra Chola I"
            }
        ],
        "events": [
            {"year": "c. 300 BCE – 300 CE", "title": "Classical Sangam Age in Tamilakam", "desc": "Flourishing of Old Tamil poetry (Ettuthokai, Pattupattu) under the Chera, Chola, and Pandya crowns."},
            {"year": "c. 130 CE", "title": "Karikala Chola builds the Kallanai (Grand Anicut) on the Kaveri", "desc": "Oldest surviving stone water-diversion dam in continuous use in the world, irrigating the Delta."},
            {"year": "575 CE", "title": "Simhavishnu founds the Greater Pallava Dynasty at Kanchipuram", "desc": "Ends the mysterious Kalabhra interregnum, inaugurating monumental rock-cut Dravidian architecture."},
            {"year": "642 CE", "title": "Narasimhavarman I (Mamalla) captures Vatapi and sculpts Mamallapuram", "desc": "Carves monolithic rathas and the celebrated 'Descent of the Ganga' open-air rock bas-relief."},
            {"year": "848 CE", "title": "Vijayalaya Chola captures Thanjavur, founding the Imperial Chola Dynasty", "desc": "Transforms a local principality into the dominant maritime empire of the Indian Ocean."},
            {"year": "985–1014 CE", "title": "Reign of Rajaraja Chola I; consecration of the Brihadisvara Temple (1010 CE)", "desc": "Pioneers systematic revenue cadastre, imperial naval fleets, and supreme Dravidian granite architecture."},
            {"year": "1014–1044 CE", "title": "Reign of Rajendra Chola I; Naval expedition to Srivijaya and Kadaram", "desc": "Conquers 14 ports in Sumatra and Malaya; brings the sacred Ganga waters to his new capital."},
            {"year": "1070 CE", "title": "Accession of Kulottunga Chola I; union of Chola and Eastern Chalukya crowns", "desc": "Dispatches major mercantile embassies to Song China and abolishes transit tolls ('Sungam Tavirtta Cholan')."}
        ]
    }
}

def main():
    json_path = os.path.join("frontend", "src", "data", "ancient-empires.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for emp in data.get("empires", []):
        eid = emp["id"]
        if eid in ENRICHMENTS:
            enrich = ENRICHMENTS[eid]
            if "capitals" in enrich:
                emp["capitals"] = enrich["capitals"]
            if "locations" in enrich:
                emp["locations"] = enrich["locations"]
            if "battles" in enrich:
                emp["battles"] = enrich["battles"]
            if "events" in enrich:
                emp["events"] = enrich["events"]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Successfully enriched ancient-empires.json for all 10 empires!")

if __name__ == "__main__":
    main()
