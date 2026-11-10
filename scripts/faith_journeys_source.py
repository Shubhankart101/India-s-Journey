"""Hand-authored content for the faith-journey maps: verse specs, epic fill-ins and the journeys themselves.

Verse *text* is never typed here. scripts/pull_faith_verses.py copies it from the source pages named by each spec into
data/faith-sources/verses.json; only the English translations (our own) and citations live in this file.
scripts/build_faith_journeys.py joins everything into data/faith-journeys.json.
"""
from __future__ import annotations

WS = "https://sa.wikisource.org/wiki/"
SC = "https://suttacentral.net/"
FR = "https://fr.wikisource.org/wiki/Fables_de_La_Fontaine_(%C3%A9d._1874)/%C3%80_Monseigneur_le_Dauphin"


def ws(page, needle, lang, citation, work, join_next=0):
    return {"provider": "ws", "url": WS + page, "needle": needle, "join_next": join_next, "lang": lang,
            "citation": citation, "work": work, "verified_from": WS + page}


def sc(uid, segment, citation, human=None, work="Pali Canon", join_next=0):
    return {"provider": "sc", "uid": uid, "segment": segment, "join_next": join_next, "lang": "pi", "citation": citation,
            "work": work, "verified_from": SC + (human or uid) + "/en/sujato"}


def gg(ang, needle, citation, join_next=0):
    return {"provider": "gg", "ang": ang, "needle": needle, "join_next": join_next, "lang": "pa",
            "citation": citation, "work": "Guru Granth Sahib",
            "verified_from": f"https://www.sikhitothemax.org/ang?ang={ang}&source=G"}


