import { useEffect, useMemo, useRef, useState } from 'react';
import metroData from '../data/metro-networks.json';
import './MetroAtlas.css';

// 17 Indian Metro Cities: High-Resolution Spacious Transit Networks (metrosafar.com/maps)
export const CITY_LAYOUTS = {
  'delhi-ncr': {
    width: 1400,
    height: 1100,
    waterways: [
      {
        id: 'yamuna',
        name: 'River Yamuna (यमुना नदी)',
        path: 'M 880,20 Q 850,180 810,330 T 780,480 T 820,620 T 890,780 T 980,950 T 1060,1100',
        stroke: '#0284c7',
        width: 32,
        opacity: 0.55,
      },
      {
        id: 'najafgarh',
        name: 'Najafgarh Drain',
        path: 'M 100,820 Q 260,700 380,580 T 640,410 T 810,330',
        stroke: '#0369a1',
        width: 8,
        opacity: 0.4,
      },
    ],
    roads: [
      { id: 'ring-road', name: 'Ring Road (Mahatma Gandhi Marg)', path: 'M 540,420 C 760,400 840,490 810,690 C 770,860 480,850 420,660 Z', stroke: 'rgba(255,255,255,0.12)', width: 5 },
      { id: 'outer-ring', name: 'Outer Ring Road', path: 'M 420,280 C 920,240 1020,440 980,800 C 900,1020 360,1000 260,640 Z', stroke: 'rgba(255,255,255,0.08)', width: 4, dash: '6,6' },
      { id: 'border-up', name: 'Delhi - Uttar Pradesh Border', path: 'M 1000,140 L 960,440 L 910,720 L 1100,1000', stroke: '#f59e0b', width: 2, dash: '8,6', opacity: 0.4 },
      { id: 'border-haryana', name: 'Delhi - Haryana Border', path: 'M 180,240 L 160,520 L 300,980 L 540,1100', stroke: '#f59e0b', width: 2, dash: '8,6', opacity: 0.4 },
    ],
    geoLines: [
      { id: 'red', name: 'Red Line (Line 1)', color: '#dc2626', path: 'M 260,290 L 460,290 Q 600,310 740,330 L 940,330 L 1220,270', status: 'Operational' },
      { id: 'yellow', name: 'Yellow Line (Line 2)', color: '#eab308', path: 'M 680,100 L 680,230 L 740,330 L 680,430 L 680,520 L 680,610 L 640,710 L 600,800 Q 550,900 500,960 L 420,1030', status: 'Operational' },
      { id: 'blue', name: 'Blue Line (Line 3 & 4)', color: '#2563eb', path: 'M 180,840 Q 280,740 360,650 L 680,520 L 820,520 L 960,610 L 1100,650 L 1280,650', status: 'Operational' },
      { id: 'blue-branch', name: 'Blue Line Vaishali Branch', color: '#2563eb', path: 'M 820,520 L 940,490 L 1060,480 L 1160,440', status: 'Operational' },
      { id: 'violet', name: 'Violet Line (Line 6)', color: '#7c3aed', path: 'M 740,330 L 820,520 L 680,610 L 780,720 L 860,800 L 880,950', status: 'Operational' },
      { id: 'pink', name: 'Pink Line (Ring Line 7)', color: '#ec4899', path: 'M 680,230 Q 820,220 940,330 L 1060,480 L 960,610 Q 880,700 860,680 L 780,720 L 640,710 Q 480,700 460,650 L 360,650 Q 300,520 460,290 L 680,230 Z', status: 'Operational Ring' },
      { id: 'magenta', name: 'Magenta Line (Line 8)', color: '#d946ef', path: 'M 360,650 Q 460,760 600,800 L 860,800 Q 980,740 1100,650', status: 'Operational' },
      { id: 'orange', name: 'Airport Express (Orange)', color: '#ea580c', path: 'M 680,430 L 560,540 L 420,680 L 320,800 L 180,840', status: 'Operational' },
      { id: 'rapid', name: 'Rapid Metro Gurugram', color: '#64748b', path: 'M 500,960 L 560,940 L 580,1020 L 520,1040 L 500,960', status: 'Operational Loop' },
      { id: 'aqua', name: 'Noida Aqua Line', color: '#06b6d4', path: 'M 1100,650 L 1140,760 L 1200,880 L 1280,1020', status: 'Operational' },
      { id: 'silver-p4', name: 'Phase 4 Golden/Silver Alignment', color: '#d97706', path: 'M 320,800 L 460,850 L 620,890 L 860,950', status: 'Under Construction (Phase 4)', dash: '6,6' },
      { id: 'rrts', name: 'Namo Bharat Regional Rapid Transit', color: '#991b1b', path: 'M 860,680 L 1060,480 L 1220,200 L 1340,60', status: 'Semi-High Speed RRTS (160 km/h)' },
    ],
    stations: [
      { name: 'Kashmere Gate', hindi: 'कश्मीरी गेट', x: 740, y: 330, lines: ['Red Line (Line 1)', 'Yellow Line (Line 2)', 'Violet Line (Line 6)'], interchange: true, footfall: '350,000', lat: 28.6675, lng: 77.2285, anchor: 'start', dx: 18, dy: -6, connections: ['Rithala', 'Netaji Subhash Place', 'Welcome', 'Samaypur Badli', 'Azadpur', 'New Delhi Railway Station', 'Mandi House', 'Central Secretariat'] },
      { name: 'New Delhi Railway Station', hindi: 'नई दिल्ली', x: 680, y: 430, lines: ['Yellow Line (Line 2)', 'Airport Express (Orange)'], interchange: true, footfall: '290,000', lat: 28.6431, lng: 77.2223, anchor: 'end', dx: -18, dy: 4, connections: ['Kashmere Gate', 'Rajiv Chowk (CP)', 'IGI Airport T3'] },
      { name: 'Rajiv Chowk (CP)', hindi: 'राजीव चौक', x: 680, y: 520, lines: ['Yellow Line (Line 2)', 'Blue Line (Line 3 & 4)'], interchange: true, footfall: '500,000', lat: 28.6328, lng: 77.2195, anchor: 'end', dx: -18, dy: 4, connections: ['New Delhi Railway Station', 'Central Secretariat', 'Janakpuri West', 'Mandi House'] },
      { name: 'Mandi House', hindi: 'मंडी हाउस', x: 820, y: 520, lines: ['Blue Line (Line 3 & 4)', 'Violet Line (Line 6)'], interchange: true, footfall: '170,000', lat: 28.6258, lng: 77.2343, anchor: 'start', dx: 18, dy: 4, connections: ['Rajiv Chowk (CP)', 'Central Secretariat', 'Kashmere Gate', 'Mayur Vihar Phase 1', 'Anand Vihar ISBT'] },
      { name: 'Central Secretariat', hindi: 'केंद्रीय सचिवालय', x: 680, y: 610, lines: ['Yellow Line (Line 2)', 'Violet Line (Line 6)'], interchange: true, footfall: '210,000', lat: 28.6146, lng: 77.2119, anchor: 'end', dx: -18, dy: 4, connections: ['Rajiv Chowk (CP)', 'Dilli Haat INA', 'Mandi House', 'Lajpat Nagar'] },
      { name: 'Dilli Haat INA', hindi: 'दिल्ली हाट आईएनए', x: 640, y: 710, lines: ['Yellow Line (Line 2)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '160,000', lat: 28.5744, lng: 77.2096, anchor: 'end', dx: -18, dy: 4, connections: ['Central Secretariat', 'Hauz Khas', 'Lajpat Nagar', 'Netaji Subhash Place'] },
      { name: 'Lajpat Nagar', hindi: 'लाजपत नगर', x: 780, y: 720, lines: ['Violet Line (Line 6)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '190,000', lat: 28.5708, lng: 77.2378, anchor: 'start', dx: 18, dy: 4, connections: ['Central Secretariat', 'Kalkaji Mandir', 'Dilli Haat INA', 'Sarai Kale Khan'] },
      { name: 'Hauz Khas', hindi: 'हौज़ खास', x: 600, y: 800, lines: ['Yellow Line (Line 2)', 'Magenta Line (Line 8)'], interchange: true, footfall: '280,000', lat: 28.5432, lng: 77.2066, anchor: 'end', dx: -18, dy: 4, connections: ['Dilli Haat INA', 'Sikanderpur', 'Janakpuri West', 'Kalkaji Mandir'] },
      { name: 'Kalkaji Mandir', hindi: 'कालकाजी मंदिर', x: 860, y: 800, lines: ['Violet Line (Line 6)', 'Magenta Line (Line 8)'], interchange: true, footfall: '185,000', lat: 28.5492, lng: 77.2581, anchor: 'start', dx: 18, dy: 4, connections: ['Lajpat Nagar', 'Hauz Khas', 'Botanical Garden'] },
      { name: 'Botanical Garden', hindi: 'बॉटनिकल गार्डन', x: 1100, y: 650, lines: ['Blue Line (Line 3 & 4)', 'Magenta Line (Line 8)'], interchange: true, footfall: '220,000', lat: 28.5642, lng: 77.3342, anchor: 'start', dx: 18, dy: 4, connections: ['Mayur Vihar Phase 1', 'Noida Electronic City', 'Kalkaji Mandir', 'Depot Greater Noida'] },
      { name: 'Mayur Vihar Phase 1', hindi: 'मयूर विहार फेस 1', x: 960, y: 610, lines: ['Blue Line (Line 3 & 4)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '145,000', lat: 28.6045, lng: 77.2945, anchor: 'start', dx: 18, dy: 4, connections: ['Mandi House', 'Botanical Garden', 'Anand Vihar ISBT', 'Sarai Kale Khan'] },
      { name: 'Sarai Kale Khan', hindi: 'सराय काले खां', x: 860, y: 680, lines: ['Pink Line (Ring Line 7)', 'Namo Bharat RRTS'], interchange: true, footfall: '180,000', lat: 28.5908, lng: 77.2569, anchor: 'start', dx: 18, dy: 14, connections: ['Mayur Vihar Phase 1', 'Lajpat Nagar', 'Anand Vihar ISBT'] },
      { name: 'Anand Vihar ISBT', hindi: 'आनंद विहार', x: 1060, y: 480, lines: ['Blue Line (Line 3 & 4)', 'Pink Line (Ring Line 7)', 'Namo Bharat RRTS'], interchange: true, footfall: '260,000', lat: 28.6469, lng: 77.3161, anchor: 'start', dx: 18, dy: 4, connections: ['Mandi House', 'Vaishali', 'Mayur Vihar Phase 1', 'Welcome', 'Sarai Kale Khan', 'Ghaziabad RRTS'] },
      { name: 'Netaji Subhash Place', hindi: 'नेताजी सुभाष प्लेस', x: 460, y: 290, lines: ['Red Line (Line 1)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '175,000', lat: 28.6953, lng: 77.1528, anchor: 'end', dx: -18, dy: 4, connections: ['Rithala', 'Kashmere Gate', 'Azadpur', 'Dilli Haat INA'] },
      { name: 'Azadpur', hindi: 'आज़ादपुर', x: 680, y: 230, lines: ['Yellow Line (Line 2)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '155,000', lat: 28.7067, lng: 77.1783, anchor: 'start', dx: 18, dy: 4, connections: ['Samaypur Badli', 'Kashmere Gate', 'Netaji Subhash Place', 'Welcome'] },
      { name: 'Welcome', hindi: 'वेलकम', x: 940, y: 330, lines: ['Red Line (Line 1)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '160,000', lat: 28.6722, lng: 77.2778, anchor: 'start', dx: 18, dy: 4, connections: ['Kashmere Gate', 'Shaheed Sthal (Ghaziabad)', 'Azadpur', 'Anand Vihar ISBT'] },
      { name: 'Janakpuri West', hindi: 'जनकपुरी पश्चिम', x: 360, y: 650, lines: ['Blue Line (Line 3 & 4)', 'Magenta Line (Line 8)'], interchange: true, footfall: '150,000', lat: 28.6294, lng: 77.0778, anchor: 'end', dx: -18, dy: 4, connections: ['Dwarka Sector 21', 'Rajiv Chowk (CP)', 'Hauz Khas'] },
      { name: 'Dwarka Sector 21', hindi: 'द्वारका सेक्टर 21', x: 180, y: 840, lines: ['Blue Line (Line 3 & 4)', 'Airport Express (Orange)'], interchange: true, footfall: '125,000', lat: 28.5522, lng: 77.0583, anchor: 'end', dx: -18, dy: 4, connections: ['Janakpuri West', 'IGI Airport T3'] },
      { name: 'IGI Airport T3', hindi: 'आईजीआई एयरपोर्ट टी3', x: 320, y: 800, lines: ['Airport Express (Orange)'], interchange: false, footfall: '75,000', lat: 28.5562, lng: 77.0863, anchor: 'middle', dx: 0, dy: 22, connections: ['New Delhi Railway Station', 'Dwarka Sector 21'] },
      { name: 'Sikanderpur', hindi: 'सिकंदरपुर', x: 500, y: 960, lines: ['Yellow Line (Line 2)', 'Rapid Metro Gurugram'], interchange: true, footfall: '130,000', lat: 28.4819, lng: 77.0928, anchor: 'end', dx: -18, dy: 4, connections: ['Hauz Khas', 'Millennium City Centre Gurugram', 'Cyber City Gurugram'] },
      { name: 'Millennium City Centre Gurugram', hindi: 'मिलेनियम सिटी सेंटर', x: 420, y: 1030, lines: ['Yellow Line (Line 2)'], interchange: false, footfall: '140,000', lat: 28.4593, lng: 77.0725, anchor: 'end', dx: -18, dy: 4, connections: ['Sikanderpur'] },
      { name: 'Rithala', hindi: 'रिठाला', x: 260, y: 290, lines: ['Red Line (Line 1)'], interchange: false, footfall: '90,000', lat: 28.7206, lng: 77.1072, anchor: 'end', dx: -18, dy: 4, connections: ['Netaji Subhash Place'] },
      { name: 'Shaheed Sthal (Ghaziabad)', hindi: 'शहीद स्थल गाज़ियाबाद', x: 1220, y: 270, lines: ['Red Line (Line 1)'], interchange: false, footfall: '105,000', lat: 28.6719, lng: 77.4189, anchor: 'start', dx: 18, dy: 4, connections: ['Welcome'] },
      { name: 'Samaypur Badli', hindi: 'समयपुर बादली', x: 680, y: 100, lines: ['Yellow Line (Line 2)'], interchange: false, footfall: '85,000', lat: 28.7456, lng: 77.1358, anchor: 'start', dx: 18, dy: 4, connections: ['Azadpur'] },
      { name: 'Noida Electronic City', hindi: 'नोएडा इलेक्ट्रॉनिक सिटी', x: 1280, y: 650, lines: ['Blue Line (Line 3 & 4)'], interchange: false, footfall: '110,000', lat: 28.6272, lng: 77.3725, anchor: 'start', dx: 18, dy: 4, connections: ['Botanical Garden'] },
      { name: 'Vaishali', hindi: 'वैशाली', x: 1160, y: 440, lines: ['Blue Line (Line 3 & 4)'], interchange: false, footfall: '80,000', lat: 28.6497, lng: 77.3397, anchor: 'start', dx: 18, dy: 4, connections: ['Anand Vihar ISBT'] },
      { name: 'Cyber City Gurugram', hindi: 'साइबर सिटी', x: 580, y: 1020, lines: ['Rapid Metro Gurugram'], interchange: false, footfall: '95,000', lat: 28.4958, lng: 77.0886, anchor: 'start', dx: 18, dy: 4, connections: ['Sikanderpur'] },
      { name: 'Depot Greater Noida', hindi: 'डिपो स्टेशन ग्रेटर नोएडा', x: 1280, y: 1020, lines: ['Noida Aqua Line'], interchange: false, footfall: '25,000', lat: 28.4358, lng: 77.5269, anchor: 'start', dx: 18, dy: 4, connections: ['Botanical Garden'] },
      { name: 'Ghaziabad RRTS', hindi: 'गाज़ियाबाद नमो भारत', x: 1220, y: 200, lines: ['Namo Bharat RRTS'], interchange: false, footfall: '65,000', lat: 28.6658, lng: 77.4372, anchor: 'start', dx: 18, dy: 4, connections: ['Anand Vihar ISBT'] },
    ],
  },
  'mumbai': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'arabian-sea', name: 'Arabian Sea Coast', path: 'M 160,30 Q 140,320 200,600 T 260,920', stroke: '#0284c7', width: 36, opacity: 0.5 },
      { id: 'thane-creek', name: 'Thane Creek Basin', path: 'M 1000,50 Q 940,300 880,550 T 780,880', stroke: '#0284c7', width: 28, opacity: 0.5 },
    ],
    roads: [
      { id: 'weh', name: 'Western Express Highway (WEH)', path: 'M 540,50 L 530,380 L 520,560 L 440,820', stroke: 'rgba(255,255,255,0.12)', width: 4 },
    ],
    geoLines: [
      { id: 'line1', name: 'Line 1 (Blue Corridor)', color: '#0284c7', path: 'M 240,380 L 530,380 L 880,380', status: 'Operational' },
      { id: 'line2a', name: 'Line 2A (Yellow Corridor)', color: '#facc15', path: 'M 420,80 L 330,220 L 240,380 L 260,480', status: 'Operational' },
      { id: 'line7', name: 'Line 7 (Red Corridor)', color: '#ef4444', path: 'M 550,80 L 538,220 L 530,380 L 520,480', status: 'Operational' },
      { id: 'line3', name: 'Line 3 (Aqua Underground)', color: '#06b6d4', path: 'M 550,260 L 520,380 L 530,540 L 480,720 L 400,880', status: 'Operational' },
    ],
    stations: [
      { name: 'Versova', hindi: 'वर्सोवा', x: 240, y: 380, lines: ['Line 1 (Blue Corridor)'], interchange: false, footfall: '65,000', lat: 19.1311, lng: 72.8197, anchor: 'end', dx: -18, dy: 4, connections: ['DN Nagar'] },
      { name: 'DN Nagar', hindi: 'डी एन नगर', x: 350, y: 380, lines: ['Line 1 (Blue Corridor)', 'Line 2A (Yellow Corridor)'], interchange: true, footfall: '140,000', lat: 19.1306, lng: 72.8319, anchor: 'middle', dx: 0, dy: -18, connections: ['Versova', 'Andheri / WEH', 'Dahisar West'] },
      { name: 'Andheri / WEH', hindi: 'अंधेरी वेस्टर्न एक्सप्रेस', x: 530, y: 380, lines: ['Line 1 (Blue Corridor)', 'Line 7 (Red Corridor)'], interchange: true, footfall: '240,000', lat: 19.1197, lng: 72.8464, anchor: 'start', dx: 18, dy: 4, connections: ['DN Nagar', 'Ghatkopar', 'Dahisar East', 'CSMIA Terminal 2'] },
      { name: 'Ghatkopar', hindi: 'घाटकोपर', x: 880, y: 380, lines: ['Line 1 (Blue Corridor)'], interchange: true, footfall: '185,000', lat: 19.0864, lng: 72.9081, anchor: 'start', dx: 18, dy: 4, connections: ['Andheri / WEH'] },
      { name: 'Dahisar East', hindi: 'दहिसर पूर्व', x: 550, y: 80, lines: ['Line 7 (Red Corridor)'], interchange: false, footfall: '70,000', lat: 19.2567, lng: 72.8606, anchor: 'start', dx: 18, dy: 4, connections: ['Andheri / WEH'] },
      { name: 'Dahisar West', hindi: 'दहिसर पश्चिम', x: 420, y: 80, lines: ['Line 2A (Yellow Corridor)'], interchange: false, footfall: '65,000', lat: 19.2558, lng: 72.8533, anchor: 'end', dx: -18, dy: 4, connections: ['DN Nagar'] },
      { name: 'CSMIA Terminal 2', hindi: 'छत्रपति शिवाजी एयरपोर्ट', x: 550, y: 260, lines: ['Line 3 (Aqua Underground)'], interchange: true, footfall: '80,000', lat: 19.0974, lng: 72.8744, anchor: 'start', dx: 18, dy: 4, connections: ['Andheri / WEH', 'Bandra-Kurla Complex (BKC)'] },
      { name: 'Bandra-Kurla Complex (BKC)', hindi: 'बीकेसी', x: 530, y: 540, lines: ['Line 3 (Aqua Underground)'], interchange: true, footfall: '110,000', lat: 19.0667, lng: 72.8667, anchor: 'start', dx: 18, dy: 4, connections: ['CSMIA Terminal 2', 'Cuffe Parade'] },
      { name: 'Cuffe Parade', hindi: 'कफ परेड', x: 400, y: 880, lines: ['Line 3 (Aqua Underground)'], interchange: false, footfall: '45,000', lat: 18.9167, lng: 72.8167, anchor: 'end', dx: -18, dy: 4, connections: ['Bandra-Kurla Complex (BKC)'] },
    ],
  },
  'bengaluru': {
    width: 1200,
    height: 950,
    waterways: [],
    roads: [
      { id: 'orr-blr', name: 'Outer Ring Road (ORR)', path: 'M 220,460 C 260,780 940,780 1000,430 C 960,140 300,140 220,460 Z', stroke: 'rgba(255,255,255,0.08)', width: 4, dash: '6,6' },
    ],
    geoLines: [
      { id: 'purple', name: 'Purple Line (East-West)', color: '#9333ea', path: 'M 140,640 L 340,540 L 560,440 L 800,440 L 1100,340', status: 'Operational' },
      { id: 'green', name: 'Green Line (North-South)', color: '#15803d', path: 'M 400,120 L 480,270 L 560,440 L 600,630 L 640,840', status: 'Operational' },
      { id: 'yellow', name: 'Yellow Line (Electronic City)', color: '#eab308', path: 'M 560,630 L 700,680 L 860,770 L 1040,850', status: 'Operational' },
    ],
    stations: [
      { name: 'Kempegowda Majestic', hindi: 'ಮೆಜೆಸ್ಟಿಕ್', x: 560, y: 440, lines: ['Purple Line (East-West)', 'Green Line (North-South)'], interchange: true, footfall: '240,000', lat: 12.9757, lng: 77.5728, anchor: 'end', dx: -18, dy: -12, connections: ['MG Road', 'Mysuru Road', 'Yeshwanthpur', 'Silk Board'] },
      { name: 'MG Road', hindi: 'ಎಂ ಜಿ ರಸ್ತೆ', x: 680, y: 440, lines: ['Purple Line (East-West)'], interchange: false, footfall: '95,000', lat: 12.9756, lng: 77.6066, anchor: 'middle', dx: 0, dy: -18, connections: ['Kempegowda Majestic', 'Indiranagar'] },
      { name: 'Indiranagar', hindi: 'ಇಂದಿರಾನಗರ', x: 820, y: 430, lines: ['Purple Line (East-West)'], interchange: false, footfall: '85,000', lat: 12.9783, lng: 77.6386, anchor: 'middle', dx: 0, dy: -18, connections: ['MG Road', 'Whitefield (Kadugodi)'] },
      { name: 'Whitefield (Kadugodi)', hindi: 'ವೈಟ್‌ಫೀಲ್ಡ್', x: 1100, y: 340, lines: ['Purple Line (East-West)'], interchange: false, footfall: '80,000', lat: 12.9961, lng: 77.7611, anchor: 'start', dx: 18, dy: 4, connections: ['Indiranagar'] },
      { name: 'Mysuru Road', hindi: 'ಮೈಸೂರು ರಸ್ತೆ', x: 340, y: 540, lines: ['Purple Line (East-West)'], interchange: false, footfall: '60,000', lat: 12.9469, lng: 77.5278, anchor: 'end', dx: -18, dy: 4, connections: ['Kempegowda Majestic'] },
      { name: 'Yeshwanthpur', hindi: 'ಯಶವಂತಪುರ', x: 480, y: 270, lines: ['Green Line (North-South)'], interchange: true, footfall: '90,000', lat: 13.0233, lng: 77.5500, anchor: 'end', dx: -18, dy: 4, connections: ['Kempegowda Majestic'] },
      { name: 'Silk Board', hindi: 'ಸಿಲ್ಕ್ ಬೋರ್ಡ್', x: 700, y: 680, lines: ['Yellow Line (Electronic City)'], interchange: true, footfall: '110,000', lat: 12.9172, lng: 77.6228, anchor: 'start', dx: 18, dy: 4, connections: ['Kempegowda Majestic', 'Electronic City'] },
      { name: 'Electronic City', hindi: 'ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಸಿಟಿ', x: 960, y: 820, lines: ['Yellow Line (Electronic City)'], interchange: false, footfall: '85,000', lat: 12.8452, lng: 77.6602, anchor: 'start', dx: 18, dy: 4, connections: ['Silk Board'] },
    ],
  },
  'kolkata': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'hooghly', name: 'River Hooghly (Deepest Under-River Tunnel 33m)', path: 'M 480,30 Q 500,260 520,480 T 470,920', stroke: '#0284c7', width: 36, opacity: 0.7 },
    ],
    roads: [],
    geoLines: [
      { id: 'blue', name: 'Blue Line (Line 1 Historic)', color: '#2563eb', path: 'M 620,80 L 620,310 L 620,480 L 660,670 L 720,880', status: 'Operational' },
      { id: 'green', name: 'Green Line (Line 2 Underwater)', color: '#16a34a', path: 'M 280,480 L 440,480 L 620,480 L 860,480 L 1060,430', status: 'Operational (Underwater)' },
      { id: 'orange', name: 'Orange Line (Line 6 Airport)', color: '#ea580c', path: 'M 720,880 L 920,770 L 980,580 L 1020,230', status: 'Operational / Ext.' },
    ],
    stations: [
      { name: 'Howrah Station (33m Deep Underwater)', hindi: 'হাওড়া স্টেশন', x: 440, y: 480, lines: ['Green Line (Line 2 Underwater)'], interchange: true, footfall: '220,000', lat: 22.5833, lng: 88.3425, anchor: 'end', dx: -18, dy: 4, connections: ['Esplanade'] },
      { name: 'Esplanade', hindi: 'এসপ্ল্যানেড', x: 620, y: 480, lines: ['Blue Line (Line 1 Historic)', 'Green Line (Line 2 Underwater)'], interchange: true, footfall: '260,000', lat: 22.5647, lng: 88.3516, anchor: 'end', dx: -18, dy: -14, connections: ['Howrah Station (33m Deep Underwater)', 'Sealdah', 'Dum Dum', 'Park Street'] },
      { name: 'Sealdah', hindi: 'শিয়ালদহ', x: 740, y: 480, lines: ['Green Line (Line 2 Underwater)'], interchange: true, footfall: '190,000', lat: 22.5683, lng: 88.3719, anchor: 'start', dx: 18, dy: 4, connections: ['Esplanade', 'Salt Lake Sector V'] },
      { name: 'Salt Lake Sector V', hindi: 'সল্টলেক সেক্টর ৫', x: 1060, y: 430, lines: ['Green Line (Line 2 Underwater)'], interchange: false, footfall: '110,000', lat: 22.5804, lng: 88.4372, anchor: 'start', dx: 18, dy: 4, connections: ['Sealdah'] },
      { name: 'Dum Dum', hindi: 'দমদম', x: 620, y: 210, lines: ['Blue Line (Line 1 Historic)'], interchange: true, footfall: '175,000', lat: 22.6219, lng: 88.3936, anchor: 'start', dx: 18, dy: 4, connections: ['Esplanade'] },
      { name: 'Park Street', hindi: 'পার্ক স্ট্রিট', x: 620, y: 570, lines: ['Blue Line (Line 1 Historic)'], interchange: false, footfall: '130,000', lat: 22.5511, lng: 88.3522, anchor: 'end', dx: -18, dy: 4, connections: ['Esplanade', 'Kavi Subhash'] },
      { name: 'Kavi Subhash', hindi: 'কবি সুভাষ', x: 720, y: 880, lines: ['Blue Line (Line 1 Historic)', 'Orange Line (Line 6 Airport)'], interchange: true, footfall: '140,000', lat: 22.4719, lng: 88.3967, anchor: 'start', dx: 18, dy: 4, connections: ['Park Street'] },
    ],
  },
  'chennai': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'bay-of-bengal', name: 'Bay of Bengal Coastline', path: 'M 980,50 Q 940,400 880,900', stroke: '#0284c7', width: 32, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'blue', name: 'Blue Line (Corridor 1)', color: '#1d4ed8', path: 'M 800,100 L 700,280 L 620,440 L 460,630 L 280,830', status: 'Operational' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#15803d', path: 'M 700,280 L 520,350 L 400,470 L 420,660', status: 'Operational' },
    ],
    stations: [
      { name: 'Chennai Central (MGR)', hindi: 'சென்னை சென்ट्रல்', x: 700, y: 280, lines: ['Blue Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '110,000', lat: 13.0827, lng: 80.2707, anchor: 'start', dx: 18, dy: 4, connections: ['Alandur', 'Koyambedu Wholesale Hub'] },
      { name: 'Alandur', hindi: 'ஆலந்தூர்', x: 420, y: 660, lines: ['Blue Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '65,000', lat: 13.0039, lng: 80.2014, anchor: 'end', dx: -18, dy: 4, connections: ['Chennai Central (MGR)', 'Chennai Airport', 'Koyambedu Wholesale Hub'] },
      { name: 'Chennai Airport', hindi: 'சென்னை விமான நிலையம்', x: 280, y: 830, lines: ['Blue Line (Corridor 1)'], interchange: false, footfall: '55,000', lat: 12.9806, lng: 80.1636, anchor: 'end', dx: -18, dy: 4, connections: ['Alandur'] },
      { name: 'Koyambedu Wholesale Hub', hindi: 'கோயம்பேடு', x: 400, y: 470, lines: ['Green Line (Corridor 2)'], interchange: true, footfall: '70,000', lat: 13.0733, lng: 80.1942, anchor: 'end', dx: -18, dy: 4, connections: ['Chennai Central (MGR)', 'Alandur'] },
    ],
  },
  'hyderabad': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'musi', name: 'River Musi', path: 'M 100,620 Q 500,610 1100,630', stroke: '#0284c7', width: 12, opacity: 0.4 },
    ],
    roads: [],
    geoLines: [
      { id: 'red', name: 'Red Line (Corridor 1)', color: '#dc2626', path: 'M 220,140 L 520,390 L 680,570 L 980,800', status: 'Operational' },
      { id: 'blue', name: 'Blue Line (Corridor 3)', color: '#2563eb', path: 'M 180,570 L 520,390 L 820,340 L 1060,410', status: 'Operational' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#16a34a', path: 'M 700,200 L 700,430 L 680,570', status: 'Operational' },
    ],
    stations: [
      { name: 'Ameerpet Hub', hindi: 'అమీర్‌పేట్', x: 520, y: 390, lines: ['Red Line (Corridor 1)', 'Blue Line (Corridor 3)'], interchange: true, footfall: '140,000', lat: 17.4375, lng: 78.4483, anchor: 'end', dx: -18, dy: -12, connections: ['Raidurg (HITEC City)', 'MGBS Central', 'Miyapur Depot', 'Secunderabad East'] },
      { name: 'Raidurg (HITEC City)', hindi: 'రాయదుర్గం', x: 180, y: 570, lines: ['Blue Line (Corridor 3)'], interchange: false, footfall: '95,000', lat: 17.4428, lng: 78.3772, anchor: 'end', dx: -18, dy: 4, connections: ['Ameerpet Hub'] },
      { name: 'MGBS Central', hindi: 'ఎంజీబీఎస్', x: 680, y: 570, lines: ['Red Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '85,000', lat: 17.3789, lng: 78.4811, anchor: 'start', dx: 18, dy: 14, connections: ['Ameerpet Hub', 'Secunderabad East', 'LB Nagar'] },
      { name: 'Secunderabad East', hindi: 'సికింద్రాబాద్ ఈస్ట్', x: 820, y: 340, lines: ['Blue Line (Corridor 3)', 'Green Line (Corridor 2)'], interchange: true, footfall: '90,000', lat: 17.4339, lng: 78.5042, anchor: 'start', dx: 18, dy: 4, connections: ['Ameerpet Hub', 'MGBS Central'] },
      { name: 'Miyapur Depot', hindi: 'మియాపూర్', x: 220, y: 140, lines: ['Red Line (Corridor 1)'], interchange: false, footfall: '55,000', lat: 17.4967, lng: 78.3614, anchor: 'end', dx: -18, dy: 4, connections: ['Ameerpet Hub'] },
      { name: 'LB Nagar', hindi: 'ఎల్బీ నగర్', x: 980, y: 800, lines: ['Red Line (Corridor 1)'], interchange: false, footfall: '65,000', lat: 17.3486, lng: 78.5519, anchor: 'start', dx: 18, dy: 4, connections: ['MGBS Central'] },
    ],
  },
  'kochi': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'vembanad', name: 'Vembanad Backwaters & Coast', path: 'M 420,70 Q 380,470 440,900', stroke: '#0284c7', width: 50, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'rail', name: 'Kochi Metro Rail (Aluva - Thripunithura)', color: '#0284c7', path: 'M 780,110 L 700,330 L 660,540 L 760,810', status: 'Operational' },
      { id: 'water-1', name: 'Water Metro (High Court - Vypin)', color: '#06b6d4', path: 'M 460,490 L 300,540', status: 'Electric Ferry Route', dash: '8,6' },
      { id: 'water-2', name: 'Water Metro (High Court - Fort Kochi)', color: '#06b6d4', path: 'M 460,490 L 240,700', status: 'Electric Ferry Route', dash: '8,6' },
    ],
    stations: [
      { name: 'High Court Water Terminal', hindi: 'ഹൈക്കോടതി', x: 460, y: 490, lines: ['Kochi Water Metro Hub'], interchange: true, footfall: '24,000', lat: 9.9814, lng: 76.2753, anchor: 'end', dx: -18, dy: 4, connections: ['MG Road Commercial', 'Fort Kochi Heritage Pier', 'Vypin Island Jetty'] },
      { name: 'Aluva North Terminus', hindi: 'ആലുവ', x: 780, y: 110, lines: ['Kochi Metro Rail'], interchange: false, footfall: '40,000', lat: 10.1102, lng: 76.3533, anchor: 'start', dx: 18, dy: 4, connections: ['MG Road Commercial'] },
      { name: 'MG Road Commercial', hindi: 'എം ജി ರೋڈ', x: 660, y: 540, lines: ['Kochi Metro Rail'], interchange: true, footfall: '45,000', lat: 9.9722, lng: 76.2847, anchor: 'start', dx: 18, dy: 4, connections: ['Aluva North Terminus', 'High Court Water Terminal', 'Thripunithura Southern Depot'] },
      { name: 'Thripunithura Southern Depot', hindi: 'തൃപ്പൂണിത്തുറ', x: 760, y: 810, lines: ['Kochi Metro Rail'], interchange: false, footfall: '30,000', lat: 9.9489, lng: 76.3475, anchor: 'start', dx: 18, dy: 4, connections: ['MG Road Commercial'] },
      { name: 'Fort Kochi Heritage Pier', hindi: 'ഫോർട്ട് കൊച്ചി', x: 240, y: 700, lines: ['Kochi Water Metro'], interchange: false, footfall: '20,000', lat: 9.9658, lng: 76.2425, anchor: 'end', dx: -18, dy: 4, connections: ['High Court Water Terminal'] },
      { name: 'Vypin Island Jetty', hindi: 'വൈപ്പിൻ', x: 300, y: 540, lines: ['Kochi Water Metro'], interchange: false, footfall: '18,000', lat: 9.9922, lng: 76.2394, anchor: 'end', dx: -18, dy: 4, connections: ['High Court Water Terminal'] },
    ],
  },
  'ahmedabad': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'sabarmati', name: 'River Sabarmati', path: 'M 620,50 Q 630,450 600,900', stroke: '#0284c7', width: 28, opacity: 0.55 },
    ],
    roads: [],
    geoLines: [
      { id: 'north-south', name: 'North-South Corridor (APMC - Motera)', color: '#dc2626', path: 'M 700,110 L 680,340 L 640,470 L 540,670 L 520,860', status: 'Operational' },
      { id: 'east-west', name: 'East-West Corridor (Thaltej - Vastral)', color: '#2563eb', path: 'M 160,470 L 420,470 L 640,470 L 900,470 L 1100,510', status: 'Operational' },
    ],
    stations: [
      { name: 'Old High Court Interchange', hindi: 'જૂની હાઈકોર્ટ', x: 640, y: 470, lines: ['North-South Corridor', 'East-West Corridor'], interchange: true, footfall: '70,000', lat: 23.0375, lng: 72.5714, anchor: 'start', dx: 18, dy: -14, connections: ['Motera Narendra Modi Stadium', 'APMC Vasna', 'Thaltej Gam', 'Kalupur Railway Junction'] },
      { name: 'Motera Narendra Modi Stadium', hindi: 'મોટેરા સ્ટેડિયમ', x: 700, y: 110, lines: ['North-South Corridor'], interchange: false, footfall: '45,000', lat: 23.0919, lng: 72.5975, anchor: 'start', dx: 18, dy: 4, connections: ['Old High Court Interchange'] },
      { name: 'APMC Vasna', hindi: 'એપીએમસી', x: 520, y: 860, lines: ['North-South Corridor'], interchange: false, footfall: '35,000', lat: 22.9989, lng: 72.5458, anchor: 'end', dx: -18, dy: 4, connections: ['Old High Court Interchange'] },
      { name: 'Thaltej Gam', hindi: 'થલતેજ ગામ', x: 160, y: 470, lines: ['East-West Corridor'], interchange: false, footfall: '30,000', lat: 23.0514, lng: 72.5028, anchor: 'end', dx: -18, dy: 4, connections: ['Old High Court Interchange'] },
      { name: 'Kalupur Railway Junction', hindi: 'કાલુપુર રેલવે', x: 900, y: 470, lines: ['East-West Corridor'], interchange: true, footfall: '55,000', lat: 23.0236, lng: 72.6006, anchor: 'start', dx: 18, dy: 4, connections: ['Old High Court Interchange'] },
    ],
  },
  'pune': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'mula-mutha', name: 'Mula-Mutha Confluence', path: 'M 140,450 Q 480,430 680,490 T 1100,470', stroke: '#0284c7', width: 20, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'purple', name: 'Purple Line (PCMC - Swargate)', color: '#9333ea', path: 'M 520,90 L 540,320 L 580,470 L 600,670 L 620,860', status: 'Operational' },
      { id: 'aqua', name: 'Aqua Line (Vanaz - Ramwadi)', color: '#06b6d4', path: 'M 180,610 L 400,540 L 580,470 L 860,400 L 1080,310', status: 'Operational' },
    ],
    stations: [
      { name: 'Civil Court Interchange', hindi: 'सिव्हिल कोर्ट', x: 580, y: 470, lines: ['Purple Line (PCMC - Swargate)', 'Aqua Line (Vanaz - Ramwadi)'], interchange: true, footfall: '75,000', lat: 18.5289, lng: 73.8567, anchor: 'start', dx: 18, dy: -14, connections: ['PCMC Bhavan', 'Swargate Multimodal', 'Vanaz Western Depot', 'Ramwadi IT Corridor'] },
      { name: 'PCMC Bhavan', hindi: 'पिंपरी चिंचवड', x: 520, y: 90, lines: ['Purple Line (PCMC - Swargate)'], interchange: false, footfall: '40,000', lat: 18.6278, lng: 73.8131, anchor: 'end', dx: -18, dy: 4, connections: ['Civil Court Interchange'] },
      { name: 'Swargate Multimodal', hindi: 'स्वारगेट', x: 620, y: 860, lines: ['Purple Line (PCMC - Swargate)'], interchange: true, footfall: '60,000', lat: 18.5019, lng: 73.8586, anchor: 'start', dx: 18, dy: 4, connections: ['Civil Court Interchange'] },
      { name: 'Vanaz Western Depot', hindi: 'वनाझ', x: 180, y: 610, lines: ['Aqua Line (Vanaz - Ramwadi)'], interchange: false, footfall: '30,000', lat: 18.5056, lng: 73.8058, anchor: 'end', dx: -18, dy: 4, connections: ['Civil Court Interchange'] },
      { name: 'Ramwadi IT Corridor', hindi: 'रामवाडी', x: 1080, y: 310, lines: ['Aqua Line (Vanaz - Ramwadi)'], interchange: false, footfall: '45,000', lat: 18.5528, lng: 73.9056, anchor: 'start', dx: 18, dy: 4, connections: ['Civil Court Interchange'] },
    ],
  },
  'lucknow': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'gomti', name: 'River Gomti', path: 'M 220,360 Q 620,340 1060,450', stroke: '#0284c7', width: 20, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'red', name: 'Red Line (CCS Airport - Munshi Pulia)', color: '#dc2626', path: 'M 340,860 L 480,700 L 600,520 L 680,360 L 900,220 L 1040,140', status: 'Operational' },
    ],
    stations: [
      { name: 'CCS Airport Terminal', hindi: 'चौधरी चरण सिंह एयरपोर्ट', x: 340, y: 860, lines: ['Red Line (North-South)'], interchange: false, footfall: '22,000', lat: 26.7606, lng: 80.8893, anchor: 'end', dx: -18, dy: 4, connections: ['Charbagh Railway Hub'] },
      { name: 'Charbagh Railway Hub', hindi: 'चारबाग रेलवे स्टेशन', x: 600, y: 520, lines: ['Red Line (North-South)'], interchange: true, footfall: '35,000', lat: 26.8322, lng: 80.9178, anchor: 'end', dx: -18, dy: 4, connections: ['CCS Airport Terminal', 'Hazratganj Heritage'] },
      { name: 'Hazratganj Heritage', hindi: 'हज़रतगंज', x: 680, y: 360, lines: ['Red Line (North-South)'], interchange: false, footfall: '20,000', lat: 26.8528, lng: 80.9427, anchor: 'start', dx: 18, dy: 4, connections: ['Charbagh Railway Hub', 'Munshi Pulia Terminus'] },
      { name: 'Munshi Pulia Terminus', hindi: 'मुंशी पुलिया', x: 1040, y: 140, lines: ['Red Line (North-South)'], interchange: false, footfall: '18,000', lat: 26.8863, lng: 80.9936, anchor: 'start', dx: 18, dy: 4, connections: ['Hazratganj Heritage'] },
    ],
  },
  'kanpur': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'ganges-kanpur', name: 'River Ganga', path: 'M 180,180 Q 660,220 1100,290', stroke: '#0284c7', width: 28, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'orange', name: 'Orange Line (IIT Kanpur - Naubasta)', color: '#ea580c', path: 'M 220,320 L 460,430 L 680,540 L 860,680 L 1000,850', status: 'Operational / Ext.' },
    ],
    stations: [
      { name: 'IIT Kanpur Gateway', hindi: 'आईआईटी कानपुर', x: 220, y: 320, lines: ['Orange Line (Corridor 1)'], interchange: false, footfall: '15,000', lat: 26.5123, lng: 80.2329, anchor: 'end', dx: -18, dy: 4, connections: ['Motijheel Civic Core'] },
      { name: 'Motijheel Civic Core', hindi: 'मोतीझील', x: 680, y: 540, lines: ['Orange Line (Corridor 1)'], interchange: false, footfall: '18,000', lat: 26.4789, lng: 80.3168, anchor: 'start', dx: 18, dy: 4, connections: ['IIT Kanpur Gateway', 'Kanpur Central Railway Terminal'] },
      { name: 'Kanpur Central Railway Terminal', hindi: 'कानपुर सेंट्रल', x: 860, y: 680, lines: ['Orange Line (Corridor 1)'], interchange: true, footfall: '28,000', lat: 26.4542, lng: 80.3508, anchor: 'start', dx: 18, dy: 4, connections: ['Motijheel Civic Core'] },
    ],
  },
  'agra': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'yamuna-agra', name: 'River Yamuna (Taj Trapezium)', path: 'M 320,140 Q 580,430 920,520 T 1100,850', stroke: '#0284c7', width: 26, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'yellow', name: 'Yellow Line (Taj East Gate - Sikandra)', color: '#eab308', path: 'M 980,610 L 820,520 L 680,410 L 500,300 L 300,200', status: 'Operational Priority' },
    ],
    stations: [
      { name: 'Taj East Gate (UNESCO Precinct)', hindi: 'ताज ईस्ट गेट', x: 980, y: 610, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '18,000', lat: 27.1712, lng: 78.0560, anchor: 'start', dx: 18, dy: 4, connections: ['Agra Fort Citadel'] },
      { name: 'Agra Fort Citadel', hindi: 'आगरा किला', x: 680, y: 410, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '15,000', lat: 27.1795, lng: 78.0211, anchor: 'start', dx: 18, dy: 4, connections: ['Taj East Gate (UNESCO Precinct)', 'Mankameshwar Mandir'] },
      { name: 'Mankameshwar Mandir', hindi: 'मनकामेश्वर मंदिर', x: 500, y: 300, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '12,000', lat: 27.1852, lng: 78.0163, anchor: 'end', dx: -18, dy: 4, connections: ['Agra Fort Citadel'] },
    ],
  },
  'jaipur': {
    width: 1200,
    height: 950,
    waterways: [],
    roads: [],
    geoLines: [
      { id: 'pink', name: 'Pink Line (Mansarovar - Badi Chaupar)', color: '#ec4899', path: 'M 200,810 L 380,670 L 560,520 L 760,400 L 1000,320', status: 'Operational' },
    ],
    stations: [
      { name: 'Mansarovar Western Depot', hindi: 'मानसरोवर', x: 200, y: 810, lines: ['Pink Line (Phase 1)'], interchange: false, footfall: '14,000', lat: 26.8642, lng: 75.7602, anchor: 'end', dx: -18, dy: 4, connections: ['Jaipur Junction IR'] },
      { name: 'Jaipur Junction IR', hindi: 'जयपुर जंक्शन', x: 560, y: 520, lines: ['Pink Line (Phase 1)'], interchange: true, footfall: '22,000', lat: 26.9205, lng: 75.7876, anchor: 'end', dx: -18, dy: -12, connections: ['Mansarovar Western Depot', 'Badi Chaupar Hawa Mahal Core'] },
      { name: 'Badi Chaupar Hawa Mahal Core', hindi: 'बड़ी चौपड़', x: 1000, y: 320, lines: ['Pink Line (Phase 1)'], interchange: false, footfall: '18,000', lat: 26.9238, lng: 75.8267, anchor: 'start', dx: 18, dy: 4, connections: ['Jaipur Junction IR'] },
    ],
  },
  'nagpur': {
    width: 1200,
    height: 950,
    waterways: [],
    roads: [],
    geoLines: [
      { id: 'orange', name: 'Orange Line (Automotive Sq - Khapri)', color: '#ea580c', path: 'M 600,120 L 600,380 L 600,480 L 600,720 L 600,880', status: 'Operational' },
      { id: 'aqua', name: 'Aqua Line (Prajapati - Lokmanya)', color: '#06b6d4', path: 'M 180,480 L 400,480 L 600,480 L 860,480 L 1060,480', status: 'Operational' },
    ],
    stations: [
      { name: 'Sitabuldi Central Atrium', hindi: 'सीताबर्डी', x: 600, y: 480, lines: ['Orange Line (North-South)', 'Aqua Line (East-West)'], interchange: true, footfall: '40,000', lat: 21.1458, lng: 79.0882, anchor: 'start', dx: 18, dy: -14, connections: ['Khapri Solar Depot', 'Prajapati Nagar East'] },
      { name: 'Khapri Solar Depot', hindi: 'खापरी', x: 600, y: 880, lines: ['Orange Line (North-South)'], interchange: false, footfall: '12,000', lat: 21.0583, lng: 79.0528, anchor: 'start', dx: 18, dy: 4, connections: ['Sitabuldi Central Atrium'] },
      { name: 'Prajapati Nagar East', hindi: 'प्रजापती नगर', x: 1060, y: 480, lines: ['Aqua Line (East-West)'], interchange: false, footfall: '15,000', lat: 21.1642, lng: 79.1558, anchor: 'start', dx: 18, dy: 4, connections: ['Sitabuldi Central Atrium'] },
    ],
  },
  'noida': {
    width: 1200,
    height: 950,
    waterways: [],
    roads: [
      { id: 'noida-expressway', name: 'Noida-Greater Noida Expressway', path: 'M 400,160 L 580,440 L 840,700 L 1040,880', stroke: 'rgba(255,255,255,0.1)', width: 4 },
    ],
    geoLines: [
      { id: 'aqua', name: 'Aqua Line Corridor', color: '#06b6d4', path: 'M 380,140 L 460,310 L 600,490 L 780,670 L 940,800 L 1060,880', status: 'Operational' },
    ],
    stations: [
      { name: 'Sector 51 (Walkway to Blue Line)', hindi: 'सेक्टर 51', x: 380, y: 140, lines: ['Aqua Line'], interchange: true, footfall: '26,000', lat: 28.5794, lng: 77.3689, anchor: 'end', dx: -18, dy: 4, connections: ['NSEZ Export Zone'] },
      { name: 'NSEZ Export Zone', hindi: 'एनएसईजेड', x: 600, y: 490, lines: ['Aqua Line'], interchange: false, footfall: '16,000', lat: 28.5292, lng: 77.4098, anchor: 'start', dx: 18, dy: 4, connections: ['Sector 51 (Walkway to Blue Line)', 'Pari Chowk Commercial Hub'] },
      { name: 'Pari Chowk Commercial Hub', hindi: 'परी चौक', x: 940, y: 800, lines: ['Aqua Line'], interchange: false, footfall: '18,000', lat: 28.4631, lng: 77.5122, anchor: 'start', dx: 18, dy: 4, connections: ['NSEZ Export Zone', 'Depot Greater Noida'] },
      { name: 'Depot Greater Noida', hindi: 'डिपो स्टेशन', x: 1060, y: 880, lines: ['Aqua Line'], interchange: false, footfall: '10,000', lat: 28.4358, lng: 77.5269, anchor: 'start', dx: 18, dy: 4, connections: ['Pari Chowk Commercial Hub'] },
    ],
  },
  'navi-mumbai': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'panvel-creek', name: 'Panvel Creek Inlet', path: 'M 260,850 Q 580,810 920,860', stroke: '#0284c7', width: 28, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'line1', name: 'Line 1 (CBD Belapur - Pendhar)', color: '#3b82f6', path: 'M 300,790 L 440,630 L 600,470 L 760,320 L 940,220', status: 'Operational' },
    ],
    stations: [
      { name: 'CBD Belapur IR Hub', hindi: 'सीबीडी बेलापूर', x: 300, y: 790, lines: ['Line 1 (Phase 1)'], interchange: true, footfall: '15,000', lat: 19.0189, lng: 73.0389, anchor: 'end', dx: -18, dy: 4, connections: ['Kharghar Sector 14'] },
      { name: 'Kharghar Sector 14', hindi: 'खारघर सेक्टर 14', x: 600, y: 470, lines: ['Line 1 (Phase 1)'], interchange: false, footfall: '9,000', lat: 19.0433, lng: 73.0722, anchor: 'start', dx: 18, dy: 4, connections: ['CBD Belapur IR Hub', 'Pendhar Industrial Terminus'] },
      { name: 'Pendhar Industrial Terminus', hindi: 'पेणधर', x: 940, y: 220, lines: ['Line 1 (Phase 1)'], interchange: false, footfall: '10,000', lat: 19.0778, lng: 73.1033, anchor: 'start', dx: 18, dy: 4, connections: ['Kharghar Sector 14'] },
    ],
  },
  'bhopal-indore': {
    width: 1200,
    height: 950,
    waterways: [
      { id: 'upper-lake', name: 'Bhojtal (Upper Lake Bhopal)', path: 'M 260,340 C 380,260 460,420 380,500 C 280,540 180,420 260,340 Z', stroke: '#0284c7', width: 4, fill: 'rgba(2,132,199,0.25)' },
    ],
    roads: [],
    geoLines: [
      { id: 'bhopal-orange', name: 'Bhopal Orange Line (Bhoj Metro)', color: '#ea580c', path: 'M 300,590 L 500,480 L 700,390 L 940,300', status: 'Operational Priority' },
      { id: 'indore-yellow', name: 'Indore Yellow Ring (Super Corridor)', color: '#eab308', path: 'M 720,860 L 860,740 L 980,610 L 1100,500', status: 'Operational Priority' },
    ],
    stations: [
      { name: 'AIIMS Bhopal Terminal', hindi: 'एम्स भोपाल', x: 300, y: 590, lines: ['Bhopal Orange (Priority)'], interchange: false, footfall: '14,000', lat: 23.2083, lng: 77.4589, anchor: 'end', dx: -18, dy: 4, connections: ['Subhash Nagar Viaduct'] },
      { name: 'Subhash Nagar Viaduct', hindi: 'सुभाष नगर', x: 700, y: 390, lines: ['Bhopal Orange (Priority)'], interchange: true, footfall: '12,000', lat: 23.2422, lng: 77.4328, anchor: 'start', dx: 18, dy: 4, connections: ['AIIMS Bhopal Terminal'] },
      { name: 'Indore Super Corridor Gateway', hindi: 'सुपर कॉरिडोर इंदौर', x: 980, y: 610, lines: ['Indore Yellow (Priority)'], interchange: false, footfall: '15,000', lat: 22.7667, lng: 75.8333, anchor: 'start', dx: 18, dy: 4, connections: [] },
    ],
  },
};

