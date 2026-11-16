import json
import math
import re

with open('frontend/src/data/metro/all_city_packs.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'export const CITY_RAW_DATA = (\{[\s\S]*?\n\};)', content)
if not m:
    print("Could not find CITY_RAW_DATA")
    exit(1)

raw_json_str = m.group(1).rstrip(';')
city_data = json.loads(raw_json_str)

def make_curve(p1, p2, bend=0.01, num_pts=15):
    """Generates an organic meandering curve between two coordinates."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    nx = -dy / (dist or 1)
    ny = dx / (dist or 1)
    pts = []
    for i in range(num_pts + 1):
        t = i / num_pts
        # Base interpolation
        x = p1[0] + dx * t
        y = p1[1] + dy * t
        # Natural sine wave meander
        wiggle = math.sin(t * math.pi * 2.5) * bend + math.sin(t * math.pi * 5) * (bend * 0.4)
        pts.append([round(x + nx * wiggle, 5), round(y + ny * wiggle, 5)])
    return pts

def make_ring(cx, cy, rx, ry, num_pts=24, irregular=0.005):
    """Generates an organic ring road / bypass around a city center."""
    pts = []
    for i in range(num_pts + 1):
        angle = (i / num_pts) * 2 * math.pi
        w = math.sin(angle * 3) * irregular
        x = cx + (rx + w) * math.cos(angle)
        y = cy + (ry + w) * math.sin(angle)
        pts.append([round(x, 5), round(y, 5)])
    return pts

def make_radial(cx, cy, angle_deg, length, num_pts=10, bend=0.004):
    """Generates a radial highway originating from or passing through city center."""
    rad = math.radians(angle_deg)
    dx = math.cos(rad) * length
    dy = math.sin(rad) * length
    p1 = [cx - dx * 0.3, cy - dy * 0.3]
    p2 = [cx + dx, cy + dy]
    return make_curve(p1, p2, bend=bend, num_pts=num_pts)

# City Geographic Blueprints (Center, Rivers, Roads, Rail)
CITY_GEOMETRIES = {
    "mumbai": {
        "cx": 72.85, "cy": 19.07,
        "water": [
            # Arabian Sea West Coastline
            {"n": "Arabian Sea Coast", "t": "coastline", "g": make_curve([72.81, 18.90], [72.80, 19.30], bend=0.018, num_pts=30)},
            # Thane Creek East Coastline
            {"n": "Thane Creek", "t": "bay", "g": make_curve([72.93, 18.98], [72.99, 19.22], bend=0.012, num_pts=25)},
            # Mithi River
            {"n": "Mithi River", "t": "river", "g": make_curve([72.89, 19.12], [72.85, 19.05], bend=0.008, num_pts=15)},
            # Mahim Bay
            {"n": "Mahim Bay", "t": "bay", "g": make_curve([72.83, 19.05], [72.84, 19.03], bend=0.006, num_pts=10)},
            # Powai Lake
            {"n": "Powai Lake", "t": "lake", "g": make_ring(72.91, 19.126, 0.012, 0.008, num_pts=16)},
            # Tulsi Lake
            {"n": "Tulsi Lake", "t": "lake", "g": make_ring(72.92, 19.19, 0.009, 0.007, num_pts=14)},
        ],
        "roads": [
            # Western Express Highway (WEH)
            {"c": 3, "g": make_curve([72.84, 19.04], [72.86, 19.26], bend=-0.01, num_pts=20)},
            # Eastern Express Highway (EEH)
            {"c": 3, "g": make_curve([72.87, 19.01], [72.97, 19.20], bend=0.012, num_pts=20)},
            # SV Road
            {"c": 2, "g": make_curve([72.835, 19.05], [72.845, 19.25], bend=-0.008, num_pts=18)},
            # Link Road
            {"c": 2, "g": make_curve([72.825, 19.08], [72.84, 19.26], bend=-0.007, num_pts=18)},
            # Jogeshwari-Vikhroli Link Road (JVLR)
            {"c": 3, "g": make_curve([72.835, 19.135], [72.935, 19.12], bend=0.006, num_pts=15)},
            # Santa Cruz-Chembur Link Road (SCLR)
            {"c": 3, "g": make_curve([72.855, 19.075], [72.91, 19.065], bend=0.005, num_pts=12)},
            # Ghodbunder Road Thane
            {"c": 3, "g": make_curve([72.97, 19.20], [72.88, 19.28], bend=0.015, num_pts=16)},
            # Bandra-Worli Sea Link
            {"c": 3, "g": make_curve([72.815, 19.01], [72.825, 19.05], bend=0.005, num_pts=10)},
            # Eastern Freeway
            {"c": 3, "g": make_curve([72.84, 18.94], [72.89, 19.04], bend=0.008, num_pts=14)},
            # LBS Marg
            {"c": 2, "g": make_curve([72.87, 19.06], [72.96, 19.19], bend=0.009, num_pts=16)},
        ],
        "rail": [
            # Western Railway Trunk
            {"g": make_curve([72.82, 18.93], [72.85, 19.28], bend=-0.008, num_pts=22)},
            # Central Railway Trunk
            {"g": make_curve([72.835, 18.94], [72.98, 19.20], bend=0.012, num_pts=22)},
            # Harbour Line
            {"g": make_curve([72.84, 18.95], [72.94, 19.06], bend=0.015, num_pts=18)},
        ]
    },
    "bengaluru": {
        "cx": 77.60, "cy": 12.97,
        "water": [
            # Ulsoor Lake
            {"n": "Ulsoor Lake", "t": "lake", "g": make_ring(77.62, 12.982, 0.007, 0.006, num_pts=16)},
            # Bellandur Lake
            {"n": "Bellandur Lake", "t": "lake", "g": make_ring(77.67, 12.936, 0.018, 0.009, num_pts=20)},
            # Varthur Lake
            {"n": "Varthur Lake", "t": "lake", "g": make_ring(77.72, 12.942, 0.015, 0.008, num_pts=18)},
            # Hebbal Lake
            {"n": "Hebbal Lake", "t": "lake", "g": make_ring(77.59, 13.045, 0.011, 0.007, num_pts=16)},
            # Sankey Tank
            {"n": "Sankey Tank", "t": "lake", "g": make_ring(77.575, 13.008, 0.005, 0.005, num_pts=12)},
            # Madivala Lake
            {"n": "Madivala Lake", "t": "lake", "g": make_ring(77.62, 12.912, 0.011, 0.008, num_pts=16)},
            # Vrishabhavathi River Channel
            {"n": "Vrishabhavathi Valley", "t": "stream", "g": make_curve([77.53, 12.98], [77.49, 12.87], bend=0.009, num_pts=15)},
        ],
        "roads": [
            # Outer Ring Road (ORR) Full Loop
            {"c": 3, "g": make_ring(77.61, 12.97, 0.095, 0.085, num_pts=32, irregular=0.008)},
            # Inner Ring Road
            {"c": 2, "g": make_curve([77.60, 12.93], [77.64, 12.98], bend=0.008, num_pts=12)},
            # Hosur Road (NH 44 South)
            {"c": 3, "g": make_radial(77.60, 12.95, -70, 0.16, num_pts=16)},
            # Bellary Road (Airport Road NH 44 North)
            {"c": 3, "g": make_radial(77.59, 12.99, 80, 0.18, num_pts=18)},
            # Old Madras Road (East NH 75)
            {"c": 3, "g": make_radial(77.63, 12.98, 15, 0.16, num_pts=16)},
            # Tumkur Road (North-West NH 48)
            {"c": 3, "g": make_radial(77.54, 13.00, 140, 0.16, num_pts=16)},
            # Mysore Road (South-West)
            {"c": 3, "g": make_radial(77.55, 12.95, -135, 0.15, num_pts=15)},
            # Sarjapur Road
            {"c": 2, "g": make_radial(77.62, 12.93, -40, 0.14, num_pts=14)},
            # Kanakapura Road
            {"c": 2, "g": make_radial(77.57, 12.92, -105, 0.14, num_pts=14)},
            # Bannerghatta Road
            {"c": 2, "g": make_radial(77.59, 12.93, -85, 0.14, num_pts=14)},
            # NICE Peripheral Road
            {"c": 3, "g": make_curve([77.47, 12.98], [77.65, 12.84], bend=-0.02, num_pts=20)},
        ],
        "rail": [
            # SWR Bangalore City – Yeshvantpur – Tumkur
            {"g": make_curve([77.57, 12.975], [77.53, 13.05], bend=-0.006, num_pts=15)},
            # SWR Bangalore City – Cantonment – KR Puram – Chennai
            {"g": make_curve([77.57, 12.975], [77.72, 13.01], bend=0.007, num_pts=18)},
            # SWR Bangalore City – Kengeri – Mysore
            {"g": make_curve([77.57, 12.975], [77.48, 12.91], bend=-0.008, num_pts=16)},
        ]
    },
    "kolkata": {
        "cx": 88.36, "cy": 22.56,
        "water": [
            # Majestic Hooghly River North to South
            {"n": "Hooghly River (Ganga)", "t": "river", "g": make_curve([88.36, 22.68], [88.31, 22.46], bend=0.016, num_pts=35)},
            # Circular Canal / Bagbazar Canal
            {"n": "Circular Canal", "t": "canal", "g": make_curve([88.37, 22.60], [88.40, 22.56], bend=0.008, num_pts=15)},
            # Subhas Sarobar
            {"n": "Subhas Sarobar", "t": "lake", "g": make_ring(88.40, 22.57, 0.006, 0.004, num_pts=12)},
            # Rabindra Sarobar (Dhakuria Lake)
            {"n": "Rabindra Sarobar", "t": "lake", "g": make_ring(88.36, 22.51, 0.009, 0.004, num_pts=14)},
            # East Kolkata Wetlands
            {"n": "East Kolkata Wetlands", "t": "lake", "g": make_ring(88.44, 22.54, 0.022, 0.015, num_pts=20)},
        ],
        "roads": [
            # Eastern Metropolitan Bypass (EM Bypass)
            {"c": 3, "g": make_curve([88.41, 22.61], [88.39, 22.47], bend=-0.012, num_pts=24)},
            # AJC Bose Road / Maa Flyover
            {"c": 3, "g": make_curve([88.34, 22.54], [88.41, 22.54], bend=0.005, num_pts=14)},
            # VIP Road (To Airport)
            {"c": 3, "g": make_curve([88.40, 22.59], [88.44, 22.65], bend=0.008, num_pts=16)},
            # Belghoria Expressway
            {"c": 3, "g": make_curve([88.35, 22.65], [88.44, 22.64], bend=0.006, num_pts=14)},
            # Kona Expressway (Howrah side)
            {"c": 3, "g": make_curve([88.29, 22.56], [88.33, 22.56], bend=0.005, num_pts=10)},
            # Central Avenue (Chittaranjan Avenue)
            {"c": 2, "g": make_curve([88.36, 22.56], [88.37, 22.61], bend=0.003, num_pts=12)},
            # Diamond Harbour Road
            {"c": 2, "g": make_curve([88.33, 22.53], [88.31, 22.44], bend=-0.006, num_pts=15)},
            # Grand Trunk Road (Howrah)
            {"c": 2, "g": make_curve([88.33, 22.62], [88.31, 22.55], bend=-0.005, num_pts=15)},
        ],
        "rail": [
            # Howrah Railway Terminal & Trunks West
            {"g": make_curve([88.34, 22.585], [88.27, 22.62], bend=-0.008, num_pts=16)},
            # Sealdah Railway Terminal & Eastern Railway North
            {"g": make_curve([88.37, 22.568], [88.39, 22.66], bend=0.006, num_pts=18)},
            # Sealdah South Lines
            {"g": make_curve([88.37, 22.565], [88.37, 22.46], bend=0.005, num_pts=16)},
        ]
    },
    "chennai": {
        "cx": 80.24, "cy": 13.06,
        "water": [
            # Bay of Bengal Coastline North to South
            {"n": "Bay of Bengal Coast", "t": "coastline", "g": make_curve([80.30, 13.18], [80.27, 12.92], bend=0.012, num_pts=30)},
            # Cooum River winding through heart of Chennai
            {"n": "Cooum River", "t": "river", "g": make_curve([80.14, 13.07], [80.285, 13.07], bend=0.011, num_pts=22)},
            # Adyar River
            {"n": "Adyar River", "t": "river", "g": make_curve([80.15, 13.01], [80.275, 13.01], bend=0.009, num_pts=20)},
            # Buckingham Canal
            {"n": "Buckingham Canal", "t": "canal", "g": make_curve([80.28, 13.14], [80.25, 12.94], bend=0.006, num_pts=22)},
        ],
        "roads": [
            # Anna Salai (Mount Road)
            {"c": 3, "g": make_curve([80.28, 13.08], [80.19, 13.00], bend=-0.007, num_pts=18)},
            # Grand Southern Trunk (GST Road / NH 32)
            {"c": 3, "g": make_radial(80.18, 12.99, -125, 0.15, num_pts=16)},
            # Old Mahabalipuram Road (OMR IT Corridor)
            {"c": 3, "g": make_radial(80.25, 12.99, -85, 0.16, num_pts=18)},
            # East Coast Road (ECR)
            {"c": 2, "g": make_radial(80.26, 12.98, -80, 0.15, num_pts=16)},
            # Inner Ring Road (Jawaharlal Nehru Road)
            {"c": 3, "g": make_curve([80.20, 13.12], [80.20, 12.98], bend=0.01, num_pts=20)},
            # Poonamallee High Road (NH 48)
            {"c": 3, "g": make_radial(80.27, 13.08, 175, 0.18, num_pts=18)},
        ],
        "rail": [
            # Chennai Central to North (Arakkonam/Gudur)
            {"g": make_curve([80.275, 13.082], [80.21, 13.15], bend=0.007, num_pts=16)},
            # Chennai Beach – Egmore – Tambaram (South Suburb Trunk)
            {"g": make_curve([80.29, 13.09], [80.12, 12.92], bend=-0.009, num_pts=22)},
        ]
    },
    "hyderabad": {
        "cx": 78.47, "cy": 17.40,
        "water": [
            # Hussain Sagar Lake Centerpiece
            {"n": "Hussain Sagar Lake", "t": "lake", "g": make_ring(78.47, 17.425, 0.015, 0.013, num_pts=20)},
            # Musi River flowing West to East
            {"n": "Musi River", "t": "river", "g": make_curve([78.38, 17.37], [78.58, 17.38], bend=0.009, num_pts=25)},
            # Osman Sagar
            {"n": "Osman Sagar (Gandipet)", "t": "lake", "g": make_ring(78.30, 17.38, 0.022, 0.014, num_pts=18)},
            # Mir Alam Tank
            {"n": "Mir Alam Tank", "t": "lake", "g": make_ring(78.44, 17.35, 0.012, 0.009, num_pts=15)},
        ],
        "roads": [
            # Nehru Outer Ring Road (ORR) Expressway
            {"c": 3, "g": make_ring(78.46, 17.40, 0.15, 0.13, num_pts=36, irregular=0.01)},
            # Inner Ring Road
            {"c": 3, "g": make_ring(78.47, 17.41, 0.075, 0.065, num_pts=28, irregular=0.006)},
            # PV Narasimha Rao Expressway (Airport Elevated)
            {"c": 3, "g": make_curve([78.44, 17.38], [78.40, 17.32], bend=0.006, num_pts=14)},
            # Gachibowli – Hitec City Arterial (Cyberabad)
            {"c": 2, "g": make_curve([78.35, 17.42], [78.41, 17.45], bend=0.005, num_pts=12)},
            # Sardar Patel Road Secunderabad
            {"c": 2, "g": make_curve([78.46, 17.44], [78.52, 17.44], bend=-0.004, num_pts=12)},
        ],
        "rail": [
            # Secunderabad – Hyderabad Deccan (Nampally) – Lingampalli
            {"g": make_curve([78.50, 17.43], [78.32, 17.49], bend=0.008, num_pts=20)},
            # Kazipet – Secunderabad Trunk
            {"g": make_curve([78.58, 17.45], [78.50, 17.43], bend=0.004, num_pts=12)},
        ]
    },
    "pune": {
        "cx": 73.85, "cy": 18.53,
        "water": [
            # Mula River
            {"n": "Mula River", "t": "river", "g": make_curve([73.74, 18.58], [73.87, 18.53], bend=0.011, num_pts=22)},
            # Mutha River
            {"n": "Mutha River", "t": "river", "g": make_curve([73.79, 18.48], [73.86, 18.53], bend=0.008, num_pts=18)},
            # Mula-Mutha Confluence River East
            {"n": "Mula-Mutha River", "t": "river", "g": make_curve([73.87, 18.53], [73.98, 18.54], bend=0.007, num_pts=16)},
            # Pashan Lake
            {"n": "Pashan Lake", "t": "lake", "g": make_ring(73.79, 18.54, 0.007, 0.006, num_pts=14)},
            # Khadakwasla Reservoir
            {"n": "Khadakwasla Lake", "t": "lake", "g": make_ring(73.76, 18.43, 0.02, 0.01, num_pts=16)},
        ],
        "roads": [
            # Katraj-Dehu Road Bypass (NH 48 Western Bypass)
            {"c": 3, "g": make_curve([73.74, 18.66], [73.86, 18.45], bend=-0.015, num_pts=24)},
            # Old Pune-Mumbai Highway
            {"c": 3, "g": make_curve([73.78, 18.65], [73.85, 18.53], bend=0.008, num_pts=18)},
            # Ahmednagar Road
            {"c": 3, "g": make_radial(73.87, 18.54, 45, 0.14, num_pts=14)},
            # Solapur Road (NH 65)
            {"c": 3, "g": make_radial(73.88, 18.50, -35, 0.14, num_pts=14)},
            # Senapati Bapat Road / Ganeshkhind Road
            {"c": 2, "g": make_curve([73.83, 18.52], [73.85, 18.54], bend=0.004, num_pts=10)},
            # Karve Road / Paud Road
            {"c": 2, "g": make_radial(73.84, 18.51, -145, 0.12, num_pts=12)},
        ],
        "rail": [
            # Pune Junction – Shivajinagar – Pimpri – Lonavala (Central Railway)
            {"g": make_curve([73.87, 18.525], [73.78, 18.64], bend=0.007, num_pts=20)},
            # Pune Junction – Daund Trunk East
            {"g": make_curve([73.87, 18.525], [73.96, 18.51], bend=-0.005, num_pts=14)},
        ]
    },
    "ahmedabad": {
        "cx": 72.58, "cy": 23.03,
        "water": [
            # Majestic Sabarmati River through heart of Ahmedabad & Gandhinagar
            {"n": "Sabarmati Riverfront", "t": "river", "g": make_curve([72.66, 23.25], [72.56, 22.95], bend=0.015, num_pts=35)},
            # Kankaria Lake Historic Centerpiece
            {"n": "Kankaria Lake", "t": "lake", "g": make_ring(72.60, 23.006, 0.007, 0.007, num_pts=16)},
            # Chandola Lake
            {"n": "Chandola Lake", "t": "lake", "g": make_ring(72.59, 22.98, 0.01, 0.007, num_pts=14)},
            # Narmada Main Canal
            {"n": "Narmada Canal", "t": "canal", "g": make_curve([72.50, 23.16], [72.70, 23.18], bend=0.005, num_pts=16)},
        ],
        "roads": [
            # Sardar Patel Ring Road (SP Ring Road)
            {"c": 3, "g": make_ring(72.58, 23.05, 0.11, 0.10, num_pts=32, irregular=0.007)},
            # 132 Feet Ring Road
            {"c": 2, "g": make_ring(72.56, 23.04, 0.06, 0.055, num_pts=24, irregular=0.005)},
            # Sarkhej-Gandhinagar (SG) Highway
            {"c": 3, "g": make_curve([72.50, 22.98], [72.60, 23.17], bend=-0.008, num_pts=20)},
            # Ashram Road River Corridor
            {"c": 2, "g": make_curve([72.565, 23.00], [72.58, 23.08], bend=0.005, num_pts=14)},
            # Airport Road
            {"c": 2, "g": make_curve([72.60, 23.06], [72.63, 23.08], bend=0.004, num_pts=10)},
        ],
        "rail": [
            # Ahmedabad Kalupur Junction – Sabarmati – Mehsana Trunk
            {"g": make_curve([72.60, 23.025], [72.58, 23.12], bend=-0.006, num_pts=18)},
            # Kalupur to Vadodara / Mumbai Trunk South
            {"g": make_curve([72.60, 23.025], [72.62, 22.94], bend=0.005, num_pts=16)},
        ]
    },
    "kochi": {
        "cx": 76.30, "cy": 10.00,
        "water": [
            # Arabian Sea Coastline
            {"n": "Arabian Sea Coast", "t": "coastline", "g": make_curve([76.24, 9.90], [76.21, 10.15], bend=0.01, num_pts=25)},
            # Vembanad Lake & Kochi Backwaters
            {"n": "Vembanad Lake Backwaters", "t": "lake", "g": make_curve([76.26, 9.92], [76.32, 10.05], bend=0.016, num_pts=22)},
            # Periyar River North
            {"n": "Periyar River", "t": "river", "g": make_curve([76.32, 10.11], [76.37, 10.12], bend=0.008, num_pts=16)},
            # Willingdon Island Channel
            {"n": "Willingdon Harbour Channel", "t": "bay", "g": make_curve([76.26, 9.95], [76.28, 9.97], bend=0.005, num_pts=10)},
        ],
        "roads": [
            # Kochi Bypass (NH 66)
            {"c": 3, "g": make_curve([76.31, 9.95], [76.31, 10.05], bend=0.006, num_pts=16)},
            # MG Road Ernakulam
            {"c": 2, "g": make_curve([76.28, 9.96], [76.28, 9.99], bend=0.003, num_pts=10)},
            # Seaport-Airport Road
            {"c": 3, "g": make_curve([76.35, 9.98], [76.35, 10.10], bend=-0.005, num_pts=15)},
            # SA Road
            {"c": 2, "g": make_curve([76.29, 9.96], [76.32, 9.97], bend=0.004, num_pts=10)},
        ],
        "rail": [
            # Ernakulam Junction (South) to Aluva (Southern Railway)
            {"g": make_curve([76.29, 9.965], [76.35, 10.11], bend=0.008, num_pts=20)},
        ]
    },
    "lucknow": {
        "cx": 80.93, "cy": 26.85,
        "water": [
            # Gomti River Meandering through City
            {"n": "Gomti River", "t": "river", "g": make_curve([80.86, 26.89], [81.01, 26.82], bend=0.016, num_pts=30)},
            # Kukrail River
            {"n": "Kukrail River", "t": "stream", "g": make_curve([80.98, 26.92], [80.96, 26.86], bend=0.006, num_pts=12)},
        ],
        "roads": [
            # Amar Shaheed Path Expressway
            {"c": 3, "g": make_curve([80.91, 26.78], [81.02, 26.87], bend=0.012, num_pts=18)},
            # Kanpur Road (NH 27)
            {"c": 3, "g": make_radial(80.90, 26.82, -125, 0.14, num_pts=14)},
            # Faizabad Road (Ayodhya Highway)
            {"c": 3, "g": make_radial(80.97, 26.87, 40, 0.14, num_pts=14)},
            # Mahatma Gandhi Marg
            {"c": 2, "g": make_curve([80.93, 26.84], [80.96, 26.85], bend=0.004, num_pts=10)},
            # Ring Road North
            {"c": 2, "g": make_curve([80.90, 26.89], [80.98, 26.90], bend=0.006, num_pts=14)},
        ],
        "rail": [
            # Charbagh Railway Terminal – Kanpur Trunk & Delhi Trunk
            {"g": make_curve([80.92, 26.83], [80.86, 26.80], bend=-0.006, num_pts=15)},
            {"g": make_curve([80.92, 26.83], [80.99, 26.87], bend=0.005, num_pts=14)},
        ]
    },
    "kanpur": {
        "cx": 80.32, "cy": 26.46,
        "water": [
            # Holy River Ganga along Kanpur's Northern Edge
            {"n": "Ganga River", "t": "river", "g": make_curve([80.25, 26.52], [80.40, 26.44], bend=0.014, num_pts=25)},
            # Lower Ganga Canal
            {"n": "Ganga Canal", "t": "canal", "g": make_curve([80.26, 26.47], [80.34, 26.41], bend=0.006, num_pts=15)},
        ],
        "roads": [
            # Grand Trunk Road (GT Road / NH 19)
            {"c": 3, "g": make_curve([80.24, 26.49], [80.38, 26.44], bend=0.007, num_pts=18)},
            # Kanpur Ring Road / Bypass
            {"c": 3, "g": make_curve([80.26, 26.42], [80.37, 26.40], bend=-0.006, num_pts=16)},
            # Mall Road Kanpur
            {"c": 2, "g": make_curve([80.33, 26.47], [80.36, 26.46], bend=0.003, num_pts=10)},
            # Kalpi Road
            {"c": 2, "g": make_radial(80.31, 26.46, -140, 0.12, num_pts=12)},
        ],
        "rail": [
            # North Central Railway Delhi – Kanpur Central – Howrah Mainline
            {"g": make_curve([80.25, 26.47], [80.39, 26.44], bend=-0.005, num_pts=18)},
        ]
    },
    "agra": {
        "cx": 78.01, "cy": 27.18,
        "water": [
            # River Yamuna curving past Agra Fort and Taj Mahal
            {"n": "Yamuna River", "t": "river", "g": make_curve([77.96, 27.23], [78.07, 27.16], bend=0.015, num_pts=25)},
        ],
        "roads": [
            # NH 19 (Delhi-Agra-Kolkata Highway)
            {"c": 3, "g": make_curve([77.94, 27.23], [78.06, 27.19], bend=0.008, num_pts=16)},
            # Fatehabad Road (Taj Tourism Corridor)
            {"c": 2, "g": make_radial(78.02, 27.16, -45, 0.10, num_pts=12)},
            # MG Road Agra
            {"c": 2, "g": make_curve([77.99, 27.20], [78.01, 27.16], bend=-0.005, num_pts=12)},
            # Ring Road Agra
            {"c": 3, "g": make_curve([77.98, 27.14], [78.07, 27.18], bend=0.01, num_pts=16)},
        ],
        "rail": [
            # Delhi – Agra Cantt – Mumbai/Chennai Mainline
            {"g": make_curve([77.99, 27.22], [78.01, 27.14], bend=0.005, num_pts=16)},
        ]
    },
    "jaipur": {
        "cx": 75.80, "cy": 26.90,
        "water": [
            # Man Sagar Lake (Jal Mahal)
            {"n": "Man Sagar Lake", "t": "lake", "g": make_ring(75.84, 26.955, 0.009, 0.007, num_pts=16)},
            # Dravyavati River (Amanishah Nullah)
            {"n": "Dravyavati River", "t": "river", "g": make_curve([75.76, 26.96], [75.84, 26.82], bend=-0.012, num_pts=22)},
        ],
        "roads": [
            # Tonk Road
            {"c": 3, "g": make_radial(75.81, 26.89, -85, 0.14, num_pts=15)},
            # Ajmer Road (NH 48)
            {"c": 3, "g": make_radial(75.77, 26.89, -155, 0.14, num_pts=15)},
            # JLN Marg (Jawahar Lal Nehru Marg)
            {"c": 2, "g": make_radial(75.82, 26.89, -70, 0.12, num_pts=12)},
            # Jaipur Ring Road
            {"c": 3, "g": make_curve([75.70, 26.84], [75.88, 26.82], bend=0.01, num_pts=18)},
            # MI Road (Mirza Ismail Road)
            {"c": 2, "g": make_curve([75.79, 26.92], [75.83, 26.92], bend=0.003, num_pts=10)},
        ],
        "rail": [
            # Jaipur Junction Main Railway Lines
            {"g": make_curve([75.75, 26.92], [75.82, 26.85], bend=0.006, num_pts=16)},
        ]
    },
    "nagpur": {
        "cx": 79.08, "cy": 21.14,
        "water": [
            # Ambazari Lake
            {"n": "Ambazari Lake", "t": "lake", "g": make_ring(79.04, 21.13, 0.012, 0.008, num_pts=16)},
            # Futala Lake
            {"n": "Futala Lake", "t": "lake", "g": make_ring(79.045, 21.155, 0.008, 0.006, num_pts=14)},
            # Gorewada Lake
            {"n": "Gorewada Lake", "t": "lake", "g": make_ring(79.03, 21.19, 0.014, 0.01, num_pts=16)},
            # Nag River
            {"n": "Nag River", "t": "river", "g": make_curve([79.04, 21.13], [79.14, 21.14], bend=0.006, num_pts=16)},
        ],
        "roads": [
            # Nagpur Outer Ring Road
            {"c": 3, "g": make_ring(79.08, 21.14, 0.11, 0.09, num_pts=30, irregular=0.006)},
            # Wardha Road (NH 44 to Airport & MIHAN)
            {"c": 3, "g": make_radial(79.07, 21.13, -115, 0.14, num_pts=15)},
            # Amravati Road (NH 53 West)
            {"c": 3, "g": make_radial(79.05, 21.15, 165, 0.14, num_pts=14)},
            # Central Avenue Nagpur
            {"c": 2, "g": make_curve([79.08, 21.15], [79.15, 21.14], bend=0.004, num_pts=12)},
        ],
        "rail": [
            # Central Railway Delhi-Chennai & Mumbai-Howrah Grand Trunk Cross
            {"g": make_curve([79.08, 21.22], [79.08, 21.05], bend=0.005, num_pts=20)},
            {"g": make_curve([79.00, 21.14], [79.16, 21.14], bend=-0.004, num_pts=18)},
        ]
    },
    "noida": {
        "cx": 77.40, "cy": 28.52,
        "water": [
            # Yamuna River along West
            {"n": "Yamuna River", "t": "river", "g": make_curve([77.32, 28.60], [77.36, 28.45], bend=0.009, num_pts=20)},
            # Hindon River dividing Noida and Greater Noida
            {"n": "Hindon River", "t": "river", "g": make_curve([77.42, 28.62], [77.48, 28.44], bend=0.012, num_pts=22)},
        ],
        "roads": [
            # Noida-Greater Noida Expressway
            {"c": 3, "g": make_curve([77.34, 28.56], [77.50, 28.45], bend=-0.007, num_pts=18)},
            # Yamuna Expressway (To Agra)
            {"c": 3, "g": make_radial(77.51, 28.44, -135, 0.14, num_pts=14)},
            # DND Flyway
            {"c": 3, "g": make_curve([77.29, 28.57], [77.33, 28.58], bend=0.004, num_pts=10)},
            # Master Plan Road 1 & 2
            {"c": 2, "g": make_curve([77.33, 28.58], [77.40, 28.59], bend=0.003, num_pts=12)},
            {"c": 2, "g": make_curve([77.35, 28.54], [77.42, 28.57], bend=0.004, num_pts=12)},
        ],
        "rail": [
            # Delhi – Ghaziabad – Aligarh Main Railway line to the north
            {"g": make_curve([77.35, 28.64], [77.48, 28.60], bend=-0.005, num_pts=15)},
        ]
    },
    "navi-mumbai": {
        "cx": 73.06, "cy": 19.04,
        "water": [
            # Thane Creek Harbour West
            {"n": "Thane Creek Coastline", "t": "bay", "g": make_curve([72.98, 19.12], [73.00, 18.98], bend=0.01, num_pts=20)},
            # Panvel Creek
            {"n": "Panvel Creek", "t": "river", "g": make_curve([73.02, 18.99], [73.12, 19.01], bend=0.008, num_pts=16)},
            # Kasadi River Taloja
            {"n": "Kasadi River", "t": "stream", "g": make_curve([73.08, 19.08], [73.05, 19.02], bend=0.006, num_pts=14)},
        ],
        "roads": [
            # Sion-Panvel Highway
            {"c": 3, "g": make_curve([72.98, 19.06], [73.12, 19.00], bend=0.008, num_pts=18)},
            # Palm Beach Road
            {"c": 3, "g": make_curve([73.00, 19.08], [73.03, 19.01], bend=-0.006, num_pts=14)},
            # Thane-Belapur Road
            {"c": 3, "g": make_curve([73.00, 19.16], [73.02, 19.07], bend=0.005, num_pts=14)},
            # Amra Marg (To JNPT & New Airport)
            {"c": 3, "g": make_curve([73.03, 19.00], [73.05, 18.96], bend=0.004, num_pts=12)},
        ],
        "rail": [
            # Central Railway Harbour Line (Vashi – Belapur – Panvel)
            {"g": make_curve([72.98, 19.07], [73.11, 18.99], bend=0.007, num_pts=18)},
        ]
    },
    "bhopal-indore": {
        "cx": 75.86, "cy": 22.72,
        "water": [
            # Bhopal Upper Lake (Bhojtal)
            {"n": "Upper Lake (Bhojtal) Bhopal", "t": "lake", "g": make_ring(77.35, 23.24, 0.035, 0.018, num_pts=24, irregular=0.005)},
            # Bhopal Lower Lake
            {"n": "Lower Lake Bhopal", "t": "lake", "g": make_ring(77.40, 23.25, 0.01, 0.006, num_pts=14)},
            # Indore Kahn River
            {"n": "Kahn River Indore", "t": "river", "g": make_curve([75.84, 22.68], [75.88, 22.78], bend=0.008, num_pts=16)},
            # Bilawali Lake Indore
            {"n": "Bilawali Lake Indore", "t": "lake", "g": make_ring(75.88, 22.68, 0.012, 0.008, num_pts=15)},
        ],
        "roads": [
            # Indore Ring Road (AB Road)
            {"c": 3, "g": make_ring(75.86, 22.72, 0.075, 0.065, num_pts=28, irregular=0.005)},
            # Indore Super Corridor (To Airport)
            {"c": 3, "g": make_curve([75.80, 22.73], [75.82, 22.80], bend=-0.005, num_pts=14)},
            # Bhopal Hoshangabad Road (NH 46)
            {"c": 3, "g": make_curve([77.44, 23.23], [77.47, 23.15], bend=0.006, num_pts=14)},
            # Bhopal VIP Road & Airport Road
            {"c": 2, "g": make_curve([77.38, 23.25], [77.35, 23.29], bend=0.005, num_pts=12)},
        ],
        "rail": [
            # Bhopal Railway Junction Mainline
            {"g": make_curve([77.41, 23.22], [77.41, 23.32], bend=0.004, num_pts=16)},
            # Indore Junction – Ujjain Line
            {"g": make_curve([75.86, 22.71], [75.86, 22.80], bend=-0.004, num_pts=14)},
        ]
    }
}

count_updated = 0
for city_id, geom in CITY_GEOMETRIES.items():
    if city_id in city_data:
        # Erase artificial trapezoid bd box so whole canvas is seamless
        city_data[city_id]["base"]["bd"] = []
        city_data[city_id]["base"]["water"] = geom["water"]
        city_data[city_id]["base"]["roads"] = geom["roads"]
        city_data[city_id]["base"]["rail"] = geom["rail"]
        count_updated += 1
        print(f"Enriched {city_id} with {len(geom['water'])} water bodies, {len(geom['roads'])} roads, {len(geom['rail'])} rail lines")

new_json_str = json.dumps(city_data, indent=2)
new_content = content[:m.start(1)] + new_json_str + ";" + content[m.end():]

with open('frontend/src/data/metro/all_city_packs.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully enriched {count_updated} cities in all_city_packs.js!")