VERSES = {
    # Vedas and Upanishads
    "rv_10_75_5": ws("ऋग्वेदः_सूक्तं_१०.७५", "इमं मे गङ्गे", "sa", "Rigveda 10.75.5 (Nadistuti)", "Rigveda"),
    "rv_1_164_46": ws("ऋग्वेदः_सूक्तं_१.१६४", "एकं सद्विप्रा", "sa", "Rigveda 1.164.46", "Rigveda"),
    "cu_6_8_7": ws("छान्दोग्योपनिषद्/अध्यायः_६", "तत्त्वमसि", "sa", "Chandogya Upanishad 6.8.7", "Upanishads"),
    "bu_1_3_28": ws("बृहदारण्यक_उपनिषद्_1a", "असतो मा", "sa", "Brihadaranyaka Upanishad 1.3.28", "Upanishads"),
    "mu_3_1_6": ws("मुण्डकोपनिषद्", "सत्यमेव जयते", "sa", "Mundaka Upanishad 3.1.6", "Upanishads", join_next=1),
    "ka_1_3_14": ws("कठोपनिषत्/प्रथमोध्यायः/तृतीयवल्ली", "उत्तिष्ठत जाग्रत", "sa", "Katha Upanishad 1.3.14", "Upanishads", join_next=1),
    "tai_2_1_1": ws("तैत्तिरीयोपनिषदत्/ब्रह्मानन्दवल्ली", "सत्यं ज्ञानमनन्तं", "sa", "Taittiriya Upanishad 2.1.1", "Upanishads"),
    "isha_1": ws("ईशावास्\u200dयोपनिषद्", "ईशावास्यमिदँ", "sa", "Isha Upanishad 1", "Upanishads"),
    # Panchatantra
    "pt_open": ws("पञ्चतन्त्रम्_०१", "सकलार्थशास्त्रसारं", "sa", "Panchatantra, opening verse", "Panchatantra"),
    "lafontaine": {"provider": "ws", "url": FR, "needle": "Je me sers d'animaux pour instruire les hommes", "join_next": 0,
                   "lang": "fr", "citation": "La Fontaine, Fables, dedication \u00ab \u00c0 Monseigneur le Dauphin \u00bb (1668)",
                   "work": "Fables of La Fontaine", "verified_from": FR},
    # Mahavira (Jain philosophy; the Prakrit canon could not be checked against an online text)
    "ts_1_2": ws("तत्त्वार्थसूत्रम्/प्रथमोऽध्यायः", "तत्त्वार्थश्रद्धानं", "sa", "Tattvartha Sutra 1.2", "Tattvartha Sutra"),
    "ts_5_21": ws("तत्त्वार्थसूत्रम्/पञ्चमोऽध्यायः", "परस्परोपग्रहो", "sa", "Tattvartha Sutra 5.21", "Tattvartha Sutra"),
    "ts_7_13": ws("तत्त्वार्थसूत्रम्/सप्तमोऽध्यायः", "प्रमत्तयोगात्", "sa", "Tattvartha Sutra 7.13", "Tattvartha Sutra"),
    "ts_10_1": ws("तत्त्वार्थसूत्रम्/दशमोऽध्यायः", "मोहक्षयाज्ज्ञान", "sa", "Tattvartha Sutra 10.1", "Tattvartha Sutra"),
    "ts_1_1": ws("तत्त्वार्थसूत्रम्/प्रथमोऽध्यायः", "मोक्षमार्गः", "sa", "Tattvartha Sutra 1.1", "Tattvartha Sutra"),
    "ts_7_1": ws("तत्त्वार्थसूत्रम्/सप्तमोऽध्यायः", "विरतिर्व्रतम्", "sa", "Tattvartha Sutra 7.1", "Tattvartha Sutra"),
    "ts_7_11": ws("तत्त्वार्थसूत्रम्/सप्तमोऽध्यायः", "मैत्री-प्रमोद", "sa", "Tattvartha Sutra 7.11", "Tattvartha Sutra"),
    "ts_10_2": ws("तत्त्वार्थसूत्रम्/दशमोऽध्यायः", "कर्मविप्रमोक्षो", "sa", "Tattvartha Sutra 10.2", "Tattvartha Sutra"),
    # Buddha
    "mn123": sc("mn123", "mn123:20.2", "Majjhima Nikaya 123 (Acchariyabbhutasutta)"),
    "mn53": sc("mn53", "mn53:1.2", "Majjhima Nikaya 53 (Sekhasutta)"),
    "sn56_11": sc("sn56.11", "sn56.11:2.1", "Samyutta Nikaya 56.11 (Dhammacakkappavattanasutta)"),
    "snp3_1": sc("snp3.1", "snp3.1:1.1", "Sutta Nipata 3.1 (Pabbajjasutta)", join_next=3),
    "dn1": sc("dn1", "dn1:1.1.2", "Digha Nikaya 1 (Brahmajalasutta)"),
    "dn16_vesali": sc("dn16", "dn16:3.2.4", "Digha Nikaya 16 (Mahaparinibbanasutta) 3.2"),
    "dn16_kusinara": sc("dn16", "dn16:3.51.4", "Digha Nikaya 16 (Mahaparinibbanasutta) 3.51"),
    "dn16_pataligama": sc("dn16", "dn16:1.26.1", "Digha Nikaya 16 (Mahaparinibbanasutta) 1.26"),
    "sn4_5": sc("sn4.5", "sn4.5:2.3", "Samyutta Nikaya 4.5 (Pasasutta)"),
    "dhp1": sc("dhp1-20", "dhp1:1", "Dhammapada 1", "dhp1-20", join_next=5),
    "dhp5": sc("dhp1-20", "dhp5:1", "Dhammapada 5", "dhp1-20", join_next=3),
    "dhp153": sc("dhp146-156", "dhp153:1", "Dhammapada 153", "dhp146-156", join_next=3),
    "dhp183": sc("dhp179-196", "dhp183:1", "Dhammapada 183", "dhp179-196", join_next=3),
    "dhp276": sc("dhp273-289", "dhp276:1", "Dhammapada 276", "dhp273-289", join_next=3),
    "dhp354": sc("dhp334-359", "dhp354:1", "Dhammapada 354", "dhp334-359", join_next=3),
    # Guru Granth Sahib
    "gg_1_mool": gg(1, "ੴ ਸਤਿ ਨਾਮੁ", "Guru Granth Sahib, Ang 1 (Mool Mantar)"),
    "gg_1_sochai": gg(1, "ਸੋਚੈ ਸੋਚਿ", "Guru Granth Sahib, Ang 1 (Japji, pauri 1)"),
    "gg_1_hukmi": gg(1, "ਹੁਕਮੀ ਹੋਵਨਿ ਆਕਾਰ", "Guru Granth Sahib, Ang 1 (Japji, pauri 2)"),
    "gg_5": gg(5, "ਪਾਤਾਲਾ ਪਾਤਾਲ ਲਖ", "Guru Granth Sahib, Ang 5 (Japji, pauri 22)"),
    "gg_8": gg(8, "ਕਰਮ ਖੰਡ ਕੀ ਬਾਣੀ ਜੋਰੁ", "Guru Granth Sahib, Ang 8 (Japji, pauri 37)"),
    "gg_663": gg(663, "ਗਗਨ ਮੈ ਥਾਲੁ", "Guru Granth Sahib, Ang 663 (Dhanasari, Aarti)"),
    "gg_938": gg(938, "ਸਿਧ ਸਭਾ ਕਰਿ ਆਸਣਿ", "Guru Granth Sahib, Ang 938 (Ramkali, Siddh Gosht)"),
    "gg_1245": gg(1245, "ਘਾਲਿ ਖਾਇ", "Guru Granth Sahib, Ang 1245 (Sarang, shalok)", 1),
    "gg_1412": gg(1412, "ਜਉ ਤਉ ਪ੍ਰੇਮ", "Guru Granth Sahib, Ang 1412 (shalok)", 1),
    "gg_474": gg(474, "ਆਸਕੁ ਕਾਂਢੀਐ", "Guru Granth Sahib, Ang 474 (Asa di Var, shalok of Guru Angad)"),
    "gg_917": gg(917, "ਅਨੰਦੁ ਭਇਆ", "Guru Granth Sahib, Ang 917 (Ramkali, Anand)"),
    "gg_773": gg(773, "ਹਰਿ ਪਹਿਲੜੀ ਲਾਵ", "Guru Granth Sahib, Ang 773 (Suhi, Lavan)"),
    "gg_394": gg(394, "ਤੇਰਾ ਕੀਆ ਮੀਠਾ", "Guru Granth Sahib, Ang 394 (Asa)"),
    "gg_1429": gg(1429, "ਥਾਲ ਵਿਚਿ ਤਿੰਨਿ", "Guru Granth Sahib, Ang 1429 (Mundavani)"),
    "gg_262": gg(262, "ਆਦਿ ਗੁਰਏ ਨਮਹ", "Guru Granth Sahib, Ang 262 (Gauri, Sukhmani)"),
    "gg_633": gg(633, "ਜੋ ਨਰੁ ਦੁਖ ਮੈ ਦੁਖੁ ਨਹੀ", "Guru Granth Sahib, Ang 633 (Sorath, Guru Tegh Bahadur)"),
    "gg_1427": gg(1427, "ਭੈ ਕਾਹੂ ਕਉ", "Guru Granth Sahib, Ang 1427 (shalok of Guru Tegh Bahadur)", 1),
    "gg_1105": gg(1105, "ਸੂਰਾ ਸੋ ਪਹਿਚਾਨੀਐ", "Guru Granth Sahib, Ang 1105 (Maru, Bhagat Kabir)"),
}

