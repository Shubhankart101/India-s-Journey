import { useEffect, useMemo, useState } from 'react';
import metroData from '../data/metro-networks.json';
import './MetroAtlas.css';

// 17 Indian Metro Cities: Geographic ("Where It Actually Runs") & Schematic Transit Networks
export const CITY_LAYOUTS = {
  'delhi-ncr': {
    width: 720,
    height: 640,
    waterways: [
      {
        id: 'yamuna',
        name: 'River Yamuna (यमुना नदी)',
        path: 'M 470,10 Q 455,90 435,150 T 420,210 T 430,270 T 465,360 T 515,460 T 560,550 T 590,620',
        stroke: '#0284c7',
        width: 16,
        opacity: 0.65,
      },
      {
        id: 'najafgarh',
        name: 'Najafgarh Drain',
        path: 'M 50,420 Q 140,360 210,300 T 350,210 T 435,150',
        stroke: '#0369a1',
        width: 4,
        opacity: 0.45,
      },
    ],
    roads: [
      { id: 'ring-road', name: 'Ring Road (Mahatma Gandhi Marg)', path: 'M 270,210 C 390,200 425,245 410,345 C 390,430 250,425 205,330 Z', stroke: 'rgba(255,255,255,0.14)', width: 3.5 },
      { id: 'outer-ring', name: 'Outer Ring Road', path: 'M 210,140 C 460,120 510,220 490,400 C 450,510 180,500 130,320 Z', stroke: 'rgba(255,255,255,0.09)', width: 2.5, dash: '4,4' },
      { id: 'border-up', name: 'Delhi - Uttar Pradesh Border', path: 'M 500,80 L 480,220 L 455,360 L 550,500', stroke: '#f59e0b', width: 1.5, dash: '6,4', opacity: 0.45 },
      { id: 'border-haryana', name: 'Delhi - Haryana Border', path: 'M 90,120 L 80,260 L 150,490 L 270,580', stroke: '#f59e0b', width: 1.5, dash: '6,4', opacity: 0.45 },
    ],
    geoLines: [
      { id: 'red', name: 'Red Line (Line 1)', color: '#dc2626', path: 'M 110,185 L 230,185 Q 295,195 340,215 L 420,210 L 475,210 L 560,180 L 650,160', status: 'Operational' },
      { id: 'yellow', name: 'Yellow Line (Line 2)', color: '#eab308', path: 'M 370,50 L 370,130 Q 375,170 380,210 L 380,270 L 380,305 L 360,380 Q 335,460 290,530 L 250,580', status: 'Operational' },
      { id: 'blue', name: 'Blue Line (Line 3 & 4)', color: '#2563eb', path: 'M 100,450 Q 185,385 255,340 L 380,270 L 440,275 L 470,320 L 570,335 L 660,335', status: 'Operational' },
      { id: 'blue-branch', name: 'Blue Line Vaishali Branch', color: '#2563eb', path: 'M 440,275 L 500,245 L 580,240', status: 'Operational' },
      { id: 'green', name: 'Green Line (Line 5)', color: '#16a34a', path: 'M 60,250 L 180,250 Q 250,265 305,280 L 340,285', status: 'Operational' },
      { id: 'violet', name: 'Violet Line (Line 6)', color: '#7c3aed', path: 'M 380,210 L 420,240 L 420,325 Q 430,410 450,495 L 460,565', status: 'Operational' },
      { id: 'pink', name: 'Pink Line (Ring Line 7)', color: '#ec4899', path: 'M 310,135 Q 420,130 490,210 L 515,290 L 475,385 Q 415,450 350,450 L 245,435 Q 185,380 185,280 L 205,205 Q 250,145 310,135 Z', status: 'Operational Ring' },
      { id: 'magenta', name: 'Magenta Line (Line 8)', color: '#d946ef', path: 'M 150,370 Q 235,425 340,425 L 440,425 Q 495,390 535,365 L 570,335', status: 'Operational' },
      { id: 'orange', name: 'Airport Express (Orange)', color: '#ea580c', path: 'M 380,255 L 330,300 L 230,390 L 170,425 L 135,440', status: 'Operational' },
      { id: 'rapid', name: 'Rapid Metro Gurugram', color: '#64748b', path: 'M 290,530 L 315,510 L 340,530 L 335,570 L 295,575 L 290,530', status: 'Operational Loop' },
      { id: 'aqua', name: 'Noida Aqua Line', color: '#06b6d4', path: 'M 570,345 L 585,400 L 610,470 L 635,540 L 660,570', status: 'Operational' },
      { id: 'silver-p4', name: 'Phase 4 Golden/Silver Alignment', color: '#d97706', path: 'M 230,390 L 285,425 L 365,450 L 445,490', status: 'Under Construction (DMRC Phase 4)', dash: '5,5' },
      { id: 'rrts', name: 'Namo Bharat Regional Rapid Transit', color: '#991b1b', path: 'M 450,330 L 505,280 L 560,215 L 620,130 L 670,40', status: 'Semi-High Speed RRTS (160 km/h)' },
    ],
    stations: [
      { name: 'Kashmere Gate', hindi: 'कश्मीरी गेट', x: 380, y: 210, lines: ['Red Line (Line 1)', 'Yellow Line (Line 2)', 'Violet Line (Line 6)'], interchange: true, footfall: '350,000', lat: 28.6675, lng: 77.2285, connections: ['Rithala', 'Netaji Subhash Place', 'Welcome', 'Samaypur Badli', 'Azadpur', 'New Delhi Railway Station', 'Mandi House', 'Central Secretariat'] },
      { name: 'Rajiv Chowk (CP)', hindi: 'राजीव चौक', x: 380, y: 270, lines: ['Yellow Line (Line 2)', 'Blue Line (Line 3 & 4)'], interchange: true, footfall: '500,000', lat: 28.6328, lng: 77.2195, connections: ['New Delhi Railway Station', 'Central Secretariat', 'Janakpuri West', 'Mandi House'] },
      { name: 'New Delhi Railway Station', hindi: 'नई दिल्ली', x: 380, y: 245, lines: ['Yellow Line (Line 2)', 'Airport Express (Orange)'], interchange: true, footfall: '290,000', lat: 28.6431, lng: 77.2223, connections: ['Kashmere Gate', 'Rajiv Chowk (CP)', 'IGI Airport T3'] },
      { name: 'Central Secretariat', hindi: 'केंद्रीय सचिवालय', x: 380, y: 305, lines: ['Yellow Line (Line 2)', 'Violet Line (Line 6)'], interchange: true, footfall: '210,000', lat: 28.6146, lng: 77.2119, connections: ['Rajiv Chowk (CP)', 'Dilli Haat INA', 'Mandi House', 'Lajpat Nagar'] },
      { name: 'Mandi House', hindi: 'मंडी हाउस', x: 420, y: 270, lines: ['Blue Line (Line 3 & 4)', 'Violet Line (Line 6)'], interchange: true, footfall: '170,000', lat: 28.6258, lng: 77.2343, connections: ['Rajiv Chowk (CP)', 'Central Secretariat', 'Kashmere Gate', 'Mayur Vihar Phase 1', 'Anand Vihar ISBT'] },
      { name: 'Dilli Haat INA', hindi: 'दिल्ली हाट आईएनए', x: 370, y: 350, lines: ['Yellow Line (Line 2)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '160,000', lat: 28.5744, lng: 77.2096, connections: ['Central Secretariat', 'Hauz Khas', 'Lajpat Nagar', 'Netaji Subhash Place'] },
      { name: 'Hauz Khas', hindi: 'हौज़ खास', x: 360, y: 380, lines: ['Yellow Line (Line 2)', 'Magenta Line (Line 8)'], interchange: true, footfall: '280,000', lat: 28.5432, lng: 77.2066, connections: ['Dilli Haat INA', 'Sikanderpur', 'Janakpuri West', 'Kalkaji Mandir'] },
      { name: 'Lajpat Nagar', hindi: 'लाजपत नगर', x: 420, y: 355, lines: ['Violet Line (Line 6)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '190,000', lat: 28.5708, lng: 77.2378, connections: ['Central Secretariat', 'Kalkaji Mandir', 'Dilli Haat INA', 'Sarai Kale Khan'] },
      { name: 'Kalkaji Mandir', hindi: 'कालकाजी मंदिर', x: 440, y: 405, lines: ['Violet Line (Line 6)', 'Magenta Line (Line 8)'], interchange: true, footfall: '185,000', lat: 28.5492, lng: 77.2581, connections: ['Lajpat Nagar', 'Hauz Khas', 'Botanical Garden'] },
      { name: 'Botanical Garden', hindi: 'बॉटनिकल गार्डन', x: 570, y: 335, lines: ['Blue Line (Line 3 & 4)', 'Magenta Line (Line 8)'], interchange: true, footfall: '220,000', lat: 28.5642, lng: 77.3342, connections: ['Mayur Vihar Phase 1', 'Noida Electronic City', 'Kalkaji Mandir', 'Depot Greater Noida'] },
      { name: 'Mayur Vihar Phase 1', hindi: 'मयूर विहार फेस 1', x: 500, y: 320, lines: ['Blue Line (Line 3 & 4)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '145,000', lat: 28.6045, lng: 77.2945, connections: ['Mandi House', 'Botanical Garden', 'Anand Vihar ISBT', 'Sarai Kale Khan'] },
      { name: 'Anand Vihar ISBT', hindi: 'आनंद विहार', x: 540, y: 250, lines: ['Blue Line (Line 3 & 4)', 'Pink Line (Ring Line 7)', 'Namo Bharat RRTS'], interchange: true, footfall: '260,000', lat: 28.6469, lng: 77.3161, connections: ['Mandi House', 'Vaishali', 'Mayur Vihar Phase 1', 'Welcome', 'Sarai Kale Khan', 'Ghaziabad RRTS'] },
      { name: 'Sarai Kale Khan', hindi: 'सराय काले खां', x: 450, y: 330, lines: ['Pink Line (Ring Line 7)', 'Namo Bharat RRTS'], interchange: true, footfall: '180,000', lat: 28.5908, lng: 77.2569, connections: ['Mayur Vihar Phase 1', 'Lajpat Nagar', 'Anand Vihar ISBT'] },
      { name: 'Netaji Subhash Place', hindi: 'नेताजी सुभाष प्लेस', x: 230, y: 185, lines: ['Red Line (Line 1)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '175,000', lat: 28.6953, lng: 77.1528, connections: ['Rithala', 'Kashmere Gate', 'Azadpur', 'Dilli Haat INA'] },
      { name: 'Azadpur', hindi: 'आज़ादपुर', x: 310, y: 135, lines: ['Yellow Line (Line 2)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '155,000', lat: 28.7067, lng: 77.1783, connections: ['Samaypur Badli', 'Kashmere Gate', 'Netaji Subhash Place', 'Welcome'] },
      { name: 'Welcome', hindi: 'वेलकम', x: 475, y: 210, lines: ['Red Line (Line 1)', 'Pink Line (Ring Line 7)'], interchange: true, footfall: '160,000', lat: 28.6722, lng: 77.2778, connections: ['Kashmere Gate', 'Shaheed Sthal (Ghaziabad)', 'Azadpur', 'Anand Vihar ISBT'] },
      { name: 'Janakpuri West', hindi: 'जनकपुरी पश्चिम', x: 220, y: 340, lines: ['Blue Line (Line 3 & 4)', 'Magenta Line (Line 8)'], interchange: true, footfall: '150,000', lat: 28.6294, lng: 77.0778, connections: ['Dwarka Sector 21', 'Rajiv Chowk (CP)', 'Hauz Khas'] },
      { name: 'Dwarka Sector 21', hindi: 'द्वारका सेक्टर 21', x: 100, y: 450, lines: ['Blue Line (Line 3 & 4)', 'Airport Express (Orange)'], interchange: true, footfall: '125,000', lat: 28.5522, lng: 77.0583, connections: ['Janakpuri West', 'IGI Airport T3'] },
      { name: 'IGI Airport T3', hindi: 'आईजीआई एयरपोर्ट टी3', x: 170, y: 425, lines: ['Airport Express (Orange)'], interchange: false, footfall: '75,000', lat: 28.5562, lng: 77.0863, connections: ['New Delhi Railway Station', 'Dwarka Sector 21'] },
      { name: 'Sikanderpur', hindi: 'सिकंदरपुर', x: 290, y: 530, lines: ['Yellow Line (Line 2)', 'Rapid Metro Gurugram'], interchange: true, footfall: '130,000', lat: 28.4819, lng: 77.0928, connections: ['Hauz Khas', 'Millennium City Centre Gurugram', 'Cyber City Gurugram'] },
      { name: 'Millennium City Centre Gurugram', hindi: 'मिलेनियम सिटी सेंटर', x: 250, y: 580, lines: ['Yellow Line (Line 2)'], interchange: false, footfall: '140,000', lat: 28.4593, lng: 77.0725, connections: ['Sikanderpur'] },
      { name: 'Rithala', hindi: 'रिठाला', x: 110, y: 185, lines: ['Red Line (Line 1)'], interchange: false, footfall: '90,000', lat: 28.7206, lng: 77.1072, connections: ['Netaji Subhash Place'] },
      { name: 'Shaheed Sthal (Ghaziabad)', hindi: 'शहीद स्थल गाज़ियाबाद', x: 650, y: 160, lines: ['Red Line (Line 1)'], interchange: false, footfall: '105,000', lat: 28.6719, lng: 77.4189, connections: ['Welcome'] },
      { name: 'Samaypur Badli', hindi: 'समयपुर बादली', x: 370, y: 50, lines: ['Yellow Line (Line 2)'], interchange: false, footfall: '85,000', lat: 28.7456, lng: 77.1358, connections: ['Azadpur'] },
      { name: 'Noida Electronic City', hindi: 'नोएडा इलेक्ट्रॉनिक सिटी', x: 660, y: 335, lines: ['Blue Line (Line 3 & 4)'], interchange: false, footfall: '110,000', lat: 28.6272, lng: 77.3725, connections: ['Botanical Garden'] },
      { name: 'Vaishali', hindi: 'वैशाली', x: 580, y: 240, lines: ['Blue Line (Line 3 & 4)'], interchange: false, footfall: '80,000', lat: 28.6497, lng: 77.3397, connections: ['Anand Vihar ISBT'] },
      { name: 'Cyber City Gurugram', hindi: 'साइबर सिटी', x: 335, y: 570, lines: ['Rapid Metro Gurugram'], interchange: false, footfall: '95,000', lat: 28.4958, lng: 77.0886, connections: ['Sikanderpur'] },
      { name: 'Depot Greater Noida', hindi: 'डिपो स्टेशन ग्रेटर नोएडा', x: 660, y: 570, lines: ['Noida Aqua Line'], interchange: false, footfall: '25,000', lat: 28.4358, lng: 77.5269, connections: ['Botanical Garden'] },
      { name: 'Ghaziabad RRTS', hindi: 'गाज़ियाबाद नमो भारत', x: 620, y: 130, lines: ['Namo Bharat RRTS'], interchange: false, footfall: '65,000', lat: 28.6658, lng: 77.4372, connections: ['Anand Vihar ISBT'] },
    ],
  },
  'mumbai': {
    width: 620,
    height: 560,
    waterways: [
      { id: 'arabian-sea', name: 'Arabian Sea Coast', path: 'M 110,20 Q 95,200 130,380 T 170,540', stroke: '#0284c7', width: 22, opacity: 0.5 },
      { id: 'thane-creek', name: 'Thane Creek Basin', path: 'M 510,40 Q 480,180 450,320 T 400,500', stroke: '#0284c7', width: 15, opacity: 0.5 },
    ],
    roads: [
      { id: 'weh', name: 'Western Express Highway (WEH)', path: 'M 280,40 L 275,230 L 270,330 L 230,480', stroke: 'rgba(255,255,255,0.12)', width: 3 },
    ],
    geoLines: [
      { id: 'line1', name: 'Line 1 (Blue Corridor)', color: '#0284c7', path: 'M 140,230 L 275,230 L 450,230', status: 'Operational' },
      { id: 'line2a', name: 'Line 2A (Yellow Corridor)', color: '#facc15', path: 'M 220,50 L 175,140 L 140,230 L 150,290', status: 'Operational' },
      { id: 'line7', name: 'Line 7 (Red Corridor)', color: '#ef4444', path: 'M 285,50 L 278,140 L 275,230 L 270,290', status: 'Operational' },
      { id: 'line3', name: 'Line 3 (Aqua Underground)', color: '#06b6d4', path: 'M 285,160 L 270,230 L 275,320 L 250,420 L 210,520', status: 'Operational' },
    ],
    stations: [
      { name: 'Versova', hindi: 'वर्सोवा', x: 140, y: 230, lines: ['Line 1 (Blue Corridor)'], interchange: false, footfall: '65,000', lat: 19.1311, lng: 72.8197, connections: ['DN Nagar'] },
      { name: 'DN Nagar', hindi: 'डी एन नगर', x: 190, y: 230, lines: ['Line 1 (Blue Corridor)', 'Line 2A (Yellow Corridor)'], interchange: true, footfall: '140,000', lat: 19.1306, lng: 72.8319, connections: ['Versova', 'Andheri / WEH', 'Dahisar West'] },
      { name: 'Andheri / WEH', hindi: 'अंधेरी वेस्टर्न एक्सप्रेस', x: 275, y: 230, lines: ['Line 1 (Blue Corridor)', 'Line 7 (Red Corridor)'], interchange: true, footfall: '240,000', lat: 19.1197, lng: 72.8464, connections: ['DN Nagar', 'Ghatkopar', 'Dahisar East', 'CSMIA Terminal 2'] },
      { name: 'Ghatkopar', hindi: 'घाटकोपर', x: 450, y: 230, lines: ['Line 1 (Blue Corridor)'], interchange: true, footfall: '185,000', lat: 19.0864, lng: 72.9081, connections: ['Andheri / WEH'] },
      { name: 'Dahisar East', hindi: 'दहिसर पूर्व', x: 285, y: 50, lines: ['Line 7 (Red Corridor)'], interchange: false, footfall: '70,000', lat: 19.2567, lng: 72.8606, connections: ['Andheri / WEH'] },
      { name: 'Dahisar West', hindi: 'दहिसर पश्चिम', x: 220, y: 50, lines: ['Line 2A (Yellow Corridor)'], interchange: false, footfall: '65,000', lat: 19.2558, lng: 72.8533, connections: ['DN Nagar'] },
      { name: 'CSMIA Terminal 2', hindi: 'छत्रपति शिवाजी एयरपोर्ट', x: 285, y: 160, lines: ['Line 3 (Aqua Underground)'], interchange: true, footfall: '80,000', lat: 19.0974, lng: 72.8744, connections: ['Andheri / WEH', 'Bandra-Kurla Complex (BKC)'] },
      { name: 'Bandra-Kurla Complex (BKC)', hindi: 'बीकेसी', x: 275, y: 320, lines: ['Line 3 (Aqua Underground)'], interchange: true, footfall: '110,000', lat: 19.0667, lng: 72.8667, connections: ['CSMIA Terminal 2', 'Cuffe Parade'] },
      { name: 'Cuffe Parade', hindi: 'कफ परेड', x: 210, y: 520, lines: ['Line 3 (Aqua Underground)'], interchange: false, footfall: '45,000', lat: 18.9167, lng: 72.8167, connections: ['Bandra-Kurla Complex (BKC)'] },
    ],
  },
  'bengaluru': {
    width: 620,
    height: 540,
    waterways: [],
    roads: [
      { id: 'orr-blr', name: 'Outer Ring Road (ORR)', path: 'M 110,270 C 130,460 470,460 500,250 C 480,80 150,80 110,270 Z', stroke: 'rgba(255,255,255,0.08)', width: 2.5, dash: '4,4' },
    ],
    geoLines: [
      { id: 'purple', name: 'Purple Line (East-West)', color: '#9333ea', path: 'M 70,380 L 170,320 L 280,260 L 400,260 L 550,200', status: 'Operational' },
      { id: 'green', name: 'Green Line (North-South)', color: '#15803d', path: 'M 200,70 L 240,160 L 280,260 L 300,370 L 320,490', status: 'Operational' },
      { id: 'yellow', name: 'Yellow Line (Electronic City)', color: '#eab308', path: 'M 280,370 L 350,400 L 430,450 L 520,500', status: 'Operational' },
    ],
    stations: [
      { name: 'Kempegowda Majestic', hindi: 'ಮೆಜೆಸ್ಟಿಕ್', x: 280, y: 260, lines: ['Purple Line (East-West)', 'Green Line (North-South)'], interchange: true, footfall: '240,000', lat: 12.9757, lng: 77.5728, connections: ['MG Road', 'Mysuru Road', 'Yeshwanthpur', 'Silk Board'] },
      { name: 'MG Road', hindi: 'ಎಂ ಜಿ ರಸ್ತೆ', x: 340, y: 260, lines: ['Purple Line (East-West)'], interchange: false, footfall: '95,000', lat: 12.9756, lng: 77.6066, connections: ['Kempegowda Majestic', 'Indiranagar'] },
      { name: 'Indiranagar', hindi: 'ಇಂದಿರಾನಗರ', x: 410, y: 250, lines: ['Purple Line (East-West)'], interchange: false, footfall: '85,000', lat: 12.9783, lng: 77.6386, connections: ['MG Road', 'Whitefield (Kadugodi)'] },
      { name: 'Whitefield (Kadugodi)', hindi: 'ವೈಟ್‌ಫೀಲ್ಡ್', x: 550, y: 200, lines: ['Purple Line (East-West)'], interchange: false, footfall: '80,000', lat: 12.9961, lng: 77.7611, connections: ['Indiranagar'] },
      { name: 'Mysuru Road', hindi: 'ಮೈಸೂರು ರಸ್ತೆ', x: 170, y: 320, lines: ['Purple Line (East-West)'], interchange: false, footfall: '60,000', lat: 12.9469, lng: 77.5278, connections: ['Kempegowda Majestic'] },
      { name: 'Yeshwanthpur', hindi: 'ಯಶವಂತಪುರ', x: 240, y: 160, lines: ['Green Line (North-South)'], interchange: true, footfall: '90,000', lat: 13.0233, lng: 77.5500, connections: ['Kempegowda Majestic'] },
      { name: 'Silk Board', hindi: 'ಸಿಲ್ಕ್ ಬೋರ್ಡ್', x: 350, y: 400, lines: ['Yellow Line (Electronic City)'], interchange: true, footfall: '110,000', lat: 12.9172, lng: 77.6228, connections: ['Kempegowda Majestic', 'Electronic City'] },
      { name: 'Electronic City', hindi: 'ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಸಿಟಿ', x: 480, y: 480, lines: ['Yellow Line (Electronic City)'], interchange: false, footfall: '85,000', lat: 12.8452, lng: 77.6602, connections: ['Silk Board'] },
    ],
  },
  'kolkata': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'hooghly', name: 'River Hooghly (South Asia’s Deepest Tunnel)', path: 'M 250,30 Q 260,150 270,270 T 245,510', stroke: '#0284c7', width: 22, opacity: 0.7 },
    ],
    roads: [],
    geoLines: [
      { id: 'blue', name: 'Blue Line (Line 1 Historic)', color: '#2563eb', path: 'M 320,50 L 320,180 L 320,270 L 340,380 L 370,500', status: 'Operational' },
      { id: 'green', name: 'Green Line (Line 2 Underwater)', color: '#16a34a', path: 'M 150,270 L 230,270 L 320,270 L 440,270 L 540,240', status: 'Operational (Underwater)' },
      { id: 'orange', name: 'Orange Line (Line 6 Airport)', color: '#ea580c', path: 'M 370,500 L 470,440 L 500,330 L 520,130', status: 'Operational / Ext.' },
    ],
    stations: [
      { name: 'Howrah Station (33m Deep Underwater)', hindi: 'হাওড়া স্টেশন', x: 230, y: 270, lines: ['Green Line (Line 2 Underwater)'], interchange: true, footfall: '220,000', lat: 22.5833, lng: 88.3425, connections: ['Esplanade'] },
      { name: 'Esplanade', hindi: 'এসপ্ল্যানেড', x: 320, y: 270, lines: ['Blue Line (Line 1 Historic)', 'Green Line (Line 2 Underwater)'], interchange: true, footfall: '260,000', lat: 22.5647, lng: 88.3516, connections: ['Howrah Station (33m Deep Underwater)', 'Sealdah', 'Dum Dum', 'Park Street'] },
      { name: 'Sealdah', hindi: 'শিয়ালদহ', x: 380, y: 270, lines: ['Green Line (Line 2 Underwater)'], interchange: true, footfall: '190,000', lat: 22.5683, lng: 88.3719, connections: ['Esplanade', 'Salt Lake Sector V'] },
      { name: 'Salt Lake Sector V', hindi: 'সল্টলেক সেক্টর ৫', x: 540, y: 240, lines: ['Green Line (Line 2 Underwater)'], interchange: false, footfall: '110,000', lat: 22.5804, lng: 88.4372, connections: ['Sealdah'] },
      { name: 'Dum Dum', hindi: 'দমদম', x: 320, y: 120, lines: ['Blue Line (Line 1 Historic)'], interchange: true, footfall: '175,000', lat: 22.6219, lng: 88.3936, connections: ['Esplanade'] },
      { name: 'Park Street', hindi: 'পার্ক স্ট্রিট', x: 320, y: 320, lines: ['Blue Line (Line 1 Historic)'], interchange: false, footfall: '130,000', lat: 22.5511, lng: 88.3522, connections: ['Esplanade', 'Kavi Subhash'] },
      { name: 'Kavi Subhash', hindi: 'কবি সুভাষ', x: 370, y: 500, lines: ['Blue Line (Line 1 Historic)', 'Orange Line (Line 6 Airport)'], interchange: true, footfall: '140,000', lat: 22.4719, lng: 88.3967, connections: ['Park Street'] },
    ],
  },
  'chennai': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'bay-of-bengal', name: 'Bay of Bengal Coastline', path: 'M 500,30 Q 480,220 450,510', stroke: '#0284c7', width: 18, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'blue', name: 'Blue Line (Corridor 1)', color: '#1d4ed8', path: 'M 410,60 L 360,160 L 320,250 L 240,360 L 150,470', status: 'Operational' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#15803d', path: 'M 360,160 L 270,200 L 210,270 L 220,380', status: 'Operational' },
    ],
    stations: [
      { name: 'Chennai Central (MGR)', hindi: 'சென்னை சென்ट्रல்', x: 360, y: 160, lines: ['Blue Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '110,000', lat: 13.0827, lng: 80.2707, connections: ['Alandur', 'Koyambedu Wholesale Hub'] },
      { name: 'Alandur', hindi: 'ஆலந்தூர்', x: 220, y: 380, lines: ['Blue Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '65,000', lat: 13.0039, lng: 80.2014, connections: ['Chennai Central (MGR)', 'Chennai Airport', 'Koyambedu Wholesale Hub'] },
      { name: 'Chennai Airport', hindi: 'சென்னை விமான நிலையம்', x: 150, y: 470, lines: ['Blue Line (Corridor 1)'], interchange: false, footfall: '55,000', lat: 12.9806, lng: 80.1636, connections: ['Alandur'] },
      { name: 'Koyambedu Wholesale Hub', hindi: 'கோயம்பேடு', x: 210, y: 270, lines: ['Green Line (Corridor 2)'], interchange: true, footfall: '70,000', lat: 13.0733, lng: 80.1942, connections: ['Chennai Central (MGR)', 'Alandur'] },
    ],
  },
  'hyderabad': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'musi', name: 'River Musi', path: 'M 50,350 Q 250,345 570,355', stroke: '#0284c7', width: 6, opacity: 0.4 },
    ],
    roads: [],
    geoLines: [
      { id: 'red', name: 'Red Line (Corridor 1)', color: '#dc2626', path: 'M 110,80 L 260,220 L 340,320 L 490,450', status: 'Operational' },
      { id: 'blue', name: 'Blue Line (Corridor 3)', color: '#2563eb', path: 'M 90,320 L 260,220 L 410,190 L 530,230', status: 'Operational' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#16a34a', path: 'M 350,110 L 350,240 L 340,320', status: 'Operational' },
    ],
    stations: [
      { name: 'Ameerpet Hub', hindi: 'అమీర్‌పేట్', x: 260, y: 220, lines: ['Red Line (Corridor 1)', 'Blue Line (Corridor 3)'], interchange: true, footfall: '140,000', lat: 17.4375, lng: 78.4483, connections: ['Raidurg (HITEC City)', 'MGBS Central', 'Miyapur Depot', 'Secunderabad East'] },
      { name: 'Raidurg (HITEC City)', hindi: 'రాయదుర్గం', x: 90, y: 320, lines: ['Blue Line (Corridor 3)'], interchange: false, footfall: '95,000', lat: 17.4428, lng: 78.3772, connections: ['Ameerpet Hub'] },
      { name: 'MGBS Central', hindi: 'ఎంజీబీఎస్', x: 340, y: 320, lines: ['Red Line (Corridor 1)', 'Green Line (Corridor 2)'], interchange: true, footfall: '85,000', lat: 17.3789, lng: 78.4811, connections: ['Ameerpet Hub', 'Secunderabad East', 'LB Nagar'] },
      { name: 'Secunderabad East', hindi: 'సికింద్రాబాద్ ఈస్ట్', x: 410, y: 190, lines: ['Blue Line (Corridor 3)', 'Green Line (Corridor 2)'], interchange: true, footfall: '90,000', lat: 17.4339, lng: 78.5042, connections: ['Ameerpet Hub', 'MGBS Central'] },
      { name: 'Miyapur Depot', hindi: 'మియాపూర్', x: 110, y: 80, lines: ['Red Line (Corridor 1)'], interchange: false, footfall: '55,000', lat: 17.4967, lng: 78.3614, connections: ['Ameerpet Hub'] },
      { name: 'LB Nagar', hindi: 'ఎల్బీ నగర్', x: 490, y: 450, lines: ['Red Line (Corridor 1)'], interchange: false, footfall: '65,000', lat: 17.3486, lng: 78.5519, connections: ['MGBS Central'] },
    ],
  },
  'kochi': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'vembanad', name: 'Vembanad Backwaters & Coast', path: 'M 210,40 Q 190,260 220,500', stroke: '#0284c7', width: 32, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'rail', name: 'Kochi Metro Rail (Aluva - Thripunithura)', color: '#0284c7', path: 'M 390,60 L 350,180 L 330,300 L 380,450', status: 'Operational' },
      { id: 'water-1', name: 'Water Metro (High Court - Vypin)', color: '#06b6d4', path: 'M 230,270 L 150,300', status: 'Electric Ferry Route', dash: '5,4' },
      { id: 'water-2', name: 'Water Metro (High Court - Fort Kochi)', color: '#06b6d4', path: 'M 230,270 L 120,390', status: 'Electric Ferry Route', dash: '5,4' },
    ],
    stations: [
      { name: 'High Court Water Terminal', hindi: 'ഹൈക്കോടതി', x: 230, y: 270, lines: ['Kochi Water Metro Hub'], interchange: true, footfall: '24,000', lat: 9.9814, lng: 76.2753, connections: ['MG Road Commercial', 'Fort Kochi Heritage Pier', 'Vypin Island Jetty'] },
      { name: 'Aluva North Terminus', hindi: 'ആലുവ', x: 390, y: 60, lines: ['Kochi Metro Rail'], interchange: false, footfall: '40,000', lat: 10.1102, lng: 76.3533, connections: ['MG Road Commercial'] },
      { name: 'MG Road Commercial', hindi: 'എം ജി റോഡ്', x: 330, y: 300, lines: ['Kochi Metro Rail'], interchange: true, footfall: '45,000', lat: 9.9722, lng: 76.2847, connections: ['Aluva North Terminus', 'High Court Water Terminal', 'Thripunithura Southern Depot'] },
      { name: 'Thripunithura Southern Depot', hindi: 'തൃപ്പൂണിത്തുറ', x: 380, y: 450, lines: ['Kochi Metro Rail'], interchange: false, footfall: '30,000', lat: 9.9489, lng: 76.3475, connections: ['MG Road Commercial'] },
      { name: 'Fort Kochi Heritage Pier', hindi: 'ഫോർട്ട് കൊച്ചി', x: 120, y: 390, lines: ['Kochi Water Metro'], interchange: false, footfall: '20,000', lat: 9.9658, lng: 76.2425, connections: ['High Court Water Terminal'] },
      { name: 'Vypin Island Jetty', hindi: 'വൈപ്പിൻ', x: 150, y: 300, lines: ['Kochi Water Metro'], interchange: false, footfall: '18,000', lat: 9.9922, lng: 76.2394, connections: ['High Court Water Terminal'] },
    ],
  },
  'ahmedabad': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'sabarmati', name: 'River Sabarmati', path: 'M 310,30 Q 315,250 300,500', stroke: '#0284c7', width: 14, opacity: 0.55 },
    ],
    roads: [],
    geoLines: [
      { id: 'north-south', name: 'North-South Corridor (APMC - Motera)', color: '#dc2626', path: 'M 350,60 L 340,190 L 320,260 L 270,370 L 260,480', status: 'Operational' },
      { id: 'east-west', name: 'East-West Corridor (Thaltej - Vastral)', color: '#2563eb', path: 'M 80,260 L 210,260 L 320,260 L 450,260 L 550,280', status: 'Operational' },
    ],
    stations: [
      { name: 'Old High Court Interchange', hindi: 'જૂની હાઈકોર્ટ', x: 320, y: 260, lines: ['North-South Corridor', 'East-West Corridor'], interchange: true, footfall: '70,000', lat: 23.0375, lng: 72.5714, connections: ['Motera Narendra Modi Stadium', 'APMC Vasna', 'Thaltej Gam', 'Kalupur Railway Junction'] },
      { name: 'Motera Narendra Modi Stadium', hindi: 'મોટેરા સ્ટેડિયમ', x: 350, y: 60, lines: ['North-South Corridor'], interchange: false, footfall: '45,000', lat: 23.0919, lng: 72.5975, connections: ['Old High Court Interchange'] },
      { name: 'APMC Vasna', hindi: 'એપીએમસી', x: 260, y: 480, lines: ['North-South Corridor'], interchange: false, footfall: '35,000', lat: 22.9989, lng: 72.5458, connections: ['Old High Court Interchange'] },
      { name: 'Thaltej Gam', hindi: 'થલતેજ ગામ', x: 80, y: 260, lines: ['East-West Corridor'], interchange: false, footfall: '30,000', lat: 23.0514, lng: 72.5028, connections: ['Old High Court Interchange'] },
      { name: 'Kalupur Railway Junction', hindi: 'કાલુપુર રેલવે', x: 450, y: 260, lines: ['East-West Corridor'], interchange: true, footfall: '55,000', lat: 23.0236, lng: 72.6006, connections: ['Old High Court Interchange'] },
    ],
  },
  'pune': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'mula-mutha', name: 'Mula-Mutha Confluence', path: 'M 70,250 Q 240,240 340,270 T 550,260', stroke: '#0284c7', width: 10, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'purple', name: 'Purple Line (PCMC - Swargate)', color: '#9333ea', path: 'M 260,50 L 270,180 L 290,260 L 300,370 L 310,480', status: 'Operational' },
      { id: 'aqua', name: 'Aqua Line (Vanaz - Ramwadi)', color: '#06b6d4', path: 'M 90,340 L 200,300 L 290,260 L 430,220 L 540,170', status: 'Operational' },
    ],
    stations: [
      { name: 'Civil Court Interchange', hindi: 'सिव्हिल कोर्ट', x: 290, y: 260, lines: ['Purple Line (PCMC - Swargate)', 'Aqua Line (Vanaz - Ramwadi)'], interchange: true, footfall: '75,000', lat: 18.5289, lng: 73.8567, connections: ['PCMC Bhavan', 'Swargate Multimodal', 'Vanaz Western Depot', 'Ramwadi IT Corridor'] },
      { name: 'PCMC Bhavan', hindi: 'पिंपरी चिंचवड', x: 260, y: 50, lines: ['Purple Line (PCMC - Swargate)'], interchange: false, footfall: '40,000', lat: 18.6278, lng: 73.8131, connections: ['Civil Court Interchange'] },
      { name: 'Swargate Multimodal', hindi: 'स्वारगेट', x: 310, y: 480, lines: ['Purple Line (PCMC - Swargate)'], interchange: true, footfall: '60,000', lat: 18.5019, lng: 73.8586, connections: ['Civil Court Interchange'] },
      { name: 'Vanaz Western Depot', hindi: 'वनाझ', x: 90, y: 340, lines: ['Aqua Line (Vanaz - Ramwadi)'], interchange: false, footfall: '30,000', lat: 18.5056, lng: 73.8058, connections: ['Civil Court Interchange'] },
      { name: 'Ramwadi IT Corridor', hindi: 'रामवाडी', x: 540, y: 170, lines: ['Aqua Line (Vanaz - Ramwadi)'], interchange: false, footfall: '45,000', lat: 18.5528, lng: 73.9056, connections: ['Civil Court Interchange'] },
    ],
  },
  'lucknow': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'gomti', name: 'River Gomti', path: 'M 110,200 Q 310,190 530,250', stroke: '#0284c7', width: 10, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'red', name: 'Red Line (CCS Airport - Munshi Pulia)', color: '#dc2626', path: 'M 170,480 L 240,390 L 300,290 L 340,200 L 450,120 L 520,80', status: 'Operational' },
    ],
    stations: [
      { name: 'CCS Airport Terminal', hindi: 'चौधरी चरण सिंह एयरपोर्ट', x: 170, y: 480, lines: ['Red Line (North-South)'], interchange: false, footfall: '22,000', lat: 26.7606, lng: 80.8893, connections: ['Charbagh Railway Hub'] },
      { name: 'Charbagh Railway Hub', hindi: 'चारबाग रेलवे स्टेशन', x: 300, y: 290, lines: ['Red Line (North-South)'], interchange: true, footfall: '35,000', lat: 26.8322, lng: 80.9178, connections: ['CCS Airport Terminal', 'Hazratganj Heritage'] },
      { name: 'Hazratganj Heritage', hindi: 'हज़रतगंज', x: 340, y: 200, lines: ['Red Line (North-South)'], interchange: false, footfall: '20,000', lat: 26.8528, lng: 80.9427, connections: ['Charbagh Railway Hub', 'Munshi Pulia Terminus'] },
      { name: 'Munshi Pulia Terminus', hindi: 'मुंशी पुलिया', x: 520, y: 80, lines: ['Red Line (North-South)'], interchange: false, footfall: '18,000', lat: 26.8863, lng: 80.9936, connections: ['Hazratganj Heritage'] },
    ],
  },
  'kanpur': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'ganges-kanpur', name: 'River Ganga', path: 'M 90,100 Q 330,120 550,160', stroke: '#0284c7', width: 14, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'orange', name: 'Orange Line (IIT Kanpur - Naubasta)', color: '#ea580c', path: 'M 110,180 L 230,240 L 340,300 L 430,380 L 500,470', status: 'Operational / Ext.' },
    ],
    stations: [
      { name: 'IIT Kanpur Gateway', hindi: 'आईआईटी कानपुर', x: 110, y: 180, lines: ['Orange Line (Corridor 1)'], interchange: false, footfall: '15,000', lat: 26.5123, lng: 80.2329, connections: ['Motijheel Civic Core'] },
      { name: 'Motijheel Civic Core', hindi: 'मोतीझील', x: 340, y: 300, lines: ['Orange Line (Corridor 1)'], interchange: false, footfall: '18,000', lat: 26.4789, lng: 80.3168, connections: ['IIT Kanpur Gateway', 'Kanpur Central Railway Terminal'] },
      { name: 'Kanpur Central Railway Terminal', hindi: 'कानपुर सेंट्रल', x: 430, y: 380, lines: ['Orange Line (Corridor 1)'], interchange: true, footfall: '28,000', lat: 26.4542, lng: 80.3508, connections: ['Motijheel Civic Core'] },
    ],
  },
  'agra': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'yamuna-agra', name: 'River Yamuna (Taj Trapezium)', path: 'M 160,80 Q 290,240 460,290 T 550,470', stroke: '#0284c7', width: 14, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'yellow', name: 'Yellow Line (Taj East Gate - Sikandra)', color: '#eab308', path: 'M 490,340 L 410,290 L 340,230 L 250,170 L 150,110', status: 'Operational Priority' },
    ],
    stations: [
      { name: 'Taj East Gate (UNESCO Precinct)', hindi: 'ताज ईस्ट गेट', x: 490, y: 340, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '18,000', lat: 27.1712, lng: 78.0560, connections: ['Agra Fort Citadel'] },
      { name: 'Agra Fort Citadel', hindi: 'आगरा किला', x: 340, y: 230, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '15,000', lat: 27.1795, lng: 78.0211, connections: ['Taj East Gate (UNESCO Precinct)', 'Mankameshwar Mandir'] },
      { name: 'Mankameshwar Mandir', hindi: 'मनकामेश्वर मंदिर', x: 250, y: 170, lines: ['Yellow Line (Priority)'], interchange: false, footfall: '12,000', lat: 27.1852, lng: 78.0163, connections: ['Agra Fort Citadel'] },
    ],
  },
  'jaipur': {
    width: 620,
    height: 540,
    waterways: [],
    roads: [],
    geoLines: [
      { id: 'pink', name: 'Pink Line (Mansarovar - Badi Chaupar)', color: '#ec4899', path: 'M 100,450 L 190,370 L 280,290 L 380,220 L 500,180', status: 'Operational' },
    ],
    stations: [
      { name: 'Mansarovar Western Depot', hindi: 'मानसरोवर', x: 100, y: 450, lines: ['Pink Line (Phase 1)'], interchange: false, footfall: '14,000', lat: 26.8642, lng: 75.7602, connections: ['Jaipur Junction IR'] },
      { name: 'Jaipur Junction IR', hindi: 'जयपुर जंक्शन', x: 280, y: 290, lines: ['Pink Line (Phase 1)'], interchange: true, footfall: '22,000', lat: 26.9205, lng: 75.7876, connections: ['Mansarovar Western Depot', 'Badi Chaupar Hawa Mahal Core'] },
      { name: 'Badi Chaupar Hawa Mahal Core', hindi: 'बड़ी चौपड़', x: 500, y: 180, lines: ['Pink Line (Phase 1)'], interchange: false, footfall: '18,000', lat: 26.9238, lng: 75.8267, connections: ['Jaipur Junction IR'] },
    ],
  },
  'nagpur': {
    width: 620,
    height: 540,
    waterways: [],
    roads: [],
    geoLines: [
      { id: 'orange', name: 'Orange Line (Automotive Sq - Khapri)', color: '#ea580c', path: 'M 300,70 L 300,210 L 300,270 L 300,400 L 300,490', status: 'Operational' },
      { id: 'aqua', name: 'Aqua Line (Prajapati - Lokmanya)', color: '#06b6d4', path: 'M 90,270 L 200,270 L 300,270 L 430,270 L 530,270', status: 'Operational' },
    ],
    stations: [
      { name: 'Sitabuldi Central Atrium', hindi: 'सीताबर्डी', x: 300, y: 270, lines: ['Orange Line (North-South)', 'Aqua Line (East-West)'], interchange: true, footfall: '40,000', lat: 21.1458, lng: 79.0882, connections: ['Khapri Solar Depot', 'Prajapati Nagar East'] },
      { name: 'Khapri Solar Depot', hindi: 'खापरी', x: 300, y: 490, lines: ['Orange Line (North-South)'], interchange: false, footfall: '12,000', lat: 21.0583, lng: 79.0528, connections: ['Sitabuldi Central Atrium'] },
      { name: 'Prajapati Nagar East', hindi: 'प्रजापती नगर', x: 530, y: 270, lines: ['Aqua Line (East-West)'], interchange: false, footfall: '15,000', lat: 21.1642, lng: 79.1558, connections: ['Sitabuldi Central Atrium'] },
    ],
  },
  'noida': {
    width: 620,
    height: 540,
    waterways: [],
    roads: [
      { id: 'noida-expressway', name: 'Noida-Greater Noida Expressway', path: 'M 200,90 L 290,240 L 420,390 L 520,490', stroke: 'rgba(255,255,255,0.1)', width: 3 },
    ],
    geoLines: [
      { id: 'aqua', name: 'Aqua Line Corridor', color: '#06b6d4', path: 'M 190,80 L 230,170 L 300,270 L 390,370 L 470,440 L 530,490', status: 'Operational' },
    ],
    stations: [
      { name: 'Sector 51 (Walkway to Blue Line)', hindi: 'सेक्टर 51', x: 190, y: 80, lines: ['Aqua Line'], interchange: true, footfall: '26,000', lat: 28.5794, lng: 77.3689, connections: ['NSEZ Export Zone'] },
      { name: 'NSEZ Export Zone', hindi: 'एनएसईजेड', x: 300, y: 270, lines: ['Aqua Line'], interchange: false, footfall: '16,000', lat: 28.5292, lng: 77.4098, connections: ['Sector 51 (Walkway to Blue Line)', 'Pari Chowk Commercial Hub'] },
      { name: 'Pari Chowk Commercial Hub', hindi: 'परी चौक', x: 470, y: 440, lines: ['Aqua Line'], interchange: false, footfall: '18,000', lat: 28.4631, lng: 77.5122, connections: ['NSEZ Export Zone', 'Depot Greater Noida'] },
      { name: 'Depot Greater Noida', hindi: 'डिपो स्टेशन', x: 530, y: 490, lines: ['Aqua Line'], interchange: false, footfall: '10,000', lat: 28.4358, lng: 77.5269, connections: ['Pari Chowk Commercial Hub'] },
    ],
  },
  'navi-mumbai': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'panvel-creek', name: 'Panvel Creek Inlet', path: 'M 130,470 Q 290,450 460,480', stroke: '#0284c7', width: 14, opacity: 0.5 },
    ],
    roads: [],
    geoLines: [
      { id: 'line1', name: 'Line 1 (CBD Belapur - Pendhar)', color: '#3b82f6', path: 'M 150,440 L 220,350 L 300,260 L 380,180 L 470,120', status: 'Operational' },
    ],
    stations: [
      { name: 'CBD Belapur IR Hub', hindi: 'सीबीडी बेलापूर', x: 150, y: 440, lines: ['Line 1 (Phase 1)'], interchange: true, footfall: '15,000', lat: 19.0189, lng: 73.0389, connections: ['Kharghar Sector 14'] },
      { name: 'Kharghar Sector 14', hindi: 'खारघर सेक्टर 14', x: 300, y: 260, lines: ['Line 1 (Phase 1)'], interchange: false, footfall: '9,000', lat: 19.0433, lng: 73.0722, connections: ['CBD Belapur IR Hub', 'Pendhar Industrial Terminus'] },
      { name: 'Pendhar Industrial Terminus', hindi: 'पेणधर', x: 470, y: 120, lines: ['Line 1 (Phase 1)'], interchange: false, footfall: '10,000', lat: 19.0778, lng: 73.1033, connections: ['Kharghar Sector 14'] },
    ],
  },
  'bhopal-indore': {
    width: 620,
    height: 540,
    waterways: [
      { id: 'upper-lake', name: 'Bhojtal (Upper Lake Bhopal)', path: 'M 130,190 C 190,150 230,230 190,270 C 140,290 90,230 130,190 Z', stroke: '#0284c7', width: 2, fill: 'rgba(2,132,199,0.25)' },
    ],
    roads: [],
    geoLines: [
      { id: 'bhopal-orange', name: 'Bhopal Orange Line (Bhoj Metro)', color: '#ea580c', path: 'M 150,330 L 250,270 L 350,220 L 470,170', status: 'Operational Priority' },
      { id: 'indore-yellow', name: 'Indore Yellow Ring (Super Corridor)', color: '#eab308', path: 'M 360,480 L 430,410 L 490,340 L 550,280', status: 'Operational Priority' },
    ],
    stations: [
      { name: 'AIIMS Bhopal Terminal', hindi: 'एम्स भोपाल', x: 150, y: 330, lines: ['Bhopal Orange (Priority)'], interchange: false, footfall: '14,000', lat: 23.2083, lng: 77.4589, connections: ['Subhash Nagar Viaduct'] },
      { name: 'Subhash Nagar Viaduct', hindi: 'सुभाष नगर', x: 350, y: 220, lines: ['Bhopal Orange (Priority)'], interchange: true, footfall: '12,000', lat: 23.2422, lng: 77.4328, connections: ['AIIMS Bhopal Terminal'] },
      { name: 'Indore Super Corridor Gateway', hindi: 'सुपर कॉरिडोर इंदौर', x: 490, y: 340, lines: ['Indore Yellow (Priority)'], interchange: false, footfall: '15,000', lat: 22.7667, lng: 75.8333, connections: [] },
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

  // Build steps with line transitions and interchanges
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

  // Official DMRC Fare slab formula
  let tokenFare = 10;
  if (distanceKm > 32) tokenFare = 60;
  else if (distanceKm > 21) tokenFare = 50;
  else if (distanceKm > 12) tokenFare = 40;
  else if (distanceKm > 5) tokenFare = 30;
  else if (distanceKm > 2) tokenFare = 20;

  const smartCardFare = Math.round(tokenFare * 0.9); // 10% peak discount
  const offPeakFare = Math.round(tokenFare * 0.8); // 20% off-peak discount

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
  const [istTime, setIstTime] = useState(new Date());

  // Route Planner State
  const [originStation, setOriginStation] = useState('');
  const [destStation, setDestStation] = useState('');
  const [plannedRoute, setPlannedRoute] = useState(null);

  // Directory filter state
  const [directorySearch, setDirectorySearch] = useState('');
  const [gaugeFilter, setGaugeFilter] = useState('all');

  // Clock running against IST (Asia/Kolkata)
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

  // Set default origin and destination when switching cities
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
  }, [selectedCityId, currentStations]);

  const handleCityChange = (id) => {
    setSelectedCityId(id);
    setSelectedLineId(null);
    setHoveredStation(null);
    setSelectedStation(null);
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

  // Compute animated train positions based on IST clock
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

  // Filtered cities for directory matrix
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

  return (
    <div className="metro-atlas-root" aria-label="Interactive Metro Rail Workbench">
      {/* Top Header Strip with City Selector and IST Clock */}
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

        {/* Top-Level Workbench Mode Switcher */}
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

      {/* 17 Cities Navigation Pills */}
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

      {/* TAB 1 & 2: GEOGRAPHIC & SCHEMATIC MAP VIEW */}
      {(workbenchTab === 'geographic' || workbenchTab === 'schematic') && (
        <div className="metro-workbench-grid">
          <div className="metro-map-canvas-container">
            {/* Zoom controls */}
            <div className="metro-map-controls">
              <button
                type="button"
                className="metro-map-btn"
                aria-label="Zoom in"
                onClick={() => setZoom(z => Math.min(2.0, z + 0.2))}
              >
                +
              </button>
              <button
                type="button"
                className="metro-map-btn"
                aria-label="Zoom out"
                onClick={() => setZoom(z => Math.max(0.7, z - 0.2))}
              >
                −
              </button>
              <button
                type="button"
                className="metro-map-btn"
                aria-label="Reset zoom"
                onClick={() => setZoom(1)}
              >
                ↺
              </button>
            </div>

            {/* SVG Map Canvas */}
            <svg
              className={`metro-svg-canvas mode-${workbenchTab}`}
              viewBox={`0 0 ${layout.width} ${layout.height}`}
              style={{ transform: `scale(${zoom})`, transformOrigin: 'center center', transition: 'transform 0.2s ease' }}
            >
              <defs>
                <pattern id="metroGrid" width="30" height="30" patternUnits="userSpaceOnUse">
                  <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.035)" strokeWidth="1" />
                </pattern>
                <filter id="trainGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>
              <rect width="100%" height="100%" fill="url(#metroGrid)" />

              {/* Geographic Physical Waterways */}
              {layout.waterways && layout.waterways.map(w => (
                <g key={w.id} className="metro-waterway-group">
                  <path
                    d={w.path}
                    fill={w.fill || 'none'}
                    stroke={w.stroke || '#0284c7'}
                    strokeWidth={w.width || 12}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity={w.opacity || 0.6}
                  />
                  <text
                    x="68%"
                    y="42%"
                    fill="#38bdf8"
                    opacity="0.25"
                    fontSize="12"
                    fontWeight="700"
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
                const opacity = isSelected ? 1 : 0.15;
                const strokeW = line.dash ? 5 : 7;
                return (
                  <g key={line.id} className="metro-line-group" opacity={opacity} style={{ transition: 'opacity 0.25s ease' }}>
                    <path
                      d={line.path}
                      fill="none"
                      stroke={line.color}
                      strokeWidth={strokeW + 6}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      opacity={isSelected ? 0.25 : 0.05}
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

              {/* Live Train Simulation Markers */}
              {trains.map(tr => {
                const line = (layout.geoLines || []).find(l => l.id === tr.lineId);
                if (!line) return null;
                const isSelected = !selectedLineId || selectedLineId === line.id;
                if (!isSelected) return null;

                return (
                  <g key={tr.id} className="metro-live-train" filter="url(#trainGlow)">
                    <circle
                      r="5.5"
                      fill="#ffffff"
                      stroke={tr.color}
                      strokeWidth="2.5"
                      opacity="0.95"
                    />
                  </g>
                );
              })}

              {/* Stations */}
              {currentStations.map((st, idx) => {
                const isInterchange = st.interchange;
                const isHovered = hoveredStation?.name === st.name;
                const isSelected = selectedStation?.name === st.name;
                const r = isInterchange ? 9 : 6;

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
                        r={15}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth="2"
                        opacity={isHovered || isSelected ? 0.9 : 0.5}
                        strokeDasharray="3,3"
                      />
                    )}
                    <circle
                      r={isSelected ? r + 3 : isHovered ? r + 2 : r}
                      fill={isInterchange ? '#ffffff' : '#0f172a'}
                      stroke={isInterchange ? '#f59e0b' : '#ffffff'}
                      strokeWidth={isSelected ? '4' : '3'}
                    />
                    <text
                      x={st.x > layout.width * 0.6 ? -14 : 14}
                      y={4}
                      textAnchor={st.x > layout.width * 0.6 ? 'end' : 'start'}
                      fill={isSelected ? '#38bdf8' : '#f8fafc'}
                      fontSize={isInterchange ? '11px' : '9.5px'}
                      fontWeight={isInterchange ? '800' : '600'}
                      fontFamily="sans-serif"
                      stroke="#0b0f15"
                      strokeWidth="2"
                      paintOrder="stroke"
                    >
                      {isInterchange ? `★ ${st.name}` : st.name}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* Hover Station Floating Tooltip */}
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

            {/* Official Sources Banner */}
            <div className="metro-attribution-banner">
              <span className="mab-icon">🗺️</span>
              <div className="mab-content">
                <strong>Official Cartographic &amp; Transit Alignment Sources:</strong>
                <p>
                  Metro and base geography: © OpenStreetMap contributors, ODbL 1.0. Phase 4 and Phase 5 alignments: Delhi Metro Rail Corporation, influencezone.delhimetrorail.com. Counts cross-checked against DMRC’s network table and Wikipedia’s line table, August 2026. Live IST schematic engine inspired by Dtensor/metro-live &amp; RomanGolovanov/ametro. Curated transit guide inspired by digitalcreator-dev/indian-metro-networks.
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

            {/* Selected Station Inspector if clicked */}
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

      {/* TAB 3: INTERACTIVE ROUTE PLANNER & FARE FINDER (digitalcreator-dev/indian-metro-networks) */}
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
            {/* Input Selection Box */}
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

              {/* Station Info Highlights */}
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

            {/* Journey Result Summary */}
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

                  {/* Step-by-Step Transit Itinerary */}
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

      {/* TAB 4: CURATED DIRECTORY MATRIX (digitalcreator-dev/indian-metro-networks) */}
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

      {/* TAB 5: COMMUTER TRANSIT GUIDE & RULES (digitalcreator-dev/indian-metro-networks) */}
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