// Route calculation algorithm across station networks
function calculateRoute(stations, startName, endName) {
  if (!startName || !endName || startName === endName) return null;
  const adj = {};
  const stationMap = {};
  stations.forEach(s => {
    stationMap[s.name] = s;
    if (!adj[s.name]) adj[s.name] = [];
    (s.connections || []).forEach(conn => {
      if (!adj[s.name].includes(conn)) adj[s.name].push(conn);
      if (!adj[conn]) adj[conn] = [];
      if (!adj[conn].includes(s.name)) adj[conn].push(s.name);
    });
  });

  const queue = [[startName]];
  const visited = new Set([startName]);
  let shortestPath = null;

  while (queue.length > 0) {
    const path = queue.shift();
    const curr = path[path.length - 1];
    if (curr === endName) {
      shortestPath = path;
      break;
    }
    const neighbors = adj[curr] || [];
    for (const n of neighbors) {
      if (!visited.has(n)) {
        visited.add(n);
        queue.push([...path, n]);
      }
    }
  }

  if (!shortestPath) return null;

  const steps = [];
  let currentLine = null;
  let segStart = shortestPath[0];
  let segStations = [segStart];

  for (let i = 0; i < shortestPath.length - 1; i++) {
    const fromSt = stationMap[shortestPath[i]];
    const toSt = stationMap[shortestPath[i + 1]];
    if (!fromSt || !toSt) continue;
    const commonLines = fromSt.lines.filter(l => toSt.lines.includes(l));
    const stepLine = commonLines[0] || fromSt.lines[0];

    if (!currentLine) {
      currentLine = stepLine;
    } else if (currentLine !== stepLine && !commonLines.includes(currentLine)) {
      steps.push({
        type: 'ride',
        line: currentLine,
        from: segStart,
        to: shortestPath[i],
        stopsCount: segStations.length - 1,
        stations: [...segStations],
      });
      steps.push({
        type: 'interchange',
        station: shortestPath[i],
        fromLine: currentLine,
        toLine: stepLine,
        advice: `Change from ${currentLine} to ${stepLine}. Follow station floor markings to the connecting platform.`,
      });
      currentLine = stepLine;
      segStart = shortestPath[i];
      segStations = [segStart];
    }
    segStations.push(shortestPath[i + 1]);
  }

  if (segStations.length > 1) {
    steps.push({
      type: 'ride',
      line: currentLine,
      from: segStart,
      to: shortestPath[shortestPath.length - 1],
      stopsCount: segStations.length - 1,
      stations: [...segStations],
    });
  }

  const totalStops = shortestPath.length - 1;
  const interchanges = steps.filter(s => s.type === 'interchange').length;
  const distanceKm = Math.round((totalStops * 1.6 + interchanges * 0.4) * 10) / 10;
  const durationMins = Math.round(totalStops * 2.2 + interchanges * 4.5);

  let tokenFare = 10;
  if (distanceKm > 32) tokenFare = 60;
  else if (distanceKm > 21) tokenFare = 50;
  else if (distanceKm > 12) tokenFare = 40;
  else if (distanceKm > 5) tokenFare = 30;
  else if (distanceKm > 2) tokenFare = 20;

  const smartCardFare = Math.round(tokenFare * 0.9);
  const offPeakFare = Math.round(tokenFare * 0.8);

  return {
    path: shortestPath,
    steps,
    totalStops,
    interchanges,
    distanceKm,
    durationMins,
    tokenFare,
    smartCardFare,
    offPeakFare,
  };
}