# Verses for epic kingdoms that had none. "generic" ones are labelled 'From the epic (general)' in the UI.
EPIC_GENERIC = {
    "mahabharata:indraprastha": {"provider": "mbh", "ref": "1.134.6", "generic": False, "epic": "mahabharata", "entry": "indraprastha",
                                 "citation": "Mahabharata 1.134.6"},
    "mahabharata:manipura": {"provider": "mbh", "ref": "2.23.37", "generic": True, "epic": "mahabharata", "entry": "manipura",
                             "citation": "Mahabharata 2.23.37"},
    "mahabharata:saurashtra": {"provider": "mbh", "ref": "17.1.6", "generic": True, "epic": "mahabharata", "entry": "saurashtra",
                               "citation": "Mahabharata 17.1.6"},
    "ramayana:chitrakuta": {"provider": "val", "ref": "2.94.2", "generic": False, "epic": "ramayana", "entry": "chitrakuta",
                            "citation": "Valmiki Ramayana 2.94.2"},
    "ramayana:kanyakubja": {"provider": "val", "ref": "1.34.6", "generic": False, "epic": "ramayana", "entry": "kanyakubja",
                            "citation": "Valmiki Ramayana 1.34.6"},
    "ramayana:mahendra-hill": {"provider": "val", "ref": "5.1.15", "generic": False, "epic": "ramayana", "entry": "mahendra-hill",
                               "citation": "Valmiki Ramayana 5.1.15"},
    "ramayana:kashi": {"provider": "val", "ref": "3.37.13", "generic": True, "epic": "ramayana", "entry": "kashi",
                       "citation": "Valmiki Ramayana 3.37.13"},
}

# Verses for stops on the epic routes that are not entries of the kingdoms atlas (pulled the same way as EPIC_GENERIC).
EPIC_ROUTE_VERSES = {
    "route:varanavata": {"provider": "mbh", "ref": "1.154.13", "generic": False, "citation": "Mahabharata 1.154.13"},
    "route:ekachakra": {"provider": "mbh", "ref": "1.170.2", "generic": True, "citation": "Mahabharata 1.170.2"},
    "route:mahaprasthana": {"provider": "mbh", "ref": "17.2.2", "generic": False, "citation": "Mahabharata 17.2.2"},
}