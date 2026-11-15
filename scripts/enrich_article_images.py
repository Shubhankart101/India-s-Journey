#!/usr/bin/env python3
"""
Enriches articles in data/substack-latest.json, data/indian-matrix-latest.json,
and data/catalog.json with authentic lead images from Substack CDN and Pew Research.
"""
from __future__ import annotations

import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

KNOWN_IMAGES = {
    # Polity & Policy
    "what's next for modi after the midterms": "https://substackcdn.com/image/fetch/$s_!kf6B!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac221d2d-405e-42c8-83b1-1b324d598182_1152x768.jpeg",
    "what’s next for modi after the midterms": "https://substackcdn.com/image/fetch/$s_!kf6B!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac221d2d-405e-42c8-83b1-1b324d598182_1152x768.jpeg",
    "delhi police and virtue of a disproportionate": "https://substackcdn.com/image/fetch/$s_!DBFF!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1c614127-8d4d-4e7d-bac3-61dcc0a7279f_1792x1008.jpeg",
    "captain smit machchhar saves the day": "https://substackcdn.com/image/fetch/$s_!rj5P!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F42fdead7-3365-42c5-aa8c-3a50d0a7c7be_1792x1008.jpeg",
    "india’s voters are fast becoming transactional": "https://substackcdn.com/image/fetch/$s_!V4l9!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F00644181-53cb-46f7-b4a9-226aa68006ad_1728x1152.jpeg",
    "stop fearing india's $110 billion china": "https://substackcdn.com/image/fetch/$s_!tF2Z!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86d54965-39ef-4633-aae9-4abda41c7560_1152x768.jpeg",
    "why you may not ‘feel’ the gdp growth": "https://substackcdn.com/image/fetch/$s_!9RkP!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe7f22379-cb4a-493f-8461-8ee22030ce14_1152x768.jpeg",
    "modi must build the cities states": "https://substackcdn.com/image/fetch/$s_!t6xQ!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1c614127-8d4d-4e7d-bac3-61dcc0a7279f_1792x1008.jpeg",

    # Indian Matrix
    "white-collar terror": "https://substackcdn.com/image/fetch/$s_!7ed1!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7ed17470-765e-4407-acde-6e21c5df65ae_1677x938.png",
    "how idbi embalmed nehruvian socialism": "https://substackcdn.com/image/fetch/$s_!u8ev!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa7998f9e-9f1d-4ddd-897d-f0316c77bee9_1677x938.png",
    "from ‘gunda raj’ to industrial engine": "https://substackcdn.com/image/fetch/$s_!BbXY!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9173021a-0d06-4a71-a42c-f903267fc74c_1677x938.png",
    "from ₹269 a gb to almost free": "https://substackcdn.com/image/fetch/$s_!m6qA!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faed47fc2-64dc-4073-ae8a-1d54daf9fefe_1677x938.png",
    "the price of saying no tariffs": "https://substackcdn.com/image/fetch/$s_!d669!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd669431c-fc84-4072-8e7b-2db98c257b51_1677x938.png",
    "why the ballot paper brigade won't go away": "https://substackcdn.com/image/fetch/$s_!b29c!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4978a2cb-ff13-43dc-8fc9-b68bbda7738b_1677x938.png",
    "form 6 to supreme court": "https://substackcdn.com/image/fetch/$s_!e91a!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc05f15a1-7785-48fa-bb64-c2bbca93297a_1677x938.png",

    # Pew Research Center
    "what we know about eligible voters who are naturalized u.s. citizens": "https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/SR_26.10.27_naturalized_voters_crop.png",
    "how do americans feel about g20 countries?": "https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.16_G20views_featured.png",
    "social media platform use around the world": "https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.01_socialMedia_featured.png",
    "americans are negative about social media’s impact on democracy": "https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.01_socialMedia_featured.png",
    "across the globe, people increasingly say social media is harming democracy": "https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.01_socialMedia_featured.png",
}


def fetch_feed_images(url: str) -> dict[str, str]:
    mapping = {}
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as res:
            xml_data = res.read()
        root = ET.fromstring(xml_data)
        for item in root.findall('channel/item'):
            title = (item.findtext('title') or '').strip().lower()
            enc = item.find('enclosure')
            if enc is not None and enc.get('url'):
                mapping[title] = enc.get('url')
    except Exception as e:
        print(f"Warning: Could not fetch feed {url}: {e}")
    return mapping


def find_image_for_title(title: str, feed_map: dict[str, str]) -> str:
    clean = (title or '').lower().strip()
    if clean in feed_map:
        return feed_map[clean]
    for k, v in feed_map.items():
        if k in clean or clean in k:
            return v
    for k, v in KNOWN_IMAGES.items():
        if k in clean or clean in k:
            return v
    return ""


def main():
    print("Fetching live RSS feeds...")
    pp_feed = fetch_feed_images("https://politypolicy.substack.com/feed")
    im_feed = fetch_feed_images("https://indianmatrix.substack.com/feed")

    # 1. Update substack-latest.json
    pp_file = ROOT / "data" / "substack-latest.json"
    if pp_file.exists():
        data = json.loads(pp_file.read_text(encoding="utf-8"))
        for art in data.get("articles", []):
            img = find_image_for_title(art.get("title", ""), pp_feed)
            if img:
                art["image_url"] = img
        pp_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {pp_file} with article image URLs.")

    # 2. Update indian-matrix-latest.json
    im_file = ROOT / "data" / "indian-matrix-latest.json"
    if im_file.exists():
        data = json.loads(im_file.read_text(encoding="utf-8"))
        for art in data.get("articles", []):
            img = find_image_for_title(art.get("title", ""), im_feed)
            if img:
                art["image_url"] = img
        im_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        docs_im = ROOT / "docs" / "data" / "indian-matrix-latest.json"
        if docs_im.parent.exists():
            docs_im.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {im_file} with article image URLs.")

    # 3. Update data/catalog.json
    cat_file = ROOT / "data" / "catalog.json"
    if cat_file.exists():
        cat = json.loads(cat_file.read_text(encoding="utf-8"))
        combined_map = {**pp_feed, **im_feed, **KNOWN_IMAGES}
        updated = 0
        for art in cat.get("articles", []):
            title = art.get("title", "")
            img = find_image_for_title(title, combined_map)
            if img:
                art["image_url"] = img
                updated += 1
        cat_file.write_text(json.dumps(cat) + "\n", encoding="utf-8")
        print(f"Updated {updated} articles in {cat_file} with authentic image URLs.")


if __name__ == "__main__":
    main()