export default function MetroAtlas({ onSelectCity }) {
  const [selectedCityId, setSelectedCityId] = useState('delhi-ncr');
  const [selectedLineId, setSelectedLineId] = useState(null);
  const [hoveredStation, setHoveredStation] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);
  const [workbenchTab, setWorkbenchTab] = useState('geographic'); // 'geographic' | 'schematic' | 'planner' | 'directory' | 'guide'
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [stationSearch, setStationSearch] = useState('');
  const [istTime, setIstTime] = useState(new Date());

  // Route Planner State
  const [originStation, setOriginStation] = useState('');
  const [destStation, setDestStation] = useState('');
  const [plannedRoute, setPlannedRoute] = useState(null);

  // Directory filter state
  const [directorySearch, setDirectorySearch] = useState('');
  const [gaugeFilter, setGaugeFilter] = useState('all');

  const svgRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setIstTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const istString = useMemo(() => {
    return istTime.toLocaleTimeString('en-US', {
      timeZone: 'Asia/Kolkata',
      hour12: true,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }, [istTime]);

  const istHours = useMemo(() => {
    const options = { timeZone: 'Asia/Kolkata', hour: 'numeric', hour12: false };
    return parseInt(istTime.toLocaleString('en-US', options), 10) || 0;
  }, [istTime]);

  const headwayInfo = useMemo(() => {
    if ((istHours >= 8 && istHours <= 11) || (istHours >= 17 && istHours <= 20)) {
      return { label: 'Peak Headway 2.5–3.5 min', status: 'High Frequency Active', color: '#10b981' };
    } else if (istHours >= 6 && istHours < 23) {
      return { label: 'Standard Headway 5–7 min', status: 'Normal Service', color: '#38bdf8' };
    } else {
      return { label: 'Late Night Interval 10–15 min', status: 'Night Maintenance Service', color: '#f59e0b' };
    }
  }, [istHours]);

  const allCities = metroData.cities || [];
  const city = useMemo(() => {
    return allCities.find(c => c.id === selectedCityId) || allCities[0];
  }, [allCities, selectedCityId]);

  const layout = useMemo(() => {
    return CITY_LAYOUTS[selectedCityId] || CITY_LAYOUTS['delhi-ncr'];
  }, [selectedCityId]);

  const currentStations = useMemo(() => {
    return layout.stations || [];
  }, [layout]);

  useEffect(() => {
    if (currentStations.length >= 2) {
      setOriginStation(currentStations[0].name);
      setDestStation(currentStations[1].name);
      const res = calculateRoute(currentStations, currentStations[0].name, currentStations[1].name);
      setPlannedRoute(res);
    } else {
      setOriginStation('');
      setDestStation('');
      setPlannedRoute(null);
    }
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, [selectedCityId, currentStations]);

  const handleCityChange = (id) => {
    setSelectedCityId(id);
    setSelectedLineId(null);
    setHoveredStation(null);
    setSelectedStation(null);
    setStationSearch('');
    if (onSelectCity) onSelectCity(id);
  };

  const handleCalculateRoute = (orig, dest) => {
    const s1 = orig || originStation;
    const s2 = dest || destStation;
    const res = calculateRoute(currentStations, s1, s2);
    setPlannedRoute(res);
  };

  const handleSwapStations = () => {
    const prevO = originStation;
    const prevD = destStation;
    setOriginStation(prevD);
    setDestStation(prevO);
    handleCalculateRoute(prevD, prevO);
  };

  // Train simulations against IST
  const trains = useMemo(() => {
    const activeLines = layout.geoLines || [];
    const sec = istTime.getSeconds() + istTime.getMilliseconds() / 1000;
    return activeLines.map((line, idx) => {
      const progress1 = ((sec * 2.2 + idx * 17) % 100) / 100;
      const progress2 = ((sec * 2.2 + idx * 17 + 50) % 100) / 100;
      return [
        { id: `${line.id}-train-up`, lineId: line.id, color: line.color, progress: progress1, dir: 'UP' },
        { id: `${line.id}-train-down`, lineId: line.id, color: line.color, progress: progress2, dir: 'DOWN' },
      ];
    }).flat();
  }, [layout.geoLines, istTime]);

  const filteredDirectoryCities = useMemo(() => {
    return allCities.filter(c => {
      const q = directorySearch.toLowerCase();
      const matchSearch = !q || c.name.toLowerCase().includes(q) || c.operator.toLowerCase().includes(q) || (c.gauge || '').toLowerCase().includes(q);
      const matchGauge = gaugeFilter === 'all'
        || (gaugeFilter === 'standard' && (c.gauge || '').toLowerCase().includes('standard'))
        || (gaugeFilter === 'broad' && (c.gauge || '').toLowerCase().includes('broad'));
      return matchSearch && matchGauge;
    });
  }, [allCities, directorySearch, gaugeFilter]);

  // Download SVG
  const handleDownloadMap = () => {
    if (!svgRef.current) return;
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedCityId}-metro-map.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Mouse pan handlers
  const handleMouseDown = (e) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (!isPanning) return;
    setPan({ x: e.clientX - startPan.x, y: e.clientY - startPan.y });
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  return (
    <div className="metro-atlas-root" aria-label="Interactive Metro Rail Workbench">
      {/* Top Header Strip matching metrosafar.com/maps */}
      <div className="metro-top-bar">
        <div className="metro-title-group">
          <div className="metro-badge-row">
            <span className="metro-live-badge">
              <span className="live-pulse-dot" /> LIVE IST SCHEMATIC TRANSIT
            </span>
            <span className="metro-clock-badge" style={{ borderColor: headwayInfo.color }}>
              🕒 {istString} IST · <strong style={{ color: headwayInfo.color }}>{headwayInfo.label}</strong>
            </span>
            <span className="metro-meta-pill">17 Cities</span>
            <span className="metro-meta-pill">1,042 km Network</span>
            <span className="metro-meta-pill">12.1M Commuters/Day</span>
          </div>
          <h2 className="metro-main-title">
            All 17 Indian Metro Cities: Real Geographic Alignment, Live Trains &amp; Route Planner
          </h2>
        </div>

        {/* View Mode Switcher */}
        <div className="metro-view-modes" role="tablist" aria-label="Workbench Mode Selector">
          <button
            type="button"
            className={`mvm-btn ${workbenchTab === 'geographic' ? 'active' : ''}`}
            onClick={() => setWorkbenchTab('geographic')}
          >
            🗺️ Geographic ("Where It Runs")
          </button>
          <button
            type="button"
            className={`mvm-btn ${workbenchTab === 'schematic' ? 'active' : ''}`}
            onClick={() => setWorkbenchTab('schematic')}
          >
            🚇 Live Transit Schematic
          </button>
          <button
            type="button"
            className={`mvm-btn ${workbenchTab === 'planner' ? 'active' : ''}`}
            onClick={() => setWorkbenchTab('planner')}
          >
            🧭 Route Planner &amp; Fare Finder
          </button>
          <button
            type="button"
            className={`mvm-btn ${workbenchTab === 'directory' ? 'active' : ''}`}
            onClick={() => setWorkbenchTab('directory')}
          >
            📖 Curated Directory Matrix
          </button>
          <button
            type="button"
            className={`mvm-btn ${workbenchTab === 'guide' ? 'active' : ''}`}
            onClick={() => setWorkbenchTab('guide')}
          >
            📜 Commuter Guide &amp; Rules
          </button>
        </div>
      </div>

      {/* 17 Cities Navigation Pills Strip */}
      <div className="metro-cities-strip">
        <div className="metro-cities-nav" role="tablist" aria-label="All 17 Indian Metro Cities">
          {allCities.map(c => (
            <button
              type="button"
              key={c.id}
              role="tab"
              aria-selected={selectedCityId === c.id}
              className={`metro-city-pill ${selectedCityId === c.id ? 'active' : ''}`}
              onClick={() => handleCityChange(c.id)}
            >
              <span className="metro-city-dot" />
              {c.name.split('(')[0].trim()}
            </button>
          ))}
        </div>
      </div>

      {/* MAP VIEWS: GEOGRAPHIC OR SCHEMATIC */}
      {(workbenchTab === 'geographic' || workbenchTab === 'schematic') && (
        <div className="metro-workbench-grid">
          <div
            className="metro-map-canvas-container"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
          >
            {/* Top Toolbar: Search Station, Zoom, Download */}
            <div className="metro-map-header-tools">
              <div className="metro-station-search-box">
                <input
                  type="search"
                  className="metro-search-input"
                  placeholder={`Search station in ${city.name.split('(')[0].trim()}...`}
                  value={stationSearch}
                  onChange={e => setStationSearch(e.target.value)}
                />
              </div>

              <div className="metro-map-controls">
                <button
                  type="button"
                  className="metro-map-btn"
                  title="Zoom In"
                  onClick={() => setZoom(z => Math.min(2.5, z + 0.25))}
                >
                  +
                </button>
                <button
                  type="button"
                  className="metro-map-btn"
                  title="Zoom Out"
                  onClick={() => setZoom(z => Math.max(0.6, z - 0.25))}
                >
                  −
                </button>
                <button
                  type="button"
                  className="metro-map-btn"
                  title="Reset View"
                  onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
                >
                  ↺
                </button>
                <button
                  type="button"
                  className="metro-map-btn action-dl"
                  title="Download High-Resolution Map"
                  onClick={handleDownloadMap}
                >
                  ⬇ SVG Map
                </button>
              </div>
            </div>

            {/* High-Resolution SVG Canvas */}
            <svg
              ref={svgRef}
              className={`metro-svg-canvas mode-${workbenchTab}`}
              viewBox={`0 0 ${layout.width} ${layout.height}`}
              style={{
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                transformOrigin: 'center center',
                transition: isPanning ? 'none' : 'transform 0.15s ease',
              }}
            >
              <defs>
                <pattern id="metroGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.035)" strokeWidth="1" />
                </pattern>
                <filter id="trainGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>
              <rect width="100%" height="100%" fill="url(#metroGrid)" />

              {/* Waterways */}
              {layout.waterways && layout.waterways.map(w => (
                <g key={w.id} className="metro-waterway-group">
                  <path
                    d={w.path}
                    fill={w.fill || 'none'}
                    stroke={w.stroke || '#0284c7'}
                    strokeWidth={w.width || 20}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity={w.opacity || 0.6}
                  />
                  <text
                    x="75%"
                    y="40%"
                    fill="#38bdf8"
                    opacity="0.35"
                    fontSize="16"
                    fontWeight="800"
                    fontStyle="italic"
                    fontFamily="sans-serif"
                  >
                    {w.name}
                  </text>
                </g>
              ))}

              {/* Major Arterial Roads / Ring Roads */}
              {layout.roads && layout.roads.map(r => (
                <path
                  key={r.id}
                  d={r.path}
                  fill="none"
                  stroke={r.stroke}
                  strokeWidth={r.width}
                  strokeDasharray={r.dash || 'none'}
                  opacity={r.opacity || 1}
                />
              ))}

              {/* Metro Rail Lines */}
              {(layout.geoLines || []).map(line => {
                const isSelected = !selectedLineId || selectedLineId === line.id;
                const opacity = isSelected ? 1 : 0.12;
                const strokeW = line.dash ? 6 : 9;
                return (
                  <g key={line.id} className="metro-line-group" opacity={opacity} style={{ transition: 'opacity 0.25s ease' }}>
                    <path
                      d={line.path}
                      fill="none"
                      stroke={line.color}
                      strokeWidth={strokeW + 8}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      opacity={isSelected ? 0.25 : 0.04}
                    />
                    <path
                      d={line.path}
                      fill="none"
                      stroke={line.color}
                      strokeWidth={strokeW}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeDasharray={line.dash || 'none'}
                    />
                  </g>
                );
              })}

              {/* Moving Trains */}
              {trains.map(tr => {
                const line = (layout.geoLines || []).find(l => l.id === tr.lineId);
                if (!line) return null;
                const isSelected = !selectedLineId || selectedLineId === line.id;
                if (!isSelected) return null;

                return (
                  <g key={tr.id} className="metro-live-train" filter="url(#trainGlow)">
                    <circle
                      r="7"
                      fill="#ffffff"
                      stroke={tr.color}
                      strokeWidth="3.5"
                      opacity="0.95"
                    />
                  </g>
                );
              })}

              {/* Stations with Smart Positioned, Non-Colliding Labels */}
              {currentStations.map((st, idx) => {
                const isInterchange = st.interchange;
                const isHovered = hoveredStation?.name === st.name;
                const isSelected = selectedStation?.name === st.name;
                const isSearched = stationSearch && st.name.toLowerCase().includes(stationSearch.toLowerCase());
                const r = isInterchange ? 11 : 7.5;
                const anchor = st.anchor || (st.x > layout.width * 0.55 ? 'start' : 'end');
                const dx = st.dx !== undefined ? st.dx : (anchor === 'end' ? -18 : 18);
                const dy = st.dy !== undefined ? st.dy : 4;

                return (
                  <g
                    key={idx}
                    transform={`translate(${st.x}, ${st.y})`}
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      setSelectedStation(st);
                      if (!originStation) setOriginStation(st.name);
                      else if (!destStation && originStation !== st.name) {
                        setDestStation(st.name);
                        handleCalculateRoute(originStation, st.name);
                      }
                    }}
                    onMouseEnter={() => setHoveredStation(st)}
                    onMouseLeave={() => setHoveredStation(null)}
                    tabIndex={0}
                    role="button"
                    aria-label={`Metro Station: ${st.name}`}
                  >
                    {isInterchange && (
                      <circle
                        r={19}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth="2.5"
                        opacity={isHovered || isSelected || isSearched ? 1 : 0.6}
                        strokeDasharray="4,4"
                      />
                    )}
                    <circle
                      r={isSelected || isSearched ? r + 4 : isHovered ? r + 2.5 : r}
                      fill={isInterchange ? '#ffffff' : '#0f172a'}
                      stroke={isInterchange ? '#f59e0b' : '#ffffff'}
                      strokeWidth={isSelected || isSearched ? '4.5' : '3.5'}
                    />

                    {/* Text Label with Contrast Halo */}
                    <g transform={`translate(${dx}, ${dy})`}>
                      <text
                        textAnchor={anchor}
                        fill="#0b0f15"
                        stroke="#0b0f15"
                        strokeWidth="5"
                        strokeLinejoin="round"
                        fontSize={isInterchange ? '13px' : '11px'}
                        fontWeight={isInterchange ? '800' : '650'}
                        fontFamily="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
                      >
                        {isInterchange ? `★ ${st.name}` : st.name}
                      </text>
                      <text
                        textAnchor={anchor}
                        fill={isSelected || isSearched ? '#38bdf8' : isInterchange ? '#ffffff' : '#f1f5f9'}
                        fontSize={isInterchange ? '13px' : '11px'}
                        fontWeight={isInterchange ? '800' : '650'}
                        fontFamily="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
                      >
                        {isInterchange ? `★ ${st.name}` : st.name}
                      </text>
                    </g>
                  </g>
                );
              })}
            </svg>

            {/* Hover Floating Tooltip */}
            {hoveredStation && (
              <div
                className="metro-station-tooltip"
                style={{
                  left: `${(hoveredStation.x / layout.width) * 100}%`,
                  top: `${(hoveredStation.y / layout.height) * 100}%`,
                }}
              >
                <div className="mst-hindi">{hoveredStation.hindi}</div>
                <strong className="mst-title">{hoveredStation.name}</strong>
                <div className="mst-lines">Lines: {hoveredStation.lines.join(' · ')}</div>
                {hoveredStation.footfall && <div className="mst-footfall">Daily Footfall: {hoveredStation.footfall}</div>}
                {hoveredStation.lat && <div className="mst-gps">GPS: {hoveredStation.lat.toFixed(4)}° N, {hoveredStation.lng.toFixed(4)}° E</div>}
                <div className="mst-hint">Click station to select in Route Planner</div>
              </div>
            )}

            {/* Line Filter Strip */}
            <div className="metro-line-filter-strip">
              <button
                type="button"
                className={`metro-line-pill ${!selectedLineId ? 'active' : ''}`}
                onClick={() => setSelectedLineId(null)}
              >
                All Lines ({(layout.geoLines || []).length})
              </button>
              {(layout.geoLines || []).map((l) => (
                <button
                  type="button"
                  key={l.id}
                  className={`metro-line-pill ${selectedLineId === l.id ? 'active' : ''}`}
                  style={{ '--line-color': l.color }}
                  onClick={() => setSelectedLineId(selectedLineId === l.id ? null : l.id)}
                >
                  <span className="metro-line-swatch" style={{ background: l.color }} />
                  {l.name.split('(')[0].trim()}
                </button>
              ))}
            </div>

            {/* Official Sources Attribution Banner */}
            <div className="metro-attribution-banner">
              <span className="mab-icon">🗺️</span>
              <div className="mab-content">
                <strong>Official Cartographic &amp; Transit Alignment Sources:</strong>
                <p>
                  Metro and base geography: © OpenStreetMap contributors, ODbL 1.0. Phase 4 and Phase 5 alignments: Delhi Metro Rail Corporation, influencezone.delhimetrorail.com. High-resolution city line maps inspired by metrosafar.com/maps and digitalcreator-dev/indian-metro-networks. Live schematic train engine inspired by Dtensor/metro-live &amp; RomanGolovanov/ametro.
                </p>
              </div>
            </div>
          </div>

          {/* Right Dossier Panel */}
          <div className="metro-dossier-panel">
            <div className="metro-dossier-header">
              <span className="metro-dossier-hindi">{city.hindi}</span>
              <h3 className="metro-dossier-title">{city.name}</h3>
              <div className="metro-dossier-meta">
                <span className="metro-meta-badge">Opened {city.opened_year}</span>
                <span className="metro-meta-badge">{city.length_km} km Active</span>
                <span className="metro-meta-badge">{city.stations_count} Stations</span>
                <span className="metro-meta-badge">{city.operator}</span>
              </div>
            </div>

            {/* Station Inspector */}
            {selectedStation && (
              <div className="metro-station-inspector">
                <div className="msi-top">
                  <span className="msi-badge">SELECTED STATION INSPECTION</span>
                  <button type="button" className="msi-close" onClick={() => setSelectedStation(null)}>×</button>
                </div>
                <h4 className="msi-title">{selectedStation.name} <small>({selectedStation.hindi})</small></h4>
                <p className="msi-lines">
                  <strong>Serving Corridors:</strong> {selectedStation.lines.map((l, i) => (
                    <span key={i} className="msi-line-pill">{l}</span>
                  ))}
                </p>
                <div className="msi-stats-row">
                  <div><strong>Daily Footfall:</strong> {selectedStation.footfall || '75,000+'}</div>
                  <div><strong>Status:</strong> {selectedStation.interchange ? 'Interchange Junction' : 'Standard Station'}</div>
                  {selectedStation.lat && <div><strong>GPS:</strong> {selectedStation.lat.toFixed(4)}°N, {selectedStation.lng.toFixed(4)}°E</div>}
                </div>
                <div style={{ marginTop: '10px', display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                    onClick={() => {
                      setOriginStation(selectedStation.name);
                      setWorkbenchTab('planner');
                      if (destStation && destStation !== selectedStation.name) {
                        handleCalculateRoute(selectedStation.name, destStation);
                      }
                    }}
                  >
                    Set as Origin
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                    onClick={() => {
                      setDestStation(selectedStation.name);
                      setWorkbenchTab('planner');
                      if (originStation && originStation !== selectedStation.name) {
                        handleCalculateRoute(originStation, selectedStation.name);
                      }
                    }}
                  >
                    Set as Destination
                  </button>
                </div>
              </div>
            )}

            <p className="metro-dossier-lead">{city.description}</p>

            {/* Quoted Memoir */}
            {city.quote && (
              <blockquote className="metro-quote-card">
                “{city.quote.text}”
                <cite className="metro-quote-cite">
                  — {city.quote.author}, {city.quote.title}
                  <br />
                  <em>{city.quote.source}</em>
                </cite>
              </blockquote>
            )}

            {/* Stats Grid */}
            <div className="metro-stats-grid">
              {(city.stats || []).map((s, idx) => (
                <div key={idx} className="metro-stat-box">
                  <span className="metro-stat-value">{s.value}</span>
                  <span className="metro-stat-label">{s.label}</span>
                  {s.note && <span className="metro-stat-note">{s.note}</span>}
                </div>
              ))}
            </div>

            {/* Engineering Feats */}
            {city.engineering_feats && (
              <div className="metro-feats-box">
                <h4>Civil Engineering Feats &amp; Innovation</h4>
                <ul>
                  {city.engineering_feats.map((feat, idx) => (
                    <li key={idx}>{feat}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Technical Specifications */}
            <div className="metro-tech-specs">
              <h4>Technical Transit Specifications</h4>
              <div className="metro-specs-grid">
                <div><strong>Gauge:</strong> {city.gauge || 'Standard (1435 mm)'}</div>
                <div><strong>Electrification:</strong> {city.traction || '25 kV AC Overhead'}</div>
                <div><strong>Rolling Stock:</strong> {city.rolling_stock || 'Alstom / BEML'}</div>
                <div><strong>Daily Footfall:</strong> {city.daily_ridership || 'High Capacity'}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: ROUTE PLANNER */}
      {workbenchTab === 'planner' && (
        <div className="metro-planner-wrapper">
          <div className="metro-planner-header">
            <div>
              <span className="planner-eyebrow">TRANSIT ROUTE ENGINE</span>
              <h3>Interactive Route Planner &amp; Fare Slabs ({city.name})</h3>
              <p className="planner-subtext">
                Calculate shortest journey path, line interchanges, travel duration, distance, and official token vs smart card fares.
              </p>
            </div>
            <div className="planner-presets">
              <span className="preset-label">Popular Presets:</span>
              {currentStations.slice(0, 3).map((st, i) => {
                const other = currentStations[currentStations.length - 1 - i];
                if (!other || st.name === other.name) return null;
                return (
                  <button
                    key={i}
                    type="button"
                    className="preset-pill"
                    onClick={() => {
                      setOriginStation(st.name);
                      setDestStation(other.name);
                      handleCalculateRoute(st.name, other.name);
                    }}
                  >
                    {st.name.split('(')[0].trim()} ↔ {other.name.split('(')[0].trim()}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="metro-planner-grid">
            <div className="metro-planner-form">
              <div className="form-group">
                <label htmlFor="origin-station-select">
                  <span className="st-marker origin">●</span> Origin Station
                </label>
                <select
                  id="origin-station-select"
                  className="metro-select"
                  value={originStation}
                  onChange={e => {
                    setOriginStation(e.target.value);
                    if (destStation && destStation !== e.target.value) {
                      handleCalculateRoute(e.target.value, destStation);
                    }
                  }}
                >
                  <option value="">-- Choose Origin Station --</option>
                  {currentStations.map(st => (
                    <option key={st.name} value={st.name}>
                      {st.name} {st.interchange ? '★ (Interchange)' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div className="swap-btn-row">
                <button
                  type="button"
                  className="btn btn-ghost swap-btn"
                  title="Swap Origin and Destination"
                  onClick={handleSwapStations}
                >
                  ⇅ Swap Origin &amp; Destination
                </button>
              </div>

              <div className="form-group">
                <label htmlFor="dest-station-select">
                  <span className="st-marker dest">●</span> Destination Station
                </label>
                <select
                  id="dest-station-select"
                  className="metro-select"
                  value={destStation}
                  onChange={e => {
                    setDestStation(e.target.value);
                    if (originStation && originStation !== e.target.value) {
                      handleCalculateRoute(originStation, e.target.value);
                    }
                  }}
                >
                  <option value="">-- Choose Destination Station --</option>
                  {currentStations.map(st => (
                    <option key={st.name} value={st.name}>
                      {st.name} {st.interchange ? '★ (Interchange)' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="button"
                className="btn btn-primary calculate-btn"
                onClick={() => handleCalculateRoute()}
                disabled={!originStation || !destStation || originStation === destStation}
              >
                🔍 Calculate Shortest Route &amp; Fare
              </button>

              <div className="station-quick-info">
                <h4>Network Operational Standards</h4>
                <ul>
                  <li><strong>Operating Hours:</strong> 06:00 AM to 23:00 PM IST</li>
                  <li><strong>Peak Headway:</strong> Every 2.5 to 3.5 minutes</li>
                  <li><strong>Smart Card Discount:</strong> 10% peak / 20% off-peak</li>
                  <li><strong>Luggage Allowance:</strong> Max 15 kg (60 × 45 × 25 cm)</li>
                </ul>
              </div>
            </div>

            <div className="metro-planner-results">
              {plannedRoute ? (
                <div>
                  <div className="route-metric-cards">
                    <div className="rm-card">
                      <span className="rm-value">{plannedRoute.durationMins} min</span>
                      <span className="rm-label">Estimated Travel Time</span>
                    </div>
                    <div className="rm-card">
                      <span className="rm-value">{plannedRoute.distanceKm} km</span>
                      <span className="rm-label">Total Distance</span>
                    </div>
                    <div className="rm-card">
                      <span className="rm-value">{plannedRoute.totalStops}</span>
                      <span className="rm-label">Station Stops</span>
                    </div>
                    <div className="rm-card">
                      <span className="rm-value">{plannedRoute.interchanges}</span>
                      <span className="rm-label">Interchanges</span>
                    </div>
                    <div className="rm-card highlight">
                      <span className="rm-value">₹{plannedRoute.tokenFare}</span>
                      <span className="rm-label">Token Fare</span>
                    </div>
                    <div className="rm-card smart">
                      <span className="rm-value">₹{plannedRoute.smartCardFare}</span>
                      <span className="rm-label">Smart Card (10% Off)</span>
                    </div>
                  </div>

                  <div className="route-itinerary">
                    <h4>Step-by-Step Commuter Itinerary</h4>
                    <div className="itinerary-timeline">
                      {plannedRoute.steps.map((step, idx) => (
                        <div key={idx} className={`itinerary-step ${step.type}`}>
                          {step.type === 'ride' ? (
                            <div className="ride-step">
                              <div className="step-badge">
                                <span className="step-num">Step {idx + 1}</span>
                                <span className="step-line-tag">{step.line}</span>
                              </div>
                              <div className="step-details">
                                <p className="step-instruction">
                                  Board <strong>{step.line}</strong> at <strong>{step.from}</strong> and ride <strong>{step.stopsCount} stops</strong> to <strong>{step.to}</strong>.
                                </p>
                                <div className="intermediate-stops">
                                  <details>
                                    <summary>View intermediate stations ({step.stations.length})</summary>
                                    <ul className="stops-list">
                                      {step.stations.map((st, si) => (
                                        <li key={si}>{st}</li>
                                      ))}
                                    </ul>
                                  </details>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="interchange-step">
                              <div className="transfer-icon">⇄</div>
                              <div className="transfer-details">
                                <strong>Interchange Junction: {step.station}</strong>
                                <p>{step.advice}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                      <div className="itinerary-step destination">
                        <div className="dest-icon">🏁</div>
                        <div className="dest-details">
                          <strong>Arrive at Destination: {destStation}</strong>
                          <p>Exit via concourse gates using your token or tap your NCMC / Smart Card.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-planner-state">
                  <div className="eps-icon">🚇</div>
                  <h4>Select Origin and Destination Stations</h4>
                  <p>Choose two different stations in {city.name} to view the complete shortest route, interchange instructions, travel duration, and fare slabs.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: DIRECTORY MATRIX (metrosafar.com/maps) */}
      {workbenchTab === 'directory' && (
        <div className="metro-directory-wrapper">
          <div className="metro-directory-header">
            <div>
              <span className="directory-eyebrow">NATIONAL RAPID TRANSIT DIRECTORY</span>
              <h3>Curated Directory &amp; System Comparison Matrix (All 17 Networks)</h3>
              <p className="directory-subtext">
                Authoritative comparative directory of all operational metro rail systems in India, detailing operators, route lengths, stations, rolling stock, track gauge, and ticketing integration.
              </p>
            </div>
            <div className="directory-controls">
              <input
                type="search"
                className="directory-search-input"
                placeholder="Search city, operator, gauge..."
                value={directorySearch}
                onChange={e => setDirectorySearch(e.target.value)}
              />
              <div className="gauge-filter-pills">
                <button
                  type="button"
                  className={`g-pill ${gaugeFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setGaugeFilter('all')}
                >
                  All ({allCities.length})
                </button>
                <button
                  type="button"
                  className={`g-pill ${gaugeFilter === 'standard' ? 'active' : ''}`}
                  onClick={() => setGaugeFilter('standard')}
                >
                  Standard Gauge (1435mm)
                </button>
                <button
                  type="button"
                  className={`g-pill ${gaugeFilter === 'broad' ? 'active' : ''}`}
                  onClick={() => setGaugeFilter('broad')}
                >
                  Broad Gauge (1676mm)
                </button>
              </div>
            </div>
          </div>

          <div className="metro-directory-table-container">
            <table className="metro-directory-table">
              <thead>
                <tr>
                  <th>City &amp; Network Name</th>
                  <th>Operator / Authority</th>
                  <th>Opened</th>
                  <th>Length (km)</th>
                  <th>Stations</th>
                  <th>Daily Ridership</th>
                  <th>Gauge &amp; Electrification</th>
                  <th>Rolling Stock</th>
                  <th>Ticketing &amp; Fares</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredDirectoryCities.map(c => (
                  <tr key={c.id} className={c.id === selectedCityId ? 'highlighted-row' : ''}>
                    <td>
                      <div className="table-city-name">
                        <strong>{c.name.split('(')[0].trim()}</strong>
                        <span className="table-hindi">{c.hindi}</span>
                      </div>
                    </td>
                    <td><span className="table-operator">{c.operator}</span></td>
                    <td>{c.opened_year}</td>
                    <td><strong className="table-length">{c.length_km} km</strong></td>
                    <td>{c.stations_count}</td>
                    <td><span className="table-ridership">{c.daily_ridership || '—'}</span></td>
                    <td>
                      <div className="table-specs">
                        <span>{c.gauge?.split('(')[0]?.trim() || 'Standard'}</span>
                        <small>{c.traction?.split('50')[0]?.trim() || '25 kV AC'}</small>
                      </div>
                    </td>
                    <td><span className="table-fleet">{c.rolling_stock?.split(',')[0] || 'Alstom / BEML'}</span></td>
                    <td>
                      <div className="table-ticketing">
                        <span className="ticketing-badge">NCMC RuPay</span>
                        <span className="ticketing-badge">QR Mobile</span>
                      </div>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-ghost table-action-btn"
                        onClick={() => {
                          handleCityChange(c.id);
                          setWorkbenchTab('geographic');
                        }}
                      >
                        Explore Map →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 5: COMMUTER GUIDE */}
      {workbenchTab === 'guide' && (
        <div className="metro-guide-wrapper">
          <div className="metro-guide-header">
            <span className="guide-eyebrow">COMMUTER TRANSIT HANDBOOK</span>
            <h3>Passenger Rules, Fare Policies &amp; Transit Guidelines</h3>
            <p className="guide-subtext">
              Comprehensive operational manual for commuters across Indian rapid rail networks, standardizing ticketing systems, baggage limits, women-only coach designations, and emergency protocols.
            </p>
          </div>

          <div className="metro-guide-grid">
            <div className="guide-card">
              <div className="guide-card-icon">💳</div>
              <h4>Ticketing Systems &amp; Mobility Passes</h4>
              <ul>
                <li><strong>National Common Mobility Card (NCMC):</strong> Interoperable contactless "One Nation One Card" on RuPay open loop standards. Operates across DMRC, BMRCL, Maha Metro, BEST, and suburban rail.</li>
                <li><strong>WhatsApp QR Ticketing:</strong> Available on official bots (+91 96508 55800 for Delhi, BMRCL bot for Bengaluru). Eliminates concourse queue times.</li>
                <li><strong>Smart Card Recharges:</strong> Provides 10% discount during standard hours and 20% discount during off-peak hours (06:00–08:00, 12:00–17:00, 21:00–23:00).</li>
                <li><strong>Tourist Passes:</strong> 1-day unlimited transit pass (₹200 including ₹50 refundable deposit) and 3-day unlimited pass (₹500).</li>
              </ul>
            </div>

            <div className="guide-card">
              <div className="guide-card-icon">👩</div>
              <h4>Women-Only Reserved Coaches</h4>
              <ul>
                <li><strong>Designated Location:</strong> The first coach in the direction of train travel is strictly reserved for women passengers across all broad and standard gauge lines.</li>
                <li><strong>Legal Penalties:</strong> Male commuters boarding the reserved coach are liable to a fine of ₹250 under Section 64 of the Metro Railways (Operations and Maintenance) Act, 2002.</li>
                <li><strong>Safety Surveillance:</strong> Continuous CCTV monitoring with direct live feeds to the Central Operation Control Centre (OCC).</li>
              </ul>
            </div>

            <div className="guide-card">
              <div className="guide-card-icon">🧳</div>
              <h4>Luggage &amp; Baggage Regulations</h4>
              <ul>
                <li><strong>Weight Allowance:</strong> Maximum 15 kg per commuter on standard rapid transit lines (Airport Express allows up to 30 kg checked luggage).</li>
                <li><strong>Dimensional Envelope:</strong> Baggage dimensions must not exceed 60 cm (length) × 45 cm (width) × 25 cm (height).</li>
                <li><strong>Prohibited Items:</strong> Dangerous flammable articles, sharp edged instruments, inflammable chemicals, and open food/beverages are strictly prohibited.</li>
              </ul>
            </div>

            <div className="guide-card">
              <div className="guide-card-icon">🚨</div>
              <h4>Platform Safety &amp; Emergency Systems</h4>
              <ul>
                <li><strong>Tactile Yellow Line:</strong> Commuters must stand behind the tactile yellow strip until the train comes to a complete halt and platform doors align.</li>
                <li><strong>Emergency Stop Plunger (ESP):</strong> Located on blue call posts at both platform ends. Can be actuated by any commuter to cut track traction in case of track falls.</li>
                <li><strong>Passenger Emergency Alarm (PEA):</strong> Red lever inside every coach allowing immediate 2-way audio communication with the train operator.</li>
                <li><strong>Medical &amp; Lost Property:</strong> Automated External Defibrillators (AEDs) and first aid available at all Station Control Rooms (SCR). Central lost property office at Kashmere Gate (DMRC).</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}