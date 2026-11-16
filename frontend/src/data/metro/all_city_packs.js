// All 17 Indian Metro Networks: Authentic Cartographic Packs & Station Coordinates
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

export const CITY_RAW_DATA = {
  "mumbai": {
    "name": "Mumbai Metro & Monorail",
    "hindi": "\u092e\u0941\u0902\u092c\u0908 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                72.81,
                18.9
              ],
              [
                72.83,
                18.92
              ],
              [
                72.84,
                18.95
              ],
              [
                72.86,
                18.99
              ],
              [
                72.9,
                19.01
              ],
              [
                72.93,
                19.05
              ],
              [
                72.98,
                19.12
              ],
              [
                72.99,
                19.18
              ],
              [
                72.98,
                19.26
              ],
              [
                72.95,
                19.28
              ],
              [
                72.89,
                19.28
              ],
              [
                72.84,
                19.26
              ],
              [
                72.81,
                19.2
              ],
              [
                72.8,
                19.14
              ],
              [
                72.81,
                19.06
              ],
              [
                72.8,
                19.0
              ],
              [
                72.81,
                18.9
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              72.815,
              18.905
            ],
            [
              72.822,
              18.925
            ],
            [
              72.824,
              18.943
            ],
            [
              72.798,
              18.955
            ],
            [
              72.805,
              18.98
            ],
            [
              72.812,
              19.01
            ],
            [
              72.835,
              19.04
            ],
            [
              72.822,
              19.055
            ],
            [
              72.825,
              19.095
            ],
            [
              72.818,
              19.14
            ],
            [
              72.798,
              19.18
            ],
            [
              72.79,
              19.25
            ],
            [
              72.82,
              19.31
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              72.835,
              19.04
            ],
            [
              72.855,
              19.055
            ],
            [
              72.875,
              19.065
            ],
            [
              72.895,
              19.085
            ],
            [
              72.905,
              19.12
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              72.92,
              18.94
            ],
            [
              72.935,
              18.99
            ],
            [
              72.965,
              19.05
            ],
            [
              72.985,
              19.11
            ],
            [
              72.995,
              19.17
            ],
            [
              72.98,
              19.23
            ],
            [
              72.99,
              19.28
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              72.9,
              19.12
            ],
            [
              72.915,
              19.13
            ],
            [
              72.908,
              19.135
            ],
            [
              72.895,
              19.128
            ],
            [
              72.9,
              19.12
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              72.862,
              19.26
            ],
            [
              72.855,
              19.21
            ],
            [
              72.85,
              19.16
            ],
            [
              72.852,
              19.115
            ],
            [
              72.842,
              19.06
            ],
            [
              72.835,
              19.03
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              72.975,
              19.21
            ],
            [
              72.95,
              19.16
            ],
            [
              72.925,
              19.11
            ],
            [
              72.905,
              19.065
            ],
            [
              72.88,
              19.03
            ],
            [
              72.86,
              19.015
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              72.822,
              19.045
            ],
            [
              72.812,
              19.025
            ],
            [
              72.815,
              19.012
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              72.895,
              19.055
            ],
            [
              72.875,
              19.01
            ],
            [
              72.855,
              18.97
            ],
            [
              72.84,
              18.94
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              72.848,
              19.245
            ],
            [
              72.836,
              19.18
            ],
            [
              72.835,
              19.12
            ],
            [
              72.838,
              19.06
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              72.838,
              19.24
            ],
            [
              72.83,
              19.175
            ],
            [
              72.828,
              19.135
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              72.828,
              18.932
            ],
            [
              72.819,
              18.968
            ],
            [
              72.835,
              19.005
            ],
            [
              72.843,
              19.018
            ],
            [
              72.84,
              19.055
            ],
            [
              72.847,
              19.12
            ],
            [
              72.852,
              19.18
            ],
            [
              72.857,
              19.23
            ],
            [
              72.862,
              19.26
            ]
          ]
        },
        {
          "g": [
            [
              72.835,
              18.94
            ],
            [
              72.838,
              18.975
            ],
            [
              72.843,
              19.018
            ],
            [
              72.875,
              19.065
            ],
            [
              72.908,
              19.088
            ],
            [
              72.935,
              19.14
            ],
            [
              72.975,
              19.19
            ],
            [
              72.985,
              19.24
            ]
          ]
        },
        {
          "g": [
            [
              72.835,
              18.94
            ],
            [
              72.858,
              19.017
            ],
            [
              72.875,
              19.065
            ],
            [
              72.905,
              19.055
            ],
            [
              72.935,
              19.05
            ],
            [
              72.97,
              19.06
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Chhatrapati Shivaji Maharaj Terminus",
          "ll": [
            72.835,
            18.94
          ],
          "r": 5
        },
        {
          "n": "Gateway of India",
          "ll": [
            72.834,
            18.922
          ],
          "r": 4
        },
        {
          "n": "Bandra Kurla Complex (BKC)",
          "ll": [
            72.865,
            19.065
          ],
          "r": 5
        },
        {
          "n": "Worli Sea Face",
          "ll": [
            72.815,
            19.012
          ],
          "r": 4
        },
        {
          "n": "Dadar Central Junction",
          "ll": [
            72.843,
            19.018
          ],
          "r": 4
        },
        {
          "n": "Sanjay Gandhi National Park",
          "ll": [
            72.91,
            19.23
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "mum-l1",
        "nm": "Line 1 (Blue Corridor: Versova - Ghatkopar)",
        "c": "#0284c7",
        "seq": [
          "Versova",
          "DN Nagar",
          "Azad Nagar",
          "Andheri",
          "Western Express Highway",
          "Chakala",
          "Airport Road",
          "Marol Naka",
          "Saki Naka",
          "Asalpha",
          "Jagruti Nagar",
          "Ghatkopar"
        ],
        "segs": [
          [
            [
              72.8197,
              19.1311
            ],
            [
              72.8315,
              19.1245
            ],
            [
              72.842,
              19.125
            ],
            [
              72.8525,
              19.1197
            ],
            [
              72.858,
              19.115
            ],
            [
              72.864,
              19.112
            ],
            [
              72.8735,
              19.1105
            ],
            [
              72.882,
              19.109
            ],
            [
              72.889,
              19.102
            ],
            [
              72.898,
              19.095
            ],
            [
              72.905,
              19.092
            ],
            [
              72.9125,
              19.088
            ]
          ]
        ]
      },
      {
        "id": "mum-l2a",
        "nm": "Line 2A (Yellow Line: Dahisar East - Andheri West)",
        "c": "#eab308",
        "seq": [
          "Dahisar East",
          "Anand Nagar",
          "Kandarpada",
          "Mandapeshwar",
          "Eksar",
          "Borivali West",
          "Pahadi Eksar",
          "Kandivali West",
          "Dahanukarwadi",
          "Valnai",
          "Malad West",
          "Lower Malad",
          "Pahadi Goregaon",
          "Goregaon West",
          "Oshiwara",
          "Lower Oshiwara",
          "Andheri West"
        ],
        "segs": [
          [
            [
              72.862,
              19.257
            ],
            [
              72.856,
              19.252
            ],
            [
              72.852,
              19.245
            ],
            [
              72.848,
              19.238
            ],
            [
              72.844,
              19.23
            ],
            [
              72.84,
              19.222
            ],
            [
              72.838,
              19.215
            ],
            [
              72.836,
              19.208
            ],
            [
              72.834,
              19.2
            ],
            [
              72.832,
              19.192
            ],
            [
              72.831,
              19.184
            ],
            [
              72.83,
              19.176
            ],
            [
              72.829,
              19.168
            ],
            [
              72.828,
              19.16
            ],
            [
              72.827,
              19.15
            ],
            [
              72.828,
              19.14
            ],
            [
              72.83,
              19.13
            ]
          ]
        ]
      },
      {
        "id": "mum-l7",
        "nm": "Line 7 (Red Line: Dahisar East - Gundavali)",
        "c": "#ef4444",
        "seq": [
          "Dahisar East",
          "Ovaripada",
          "National Park",
          "Devipada",
          "Magathane",
          "Poisar",
          "Akurli",
          "Kurar",
          "Dindoshi",
          "Aarey",
          "Goregaon East",
          "Jogeshwari East",
          "Mogra",
          "Gundavali"
        ],
        "segs": [
          [
            [
              72.862,
              19.257
            ],
            [
              72.863,
              19.248
            ],
            [
              72.864,
              19.238
            ],
            [
              72.8645,
              19.228
            ],
            [
              72.865,
              19.218
            ],
            [
              72.864,
              19.208
            ],
            [
              72.863,
              19.198
            ],
            [
              72.862,
              19.188
            ],
            [
              72.861,
              19.178
            ],
            [
              72.86,
              19.168
            ],
            [
              72.859,
              19.158
            ],
            [
              72.858,
              19.145
            ],
            [
              72.857,
              19.132
            ],
            [
              72.858,
              19.117
            ]
          ]
        ]
      },
      {
        "id": "mum-l3",
        "nm": "Line 3 (Aqua Underground: Aarey - BKC - Cuffe Parade)",
        "c": "#06b6d4",
        "seq": [
          "Aarey JVLR",
          "SEEPZ",
          "MIDC",
          "Marol Naka",
          "CSMIA T2",
          "Sahar Road",
          "CSMIA T1",
          "Santacruz",
          "Vidyanagari",
          "BKC",
          "Dharavi",
          "Shitaladevi",
          "Dadar",
          "Siddhivinayak",
          "Worli",
          "Acharya Atre Chowk",
          "Science Museum",
          "Mahalaxmi",
          "Mumbai Central",
          "Grant Road",
          "Girgaon",
          "Kalbadevi",
          "CSMT",
          "Hutatma Chowk",
          "Churchgate",
          "Vidhan Bhavan",
          "Cuffe Parade"
        ],
        "segs": [
          [
            [
              72.875,
              19.139
            ],
            [
              72.878,
              19.129
            ],
            [
              72.88,
              19.119
            ],
            [
              72.882,
              19.109
            ],
            [
              72.874,
              19.098
            ],
            [
              72.868,
              19.096
            ],
            [
              72.854,
              19.09
            ],
            [
              72.846,
              19.082
            ],
            [
              72.855,
              19.073
            ],
            [
              72.865,
              19.065
            ],
            [
              72.855,
              19.048
            ],
            [
              72.845,
              19.035
            ],
            [
              72.841,
              19.019
            ],
            [
              72.832,
              19.016
            ],
            [
              72.822,
              19.008
            ],
            [
              72.818,
              18.998
            ],
            [
              72.82,
              18.988
            ],
            [
              72.822,
              18.981
            ],
            [
              72.819,
              18.971
            ],
            [
              72.816,
              18.963
            ],
            [
              72.818,
              18.955
            ],
            [
              72.825,
              18.948
            ],
            [
              72.835,
              18.94
            ],
            [
              72.832,
              18.932
            ],
            [
              72.828,
              18.935
            ],
            [
              72.825,
              18.927
            ],
            [
              72.819,
              18.915
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Versova",
        "hindi": "\u0935\u0930\u094d\u0938\u094b\u0935\u093e",
        "ll": [
          72.8197,
          19.1311
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "DN Nagar",
        "hindi": "\u0921\u0940 \u090f\u0928 \u0928\u0917\u0930",
        "ll": [
          72.8315,
          19.1245
        ],
        "l": [
          "mum-l1",
          "mum-l2a"
        ],
        "interchange": true
      },
      {
        "n": "Azad Nagar",
        "hindi": "\u0906\u091c\u093c\u093e\u0926 \u0928\u0917\u0930",
        "ll": [
          72.842,
          19.125
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Andheri",
        "hindi": "\u0905\u0902\u0927\u0947\u0930\u0940",
        "ll": [
          72.8525,
          19.1197
        ],
        "l": [
          "mum-l1"
        ],
        "interchange": true
      },
      {
        "n": "Western Express Highway",
        "hindi": "\u0935\u0947\u0938\u094d\u091f\u0930\u094d\u0928 \u090f\u0915\u094d\u0938\u092a\u094d\u0930\u0947\u0938 \u0939\u093e\u0908\u0935\u0947",
        "ll": [
          72.858,
          19.115
        ],
        "l": [
          "mum-l1",
          "mum-l7"
        ],
        "interchange": true
      },
      {
        "n": "Chakala",
        "hindi": "\u091a\u0915\u0932\u093e",
        "ll": [
          72.864,
          19.112
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Airport Road",
        "hindi": "\u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f \u0930\u094b\u0921",
        "ll": [
          72.8735,
          19.1105
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Marol Naka",
        "hindi": "\u092e\u0930\u094b\u0932 \u0928\u093e\u0915\u093e",
        "ll": [
          72.882,
          19.109
        ],
        "l": [
          "mum-l1",
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Saki Naka",
        "hindi": "\u0938\u093e\u0915\u0940 \u0928\u093e\u0915\u093e",
        "ll": [
          72.889,
          19.102
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Asalpha",
        "hindi": "\u0905\u0938\u093e\u0932\u094d\u092b\u093e",
        "ll": [
          72.898,
          19.095
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Jagruti Nagar",
        "hindi": "\u091c\u093e\u0917\u0943\u0924\u093f \u0928\u0917\u0930",
        "ll": [
          72.905,
          19.092
        ],
        "l": [
          "mum-l1"
        ]
      },
      {
        "n": "Ghatkopar",
        "hindi": "\u0918\u093e\u091f\u0915\u094b\u092a\u0930",
        "ll": [
          72.9125,
          19.088
        ],
        "l": [
          "mum-l1"
        ],
        "interchange": true
      },
      {
        "n": "Dahisar East",
        "hindi": "\u0926\u0939\u093f\u0938\u0930 \u092a\u0942\u0930\u094d\u0935",
        "ll": [
          72.862,
          19.257
        ],
        "l": [
          "mum-l2a",
          "mum-l7"
        ],
        "interchange": true
      },
      {
        "n": "Anand Nagar",
        "hindi": "\u0906\u0928\u0902\u0926 \u0928\u0917\u0930",
        "ll": [
          72.856,
          19.252
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Kandarpada",
        "hindi": "\u0915\u0902\u0926\u0930\u092a\u093e\u0921\u093c\u093e",
        "ll": [
          72.852,
          19.245
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Mandapeshwar",
        "hindi": "\u092e\u0902\u0921\u092a\u0947\u0936\u094d\u0935\u0930",
        "ll": [
          72.848,
          19.238
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Eksar",
        "hindi": "\u090f\u0915\u0938\u0930",
        "ll": [
          72.844,
          19.23
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Borivali West",
        "hindi": "\u092c\u094b\u0930\u0940\u0935\u0932\u0940 \u092a\u0936\u094d\u091a\u093f\u092e",
        "ll": [
          72.84,
          19.222
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Pahadi Eksar",
        "hindi": "\u092a\u0939\u093e\u0921\u093c\u0940 \u090f\u0915\u0938\u0930",
        "ll": [
          72.838,
          19.215
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Kandivali West",
        "hindi": "\u0915\u093e\u0902\u0926\u093f\u0935\u0932\u0940 \u092a\u0936\u094d\u091a\u093f\u092e",
        "ll": [
          72.836,
          19.208
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Dahanukarwadi",
        "hindi": "\u0926\u0939\u093e\u0928\u0941\u0915\u0930\u0935\u093e\u0921\u093c\u0940",
        "ll": [
          72.834,
          19.2
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Valnai",
        "hindi": "\u0935\u0932\u0928\u0908",
        "ll": [
          72.832,
          19.192
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Malad West",
        "hindi": "\u092e\u093e\u0932\u093e\u0921 \u092a\u0936\u094d\u091a\u093f\u092e",
        "ll": [
          72.831,
          19.184
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Lower Malad",
        "hindi": "\u0932\u094b\u0905\u0930 \u092e\u093e\u0932\u093e\u0921",
        "ll": [
          72.83,
          19.176
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Pahadi Goregaon",
        "hindi": "\u092a\u0939\u093e\u0921\u093c\u0940 \u0917\u094b\u0930\u0947\u0917\u093e\u0902\u0935",
        "ll": [
          72.829,
          19.168
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Goregaon West",
        "hindi": "\u0917\u094b\u0930\u0947\u0917\u093e\u0902\u0935 \u092a\u0936\u094d\u091a\u093f\u092e",
        "ll": [
          72.828,
          19.16
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Oshiwara",
        "hindi": "\u0913\u0936\u093f\u0935\u0930\u093e",
        "ll": [
          72.827,
          19.15
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Lower Oshiwara",
        "hindi": "\u0932\u094b\u0905\u0930 \u0913\u0936\u093f\u0935\u0930\u093e",
        "ll": [
          72.828,
          19.14
        ],
        "l": [
          "mum-l2a"
        ]
      },
      {
        "n": "Andheri West",
        "hindi": "\u0905\u0902\u0927\u0947\u0930\u0940 \u092a\u0936\u094d\u091a\u093f\u092e",
        "ll": [
          72.83,
          19.13
        ],
        "l": [
          "mum-l2a",
          "mum-l1"
        ],
        "interchange": true
      },
      {
        "n": "Ovaripada",
        "hindi": "\u0913\u0935\u0930\u0940\u092a\u093e\u0921\u093c\u093e",
        "ll": [
          72.863,
          19.248
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "National Park",
        "hindi": "\u0928\u0947\u0936\u0928\u0932 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          72.864,
          19.238
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Devipada",
        "hindi": "\u0926\u0947\u0935\u0940\u092a\u093e\u0921\u093c\u093e",
        "ll": [
          72.8645,
          19.228
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Magathane",
        "hindi": "\u092e\u093e\u0917\u093e\u0920\u093e\u0923\u0947",
        "ll": [
          72.865,
          19.218
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Poisar",
        "hindi": "\u092a\u094b\u0908\u0938\u0930",
        "ll": [
          72.864,
          19.208
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Akurli",
        "hindi": "\u0906\u0915\u0941\u0930\u094d\u0932\u0940",
        "ll": [
          72.863,
          19.198
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Kurar",
        "hindi": "\u0915\u0941\u0930\u093e\u0930",
        "ll": [
          72.862,
          19.188
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Dindoshi",
        "hindi": "\u0926\u093f\u0902\u0921\u094b\u0936\u0940",
        "ll": [
          72.861,
          19.178
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Aarey",
        "hindi": "\u0906\u0930\u0947",
        "ll": [
          72.86,
          19.168
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Goregaon East",
        "hindi": "\u0917\u094b\u0930\u0947\u0917\u093e\u0902\u0935 \u092a\u0942\u0930\u094d\u0935",
        "ll": [
          72.859,
          19.158
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Jogeshwari East",
        "hindi": "\u091c\u094b\u0917\u0947\u0936\u094d\u0935\u0930\u0940 \u092a\u0942\u0930\u094d\u0935",
        "ll": [
          72.858,
          19.145
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Mogra",
        "hindi": "\u092e\u094b\u0917\u0930\u093e",
        "ll": [
          72.857,
          19.132
        ],
        "l": [
          "mum-l7"
        ]
      },
      {
        "n": "Gundavali",
        "hindi": "\u0917\u0941\u0902\u0926\u0935\u0932\u0940",
        "ll": [
          72.858,
          19.117
        ],
        "l": [
          "mum-l7",
          "mum-l1"
        ],
        "interchange": true
      },
      {
        "n": "Aarey JVLR",
        "hindi": "\u0906\u0930\u0947 \u091c\u0947\u0935\u0940\u090f\u0932\u0906\u0930",
        "ll": [
          72.875,
          19.139
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "SEEPZ",
        "hindi": "\u0938\u0940\u092a\u094d\u091c\u093c",
        "ll": [
          72.878,
          19.129
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "MIDC",
        "hindi": "\u090f\u092e\u0906\u0908\u0921\u0940\u0938\u0940",
        "ll": [
          72.88,
          19.119
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "CSMIA T2",
        "hindi": "\u0938\u0940\u090f\u0938\u090f\u092e\u0906\u0908\u090f \u091f\u09402 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          72.874,
          19.098
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Sahar Road",
        "hindi": "\u0938\u0939\u093e\u0930 \u0930\u094b\u0921",
        "ll": [
          72.868,
          19.096
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "CSMIA T1",
        "hindi": "\u0938\u0940\u090f\u0938\u090f\u092e\u0906\u0908\u090f \u091f\u09401",
        "ll": [
          72.854,
          19.09
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Santacruz",
        "hindi": "\u0938\u093e\u0902\u0924\u093e\u0915\u094d\u0930\u0942\u091c\u093c",
        "ll": [
          72.846,
          19.082
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Vidyanagari",
        "hindi": "\u0935\u093f\u0926\u094d\u092f\u093e\u0928\u0917\u0930\u0940",
        "ll": [
          72.855,
          19.073
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "BKC",
        "hindi": "\u092c\u0940\u0915\u0947\u0938\u0940 (\u092c\u093e\u0902\u0926\u094d\u0930\u093e \u0915\u0941\u0930\u094d\u0932\u093e \u0915\u0949\u092e\u094d\u092a\u094d\u0932\u0947\u0915\u094d\u0938)",
        "ll": [
          72.865,
          19.065
        ],
        "l": [
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Dharavi",
        "hindi": "\u0927\u093e\u0930\u093e\u0935\u0940",
        "ll": [
          72.855,
          19.048
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Shitaladevi",
        "hindi": "\u0936\u0940\u0924\u0932\u093e\u0926\u0947\u0935\u0940",
        "ll": [
          72.845,
          19.035
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Dadar",
        "hindi": "\u0926\u093e\u0926\u0930",
        "ll": [
          72.841,
          19.019
        ],
        "l": [
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Siddhivinayak",
        "hindi": "\u0938\u093f\u0926\u094d\u0927\u093f\u0935\u093f\u0928\u093e\u092f\u0915",
        "ll": [
          72.832,
          19.016
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Worli",
        "hindi": "\u0935\u0930\u094d\u0932\u0940",
        "ll": [
          72.822,
          19.008
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Acharya Atre Chowk",
        "hindi": "\u0906\u091a\u093e\u0930\u094d\u092f \u0905\u0924\u094d\u0930\u0947 \u091a\u094c\u0915",
        "ll": [
          72.818,
          18.998
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Science Museum",
        "hindi": "\u0938\u093e\u0907\u0902\u0938 \u092e\u094d\u092f\u0942\u091c\u093f\u092f\u092e",
        "ll": [
          72.82,
          18.988
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Mahalaxmi",
        "hindi": "\u092e\u0939\u093e\u0932\u0915\u094d\u0937\u094d\u092e\u0940",
        "ll": [
          72.822,
          18.981
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Mumbai Central",
        "hindi": "\u092e\u0941\u0902\u092c\u0908 \u0938\u0947\u0902\u091f\u094d\u0930\u0932",
        "ll": [
          72.819,
          18.971
        ],
        "l": [
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Grant Road",
        "hindi": "\u0917\u094d\u0930\u093e\u0902\u091f \u0930\u094b\u0921",
        "ll": [
          72.816,
          18.963
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Girgaon",
        "hindi": "\u0917\u093f\u0930\u0917\u093e\u0902\u0935",
        "ll": [
          72.818,
          18.955
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Kalbadevi",
        "hindi": "\u0915\u093e\u0932\u092c\u093e\u0926\u0947\u0935\u0940",
        "ll": [
          72.825,
          18.948
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "CSMT",
        "hindi": "\u0938\u0940\u090f\u0938\u090f\u092e\u091f\u0940",
        "ll": [
          72.835,
          18.94
        ],
        "l": [
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Hutatma Chowk",
        "hindi": "\u0939\u0941\u0924\u093e\u0924\u094d\u092e\u093e \u091a\u094c\u0915 (\u092b\u094d\u0932\u094b\u0930\u093e \u092b\u093e\u0909\u0902\u091f\u0947\u0928)",
        "ll": [
          72.832,
          18.932
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Churchgate",
        "hindi": "\u091a\u0930\u094d\u091a\u0917\u0947\u091f",
        "ll": [
          72.828,
          18.935
        ],
        "l": [
          "mum-l3"
        ],
        "interchange": true
      },
      {
        "n": "Vidhan Bhavan",
        "hindi": "\u0935\u093f\u0927\u093e\u0928 \u092d\u0935\u0928",
        "ll": [
          72.825,
          18.927
        ],
        "l": [
          "mum-l3"
        ]
      },
      {
        "n": "Cuffe Parade",
        "hindi": "\u0915\u092b \u092a\u0930\u0947\u0921",
        "ll": [
          72.819,
          18.915
        ],
        "l": [
          "mum-l3"
        ]
      }
    ],
    "links": [
      [
        "Andheri",
        "Western Express Highway"
      ],
      [
        "Gundavali",
        "Western Express Highway"
      ],
      [
        "DN Nagar",
        "Andheri West"
      ]
    ]
  },
  "bengaluru": {
    "name": "Bengaluru Namma Metro",
    "hindi": "\u0ca8\u0cae\u0ccd\u0cae \u0cae\u0cc6\u0c9f\u0ccd\u0cb0\u0ccb \u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                77.46,
                12.88
              ],
              [
                77.48,
                13.06
              ],
              [
                77.58,
                13.08
              ],
              [
                77.72,
                13.03
              ],
              [
                77.78,
                12.98
              ],
              [
                77.74,
                12.83
              ],
              [
                77.66,
                12.79
              ],
              [
                77.52,
                12.82
              ],
              [
                77.46,
                12.88
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              77.55,
              13.02
            ],
            [
              77.53,
              12.96
            ],
            [
              77.51,
              12.92
            ],
            [
              77.48,
              12.88
            ],
            [
              77.42,
              12.82
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              77.64,
              12.935
            ],
            [
              77.67,
              12.93
            ],
            [
              77.71,
              12.935
            ],
            [
              77.745,
              12.94
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              77.618,
              12.98
            ],
            [
              77.625,
              12.985
            ],
            [
              77.622,
              12.978
            ],
            [
              77.618,
              12.98
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              77.575,
              13.008
            ],
            [
              77.585,
              13.04
            ],
            [
              77.595,
              13.045
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              77.535,
              13.01
            ],
            [
              77.585,
              13.04
            ],
            [
              77.645,
              13.02
            ],
            [
              77.685,
              12.99
            ],
            [
              77.7,
              12.95
            ],
            [
              77.675,
              12.925
            ],
            [
              77.625,
              12.917
            ],
            [
              77.57,
              12.92
            ],
            [
              77.52,
              12.945
            ],
            [
              77.535,
              13.01
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              77.46,
              13.03
            ],
            [
              77.47,
              12.92
            ],
            [
              77.52,
              12.86
            ],
            [
              77.62,
              12.84
            ],
            [
              77.68,
              12.82
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              77.625,
              12.917
            ],
            [
              77.65,
              12.88
            ],
            [
              77.675,
              12.845
            ],
            [
              77.705,
              12.805
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              77.585,
              12.99
            ],
            [
              77.585,
              13.04
            ],
            [
              77.595,
              13.09
            ],
            [
              77.61,
              13.15
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              77.57,
              12.965
            ],
            [
              77.518,
              12.948
            ],
            [
              77.48,
              12.91
            ],
            [
              77.44,
              12.87
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              77.48,
              12.91
            ],
            [
              77.53,
              12.955
            ],
            [
              77.57,
              12.977
            ],
            [
              77.6,
              12.993
            ],
            [
              77.652,
              12.991
            ],
            [
              77.665,
              12.998
            ],
            [
              77.76,
              12.996
            ]
          ]
        },
        {
          "g": [
            [
              77.57,
              12.977
            ],
            [
              77.55,
              13.004
            ],
            [
              77.545,
              13.023
            ],
            [
              77.58,
              13.09
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Vidhana Soudha (Karnataka State Assembly)",
          "ll": [
            77.591,
            12.979
          ],
          "r": 5
        },
        {
          "n": "KSR Bengaluru Central (Majestic)",
          "ll": [
            77.572,
            12.977
          ],
          "r": 5
        },
        {
          "n": "MG Road & Brigade Road",
          "ll": [
            77.607,
            12.975
          ],
          "r": 4
        },
        {
          "n": "Whitefield IT Export Zone",
          "ll": [
            77.75,
            12.97
          ],
          "r": 4
        },
        {
          "n": "Electronic City Tech Hub",
          "ll": [
            77.675,
            12.845
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "blr-purple",
        "nm": "Purple Line (Whitefield Kadugodi - Challaghatta)",
        "c": "#9333ea",
        "seq": [
          "Whitefield (Kadugodi)",
          "Hopefarm Channasandra",
          "Kadugodi Tree Park",
          "Pattandur Agrahara",
          "Sri Sathya Sai Hospital",
          "Nallurhalli",
          "Kundalahalli",
          "Seetharampalya",
          "Hoodi",
          "Garudacharpalya",
          "Singayyanapalya",
          "KR Puram",
          "Benniganahalli",
          "Baiyappanahalli",
          "Swami Vivekananda Road",
          "Indiranagar",
          "Halasuru",
          "Trinity",
          "MG Road",
          "Cubbon Park",
          "Dr. BR Ambedkar Vidhana Soudha",
          "Sir M Visveshwaraya Central College",
          "Nadaprabhu Kempegowda Majestic",
          "KSR City Railway Station",
          "Magadi Road",
          "Hosahalli",
          "Vijayanagar",
          "Attiguppe",
          "Deepanjali Nagar",
          "Mysuru Road",
          "Pantharapalya",
          "Rajarajeshwari Nagar",
          "Jnanabharathi",
          "Pattanagere",
          "Kengeri Bus Terminal",
          "Kengeri",
          "Challaghatta"
        ],
        "segs": [
          [
            [
              77.76,
              12.996
            ],
            [
              77.75,
              12.986
            ],
            [
              77.74,
              12.985
            ],
            [
              77.73,
              12.984
            ],
            [
              77.72,
              12.983
            ],
            [
              77.71,
              12.982
            ],
            [
              77.7,
              12.982
            ],
            [
              77.69,
              12.985
            ],
            [
              77.68,
              12.989
            ],
            [
              77.675,
              12.993
            ],
            [
              77.67,
              12.995
            ],
            [
              77.665,
              12.998
            ],
            [
              77.658,
              12.994
            ],
            [
              77.652,
              12.991
            ],
            [
              77.643,
              12.986
            ],
            [
              77.638,
              12.978
            ],
            [
              77.627,
              12.976
            ],
            [
              77.618,
              12.973
            ],
            [
              77.607,
              12.975
            ],
            [
              77.598,
              12.98
            ],
            [
              77.591,
              12.979
            ],
            [
              77.583,
              12.976
            ],
            [
              77.572,
              12.977
            ],
            [
              77.568,
              12.975
            ],
            [
              77.555,
              12.973
            ],
            [
              77.545,
              12.972
            ],
            [
              77.537,
              12.97
            ],
            [
              77.528,
              12.964
            ],
            [
              77.522,
              12.957
            ],
            [
              77.518,
              12.948
            ],
            [
              77.512,
              12.94
            ],
            [
              77.505,
              12.932
            ],
            [
              77.498,
              12.925
            ],
            [
              77.492,
              12.918
            ],
            [
              77.485,
              12.912
            ],
            [
              77.478,
              12.906
            ],
            [
              77.469,
              12.898
            ]
          ]
        ]
      },
      {
        "id": "blr-green",
        "nm": "Green Line (Madavara - Silk Institute)",
        "c": "#16a34a",
        "seq": [
          "Madavara (BIEC)",
          "Chikkabidarakallu",
          "Manjunathanagar",
          "Nagasandra",
          "Dasarahalli",
          "Jalahalli",
          "Peenya Industry",
          "Peenya",
          "Goraguntepalya",
          "Yeshwanthpur",
          "Sandal Soap Factory",
          "Mahalakshmi",
          "Rajajinagar",
          "Mahakavi Kuvempu Road",
          "Sampige Road",
          "Nadaprabhu Kempegowda Majestic",
          "Chickpete",
          "Krishna Rajendra Market",
          "National College",
          "Lalbagh",
          "South End Circle",
          "Jayanagar",
          "RV Road",
          "Banashankari",
          "JP Nagar",
          "Yelachenahalli",
          "Konanakunte Cross",
          "Doddakallasandra",
          "Vajrahalli",
          "Thalaghattapura",
          "Silk Institute"
        ],
        "segs": [
          [
            [
              77.478,
              13.065
            ],
            [
              77.485,
              13.055
            ],
            [
              77.492,
              13.045
            ],
            [
              77.5,
              13.038
            ],
            [
              77.508,
              13.03
            ],
            [
              77.515,
              13.022
            ],
            [
              77.522,
              13.018
            ],
            [
              77.528,
              13.012
            ],
            [
              77.535,
              13.008
            ],
            [
              77.545,
              13.004
            ],
            [
              77.552,
              12.998
            ],
            [
              77.556,
              12.992
            ],
            [
              77.56,
              12.988
            ],
            [
              77.563,
              12.983
            ],
            [
              77.567,
              12.98
            ],
            [
              77.572,
              12.977
            ],
            [
              77.575,
              12.971
            ],
            [
              77.577,
              12.964
            ],
            [
              77.576,
              12.955
            ],
            [
              77.578,
              12.946
            ],
            [
              77.58,
              12.938
            ],
            [
              77.582,
              12.93
            ],
            [
              77.583,
              12.922
            ],
            [
              77.573,
              12.915
            ],
            [
              77.568,
              12.908
            ],
            [
              77.565,
              12.898
            ],
            [
              77.56,
              12.888
            ],
            [
              77.555,
              12.879
            ],
            [
              77.548,
              12.87
            ],
            [
              77.54,
              12.862
            ],
            [
              77.532,
              12.854
            ]
          ]
        ]
      },
      {
        "id": "blr-yellow",
        "nm": "Yellow Line (RV Road - Bommasandra)",
        "c": "#eab308",
        "seq": [
          "RV Road",
          "Ragigudda",
          "Jayadeva Hospital",
          "BTM Layout",
          "Central Silk Board",
          "Bommanahalli",
          "Hongasandra",
          "Kudlu Gate",
          "Singasandra",
          "Hosa Road",
          "Beratena Agrahara",
          "Electronic City",
          "Infosys Foundation",
          "Huskur Road",
          "Hebbagodi",
          "Bommasandra"
        ],
        "segs": [
          [
            [
              77.583,
              12.922
            ],
            [
              77.592,
              12.916
            ],
            [
              77.602,
              12.918
            ],
            [
              77.612,
              12.916
            ],
            [
              77.625,
              12.917
            ],
            [
              77.632,
              12.905
            ],
            [
              77.638,
              12.895
            ],
            [
              77.645,
              12.885
            ],
            [
              77.652,
              12.875
            ],
            [
              77.658,
              12.865
            ],
            [
              77.665,
              12.855
            ],
            [
              77.672,
              12.845
            ],
            [
              77.678,
              12.835
            ],
            [
              77.685,
              12.825
            ],
            [
              77.692,
              12.815
            ],
            [
              77.698,
              12.805
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Whitefield (Kadugodi)",
        "hindi": "\u0935\u094d\u0939\u093e\u0907\u091f\u092b\u0940\u0932\u094d\u0921",
        "ll": [
          77.76,
          12.996
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Hopefarm Channasandra",
        "hindi": "\u0939\u094b\u092a\u092b\u093e\u0930\u094d\u092e",
        "ll": [
          77.75,
          12.986
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Kadugodi Tree Park",
        "hindi": "\u0915\u093e\u0921\u0941\u0917\u094b\u0921\u0940 \u091f\u094d\u0930\u0940 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          77.74,
          12.985
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Pattandur Agrahara",
        "hindi": "\u092a\u091f\u094d\u091f\u0902\u0926\u0942\u0930 \u0905\u0917\u094d\u0930\u0939\u093e\u0930\u093e",
        "ll": [
          77.73,
          12.984
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Sri Sathya Sai Hospital",
        "hindi": "\u0938\u0924\u094d\u092f \u0938\u093e\u0908\u0902 \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          77.72,
          12.983
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Nallurhalli",
        "hindi": "\u0928\u0932\u094d\u0932\u0942\u0930\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.71,
          12.982
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Kundalahalli",
        "hindi": "\u0915\u0941\u0902\u0921\u0932\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.7,
          12.982
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Seetharampalya",
        "hindi": "\u0938\u0940\u0924\u093e\u0930\u093e\u092e\u092a\u093e\u0932\u094d\u092f\u093e",
        "ll": [
          77.69,
          12.985
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Hoodi",
        "hindi": "\u0939\u0942\u0921\u0940",
        "ll": [
          77.68,
          12.989
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Garudacharpalya",
        "hindi": "\u0917\u0930\u0941\u0921\u093c\u093e\u091a\u093e\u0930\u092a\u093e\u0932\u094d\u092f\u093e",
        "ll": [
          77.675,
          12.993
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Singayyanapalya",
        "hindi": "\u0938\u093f\u0902\u0917\u092f\u094d\u092f\u0928\u093e\u092a\u093e\u0932\u094d\u092f\u093e",
        "ll": [
          77.67,
          12.995
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "KR Puram",
        "hindi": "\u0915\u0947\u0906\u0930 \u092a\u0941\u0930\u092e",
        "ll": [
          77.665,
          12.998
        ],
        "l": [
          "blr-purple"
        ],
        "interchange": true
      },
      {
        "n": "Benniganahalli",
        "hindi": "\u092c\u0947\u0928\u094d\u0928\u093f\u0917\u0928\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.658,
          12.994
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Baiyappanahalli",
        "hindi": "\u092c\u0948\u092f\u092a\u094d\u092a\u0928\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.652,
          12.991
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Swami Vivekananda Road",
        "hindi": "\u0938\u094d\u0935\u093e\u092e\u0940 \u0935\u093f\u0935\u0947\u0915\u093e\u0928\u0902\u0926 \u0930\u094b\u0921",
        "ll": [
          77.643,
          12.986
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Indiranagar",
        "hindi": "\u0907\u0902\u0926\u093f\u0930\u093e\u0928\u0917\u0930",
        "ll": [
          77.638,
          12.978
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Halasuru",
        "hindi": "\u0939\u0932\u0938\u0942\u0930\u0941",
        "ll": [
          77.627,
          12.976
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Trinity",
        "hindi": "\u091f\u094d\u0930\u093f\u0928\u093f\u091f\u0940",
        "ll": [
          77.618,
          12.973
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "MG Road",
        "hindi": "\u090f\u092e\u091c\u0940 \u0930\u094b\u0921",
        "ll": [
          77.607,
          12.975
        ],
        "l": [
          "blr-purple"
        ],
        "interchange": true
      },
      {
        "n": "Cubbon Park",
        "hindi": "\u0915\u092c\u094d\u092c\u0928 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          77.598,
          12.98
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Dr. BR Ambedkar Vidhana Soudha",
        "hindi": "\u0935\u093f\u0927\u093e\u0928 \u0938\u094c\u0927",
        "ll": [
          77.591,
          12.979
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Sir M Visveshwaraya Central College",
        "hindi": "\u0935\u093f\u0936\u094d\u0935\u0947\u0936\u094d\u0935\u0930\u092f\u094d\u092f\u093e \u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          77.583,
          12.976
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Nadaprabhu Kempegowda Majestic",
        "hindi": "\u0915\u0947\u092e\u094d\u092a\u0947\u0917\u094c\u0921\u093c\u093e \u092e\u0948\u091c\u0947\u0938\u094d\u091f\u093f\u0915",
        "ll": [
          77.572,
          12.977
        ],
        "l": [
          "blr-purple",
          "blr-green"
        ],
        "interchange": true
      },
      {
        "n": "KSR City Railway Station",
        "hindi": "\u0915\u0947\u090f\u0938\u0906\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          77.568,
          12.975
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Magadi Road",
        "hindi": "\u092e\u093e\u0917\u0921\u0940 \u0930\u094b\u0921",
        "ll": [
          77.555,
          12.973
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Hosahalli",
        "hindi": "\u0939\u094b\u0938\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.545,
          12.972
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Vijayanagar",
        "hindi": "\u0935\u093f\u091c\u092f\u0928\u0917\u0930",
        "ll": [
          77.537,
          12.97
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Attiguppe",
        "hindi": "\u0905\u0924\u094d\u0924\u093f\u0917\u0941\u092a\u094d\u092a\u0947",
        "ll": [
          77.528,
          12.964
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Deepanjali Nagar",
        "hindi": "\u0926\u0940\u092a\u093e\u0902\u091c\u0932\u093f \u0928\u0917\u0930",
        "ll": [
          77.522,
          12.957
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Mysuru Road",
        "hindi": "\u092e\u0948\u0938\u0942\u0930\u0941 \u0930\u094b\u0921",
        "ll": [
          77.518,
          12.948
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Pantharapalya",
        "hindi": "\u092a\u0902\u0925\u0930\u092a\u093e\u0932\u094d\u092f\u093e",
        "ll": [
          77.512,
          12.94
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Rajarajeshwari Nagar",
        "hindi": "\u0930\u093e\u091c\u093e\u0930\u093e\u092e\u0947\u0936\u094d\u0935\u0930\u0940 \u0928\u0917\u0930",
        "ll": [
          77.505,
          12.932
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Jnanabharathi",
        "hindi": "\u091c\u094d\u091e\u093e\u0928\u092d\u093e\u0930\u0924\u0940 (\u092c\u0940\u092f\u0942)",
        "ll": [
          77.498,
          12.925
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Pattanagere",
        "hindi": "\u092a\u091f\u094d\u091f\u0923\u0917\u0947\u0930\u0947",
        "ll": [
          77.492,
          12.918
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Kengeri Bus Terminal",
        "hindi": "\u0915\u0947\u0902\u0917\u0947\u0930\u0940 \u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          77.485,
          12.912
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Kengeri",
        "hindi": "\u0915\u0947\u0902\u0917\u0947\u0930\u0940",
        "ll": [
          77.478,
          12.906
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Challaghatta",
        "hindi": "\u091a\u0932\u094d\u0932\u093e\u0918\u091f\u094d\u091f\u093e",
        "ll": [
          77.469,
          12.898
        ],
        "l": [
          "blr-purple"
        ]
      },
      {
        "n": "Madavara (BIEC)",
        "hindi": "\u092e\u093e\u0926\u0935\u093e\u0930 (\u092c\u0940\u0906\u0908\u0908\u0938\u0940)",
        "ll": [
          77.478,
          13.065
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Chikkabidarakallu",
        "hindi": "\u091a\u093f\u0915\u094d\u0915\u092c\u093f\u0926\u093e\u0930\u0915\u0932\u094d\u0932\u0941",
        "ll": [
          77.485,
          13.055
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Manjunathanagar",
        "hindi": "\u092e\u0902\u091c\u0941\u0928\u093e\u0925\u0928\u0917\u0930",
        "ll": [
          77.492,
          13.045
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Nagasandra",
        "hindi": "\u0928\u093e\u0917\u0938\u0902\u0926\u094d\u0930\u093e",
        "ll": [
          77.5,
          13.038
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Dasarahalli",
        "hindi": "\u0926\u093e\u0938\u0930\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.508,
          13.03
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Jalahalli",
        "hindi": "\u091c\u093e\u0932\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.515,
          13.022
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Peenya Industry",
        "hindi": "\u092a\u0940\u0928\u094d\u092f\u093e \u0907\u0902\u0921\u0938\u094d\u091f\u094d\u0930\u0940",
        "ll": [
          77.522,
          13.018
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Peenya",
        "hindi": "\u092a\u0940\u0928\u094d\u092f\u093e",
        "ll": [
          77.528,
          13.012
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Goraguntepalya",
        "hindi": "\u0917\u094b\u0930\u0917\u0941\u0902\u091f\u0947\u092a\u093e\u0932\u094d\u092f\u093e",
        "ll": [
          77.535,
          13.008
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Yeshwanthpur",
        "hindi": "\u092f\u0936\u0935\u0902\u0924\u092a\u0941\u0930",
        "ll": [
          77.545,
          13.004
        ],
        "l": [
          "blr-green"
        ],
        "interchange": true
      },
      {
        "n": "Sandal Soap Factory",
        "hindi": "\u0938\u0948\u0902\u0921\u0932 \u0938\u094b\u092a \u092b\u0948\u0915\u094d\u091f\u094d\u0930\u0940",
        "ll": [
          77.552,
          12.998
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Mahalakshmi",
        "hindi": "\u092e\u0939\u093e\u0932\u0915\u094d\u0937\u094d\u092e\u0940",
        "ll": [
          77.556,
          12.992
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Rajajinagar",
        "hindi": "\u0930\u093e\u091c\u093e\u091c\u0940\u0928\u0917\u0930",
        "ll": [
          77.56,
          12.988
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Mahakavi Kuvempu Road",
        "hindi": "\u0915\u0941\u0935\u0947\u092e\u094d\u092a\u0941 \u0930\u094b\u0921",
        "ll": [
          77.563,
          12.983
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Sampige Road",
        "hindi": "\u0938\u0902\u092a\u093f\u0917\u0947 \u0930\u094b\u0921",
        "ll": [
          77.567,
          12.98
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Chickpete",
        "hindi": "\u091a\u093f\u0915\u094d\u0915\u092a\u0947\u091f\u093e",
        "ll": [
          77.575,
          12.971
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Krishna Rajendra Market",
        "hindi": "\u0915\u0947\u0906\u0930 \u092e\u093e\u0930\u094d\u0915\u0947\u091f",
        "ll": [
          77.577,
          12.964
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "National College",
        "hindi": "\u0928\u0947\u0936\u0928\u0932 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          77.576,
          12.955
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Lalbagh",
        "hindi": "\u0932\u093e\u0932\u092c\u093e\u0917",
        "ll": [
          77.578,
          12.946
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "South End Circle",
        "hindi": "\u0938\u093e\u0909\u0925 \u090f\u0902\u0921 \u0938\u0930\u094d\u0915\u0932",
        "ll": [
          77.58,
          12.938
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Jayanagar",
        "hindi": "\u091c\u092f\u0928\u0917\u0930",
        "ll": [
          77.582,
          12.93
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "RV Road",
        "hindi": "\u0906\u0930\u0935\u0940 \u0930\u094b\u0921 (\u0930\u093e\u0937\u094d\u091f\u094d\u0930\u0940\u092f \u0935\u093f\u0926\u094d\u092f\u093e\u0932\u092f)",
        "ll": [
          77.583,
          12.922
        ],
        "l": [
          "blr-green",
          "blr-yellow"
        ],
        "interchange": true
      },
      {
        "n": "Banashankari",
        "hindi": "\u092c\u0928\u0936\u0902\u0915\u0930\u0940",
        "ll": [
          77.573,
          12.915
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "JP Nagar",
        "hindi": "\u091c\u0947\u092a\u0940 \u0928\u0917\u0930",
        "ll": [
          77.568,
          12.908
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Yelachenahalli",
        "hindi": "\u092f\u0932\u093e\u091a\u0947\u0928\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.565,
          12.898
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Konanakunte Cross",
        "hindi": "\u0915\u094b\u0923\u0928\u0915\u0941\u0902\u091f\u0947 \u0915\u094d\u0930\u0949\u0938",
        "ll": [
          77.56,
          12.888
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Doddakallasandra",
        "hindi": "\u0926\u094b\u0921\u094d\u0921\u0915\u0932\u094d\u0932\u093e\u0938\u093e\u0902\u0926\u094d\u0930\u093e",
        "ll": [
          77.555,
          12.879
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Vajrahalli",
        "hindi": "\u0935\u091c\u094d\u0930\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.548,
          12.87
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Thalaghattapura",
        "hindi": "\u0925\u0932\u0918\u091f\u094d\u091f\u092a\u0941\u0930\u093e",
        "ll": [
          77.54,
          12.862
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Silk Institute",
        "hindi": "\u0938\u093f\u0932\u094d\u0915 \u0907\u0902\u0938\u094d\u091f\u0940\u091f\u094d\u092f\u0942\u091f",
        "ll": [
          77.532,
          12.854
        ],
        "l": [
          "blr-green"
        ]
      },
      {
        "n": "Ragigudda",
        "hindi": "\u0930\u093e\u0917\u093f\u0917\u0941\u0921\u094d\u0921\u093e",
        "ll": [
          77.592,
          12.916
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Jayadeva Hospital",
        "hindi": "\u091c\u092f\u0926\u0947\u0935 \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          77.602,
          12.918
        ],
        "l": [
          "blr-yellow"
        ],
        "interchange": true
      },
      {
        "n": "BTM Layout",
        "hindi": "\u092c\u0940\u091f\u0940\u090f\u092e \u0932\u0947\u0906\u0909\u091f",
        "ll": [
          77.612,
          12.916
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Central Silk Board",
        "hindi": "\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0938\u093f\u0932\u094d\u0915 \u092c\u094b\u0930\u094d\u0921",
        "ll": [
          77.625,
          12.917
        ],
        "l": [
          "blr-yellow"
        ],
        "interchange": true
      },
      {
        "n": "Bommanahalli",
        "hindi": "\u092c\u094b\u092e\u094d\u092e\u0928\u0939\u0932\u094d\u0932\u0940",
        "ll": [
          77.632,
          12.905
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Hongasandra",
        "hindi": "\u0939\u094b\u0902\u0917\u093e\u0938\u093e\u0902\u0926\u094d\u0930\u093e",
        "ll": [
          77.638,
          12.895
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Kudlu Gate",
        "hindi": "\u0915\u0941\u0921\u0932\u0942 \u0917\u0947\u091f",
        "ll": [
          77.645,
          12.885
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Singasandra",
        "hindi": "\u0938\u093f\u0902\u0917\u093e\u0938\u093e\u0902\u0926\u094d\u0930\u093e",
        "ll": [
          77.652,
          12.875
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Hosa Road",
        "hindi": "\u0939\u094b\u0938\u093e \u0930\u094b\u0921",
        "ll": [
          77.658,
          12.865
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Beratena Agrahara",
        "hindi": "\u092c\u0947\u0930\u093e\u0924\u0947\u0928\u093e \u0905\u0917\u094d\u0930\u0939\u093e\u0930\u093e",
        "ll": [
          77.665,
          12.855
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Electronic City",
        "hindi": "\u0907\u0932\u0947\u0915\u094d\u091f\u094d\u0930\u0949\u0928\u093f\u0915 \u0938\u093f\u091f\u0940",
        "ll": [
          77.672,
          12.845
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Infosys Foundation",
        "hindi": "\u0907\u0928\u094d\u092b\u094b\u0938\u093f\u0938 \u092b\u093e\u0909\u0902\u0921\u0947\u0936\u0928",
        "ll": [
          77.678,
          12.835
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Huskur Road",
        "hindi": "\u0939\u0941\u0938\u094d\u0915\u0942\u0930 \u0930\u094b\u0921",
        "ll": [
          77.685,
          12.825
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Hebbagodi",
        "hindi": "\u0939\u0947\u092c\u094d\u092c\u093e\u0917\u094b\u0921\u0940",
        "ll": [
          77.692,
          12.815
        ],
        "l": [
          "blr-yellow"
        ]
      },
      {
        "n": "Bommasandra",
        "hindi": "\u092c\u094b\u092e\u094d\u092e\u093e\u0938\u093e\u0902\u0926\u094d\u0930\u093e",
        "ll": [
          77.698,
          12.805
        ],
        "l": [
          "blr-yellow"
        ]
      }
    ],
    "links": []
  },
  "kolkata": {
    "name": "Kolkata Metro (India's First Metro & Underwater Tunnel)",
    "hindi": "\u0915\u094b\u0932\u0915\u093e\u0924\u093e \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                88.28,
                22.42
              ],
              [
                88.29,
                22.66
              ],
              [
                88.38,
                22.68
              ],
              [
                88.46,
                22.65
              ],
              [
                88.45,
                22.48
              ],
              [
                88.38,
                22.4
              ],
              [
                88.28,
                22.42
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              88.355,
              22.665
            ],
            [
              88.36,
              22.63
            ],
            [
              88.368,
              22.61
            ],
            [
              88.352,
              22.585
            ],
            [
              88.338,
              22.57
            ],
            [
              88.328,
              22.55
            ],
            [
              88.31,
              22.53
            ],
            [
              88.28,
              22.49
            ],
            [
              88.25,
              22.45
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              88.344,
              22.516
            ],
            [
              88.348,
              22.495
            ],
            [
              88.365,
              22.47
            ],
            [
              88.395,
              22.44
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              88.375,
              22.605
            ],
            [
              88.4,
              22.59
            ],
            [
              88.42,
              22.56
            ],
            [
              88.44,
              22.52
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              88.4,
              22.6
            ],
            [
              88.405,
              22.56
            ],
            [
              88.395,
              22.5
            ],
            [
              88.385,
              22.45
            ],
            [
              88.39,
              22.43
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              88.328,
              22.554
            ],
            [
              88.28,
              22.575
            ],
            [
              88.24,
              22.59
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              88.355,
              22.655
            ],
            [
              88.4,
              22.645
            ],
            [
              88.44,
              22.64
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              88.345,
              22.64
            ],
            [
              88.34,
              22.585
            ],
            [
              88.325,
              22.54
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              88.371,
              22.567
            ],
            [
              88.385,
              22.59
            ],
            [
              88.392,
              22.622
            ],
            [
              88.39,
              22.66
            ]
          ]
        },
        {
          "g": [
            [
              88.341,
              22.583
            ],
            [
              88.31,
              22.58
            ],
            [
              88.275,
              22.58
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Howrah Heritage Railway Terminal",
          "ll": [
            88.342,
            22.583
          ],
          "r": 5
        },
        {
          "n": "Victoria Memorial Hall",
          "ll": [
            88.342,
            22.544
          ],
          "r": 5
        },
        {
          "n": "Esplanade & Writers' Building Core",
          "ll": [
            88.352,
            22.565
          ],
          "r": 5
        },
        {
          "n": "Salt Lake Sector V IT Hub",
          "ll": [
            88.432,
            22.57
          ],
          "r": 4
        },
        {
          "n": "Dakshineswar Kali Temple",
          "ll": [
            88.358,
            22.653
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "kol-l1",
        "nm": "Blue Line (Line 1: Dakshineswar - Kavi Subhash)",
        "c": "#2563eb",
        "seq": [
          "Dakshineswar",
          "Baranagar",
          "Noapara",
          "Dum Dum",
          "Belgachia",
          "Shyambazar",
          "Shovabazar",
          "Girish Park",
          "MG Road Kolkata",
          "Central Kolkata",
          "Chandni Chowk Kolkata",
          "Esplanade",
          "Park Street",
          "Maidan",
          "Netaji Bhavan",
          "Jatin Das Park",
          "Kalighat",
          "Rabindra Sarobar",
          "Mahanayak Uttam Kumar",
          "Netaji",
          "Masterda Surya Sen",
          "Gitanjali",
          "Kavi Nazrul",
          "Shahid Khudiram",
          "Kavi Subhash"
        ],
        "segs": [
          [
            [
              88.358,
              22.653
            ],
            [
              88.368,
              22.641
            ],
            [
              88.38,
              22.632
            ],
            [
              88.392,
              22.622
            ],
            [
              88.388,
              22.607
            ],
            [
              88.373,
              22.601
            ],
            [
              88.366,
              22.593
            ],
            [
              88.361,
              22.584
            ],
            [
              88.358,
              22.576
            ],
            [
              88.355,
              22.571
            ],
            [
              88.353,
              22.568
            ],
            [
              88.352,
              22.564
            ],
            [
              88.35,
              22.553
            ],
            [
              88.348,
              22.545
            ],
            [
              88.346,
              22.535
            ],
            [
              88.345,
              22.525
            ],
            [
              88.344,
              22.516
            ],
            [
              88.345,
              22.507
            ],
            [
              88.346,
              22.496
            ],
            [
              88.35,
              22.485
            ],
            [
              88.355,
              22.476
            ],
            [
              88.362,
              22.466
            ],
            [
              88.372,
              22.457
            ],
            [
              88.383,
              22.449
            ],
            [
              88.395,
              22.442
            ]
          ]
        ]
      },
      {
        "id": "kol-l2",
        "nm": "Green Line (Line 2 Underwater East-West: Howrah Maidan - Sector V)",
        "c": "#16a34a",
        "seq": [
          "Howrah Maidan",
          "Howrah Railway Station",
          "Mahakaran",
          "Esplanade",
          "Sealdah",
          "Phoolbagan",
          "Salt Lake Stadium",
          "Bengal Chemical",
          "City Centre",
          "Central Park",
          "Karunamoyee",
          "Salt Lake Sector V"
        ],
        "segs": [
          [
            [
              88.328,
              22.585
            ],
            [
              88.341,
              22.583
            ],
            [
              88.349,
              22.572
            ],
            [
              88.352,
              22.564
            ],
            [
              88.371,
              22.567
            ],
            [
              88.39,
              22.571
            ],
            [
              88.402,
              22.572
            ],
            [
              88.409,
              22.573
            ],
            [
              88.414,
              22.574
            ],
            [
              88.419,
              22.575
            ],
            [
              88.423,
              22.573
            ],
            [
              88.432,
              22.57
            ]
          ]
        ]
      },
      {
        "id": "kol-l3",
        "nm": "Purple Line (Line 3: Joka - Majerhat)",
        "c": "#7c3aed",
        "seq": [
          "Joka",
          "Thakurpukur",
          "Sakherbazar",
          "Behala Chowrasta",
          "Behala Bazar",
          "Taratala",
          "Majerhat"
        ],
        "segs": [
          [
            [
              88.305,
              22.443
            ],
            [
              88.312,
              22.455
            ],
            [
              88.317,
              22.468
            ],
            [
              88.322,
              22.482
            ],
            [
              88.325,
              22.495
            ],
            [
              88.327,
              22.508
            ],
            [
              88.33,
              22.518
            ]
          ]
        ]
      },
      {
        "id": "kol-l6",
        "nm": "Orange Line (Line 6: Kavi Subhash - Hemanta Mukhopadhyay)",
        "c": "#ea580c",
        "seq": [
          "Kavi Subhash",
          "Satyajit Ray",
          "Jyotirindra Nandy",
          "Kavi Sukanta",
          "Hemanta Mukhopadhyay"
        ],
        "segs": [
          [
            [
              88.395,
              22.442
            ],
            [
              88.398,
              22.46
            ],
            [
              88.401,
              22.478
            ],
            [
              88.403,
              22.496
            ],
            [
              88.402,
              22.514
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Dakshineswar",
        "hindi": "\u0926\u0915\u094d\u0937\u093f\u0923\u0947\u0936\u094d\u0935\u0930",
        "ll": [
          88.358,
          22.653
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Baranagar",
        "hindi": "\u092c\u0930\u093e\u0928\u0917\u0930",
        "ll": [
          88.368,
          22.641
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Noapara",
        "hindi": "\u0928\u094b\u0906\u092a\u093e\u0921\u093c\u093e",
        "ll": [
          88.38,
          22.632
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Dum Dum",
        "hindi": "\u0926\u092e \u0926\u092e",
        "ll": [
          88.392,
          22.622
        ],
        "l": [
          "kol-l1"
        ],
        "interchange": true
      },
      {
        "n": "Belgachia",
        "hindi": "\u092c\u0947\u0932\u0917\u091b\u093f\u092f\u093e",
        "ll": [
          88.388,
          22.607
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Shyambazar",
        "hindi": "\u0936\u094d\u092f\u093e\u092e\u092c\u093e\u091c\u093e\u0930",
        "ll": [
          88.373,
          22.601
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Shovabazar",
        "hindi": "\u0936\u094b\u092d\u093e\u092c\u093e\u091c\u093e\u0930",
        "ll": [
          88.366,
          22.593
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Girish Park",
        "hindi": "\u0917\u093f\u0930\u0940\u0936 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          88.361,
          22.584
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "MG Road Kolkata",
        "hindi": "\u090f\u092e\u091c\u0940 \u0930\u094b\u0921 \u0915\u094b\u0932\u0915\u093e\u0924\u093e",
        "ll": [
          88.358,
          22.576
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Central Kolkata",
        "hindi": "\u0938\u0947\u0902\u091f\u094d\u0930\u0932",
        "ll": [
          88.355,
          22.571
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Chandni Chowk Kolkata",
        "hindi": "\u091a\u093e\u0902\u0926\u0928\u0940 \u091a\u094c\u0915",
        "ll": [
          88.353,
          22.568
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Esplanade",
        "hindi": "\u090f\u0938\u094d\u092a\u094d\u0932\u0947\u0928\u0947\u0921",
        "ll": [
          88.352,
          22.564
        ],
        "l": [
          "kol-l1",
          "kol-l2"
        ],
        "interchange": true
      },
      {
        "n": "Park Street",
        "hindi": "\u092a\u093e\u0930\u094d\u0915 \u0938\u094d\u091f\u094d\u0930\u0940\u091f",
        "ll": [
          88.35,
          22.553
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Maidan",
        "hindi": "\u092e\u0948\u0926\u093e\u0928",
        "ll": [
          88.348,
          22.545
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Netaji Bhavan",
        "hindi": "\u0928\u0947\u0924\u093e\u091c\u0940 \u092d\u0935\u0928",
        "ll": [
          88.346,
          22.535
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Jatin Das Park",
        "hindi": "\u091c\u0924\u093f\u0928 \u0926\u093e\u0938 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          88.345,
          22.525
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Kalighat",
        "hindi": "\u0915\u093e\u0932\u0940\u0918\u093e\u091f",
        "ll": [
          88.344,
          22.516
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Rabindra Sarobar",
        "hindi": "\u0930\u0935\u0940\u0902\u0926\u094d\u0930 \u0938\u0930\u094b\u0935\u0930",
        "ll": [
          88.345,
          22.507
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Mahanayak Uttam Kumar",
        "hindi": "\u092e\u0939\u093e\u0928\u094d\u092f\u093e\u092f\u0915 \u0909\u0924\u094d\u0924\u092e \u0915\u0941\u092e\u093e\u0930 (\u091f\u0949\u0932\u0940\u0917\u0902\u091c)",
        "ll": [
          88.346,
          22.496
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Netaji",
        "hindi": "\u0928\u0947\u0924\u093e\u091c\u0940",
        "ll": [
          88.35,
          22.485
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Masterda Surya Sen",
        "hindi": "\u092e\u093e\u0938\u094d\u091f\u0930\u0926\u093e \u0938\u0942\u0930\u094d\u092f \u0938\u0947\u0928",
        "ll": [
          88.355,
          22.476
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Gitanjali",
        "hindi": "\u0917\u0940\u0924\u093e\u0902\u091c\u0932\u093f",
        "ll": [
          88.362,
          22.466
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Kavi Nazrul",
        "hindi": "\u0915\u0935\u093f \u0928\u091c\u0930\u0941\u0932",
        "ll": [
          88.372,
          22.457
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Shahid Khudiram",
        "hindi": "\u0936\u0939\u0940\u0926 \u0916\u0941\u0926\u0940\u0930\u093e\u092e",
        "ll": [
          88.383,
          22.449
        ],
        "l": [
          "kol-l1"
        ]
      },
      {
        "n": "Kavi Subhash",
        "hindi": "\u0915\u0935\u093f \u0938\u0941\u092d\u093e\u0937 (\u0928\u094d\u092f\u0942 \u0917\u0930\u093f\u092f\u093e)",
        "ll": [
          88.395,
          22.442
        ],
        "l": [
          "kol-l1",
          "kol-l6"
        ],
        "interchange": true
      },
      {
        "n": "Howrah Maidan",
        "hindi": "\u0939\u093e\u0935\u0921\u093c\u093e \u092e\u0948\u0926\u093e\u0928",
        "ll": [
          88.328,
          22.585
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Howrah Railway Station",
        "hindi": "\u0939\u093e\u0935\u0921\u093c\u093e \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928 (\u0905\u0902\u0921\u0930\u0935\u0949\u091f\u0930)",
        "ll": [
          88.341,
          22.583
        ],
        "l": [
          "kol-l2"
        ],
        "interchange": true
      },
      {
        "n": "Mahakaran",
        "hindi": "\u092e\u0939\u093e\u0915\u0930\u0923 (\u0930\u093e\u0907\u091f\u0930\u094d\u0938 \u092c\u093f\u0932\u094d\u0921\u093f\u0902\u0917)",
        "ll": [
          88.349,
          22.572
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Sealdah",
        "hindi": "\u0938\u093f\u092f\u093e\u0932\u0926\u0939",
        "ll": [
          88.371,
          22.567
        ],
        "l": [
          "kol-l2"
        ],
        "interchange": true
      },
      {
        "n": "Phoolbagan",
        "hindi": "\u092b\u0942\u0932\u092c\u093e\u0917\u093e\u0928",
        "ll": [
          88.39,
          22.571
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Salt Lake Stadium",
        "hindi": "\u0938\u0949\u0932\u094d\u091f \u0932\u0947\u0915 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e",
        "ll": [
          88.402,
          22.572
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Bengal Chemical",
        "hindi": "\u092c\u0902\u0917\u093e\u0932 \u0915\u0947\u092e\u093f\u0915\u0932",
        "ll": [
          88.409,
          22.573
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "City Centre",
        "hindi": "\u0938\u093f\u091f\u0940 \u0938\u0947\u0902\u091f\u0930",
        "ll": [
          88.414,
          22.574
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Central Park",
        "hindi": "\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          88.419,
          22.575
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Karunamoyee",
        "hindi": "\u0915\u0930\u0941\u0923\u093e\u092e\u092f\u0940",
        "ll": [
          88.423,
          22.573
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Salt Lake Sector V",
        "hindi": "\u0938\u0949\u0932\u094d\u091f \u0932\u0947\u0915 \u0938\u0947\u0915\u094d\u091f\u0930 5",
        "ll": [
          88.432,
          22.57
        ],
        "l": [
          "kol-l2"
        ]
      },
      {
        "n": "Joka",
        "hindi": "\u091c\u094b\u0915\u093e",
        "ll": [
          88.305,
          22.443
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Thakurpukur",
        "hindi": "\u0920\u093e\u0915\u0941\u0930\u092a\u0941\u0915\u0941\u0930",
        "ll": [
          88.312,
          22.455
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Sakherbazar",
        "hindi": "\u0938\u0916\u0947\u0930\u092c\u093e\u091c\u093e\u0930",
        "ll": [
          88.317,
          22.468
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Behala Chowrasta",
        "hindi": "\u092c\u0947\u0939\u093e\u0932\u093e \u091a\u094c\u0930\u093e\u0938\u094d\u0924\u093e",
        "ll": [
          88.322,
          22.482
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Behala Bazar",
        "hindi": "\u092c\u0947\u0939\u093e\u0932\u093e \u092c\u093e\u091c\u093e\u0930",
        "ll": [
          88.325,
          22.495
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Taratala",
        "hindi": "\u0924\u093e\u0930\u093e\u0924\u0932\u093e",
        "ll": [
          88.327,
          22.508
        ],
        "l": [
          "kol-l3"
        ]
      },
      {
        "n": "Majerhat",
        "hindi": "\u092e\u093e\u091d\u0947\u0930\u0939\u093e\u091f",
        "ll": [
          88.33,
          22.518
        ],
        "l": [
          "kol-l3"
        ],
        "interchange": true
      },
      {
        "n": "Satyajit Ray",
        "hindi": "\u0938\u0924\u094d\u092f\u091c\u0940\u0924 \u0930\u0947",
        "ll": [
          88.398,
          22.46
        ],
        "l": [
          "kol-l6"
        ]
      },
      {
        "n": "Jyotirindra Nandy",
        "hindi": "\u091c\u094d\u092f\u094b\u0924\u093f\u0930\u093f\u0902\u0926\u094d\u0930 \u0928\u0902\u0926\u0940",
        "ll": [
          88.401,
          22.478
        ],
        "l": [
          "kol-l6"
        ]
      },
      {
        "n": "Kavi Sukanta",
        "hindi": "\u0915\u0935\u093f \u0938\u0941\u0915\u093e\u0902\u0924",
        "ll": [
          88.403,
          22.496
        ],
        "l": [
          "kol-l6"
        ]
      },
      {
        "n": "Hemanta Mukhopadhyay",
        "hindi": "\u0939\u0947\u092e\u0902\u0924 \u092e\u0941\u0916\u094b\u092a\u093e\u0927\u094d\u092f\u093e\u092f (\u0930\u0942\u092c\u0940)",
        "ll": [
          88.402,
          22.514
        ],
        "l": [
          "kol-l6"
        ]
      }
    ],
    "links": []
  },
  "chennai": {
    "name": "Chennai Metro (CMRL)",
    "hindi": "\u0b9a\u0bc6\u0ba9\u0bcd\u0ba9\u0bc8 \u0bae\u0bc6\u0b9f\u0bcd\u0bb0\u0bcb",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                80.12,
                12.95
              ],
              [
                80.14,
                13.15
              ],
              [
                80.25,
                13.18
              ],
              [
                80.31,
                13.12
              ],
              [
                80.29,
                13.0
              ],
              [
                80.25,
                12.92
              ],
              [
                80.16,
                12.9
              ],
              [
                80.12,
                12.95
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              80.31,
              13.18
            ],
            [
              80.3,
              13.12
            ],
            [
              80.295,
              13.09
            ],
            [
              80.285,
              13.05
            ],
            [
              80.278,
              13.02
            ],
            [
              80.268,
              12.98
            ],
            [
              80.25,
              12.9
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              80.18,
              13.075
            ],
            [
              80.22,
              13.078
            ],
            [
              80.26,
              13.08
            ],
            [
              80.285,
              13.067
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              80.18,
              13.005
            ],
            [
              80.22,
              13.015
            ],
            [
              80.25,
              13.01
            ],
            [
              80.272,
              13.008
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              80.28,
              13.11
            ],
            [
              80.275,
              13.05
            ],
            [
              80.26,
              12.99
            ],
            [
              80.245,
              12.93
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              80.275,
              13.082
            ],
            [
              80.25,
              13.055
            ],
            [
              80.225,
              13.025
            ],
            [
              80.201,
              13.004
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              80.201,
              13.004
            ],
            [
              80.165,
              12.98
            ],
            [
              80.13,
              12.94
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              80.2,
              13.11
            ],
            [
              80.194,
              13.073
            ],
            [
              80.2,
              13.03
            ],
            [
              80.201,
              13.004
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              80.25,
              13.005
            ],
            [
              80.245,
              12.96
            ],
            [
              80.23,
              12.9
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              80.275,
              13.082
            ],
            [
              80.24,
              13.1
            ],
            [
              80.2,
              13.11
            ],
            [
              80.15,
              13.12
            ]
          ]
        },
        {
          "g": [
            [
              80.29,
              13.09
            ],
            [
              80.26,
              13.08
            ],
            [
              80.23,
              13.035
            ],
            [
              80.21,
              13.008
            ],
            [
              80.165,
              12.98
            ],
            [
              80.12,
              12.92
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Puratchi Thalaivar Dr. MGR Central",
          "ll": [
            80.275,
            13.082
          ],
          "r": 5
        },
        {
          "n": "Marina Beach & Promenade",
          "ll": [
            80.285,
            13.05
          ],
          "r": 5
        },
        {
          "n": "Kathipara Cloverleaf Junction",
          "ll": [
            80.201,
            13.004
          ],
          "r": 4
        },
        {
          "n": "Chennai International Airport",
          "ll": [
            80.165,
            12.98
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "chn-blue",
        "nm": "Blue Line (Line 1: Wimco Nagar - Airport)",
        "c": "#2563eb",
        "seq": [
          "Wimco Nagar",
          "Tiruvottriyur",
          "Tollgate",
          "Washermanpet",
          "High Court Chennai",
          "Chennai Central",
          "Government Estate",
          "LIC Chennai",
          "Thousand Lights",
          "AG-DMS",
          "Teynampet",
          "Nandanam",
          "Saidapet",
          "Little Mount",
          "Guindy",
          "Alandur",
          "Meenambakkam",
          "Chennai International Airport"
        ],
        "segs": [
          [
            [
              80.301,
              13.168
            ],
            [
              80.298,
              13.155
            ],
            [
              80.294,
              13.136
            ],
            [
              80.288,
              13.111
            ],
            [
              80.286,
              13.09
            ],
            [
              80.275,
              13.082
            ],
            [
              80.273,
              13.069
            ],
            [
              80.266,
              13.062
            ],
            [
              80.255,
              13.056
            ],
            [
              80.248,
              13.045
            ],
            [
              80.245,
              13.038
            ],
            [
              80.239,
              13.029
            ],
            [
              80.228,
              13.022
            ],
            [
              80.221,
              13.016
            ],
            [
              80.213,
              13.008
            ],
            [
              80.201,
              13.004
            ],
            [
              80.182,
              12.989
            ],
            [
              80.165,
              12.98
            ]
          ]
        ]
      },
      {
        "id": "chn-green",
        "nm": "Green Line (Line 2: Chennai Central - St. Thomas Mount)",
        "c": "#16a34a",
        "seq": [
          "Chennai Central",
          "Egmore",
          "Nehru Park",
          "Kilpauk Medical College",
          "Pachaiyappa's College",
          "Shenoy Nagar",
          "Anna Nagar East",
          "Anna Nagar Tower",
          "Thirumangalam",
          "Koyambedu",
          "CMBT",
          "Arumbakkam",
          "Vadapalani",
          "Ashok Nagar",
          "Ekkattuthangal",
          "Alandur",
          "St. Thomas Mount"
        ],
        "segs": [
          [
            [
              80.275,
              13.082
            ],
            [
              80.261,
              13.078
            ],
            [
              80.252,
              13.078
            ],
            [
              80.242,
              13.078
            ],
            [
              80.233,
              13.077
            ],
            [
              80.225,
              13.078
            ],
            [
              80.218,
              13.084
            ],
            [
              80.212,
              13.085
            ],
            [
              80.199,
              13.085
            ],
            [
              80.195,
              13.074
            ],
            [
              80.203,
              13.067
            ],
            [
              80.208,
              13.061
            ],
            [
              80.211,
              13.051
            ],
            [
              80.212,
              13.036
            ],
            [
              80.205,
              13.02
            ],
            [
              80.201,
              13.004
            ],
            [
              80.198,
              12.995
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Wimco Nagar",
        "hindi": "\u0935\u093f\u092e\u0915\u094b \u0928\u0917\u0930",
        "ll": [
          80.301,
          13.168
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Tiruvottriyur",
        "hindi": "\u0924\u093f\u0930\u0941\u0935\u094b\u091f\u094d\u091f\u093f\u092f\u0942\u0930",
        "ll": [
          80.298,
          13.155
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Tollgate",
        "hindi": "\u091f\u094b\u0932\u0917\u0947\u091f",
        "ll": [
          80.294,
          13.136
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Washermanpet",
        "hindi": "\u0935\u0949\u0936\u0930\u092e\u0948\u0928\u092a\u0947\u091f",
        "ll": [
          80.288,
          13.111
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "High Court Chennai",
        "hindi": "\u0939\u093e\u0908 \u0915\u094b\u0930\u094d\u091f",
        "ll": [
          80.286,
          13.09
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Chennai Central",
        "hindi": "\u091a\u0947\u0928\u094d\u0928\u0908 \u0938\u0947\u0902\u091f\u094d\u0930\u0932",
        "ll": [
          80.275,
          13.082
        ],
        "l": [
          "chn-blue",
          "chn-green"
        ],
        "interchange": true
      },
      {
        "n": "Government Estate",
        "hindi": "\u0917\u0935\u0930\u094d\u0928\u092e\u0947\u0902\u091f \u090f\u0938\u094d\u091f\u0947\u091f",
        "ll": [
          80.273,
          13.069
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "LIC Chennai",
        "hindi": "\u090f\u0932\u0906\u0908\u0938\u0940",
        "ll": [
          80.266,
          13.062
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Thousand Lights",
        "hindi": "\u0925\u093e\u0909\u091c\u0947\u0902\u0921 \u0932\u093e\u0907\u091f\u094d\u0938",
        "ll": [
          80.255,
          13.056
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "AG-DMS",
        "hindi": "\u090f\u091c\u0940-\u0921\u0940\u090f\u092e\u090f\u0938",
        "ll": [
          80.248,
          13.045
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Teynampet",
        "hindi": "\u0924\u0947\u0928\u093e\u092e\u092a\u0947\u091f",
        "ll": [
          80.245,
          13.038
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Nandanam",
        "hindi": "\u0928\u0902\u0926\u0928\u092e",
        "ll": [
          80.239,
          13.029
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Saidapet",
        "hindi": "\u0938\u0948\u0926\u093e\u092a\u0947\u091f",
        "ll": [
          80.228,
          13.022
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Little Mount",
        "hindi": "\u0932\u093f\u091f\u093f\u0932 \u092e\u093e\u0909\u0902\u091f",
        "ll": [
          80.221,
          13.016
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Guindy",
        "hindi": "\u0917\u093f\u0902\u0921\u0940",
        "ll": [
          80.213,
          13.008
        ],
        "l": [
          "chn-blue"
        ],
        "interchange": true
      },
      {
        "n": "Alandur",
        "hindi": "\u0905\u0932\u0902\u0926\u0942\u0930",
        "ll": [
          80.201,
          13.004
        ],
        "l": [
          "chn-blue",
          "chn-green"
        ],
        "interchange": true
      },
      {
        "n": "Meenambakkam",
        "hindi": "\u092e\u0940\u0928\u092e\u094d\u092c\u093e\u0915\u094d\u0915\u092e",
        "ll": [
          80.182,
          12.989
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Chennai International Airport",
        "hindi": "\u091a\u0947\u0928\u094d\u0928\u0908 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          80.165,
          12.98
        ],
        "l": [
          "chn-blue"
        ]
      },
      {
        "n": "Egmore",
        "hindi": "\u090f\u0917\u094d\u092e\u094b\u0930",
        "ll": [
          80.261,
          13.078
        ],
        "l": [
          "chn-green"
        ],
        "interchange": true
      },
      {
        "n": "Nehru Park",
        "hindi": "\u0928\u0947\u0939\u0930\u0942 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          80.252,
          13.078
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Kilpauk Medical College",
        "hindi": "\u0915\u093f\u0932\u094d\u092a\u0949\u0915 \u092e\u0947\u0921\u093f\u0915\u0932 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          80.242,
          13.078
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Pachaiyappa's College",
        "hindi": "\u092a\u091a\u092f\u092a\u094d\u092a\u093e \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          80.233,
          13.077
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Shenoy Nagar",
        "hindi": "\u0936\u0947\u0928\u0949\u092f \u0928\u0917\u0930",
        "ll": [
          80.225,
          13.078
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Anna Nagar East",
        "hindi": "\u0905\u0928\u094d\u0928\u093e \u0928\u0917\u0930 \u0908\u0938\u094d\u091f",
        "ll": [
          80.218,
          13.084
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Anna Nagar Tower",
        "hindi": "\u0905\u0928\u094d\u0928\u093e \u0928\u0917\u0930 \u091f\u0949\u0935\u0930",
        "ll": [
          80.212,
          13.085
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Thirumangalam",
        "hindi": "\u0925\u093f\u0930\u0941\u092e\u0902\u0917\u0932\u092e",
        "ll": [
          80.199,
          13.085
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Koyambedu",
        "hindi": "\u0915\u094b\u092f\u092e\u094d\u092c\u0947\u0921\u0941",
        "ll": [
          80.195,
          13.074
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "CMBT",
        "hindi": "\u0938\u0940\u090f\u092e\u092c\u0940\u091f\u0940 \u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          80.203,
          13.067
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Arumbakkam",
        "hindi": "\u0905\u0930\u0941\u092e\u094d\u092c\u093e\u0915\u094d\u0915\u092e",
        "ll": [
          80.208,
          13.061
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Vadapalani",
        "hindi": "\u0935\u0921\u093e\u092a\u0932\u093e\u0928\u0940",
        "ll": [
          80.211,
          13.051
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Ashok Nagar",
        "hindi": "\u0905\u0936\u094b\u0915 \u0928\u0917\u0930",
        "ll": [
          80.212,
          13.036
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "Ekkattuthangal",
        "hindi": "\u090f\u0915\u094d\u0915\u093e\u091f\u094d\u091f\u0941\u0925\u093e\u0902\u0917\u0932",
        "ll": [
          80.205,
          13.02
        ],
        "l": [
          "chn-green"
        ]
      },
      {
        "n": "St. Thomas Mount",
        "hindi": "\u0938\u0947\u0902\u091f \u0925\u0949\u092e\u0938 \u092e\u093e\u0909\u0902\u091f",
        "ll": [
          80.198,
          12.995
        ],
        "l": [
          "chn-green"
        ],
        "interchange": true
      }
    ],
    "links": []
  },
  "hyderabad": {
    "name": "Hyderabad Metro (HMRL)",
    "hindi": "\u0c39\u0c48\u0c26\u0c30\u0c3e\u0c2c\u0c3e\u0c26\u0c4d \u0c2e\u0c46\u0c1f\u0c4d\u0c30\u0c4b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                78.3,
                17.32
              ],
              [
                78.33,
                17.52
              ],
              [
                78.5,
                17.54
              ],
              [
                78.62,
                17.44
              ],
              [
                78.6,
                17.3
              ],
              [
                78.44,
                17.26
              ],
              [
                78.3,
                17.32
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              78.32,
              17.37
            ],
            [
              78.4,
              17.375
            ],
            [
              78.48,
              17.378
            ],
            [
              78.56,
              17.37
            ],
            [
              78.64,
              17.36
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              78.465,
              17.42
            ],
            [
              78.475,
              17.435
            ],
            [
              78.485,
              17.425
            ],
            [
              78.475,
              17.415
            ],
            [
              78.465,
              17.42
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              78.3,
              17.38
            ],
            [
              78.32,
              17.375
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              78.34,
              17.45
            ],
            [
              78.32,
              17.52
            ],
            [
              78.46,
              17.55
            ],
            [
              78.58,
              17.48
            ],
            [
              78.6,
              17.36
            ],
            [
              78.48,
              17.28
            ],
            [
              78.36,
              17.34
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              78.44,
              17.39
            ],
            [
              78.435,
              17.35
            ],
            [
              78.43,
              17.32
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              78.361,
              17.496
            ],
            [
              78.448,
              17.437
            ],
            [
              78.48,
              17.38
            ],
            [
              78.55,
              17.35
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              78.32,
              17.48
            ],
            [
              78.44,
              17.45
            ],
            [
              78.503,
              17.434
            ],
            [
              78.54,
              17.41
            ]
          ]
        },
        {
          "g": [
            [
              78.503,
              17.434
            ],
            [
              78.495,
              17.39
            ],
            [
              78.47,
              17.33
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Charminar Historic Core",
          "ll": [
            78.474,
            17.361
          ],
          "r": 5
        },
        {
          "n": "Hitec City Cyber Towers",
          "ll": [
            78.375,
            17.45
          ],
          "r": 5
        },
        {
          "n": "Ameerpet Transit Interchange",
          "ll": [
            78.448,
            17.437
          ],
          "r": 4
        },
        {
          "n": "Secunderabad Railway Terminal",
          "ll": [
            78.503,
            17.434
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "hyd-red",
        "nm": "Red Line (Corridor 1: Miyapur - LB Nagar)",
        "c": "#dc2626",
        "seq": [
          "Miyapur",
          "JNTU College",
          "KPHB Colony",
          "Kukatpally",
          "Bharat Nagar",
          "Erragadda",
          "ESI Hospital",
          "Ameerpet",
          "Punjagutta",
          "Irrum Manzil",
          "Khairatabad",
          "Lakdi-ka-pul",
          "Assembly",
          "Nampally",
          "Gandhi Bhavan",
          "MGBS",
          "Malakpet",
          "Dilsukhnagar",
          "Chaitanyapuri",
          "Victoria Memorial",
          "LB Nagar"
        ],
        "segs": [
          [
            [
              78.361,
              17.496
            ],
            [
              78.388,
              17.494
            ],
            [
              78.401,
              17.492
            ],
            [
              78.411,
              17.487
            ],
            [
              78.423,
              17.466
            ],
            [
              78.432,
              17.458
            ],
            [
              78.441,
              17.447
            ],
            [
              78.448,
              17.437
            ],
            [
              78.452,
              17.426
            ],
            [
              78.456,
              17.418
            ],
            [
              78.461,
              17.411
            ],
            [
              78.465,
              17.404
            ],
            [
              78.468,
              17.397
            ],
            [
              78.471,
              17.391
            ],
            [
              78.474,
              17.385
            ],
            [
              78.482,
              17.378
            ],
            [
              78.496,
              17.374
            ],
            [
              78.525,
              17.368
            ],
            [
              78.537,
              17.364
            ],
            [
              78.546,
              17.359
            ],
            [
              78.553,
              17.352
            ]
          ]
        ]
      },
      {
        "id": "hyd-blue",
        "nm": "Blue Line (Corridor 2: Nagole - Raidurg)",
        "c": "#2563eb",
        "seq": [
          "Nagole",
          "Uppal",
          "Stadium",
          "NGRI",
          "Habsiguda",
          "Tarnaka",
          "Mettuguda",
          "Secunderabad East",
          "Parade Ground",
          "Paradise",
          "Begumpet",
          "Ameerpet",
          "Madhura Nagar",
          "Yusufguda",
          "Jubilee Hills Checkpost",
          "Peddamma Gudi",
          "Madhapur",
          "Durgam Cheruvu",
          "Hitec City",
          "Raidurg"
        ],
        "segs": [
          [
            [
              78.577,
              17.387
            ],
            [
              78.568,
              17.399
            ],
            [
              78.56,
              17.404
            ],
            [
              78.553,
              17.411
            ],
            [
              78.545,
              17.418
            ],
            [
              78.53,
              17.428
            ],
            [
              78.517,
              17.431
            ],
            [
              78.504,
              17.435
            ],
            [
              78.498,
              17.444
            ],
            [
              78.487,
              17.441
            ],
            [
              78.462,
              17.439
            ],
            [
              78.448,
              17.437
            ],
            [
              78.439,
              17.438
            ],
            [
              78.431,
              17.437
            ],
            [
              78.418,
              17.432
            ],
            [
              78.411,
              17.435
            ],
            [
              78.398,
              17.441
            ],
            [
              78.391,
              17.444
            ],
            [
              78.384,
              17.446
            ],
            [
              78.375,
              17.442
            ]
          ]
        ]
      },
      {
        "id": "hyd-green",
        "nm": "Green Line (Corridor 3: JBS - MGBS)",
        "c": "#16a34a",
        "seq": [
          "JBS Parade Ground",
          "Secunderabad West",
          "Gandhi Hospital",
          "Musheerabad",
          "RTC X Roads",
          "Chikkadpally",
          "Narayanguda",
          "Sultan Bazaar",
          "MGBS"
        ],
        "segs": [
          [
            [
              78.498,
              17.451
            ],
            [
              78.502,
              17.438
            ],
            [
              78.507,
              17.424
            ],
            [
              78.508,
              17.415
            ],
            [
              78.505,
              17.404
            ],
            [
              78.501,
              17.397
            ],
            [
              78.496,
              17.391
            ],
            [
              78.489,
              17.384
            ],
            [
              78.482,
              17.378
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Miyapur",
        "hindi": "\u092e\u093f\u092f\u093e\u092a\u0941\u0930",
        "ll": [
          78.361,
          17.496
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "JNTU College",
        "hindi": "\u091c\u0947\u090f\u0928\u091f\u0940\u092f\u0942 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          78.388,
          17.494
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "KPHB Colony",
        "hindi": "\u0915\u0947\u092a\u0940\u090f\u091a\u092c\u0940 \u0915\u0949\u0932\u094b\u0928\u0940",
        "ll": [
          78.401,
          17.492
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Kukatpally",
        "hindi": "\u0915\u0942\u0915\u091f\u092a\u0932\u094d\u0932\u0940",
        "ll": [
          78.411,
          17.487
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Bharat Nagar",
        "hindi": "\u092d\u093e\u0930\u0924 \u0928\u0917\u0930",
        "ll": [
          78.423,
          17.466
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Erragadda",
        "hindi": "\u090f\u0930\u094d\u0930\u093e\u0917\u0921\u094d\u0921\u093e",
        "ll": [
          78.432,
          17.458
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "ESI Hospital",
        "hindi": "\u0908\u090f\u0938\u0906\u0908 \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          78.441,
          17.447
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Ameerpet",
        "hindi": "\u0905\u092e\u0940\u0930\u092a\u0947\u091f (\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0907\u0902\u091f\u0930\u091a\u0947\u0902\u091c)",
        "ll": [
          78.448,
          17.437
        ],
        "l": [
          "hyd-red",
          "hyd-blue"
        ],
        "interchange": true
      },
      {
        "n": "Punjagutta",
        "hindi": "\u092a\u0902\u091c\u093e\u0917\u0941\u091f\u094d\u091f\u093e",
        "ll": [
          78.452,
          17.426
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Irrum Manzil",
        "hindi": "\u0907\u0930\u094d\u0930\u092e \u092e\u0902\u091c\u093f\u0932",
        "ll": [
          78.456,
          17.418
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Khairatabad",
        "hindi": "\u0916\u0948\u0930\u093e\u0924\u093e\u092c\u093e\u0926",
        "ll": [
          78.461,
          17.411
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Lakdi-ka-pul",
        "hindi": "\u0932\u0915\u0921\u093c\u0940 \u0915\u093e \u092a\u0941\u0932",
        "ll": [
          78.465,
          17.404
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Assembly",
        "hindi": "\u0905\u0938\u0947\u0902\u092c\u0932\u0940",
        "ll": [
          78.468,
          17.397
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Nampally",
        "hindi": "\u0928\u093e\u092e\u092a\u0932\u094d\u0932\u0940 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          78.471,
          17.391
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Gandhi Bhavan",
        "hindi": "\u0917\u093e\u0902\u0927\u0940 \u092d\u0935\u0928",
        "ll": [
          78.474,
          17.385
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "MGBS",
        "hindi": "\u090f\u092e\u091c\u0940\u092c\u0940\u090f\u0938 \u092c\u0938 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          78.482,
          17.378
        ],
        "l": [
          "hyd-red",
          "hyd-green"
        ],
        "interchange": true
      },
      {
        "n": "Malakpet",
        "hindi": "\u092e\u0932\u0915\u092a\u0947\u091f",
        "ll": [
          78.496,
          17.374
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Dilsukhnagar",
        "hindi": "\u0926\u093f\u0932\u0938\u0941\u0916\u0928\u0917\u0930",
        "ll": [
          78.525,
          17.368
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Chaitanyapuri",
        "hindi": "\u091a\u0948\u0924\u0928\u094d\u092f\u092a\u0941\u0930\u0940",
        "ll": [
          78.537,
          17.364
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Victoria Memorial",
        "hindi": "\u0935\u093f\u0915\u094d\u091f\u094b\u0930\u093f\u092f\u093e \u092e\u0947\u092e\u094b\u0930\u093f\u092f\u0932",
        "ll": [
          78.546,
          17.359
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "LB Nagar",
        "hindi": "\u090f\u0932\u092c\u0940 \u0928\u0917\u0930",
        "ll": [
          78.553,
          17.352
        ],
        "l": [
          "hyd-red"
        ]
      },
      {
        "n": "Raidurg",
        "hindi": "\u0930\u093e\u092f\u0926\u0941\u0930\u094d\u0917",
        "ll": [
          78.375,
          17.442
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Hitec City",
        "hindi": "\u0939\u093e\u0908\u091f\u0947\u0915 \u0938\u093f\u091f\u0940",
        "ll": [
          78.384,
          17.446
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Durgam Cheruvu",
        "hindi": "\u0926\u0941\u0930\u094d\u0917\u092e \u091a\u0947\u0930\u0941\u0935\u0942",
        "ll": [
          78.391,
          17.444
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Madhapur",
        "hindi": "\u092e\u093e\u0927\u093e\u092a\u0941\u0930",
        "ll": [
          78.398,
          17.441
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Peddamma Gudi",
        "hindi": "\u092a\u0947\u0926\u094d\u0926\u092e\u094d\u092e\u093e \u0917\u0941\u0921\u093c\u0940",
        "ll": [
          78.411,
          17.435
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Jubilee Hills Checkpost",
        "hindi": "\u091c\u0941\u092c\u0932\u0940 \u0939\u093f\u0932\u094d\u0938 \u091a\u0947\u0915\u092a\u094b\u0938\u094d\u091f",
        "ll": [
          78.418,
          17.432
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Yusufguda",
        "hindi": "\u092f\u0942\u0938\u0941\u092b\u0917\u0941\u0921\u093c\u093e",
        "ll": [
          78.431,
          17.437
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Madhura Nagar",
        "hindi": "\u092e\u0927\u0941\u0930\u093e \u0928\u0917\u0930",
        "ll": [
          78.439,
          17.438
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Begumpet",
        "hindi": "\u092c\u0947\u0917\u092e\u092a\u0947\u091f",
        "ll": [
          78.462,
          17.439
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Paradise",
        "hindi": "\u092a\u0948\u0930\u093e\u0921\u093e\u0907\u091c",
        "ll": [
          78.487,
          17.441
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Parade Ground",
        "hindi": "\u092a\u0930\u0947\u0921 \u0917\u094d\u0930\u093e\u0909\u0902\u0921",
        "ll": [
          78.498,
          17.444
        ],
        "l": [
          "hyd-blue",
          "hyd-green"
        ],
        "interchange": true
      },
      {
        "n": "Secunderabad East",
        "hindi": "\u0938\u093f\u0915\u0902\u0926\u0930\u093e\u092c\u093e\u0926 \u0908\u0938\u094d\u091f",
        "ll": [
          78.504,
          17.435
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Mettuguda",
        "hindi": "\u092e\u0947\u091f\u094d\u091f\u0941\u0917\u0941\u0921\u093c\u093e",
        "ll": [
          78.517,
          17.431
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Tarnaka",
        "hindi": "\u0924\u093e\u0930\u0928\u093e\u0915\u093e",
        "ll": [
          78.53,
          17.428
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Habsiguda",
        "hindi": "\u0939\u092c\u094d\u0938\u0940\u0917\u0941\u0921\u093c\u093e",
        "ll": [
          78.545,
          17.418
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "NGRI",
        "hindi": "\u090f\u0928\u091c\u0940\u0906\u0930\u0906\u0908",
        "ll": [
          78.553,
          17.411
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Stadium",
        "hindi": "\u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e (\u0909\u092a\u094d\u092a\u0932)",
        "ll": [
          78.56,
          17.404
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Uppal",
        "hindi": "\u0909\u092a\u094d\u092a\u0932",
        "ll": [
          78.568,
          17.399
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "Nagole",
        "hindi": "\u0928\u093e\u0917\u094b\u0932\u0947",
        "ll": [
          78.577,
          17.387
        ],
        "l": [
          "hyd-blue"
        ]
      },
      {
        "n": "JBS Parade Ground",
        "hindi": "\u091c\u0947\u092c\u0940\u090f\u0938 \u092a\u0930\u0947\u0921 \u0917\u094d\u0930\u093e\u0909\u0902\u0921",
        "ll": [
          78.498,
          17.451
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Secunderabad West",
        "hindi": "\u0938\u093f\u0915\u0902\u0926\u0930\u093e\u092c\u093e\u0926 \u0935\u0947\u0938\u094d\u091f",
        "ll": [
          78.502,
          17.438
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Gandhi Hospital",
        "hindi": "\u0917\u093e\u0902\u0927\u0940 \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          78.507,
          17.424
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Musheerabad",
        "hindi": "\u092e\u0941\u0936\u0940\u0930\u093e\u092c\u093e\u0926",
        "ll": [
          78.508,
          17.415
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "RTC X Roads",
        "hindi": "\u0906\u0930\u091f\u0940\u0938\u0940 \u0915\u094d\u0930\u0949\u0938 \u0930\u094b\u0921\u094d\u0938",
        "ll": [
          78.505,
          17.404
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Chikkadpally",
        "hindi": "\u091a\u093f\u0915\u094d\u0915\u0921\u093c\u092a\u0932\u094d\u0932\u0940",
        "ll": [
          78.501,
          17.397
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Narayanguda",
        "hindi": "\u0928\u093e\u0930\u093e\u092f\u0923\u0917\u0941\u0921\u093c\u093e",
        "ll": [
          78.496,
          17.391
        ],
        "l": [
          "hyd-green"
        ]
      },
      {
        "n": "Sultan Bazaar",
        "hindi": "\u0938\u0941\u0932\u094d\u0924\u093e\u0928 \u092c\u093e\u091c\u093e\u0930",
        "ll": [
          78.489,
          17.384
        ],
        "l": [
          "hyd-green"
        ]
      }
    ],
    "links": []
  },
  "kochi": {
    "name": "Kochi Metro & Water Metro (KMRL)",
    "hindi": "\u0d15\u0d4a\u0d1a\u0d4d\u0d1a\u0d3f \u0d2e\u0d46\u0d1f\u0d4d\u0d30\u0d4b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                76.2,
                9.92
              ],
              [
                76.22,
                10.14
              ],
              [
                76.38,
                10.15
              ],
              [
                76.4,
                9.96
              ],
              [
                76.32,
                9.9
              ],
              [
                76.2,
                9.92
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              76.22,
              9.93
            ],
            [
              76.235,
              9.97
            ],
            [
              76.24,
              10.02
            ],
            [
              76.255,
              10.08
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              76.24,
              9.965
            ],
            [
              76.27,
              9.975
            ],
            [
              76.28,
              10.01
            ],
            [
              76.31,
              10.04
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              76.33,
              10.12
            ],
            [
              76.353,
              10.11
            ],
            [
              76.38,
              10.1
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              76.308,
              10.025
            ],
            [
              76.315,
              9.99
            ],
            [
              76.32,
              9.967
            ],
            [
              76.31,
              9.93
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              76.308,
              10.025
            ],
            [
              76.33,
              10.06
            ],
            [
              76.353,
              10.11
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              76.36,
              10.01
            ],
            [
              76.35,
              9.98
            ],
            [
              76.345,
              9.95
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              76.353,
              10.11
            ],
            [
              76.32,
              10.04
            ],
            [
              76.288,
              9.99
            ],
            [
              76.292,
              9.968
            ],
            [
              76.34,
              9.95
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "High Court Marine Drive Terminal",
          "ll": [
            76.273,
            9.984
          ],
          "r": 5
        },
        {
          "n": "Fort Kochi Heritage Pier",
          "ll": [
            76.242,
            9.966
          ],
          "r": 4
        },
        {
          "n": "Aluva Riverfront Terminus",
          "ll": [
            76.353,
            10.11
          ],
          "r": 4
        },
        {
          "n": "Kakkanad Infopark IT Hub",
          "ll": [
            76.36,
            10.01
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "koc-blue",
        "nm": "Blue Line (Line 1: Aluva - Tripunithura)",
        "c": "#0284c7",
        "seq": [
          "Aluva",
          "Pulinchodu",
          "Companypady",
          "Ambattukavu",
          "Muttom",
          "Kalamassery",
          "Cochin University (CUSAT)",
          "Pathadipalam",
          "Edapally",
          "Changampuzha Park",
          "Palarivattom",
          "JLN Stadium",
          "Kaloor",
          "Lissie",
          "MG Road Kochi",
          "Maharaja's College",
          "Ernakulam South",
          "Kadavanthra",
          "Elamkulam",
          "Vyttila",
          "Thykoodam",
          "Petta",
          "Vadakkekotta",
          "SN Junction",
          "Tripunithura"
        ],
        "segs": [
          [
            [
              76.353,
              10.11
            ],
            [
              76.345,
              10.1
            ],
            [
              76.339,
              10.088
            ],
            [
              76.332,
              10.078
            ],
            [
              76.326,
              10.068
            ],
            [
              76.321,
              10.055
            ],
            [
              76.316,
              10.045
            ],
            [
              76.312,
              10.035
            ],
            [
              76.308,
              10.024
            ],
            [
              76.305,
              10.015
            ],
            [
              76.302,
              10.006
            ],
            [
              76.299,
              9.998
            ],
            [
              76.295,
              9.99
            ],
            [
              76.29,
              9.985
            ],
            [
              76.284,
              9.98
            ],
            [
              76.285,
              9.972
            ],
            [
              76.289,
              9.967
            ],
            [
              76.298,
              9.965
            ],
            [
              76.308,
              9.964
            ],
            [
              76.32,
              9.965
            ],
            [
              76.326,
              9.961
            ],
            [
              76.332,
              9.957
            ],
            [
              76.34,
              9.954
            ],
            [
              76.345,
              9.952
            ],
            [
              76.35,
              9.95
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Aluva",
        "hindi": "\u0905\u0932\u0941\u0935\u093e",
        "ll": [
          76.353,
          10.11
        ],
        "l": [
          "koc-blue"
        ],
        "interchange": true
      },
      {
        "n": "Pulinchodu",
        "hindi": "\u092a\u0941\u0932\u093f\u0902\u091a\u094b\u0921\u0941",
        "ll": [
          76.345,
          10.1
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Companypady",
        "hindi": "\u0915\u0902\u092a\u0928\u0940\u092a\u0921\u0940",
        "ll": [
          76.339,
          10.088
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Ambattukavu",
        "hindi": "\u0905\u092e\u094d\u092c\u091f\u094d\u091f\u0941\u0915\u093e\u0935\u0941",
        "ll": [
          76.332,
          10.078
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Muttom",
        "hindi": "\u092e\u0941\u091f\u094d\u091f\u092e",
        "ll": [
          76.326,
          10.068
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Kalamassery",
        "hindi": "\u0915\u0932\u092e\u0938\u094d\u0938\u0947\u0930\u0940",
        "ll": [
          76.321,
          10.055
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Cochin University (CUSAT)",
        "hindi": "\u0915\u094b\u091a\u0940\u0928 \u092f\u0942\u0928\u093f\u0935\u0930\u094d\u0938\u093f\u091f\u0940",
        "ll": [
          76.316,
          10.045
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Pathadipalam",
        "hindi": "\u092a\u0925\u093e\u0921\u0940\u092a\u093e\u0932\u092e",
        "ll": [
          76.312,
          10.035
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Edapally",
        "hindi": "\u090f\u0921\u093e\u092a\u0932\u094d\u0932\u0940 (\u0932\u0941\u0932\u0941 \u092e\u0949\u0932)",
        "ll": [
          76.308,
          10.024
        ],
        "l": [
          "koc-blue"
        ],
        "interchange": true
      },
      {
        "n": "Changampuzha Park",
        "hindi": "\u091a\u0902\u0917\u092e\u094d\u092a\u0941\u091d\u093e \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          76.305,
          10.015
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Palarivattom",
        "hindi": "\u092a\u0932\u093e\u0930\u093f\u0935\u091f\u094d\u091f\u092e",
        "ll": [
          76.302,
          10.006
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "JLN Stadium",
        "hindi": "\u091c\u0935\u093e\u0939\u0930\u0932\u093e\u0932 \u0928\u0947\u0939\u0930\u0942 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e",
        "ll": [
          76.299,
          9.998
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Kaloor",
        "hindi": "\u0915\u0932\u0942\u0930",
        "ll": [
          76.295,
          9.99
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Lissie",
        "hindi": "\u0932\u093f\u0938\u094d\u0938\u0940",
        "ll": [
          76.29,
          9.985
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "MG Road Kochi",
        "hindi": "\u090f\u092e\u091c\u0940 \u0930\u094b\u0921 \u0915\u094b\u091a\u094d\u091a\u093f",
        "ll": [
          76.284,
          9.98
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Maharaja's College",
        "hindi": "\u092e\u0939\u093e\u0930\u093e\u091c\u093e \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          76.285,
          9.972
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Ernakulam South",
        "hindi": "\u090f\u0930\u094d\u0928\u093e\u0915\u0941\u0932\u092e \u0938\u093e\u0909\u0925 \u091c\u0902\u0915\u094d\u0936\u0928",
        "ll": [
          76.289,
          9.967
        ],
        "l": [
          "koc-blue"
        ],
        "interchange": true
      },
      {
        "n": "Kadavanthra",
        "hindi": "\u0915\u0921\u0935\u0928\u094d\u0925\u0930\u093e",
        "ll": [
          76.298,
          9.965
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Elamkulam",
        "hindi": "\u090f\u0932\u092e\u0915\u0941\u0932\u092e",
        "ll": [
          76.308,
          9.964
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Vyttila",
        "hindi": "\u0935\u093e\u092f\u091f\u093f\u0932\u093e \u092e\u094b\u092c\u093f\u0932\u093f\u091f\u0940 \u0939\u092c",
        "ll": [
          76.32,
          9.965
        ],
        "l": [
          "koc-blue"
        ],
        "interchange": true
      },
      {
        "n": "Thykoodam",
        "hindi": "\u0925\u093e\u0907\u0915\u0941\u0921\u092e",
        "ll": [
          76.326,
          9.961
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Petta",
        "hindi": "\u092a\u0947\u091f\u094d\u091f\u093e",
        "ll": [
          76.332,
          9.957
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Vadakkekotta",
        "hindi": "\u0935\u0921\u0915\u094d\u0915\u0947\u0915\u094b\u091f\u094d\u091f\u093e",
        "ll": [
          76.34,
          9.954
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "SN Junction",
        "hindi": "\u090f\u0938\u090f\u0928 \u091c\u0902\u0915\u094d\u0936\u0928",
        "ll": [
          76.345,
          9.952
        ],
        "l": [
          "koc-blue"
        ]
      },
      {
        "n": "Tripunithura",
        "hindi": "\u0924\u094d\u0930\u093f\u092a\u0941\u0928\u093f\u0925\u0941\u0930\u093e \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          76.35,
          9.95
        ],
        "l": [
          "koc-blue"
        ],
        "interchange": true
      }
    ],
    "links": []
  },
  "ahmedabad": {
    "name": "Ahmedabad & Gandhinagar Metro (GMRC)",
    "hindi": "\u0a85\u0aae\u0aa6\u0abe\u0ab5\u0abe\u0aa6 \u0aae\u0ac7\u0a9f\u0acd\u0ab0\u0acb",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                72.48,
                22.95
              ],
              [
                72.5,
                23.15
              ],
              [
                72.65,
                23.24
              ],
              [
                72.7,
                23.1
              ],
              [
                72.64,
                22.95
              ],
              [
                72.48,
                22.95
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              72.66,
              23.22
            ],
            [
              72.62,
              23.15
            ],
            [
              72.597,
              23.092
            ],
            [
              72.58,
              23.06
            ],
            [
              72.57,
              23.03
            ],
            [
              72.55,
              22.99
            ],
            [
              72.535,
              22.95
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              72.598,
              23.006
            ],
            [
              72.605,
              23.01
            ],
            [
              72.608,
              23.005
            ],
            [
              72.598,
              23.006
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              72.5,
              22.98
            ],
            [
              72.51,
              23.05
            ],
            [
              72.55,
              23.12
            ],
            [
              72.63,
              23.19
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              72.53,
              23.0
            ],
            [
              72.535,
              23.04
            ],
            [
              72.56,
              23.08
            ],
            [
              72.6,
              23.07
            ],
            [
              72.61,
              23.02
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              72.46,
              23.02
            ],
            [
              72.52,
              23.15
            ],
            [
              72.68,
              23.14
            ],
            [
              72.68,
              22.98
            ],
            [
              72.46,
              23.02
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              72.61,
              22.99
            ],
            [
              72.602,
              23.022
            ],
            [
              72.58,
              23.07
            ],
            [
              72.57,
              23.12
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Sabarmati Ashram (Mahatma Gandhi)",
          "ll": [
            72.58,
            23.06
          ],
          "r": 5
        },
        {
          "n": "Narendra Modi Stadium Motera",
          "ll": [
            72.597,
            23.092
          ],
          "r": 5
        },
        {
          "n": "Old High Court Central Interchange",
          "ll": [
            72.568,
            23.038
          ],
          "r": 4
        },
        {
          "n": "Kalupur Heritage Junction",
          "ll": [
            72.602,
            23.022
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "ahm-blue",
        "nm": "Blue Line (East-West: Thaltej Gam - Vastral Gam)",
        "c": "#2563eb",
        "seq": [
          "Thaltej Gam",
          "Thaltej",
          "Doordarshan Kendra",
          "Gurukul Road",
          "Gujarat University",
          "Commerce Six Road",
          "Stadium Ahmedabad",
          "Old High Court",
          "Sabarmati Riverfront",
          "Shahpur",
          "Gheekanta",
          "Kalupur Railway Station",
          "Kankaria East",
          "Apparel Park",
          "Amraiwadi",
          "Rabari Colony",
          "Vastral",
          "Vastral Gam"
        ],
        "segs": [
          [
            [
              72.505,
              23.052
            ],
            [
              72.518,
              23.05
            ],
            [
              72.528,
              23.048
            ],
            [
              72.537,
              23.045
            ],
            [
              72.548,
              23.041
            ],
            [
              72.556,
              23.039
            ],
            [
              72.562,
              23.038
            ],
            [
              72.568,
              23.038
            ],
            [
              72.576,
              23.035
            ],
            [
              72.583,
              23.033
            ],
            [
              72.592,
              23.028
            ],
            [
              72.602,
              23.022
            ],
            [
              72.61,
              23.015
            ],
            [
              72.62,
              23.01
            ],
            [
              72.63,
              23.007
            ],
            [
              72.641,
              23.005
            ],
            [
              72.652,
              23.003
            ],
            [
              72.665,
              23.001
            ]
          ]
        ]
      },
      {
        "id": "ahm-red",
        "nm": "Red Line (North-South: Motera Stadium - APMC)",
        "c": "#dc2626",
        "seq": [
          "Motera Stadium",
          "Sabarmati",
          "AEC",
          "Ranip",
          "Vadaj",
          "Vijay Nagar",
          "Usmanpura",
          "Old High Court",
          "Gandhigram",
          "Paldi",
          "Shreyas",
          "Rajiv Nagar",
          "Jivraj Park",
          "APMC"
        ],
        "segs": [
          [
            [
              72.597,
              23.092
            ],
            [
              72.59,
              23.082
            ],
            [
              72.584,
              23.073
            ],
            [
              72.579,
              23.064
            ],
            [
              72.574,
              23.056
            ],
            [
              72.571,
              23.048
            ],
            [
              72.569,
              23.042
            ],
            [
              72.568,
              23.038
            ],
            [
              72.567,
              23.029
            ],
            [
              72.565,
              23.018
            ],
            [
              72.562,
              23.008
            ],
            [
              72.558,
              22.999
            ],
            [
              72.554,
              22.991
            ],
            [
              72.55,
              22.982
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Thaltej Gam",
        "hindi": "\u0925\u0932\u0924\u0947\u091c \u0917\u093e\u092e",
        "ll": [
          72.505,
          23.052
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Thaltej",
        "hindi": "\u0925\u0932\u0924\u0947\u091c",
        "ll": [
          72.518,
          23.05
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Doordarshan Kendra",
        "hindi": "\u0926\u0942\u0930\u0926\u0930\u094d\u0936\u0928 \u0915\u0947\u0902\u0926\u094d\u0930",
        "ll": [
          72.528,
          23.048
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Gurukul Road",
        "hindi": "\u0917\u0941\u0930\u0941\u0915\u0941\u0932 \u0930\u094b\u0921",
        "ll": [
          72.537,
          23.045
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Gujarat University",
        "hindi": "\u0917\u0941\u091c\u0930\u093e\u0924 \u092f\u0942\u0928\u093f\u0935\u0930\u094d\u0938\u093f\u091f\u0940",
        "ll": [
          72.548,
          23.041
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Commerce Six Road",
        "hindi": "\u0915\u0949\u092e\u0930\u094d\u0938 \u0938\u093f\u0915\u094d\u0938 \u0930\u094b\u0921",
        "ll": [
          72.556,
          23.039
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Stadium Ahmedabad",
        "hindi": "\u0938\u0930\u0926\u093e\u0930 \u092a\u091f\u0947\u0932 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e",
        "ll": [
          72.562,
          23.038
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Old High Court",
        "hindi": "\u0913\u0932\u094d\u0921 \u0939\u093e\u0908 \u0915\u094b\u0930\u094d\u091f (\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0907\u0902\u091f\u0930\u091a\u0947\u0902\u091c)",
        "ll": [
          72.568,
          23.038
        ],
        "l": [
          "ahm-blue",
          "ahm-red"
        ],
        "interchange": true
      },
      {
        "n": "Sabarmati Riverfront",
        "hindi": "\u0938\u093e\u092c\u0930\u092e\u0924\u0940 \u0930\u093f\u0935\u0930\u092b\u094d\u0930\u0902\u091f",
        "ll": [
          72.576,
          23.035
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Shahpur",
        "hindi": "\u0936\u093e\u0939\u092a\u0941\u0930",
        "ll": [
          72.583,
          23.033
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Gheekanta",
        "hindi": "\u0918\u0940\u0915\u093e\u0902\u091f\u093e",
        "ll": [
          72.592,
          23.028
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Kalupur Railway Station",
        "hindi": "\u0915\u093e\u0932\u0942\u092a\u0941\u0930 \u0905\u0939\u092e\u0926\u093e\u092c\u093e\u0926 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          72.602,
          23.022
        ],
        "l": [
          "ahm-blue"
        ],
        "interchange": true
      },
      {
        "n": "Kankaria East",
        "hindi": "\u0915\u093e\u0902\u0915\u0930\u093f\u092f\u093e \u0908\u0938\u094d\u091f",
        "ll": [
          72.61,
          23.015
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Apparel Park",
        "hindi": "\u0905\u092a\u0947\u0930\u0932 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          72.62,
          23.01
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Amraiwadi",
        "hindi": "\u0905\u092e\u0930\u093e\u0908\u0935\u093e\u0921\u093c\u0940",
        "ll": [
          72.63,
          23.007
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Rabari Colony",
        "hindi": "\u0930\u092c\u093e\u0930\u0940 \u0915\u0949\u0932\u094b\u0928\u0940",
        "ll": [
          72.641,
          23.005
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Vastral",
        "hindi": "\u0935\u0938\u094d\u0924\u094d\u0930\u093e\u0932",
        "ll": [
          72.652,
          23.003
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Vastral Gam",
        "hindi": "\u0935\u0938\u094d\u0924\u094d\u0930\u093e\u0932 \u0917\u093e\u092e",
        "ll": [
          72.665,
          23.001
        ],
        "l": [
          "ahm-blue"
        ]
      },
      {
        "n": "Motera Stadium",
        "hindi": "\u0928\u0930\u0947\u0902\u0926\u094d\u0930 \u092e\u094b\u0926\u0940 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e \u092e\u094b\u091f\u0947\u0930\u093e",
        "ll": [
          72.597,
          23.092
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Sabarmati",
        "hindi": "\u0938\u093e\u092c\u0930\u092e\u0924\u0940 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          72.59,
          23.082
        ],
        "l": [
          "ahm-red"
        ],
        "interchange": true
      },
      {
        "n": "AEC",
        "hindi": "\u090f\u0908\u0938\u0940",
        "ll": [
          72.584,
          23.073
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Ranip",
        "hindi": "\u0930\u093e\u0928\u0940\u092a \u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          72.579,
          23.064
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Vadaj",
        "hindi": "\u0935\u093e\u0921\u091c",
        "ll": [
          72.574,
          23.056
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Vijay Nagar",
        "hindi": "\u0935\u093f\u091c\u092f \u0928\u0917\u0930",
        "ll": [
          72.571,
          23.048
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Usmanpura",
        "hindi": "\u0909\u0938\u094d\u092e\u093e\u0928\u092a\u0941\u0930\u093e",
        "ll": [
          72.569,
          23.042
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Gandhigram",
        "hindi": "\u0917\u093e\u0902\u0927\u0940\u0917\u094d\u0930\u093e\u092e",
        "ll": [
          72.567,
          23.029
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Paldi",
        "hindi": "\u092a\u093e\u0932\u0921\u0940",
        "ll": [
          72.565,
          23.018
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Shreyas",
        "hindi": "\u0936\u094d\u0930\u0947\u092f\u0938",
        "ll": [
          72.562,
          23.008
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Rajiv Nagar",
        "hindi": "\u0930\u093e\u091c\u0940\u0935 \u0928\u0917\u0930",
        "ll": [
          72.558,
          22.999
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "Jivraj Park",
        "hindi": "\u091c\u0940\u0935\u0930\u093e\u091c \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          72.554,
          22.991
        ],
        "l": [
          "ahm-red"
        ]
      },
      {
        "n": "APMC",
        "hindi": "\u090f\u092a\u0940\u090f\u092e\u0938\u0940 \u092e\u093e\u0930\u094d\u0915\u0947\u091f",
        "ll": [
          72.55,
          22.982
        ],
        "l": [
          "ahm-red"
        ]
      }
    ],
    "links": []
  },
  "pune": {
    "name": "Pune Metro (Maha Metro)",
    "hindi": "\u092a\u0941\u0923\u0947 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                73.74,
                18.46
              ],
              [
                73.76,
                18.66
              ],
              [
                73.88,
                18.66
              ],
              [
                73.96,
                18.56
              ],
              [
                73.94,
                18.46
              ],
              [
                73.74,
                18.46
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              73.78,
              18.62
            ],
            [
              73.82,
              18.58
            ],
            [
              73.856,
              18.53
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              73.8,
              18.48
            ],
            [
              73.835,
              18.505
            ],
            [
              73.856,
              18.53
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              73.856,
              18.53
            ],
            [
              73.88,
              18.54
            ],
            [
              73.92,
              18.545
            ],
            [
              73.96,
              18.535
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              73.78,
              18.65
            ],
            [
              73.81,
              18.61
            ],
            [
              73.84,
              18.56
            ],
            [
              73.856,
              18.53
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              73.75,
              18.59
            ],
            [
              73.77,
              18.54
            ],
            [
              73.8,
              18.49
            ],
            [
              73.86,
              18.45
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              73.87,
              18.54
            ],
            [
              73.91,
              18.555
            ],
            [
              73.96,
              18.57
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              73.78,
              18.65
            ],
            [
              73.81,
              18.61
            ],
            [
              73.84,
              18.56
            ],
            [
              73.873,
              18.528
            ],
            [
              73.92,
              18.51
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Shaniwar Wada Historic Seat",
          "ll": [
            73.855,
            18.519
          ],
          "r": 5
        },
        {
          "n": "Civil Court Multimodal Underground Hub",
          "ll": [
            73.856,
            18.527
          ],
          "r": 5
        },
        {
          "n": "Pune Junction Railway",
          "ll": [
            73.873,
            18.528
          ],
          "r": 4
        },
        {
          "n": "PCMC Civic Hub",
          "ll": [
            73.82,
            18.627
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "pun-purple",
        "nm": "Purple Line (Line 1: PCMC - Swargate)",
        "c": "#7c3aed",
        "seq": [
          "PCMC",
          "Sant Tukaram Nagar",
          "Bhosari",
          "Kasarwadi",
          "Phugewadi",
          "Dapodi",
          "Bopodi",
          "Khadki",
          "Range Hill",
          "Shivajinagar",
          "Civil Court",
          "Budhwar Peth",
          "Mandai",
          "Swargate"
        ],
        "segs": [
          [
            [
              73.82,
              18.627
            ],
            [
              73.824,
              18.618
            ],
            [
              73.829,
              18.607
            ],
            [
              73.832,
              18.598
            ],
            [
              73.835,
              18.588
            ],
            [
              73.838,
              18.578
            ],
            [
              73.841,
              18.568
            ],
            [
              73.845,
              18.558
            ],
            [
              73.848,
              18.547
            ],
            [
              73.852,
              18.534
            ],
            [
              73.856,
              18.527
            ],
            [
              73.857,
              18.517
            ],
            [
              73.8575,
              18.509
            ],
            [
              73.858,
              18.501
            ]
          ]
        ]
      },
      {
        "id": "pun-aqua",
        "nm": "Aqua Line (Line 2: Vanaz - Ramwadi)",
        "c": "#06b6d4",
        "seq": [
          "Vanaz",
          "Anand Nagar Pune",
          "Ideal Colony",
          "Nal Stop",
          "Garware College",
          "Deccan Gymkhana",
          "Chhatrapati Sambhaji Udyan",
          "PMC",
          "Civil Court",
          "Mangalwar Peth",
          "Pune Railway Station",
          "Ruby Hall Clinic",
          "Bund Garden",
          "Yerawada",
          "Kalyani Nagar",
          "Ramwadi"
        ],
        "segs": [
          [
            [
              73.799,
              18.502
            ],
            [
              73.808,
              18.504
            ],
            [
              73.818,
              18.507
            ],
            [
              73.829,
              18.51
            ],
            [
              73.837,
              18.513
            ],
            [
              73.844,
              18.517
            ],
            [
              73.849,
              18.521
            ],
            [
              73.853,
              18.524
            ],
            [
              73.856,
              18.527
            ],
            [
              73.864,
              18.528
            ],
            [
              73.873,
              18.528
            ],
            [
              73.882,
              18.53
            ],
            [
              73.89,
              18.534
            ],
            [
              73.899,
              18.542
            ],
            [
              73.908,
              18.548
            ],
            [
              73.918,
              18.553
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "PCMC",
        "hindi": "\u092a\u093f\u0902\u092a\u0930\u0940 \u091a\u093f\u0902\u091a\u0935\u0921 (\u092a\u0940\u0938\u0940\u090f\u092e\u0938\u0940)",
        "ll": [
          73.82,
          18.627
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Sant Tukaram Nagar",
        "hindi": "\u0938\u0902\u0924 \u0924\u0941\u0915\u093e\u0930\u093e\u092e \u0928\u0917\u0930",
        "ll": [
          73.824,
          18.618
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Bhosari",
        "hindi": "\u092d\u094b\u0938\u0930\u0940 (\u0928\u093e\u0936\u093f\u0915 \u092b\u093e\u091f\u093e)",
        "ll": [
          73.829,
          18.607
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Kasarwadi",
        "hindi": "\u0915\u093e\u0938\u093e\u0930\u0935\u093e\u0921\u0940",
        "ll": [
          73.832,
          18.598
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Phugewadi",
        "hindi": "\u092b\u0941\u0917\u0947\u0935\u093e\u0921\u0940",
        "ll": [
          73.835,
          18.588
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Dapodi",
        "hindi": "\u0926\u093e\u092a\u094b\u0921\u0940",
        "ll": [
          73.838,
          18.578
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Bopodi",
        "hindi": "\u092c\u094b\u092a\u094b\u0921\u0940",
        "ll": [
          73.841,
          18.568
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Khadki",
        "hindi": "\u0916\u0921\u093c\u0915\u0940",
        "ll": [
          73.845,
          18.558
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Range Hill",
        "hindi": "\u0930\u0947\u0902\u091c \u0939\u093f\u0932",
        "ll": [
          73.848,
          18.547
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Shivajinagar",
        "hindi": "\u0936\u093f\u0935\u093e\u091c\u0940\u0928\u0917\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          73.852,
          18.534
        ],
        "l": [
          "pun-purple"
        ],
        "interchange": true
      },
      {
        "n": "Civil Court",
        "hindi": "\u0938\u093f\u0935\u093f\u0932 \u0915\u094b\u0930\u094d\u091f (\u092a\u0941\u0923\u0947 \u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0939\u092c)",
        "ll": [
          73.856,
          18.527
        ],
        "l": [
          "pun-purple",
          "pun-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Budhwar Peth",
        "hindi": "\u092c\u0941\u0927\u0935\u093e\u0930 \u092a\u0947\u0920",
        "ll": [
          73.857,
          18.517
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Mandai",
        "hindi": "\u092e\u0902\u0921\u0908",
        "ll": [
          73.8575,
          18.509
        ],
        "l": [
          "pun-purple"
        ]
      },
      {
        "n": "Swargate",
        "hindi": "\u0938\u094d\u0935\u093e\u0930\u0917\u0947\u091f \u092e\u0932\u094d\u091f\u0940\u092e\u0949\u0921\u0932 \u0939\u092c",
        "ll": [
          73.858,
          18.501
        ],
        "l": [
          "pun-purple"
        ],
        "interchange": true
      },
      {
        "n": "Vanaz",
        "hindi": "\u0935\u0928\u093e\u091d",
        "ll": [
          73.799,
          18.502
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Anand Nagar Pune",
        "hindi": "\u0906\u0928\u0902\u0926 \u0928\u0917\u0930 \u092a\u0941\u0923\u0947",
        "ll": [
          73.808,
          18.504
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Ideal Colony",
        "hindi": "\u0906\u0907\u0921\u093f\u092f\u0932 \u0915\u0949\u0932\u094b\u0928\u0940",
        "ll": [
          73.818,
          18.507
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Nal Stop",
        "hindi": "\u0928\u0932 \u0938\u094d\u091f\u0949\u092a",
        "ll": [
          73.829,
          18.51
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Garware College",
        "hindi": "\u0917\u0930\u0935\u093e\u0930\u0947 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          73.837,
          18.513
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Deccan Gymkhana",
        "hindi": "\u0921\u0947\u0915\u094d\u0915\u0928 \u091c\u093f\u092e\u0916\u093e\u0928\u093e",
        "ll": [
          73.844,
          18.517
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Chhatrapati Sambhaji Udyan",
        "hindi": "\u091b\u0924\u094d\u0930\u092a\u0924\u0940 \u0938\u0902\u092d\u093e\u091c\u0940 \u0909\u0926\u094d\u092f\u093e\u0928",
        "ll": [
          73.849,
          18.521
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "PMC",
        "hindi": "\u092a\u0940\u090f\u092e\u0938\u0940 (\u092a\u0941\u0923\u0947 \u092e\u0939\u093e\u0928\u0917\u0930\u092a\u093e\u0932\u093f\u0915\u093e)",
        "ll": [
          73.853,
          18.524
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Mangalwar Peth",
        "hindi": "\u092e\u0902\u0917\u0933\u0935\u093e\u0930 \u092a\u0947\u0920",
        "ll": [
          73.864,
          18.528
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Pune Railway Station",
        "hindi": "\u092a\u0941\u0923\u0947 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          73.873,
          18.528
        ],
        "l": [
          "pun-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Ruby Hall Clinic",
        "hindi": "\u0930\u0942\u092c\u0940 \u0939\u0949\u0932 \u0915\u094d\u0932\u093f\u0928\u093f\u0915",
        "ll": [
          73.882,
          18.53
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Bund Garden",
        "hindi": "\u092c\u0902\u0921 \u0917\u093e\u0930\u094d\u0921\u0928",
        "ll": [
          73.89,
          18.534
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Yerawada",
        "hindi": "\u092f\u0930\u0935\u0921\u093e",
        "ll": [
          73.899,
          18.542
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Kalyani Nagar",
        "hindi": "\u0915\u0932\u094d\u092f\u093e\u0923\u0940 \u0928\u0917\u0930",
        "ll": [
          73.908,
          18.548
        ],
        "l": [
          "pun-aqua"
        ]
      },
      {
        "n": "Ramwadi",
        "hindi": "\u0930\u093e\u092e\u0935\u093e\u0921\u0940",
        "ll": [
          73.918,
          18.553
        ],
        "l": [
          "pun-aqua"
        ]
      }
    ],
    "links": []
  },
  "lucknow": {
    "name": "Lucknow Metro (UPMRC)",
    "hindi": "\u0932\u0916\u0928\u090a \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                80.84,
                26.74
              ],
              [
                80.86,
                26.92
              ],
              [
                81.02,
                26.92
              ],
              [
                81.04,
                26.78
              ],
              [
                80.84,
                26.74
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              80.88,
              26.91
            ],
            [
              80.91,
              26.87
            ],
            [
              80.94,
              26.855
            ],
            [
              80.98,
              26.86
            ],
            [
              81.03,
              26.83
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              80.9,
              26.8
            ],
            [
              80.93,
              26.82
            ],
            [
              80.97,
              26.83
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              80.88,
              26.77
            ],
            [
              80.93,
              26.78
            ],
            [
              80.98,
              26.81
            ],
            [
              81.03,
              26.86
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              80.88,
              26.76
            ],
            [
              80.9,
              26.8
            ],
            [
              80.92,
              26.83
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              80.94,
              26.86
            ],
            [
              80.98,
              26.88
            ],
            [
              81.03,
              26.9
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              80.88,
              26.76
            ],
            [
              80.905,
              26.8
            ],
            [
              80.922,
              26.832
            ],
            [
              80.96,
              26.86
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Bara Imambara Heritage Monument",
          "ll": [
            80.912,
            26.869
          ],
          "r": 5
        },
        {
          "n": "Charbagh Heritage Railway Station",
          "ll": [
            80.922,
            26.832
          ],
          "r": 5
        },
        {
          "n": "Hazratganj Cultural Core",
          "ll": [
            80.945,
            26.852
          ],
          "r": 4
        },
        {
          "n": "Chaudhary Charan Singh International Airport",
          "ll": [
            80.883,
            26.765
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "lko-red",
        "nm": "Red Line (North-South: CCS Airport - Munshi Pulia)",
        "c": "#dc2626",
        "seq": [
          "CCS Airport",
          "Amausi",
          "Transport Nagar LKO",
          "Krishna Nagar",
          "Singar Nagar",
          "Alambagh",
          "Alambagh Bus Station",
          "Mawaiya",
          "Durgapuri",
          "Charbagh",
          "Hussainganj",
          "Sachivalaya",
          "Hazratganj",
          "KD Singh Babu Stadium",
          "Vishwavidyalaya LKO",
          "IT Chauraha",
          "Badshahnagar",
          "Mahanagar",
          "Dandiya",
          "Indiranagar LKO",
          "Munshi Pulia"
        ],
        "segs": [
          [
            [
              80.883,
              26.765
            ],
            [
              80.889,
              26.778
            ],
            [
              80.895,
              26.79
            ],
            [
              80.901,
              26.801
            ],
            [
              80.906,
              26.81
            ],
            [
              80.911,
              26.818
            ],
            [
              80.915,
              26.823
            ],
            [
              80.918,
              26.827
            ],
            [
              80.92,
              26.83
            ],
            [
              80.922,
              26.832
            ],
            [
              80.931,
              26.84
            ],
            [
              80.938,
              26.846
            ],
            [
              80.945,
              26.852
            ],
            [
              80.942,
              26.859
            ],
            [
              80.938,
              26.868
            ],
            [
              80.941,
              26.875
            ],
            [
              80.952,
              26.877
            ],
            [
              80.963,
              26.879
            ],
            [
              80.973,
              26.882
            ],
            [
              80.983,
              26.884
            ],
            [
              80.992,
              26.887
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "CCS Airport",
        "hindi": "\u091a\u094c\u0927\u0930\u0940 \u091a\u0930\u0923 \u0938\u093f\u0902\u0939 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          80.883,
          26.765
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Amausi",
        "hindi": "\u0905\u092e\u094c\u0938\u0940",
        "ll": [
          80.889,
          26.778
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Transport Nagar LKO",
        "hindi": "\u091f\u094d\u0930\u093e\u0902\u0938\u092a\u094b\u0930\u094d\u091f \u0928\u0917\u0930",
        "ll": [
          80.895,
          26.79
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Krishna Nagar",
        "hindi": "\u0915\u0943\u0937\u094d\u0923\u093e \u0928\u0917\u0930",
        "ll": [
          80.901,
          26.801
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Singar Nagar",
        "hindi": "\u0938\u093f\u0902\u0917\u093e\u0930 \u0928\u0917\u0930",
        "ll": [
          80.906,
          26.81
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Alambagh",
        "hindi": "\u0906\u0932\u092e\u092c\u093e\u0917",
        "ll": [
          80.911,
          26.818
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Alambagh Bus Station",
        "hindi": "\u0906\u0932\u092e\u092c\u093e\u0917 \u092c\u0938 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          80.915,
          26.823
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Mawaiya",
        "hindi": "\u092e\u0935\u0948\u092f\u093e",
        "ll": [
          80.918,
          26.827
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Durgapuri",
        "hindi": "\u0926\u0941\u0930\u094d\u0917\u093e\u092a\u0941\u0930\u0940",
        "ll": [
          80.92,
          26.83
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Charbagh",
        "hindi": "\u091a\u093e\u0930\u092c\u093e\u0917 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          80.922,
          26.832
        ],
        "l": [
          "lko-red"
        ],
        "interchange": true
      },
      {
        "n": "Hussainganj",
        "hindi": "\u0939\u0941\u0938\u0948\u0928\u0917\u0902\u091c",
        "ll": [
          80.931,
          26.84
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Sachivalaya",
        "hindi": "\u0938\u091a\u093f\u0935\u093e\u0932\u092f (\u0935\u093f\u0927\u093e\u0928 \u0938\u092d\u093e)",
        "ll": [
          80.938,
          26.846
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Hazratganj",
        "hindi": "\u0939\u091c\u0930\u0924\u0917\u0902\u091c",
        "ll": [
          80.945,
          26.852
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "KD Singh Babu Stadium",
        "hindi": "\u0915\u0947\u0921\u0940 \u0938\u093f\u0902\u0939 \u092c\u093e\u092c\u0942 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e",
        "ll": [
          80.942,
          26.859
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Vishwavidyalaya LKO",
        "hindi": "\u0932\u0916\u0928\u090a \u0935\u093f\u0936\u094d\u0935\u0935\u093f\u0926\u094d\u092f\u093e\u0932\u092f",
        "ll": [
          80.938,
          26.868
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "IT Chauraha",
        "hindi": "\u0906\u0908\u091f\u0940 \u091a\u094c\u0930\u093e\u0939\u093e",
        "ll": [
          80.941,
          26.875
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Badshahnagar",
        "hindi": "\u092c\u093e\u0926\u0936\u093e\u0939\u0928\u0917\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          80.952,
          26.877
        ],
        "l": [
          "lko-red"
        ],
        "interchange": true
      },
      {
        "n": "Mahanagar",
        "hindi": "\u092e\u0939\u093e\u0928\u0917\u0930",
        "ll": [
          80.963,
          26.879
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Dandiya",
        "hindi": "\u0921\u093e\u0902\u0921\u093f\u092f\u093e",
        "ll": [
          80.973,
          26.882
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Indiranagar LKO",
        "hindi": "\u0907\u0902\u0926\u093f\u0930\u093e\u0928\u0917\u0930",
        "ll": [
          80.983,
          26.884
        ],
        "l": [
          "lko-red"
        ]
      },
      {
        "n": "Munshi Pulia",
        "hindi": "\u092e\u0941\u0902\u0936\u0940 \u092a\u0941\u0932\u093f\u092f\u093e",
        "ll": [
          80.992,
          26.887
        ],
        "l": [
          "lko-red"
        ]
      }
    ],
    "links": []
  },
  "kanpur": {
    "name": "Kanpur Metro (UPMRC)",
    "hindi": "\u0915\u093e\u0928\u092a\u0941\u0930 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                80.18,
                26.38
              ],
              [
                80.2,
                26.54
              ],
              [
                80.38,
                26.54
              ],
              [
                80.4,
                26.4
              ],
              [
                80.18,
                26.38
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              80.25,
              26.55
            ],
            [
              80.3,
              26.51
            ],
            [
              80.34,
              26.48
            ],
            [
              80.39,
              26.44
            ],
            [
              80.42,
              26.4
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              80.24,
              26.42
            ],
            [
              80.3,
              26.41
            ],
            [
              80.36,
              26.39
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              80.23,
              26.515
            ],
            [
              80.28,
              26.49
            ],
            [
              80.32,
              26.47
            ],
            [
              80.355,
              26.45
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              80.32,
              26.48
            ],
            [
              80.35,
              26.47
            ],
            [
              80.38,
              26.45
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              80.25,
              26.47
            ],
            [
              80.3,
              26.455
            ],
            [
              80.352,
              26.454
            ],
            [
              80.41,
              26.43
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "IIT Kanpur Premier Institute",
          "ll": [
            80.232,
            26.512
          ],
          "r": 5
        },
        {
          "n": "Kanpur Central Railway Junction",
          "ll": [
            80.352,
            26.454
          ],
          "r": 5
        },
        {
          "n": "Motijheel Civic Core",
          "ll": [
            80.312,
            26.481
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "knp-orange",
        "nm": "Orange Line (Line 1: IIT Kanpur - Naubasta)",
        "c": "#ea580c",
        "seq": [
          "IIT Kanpur",
          "Kalyanpur",
          "SPM Hospital",
          "CSJM University",
          "Gurudev Chauraha",
          "Geeta Nagar",
          "Rawatpur",
          "LLR Hospital",
          "Moti Jheel",
          "Chunniganj",
          "Naveen Market",
          "Bada Chauraha",
          "Nayaganj",
          "Kanpur Central",
          "Jhakarkati Bus Terminal",
          "Transport Nagar KNP",
          "Baradevi",
          "Kidwai Nagar",
          "Vasant Vihar",
          "Baudh Nagar",
          "Naubasta"
        ],
        "segs": [
          [
            [
              80.232,
              26.512
            ],
            [
              80.245,
              26.508
            ],
            [
              80.258,
              26.504
            ],
            [
              80.27,
              26.5
            ],
            [
              80.282,
              26.495
            ],
            [
              80.293,
              26.49
            ],
            [
              80.302,
              26.486
            ],
            [
              80.307,
              26.484
            ],
            [
              80.312,
              26.481
            ],
            [
              80.325,
              26.475
            ],
            [
              80.334,
              26.47
            ],
            [
              80.342,
              26.465
            ],
            [
              80.348,
              26.459
            ],
            [
              80.352,
              26.454
            ],
            [
              80.354,
              26.446
            ],
            [
              80.355,
              26.438
            ],
            [
              80.354,
              26.43
            ],
            [
              80.352,
              26.422
            ],
            [
              80.35,
              26.415
            ],
            [
              80.348,
              26.408
            ],
            [
              80.345,
              26.401
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "IIT Kanpur",
        "hindi": "\u0906\u0908\u0906\u0908\u091f\u0940 \u0915\u093e\u0928\u092a\u0941\u0930",
        "ll": [
          80.232,
          26.512
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Kalyanpur",
        "hindi": "\u0915\u0932\u094d\u092f\u093e\u0923\u092a\u0941\u0930",
        "ll": [
          80.245,
          26.508
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "SPM Hospital",
        "hindi": "\u090f\u0938\u092a\u0940\u090f\u092e \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          80.258,
          26.504
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "CSJM University",
        "hindi": "\u0938\u0940\u090f\u0938\u091c\u0947\u090f\u092e \u0915\u093e\u0928\u092a\u0941\u0930 \u092f\u0942\u0928\u093f\u0935\u0930\u094d\u0938\u093f\u091f\u0940",
        "ll": [
          80.27,
          26.5
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Gurudev Chauraha",
        "hindi": "\u0917\u0941\u0930\u0941\u0926\u0947\u0935 \u091a\u094c\u0930\u093e\u0939\u093e",
        "ll": [
          80.282,
          26.495
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Geeta Nagar",
        "hindi": "\u0917\u0940\u0924\u093e \u0928\u0917\u0930",
        "ll": [
          80.293,
          26.49
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Rawatpur",
        "hindi": "\u0930\u093e\u0935\u0924\u092a\u0941\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          80.302,
          26.486
        ],
        "l": [
          "knp-orange"
        ],
        "interchange": true
      },
      {
        "n": "LLR Hospital",
        "hindi": "\u090f\u0932\u090f\u0932\u0906\u0930 \u0939\u0948\u0932\u091f \u0905\u0938\u094d\u092a\u0924\u093e\u0932",
        "ll": [
          80.307,
          26.484
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Moti Jheel",
        "hindi": "\u092e\u094b\u0924\u0940 \u091d\u0940\u0932",
        "ll": [
          80.312,
          26.481
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Chunniganj",
        "hindi": "\u091a\u0941\u0928\u094d\u0928\u0940\u0917\u0902\u091c",
        "ll": [
          80.325,
          26.475
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Naveen Market",
        "hindi": "\u0928\u0935\u0940\u0928 \u092e\u093e\u0930\u094d\u0915\u0947\u091f",
        "ll": [
          80.334,
          26.47
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Bada Chauraha",
        "hindi": "\u092c\u0921\u093c\u093e \u091a\u094c\u0930\u093e\u0939\u093e",
        "ll": [
          80.342,
          26.465
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Nayaganj",
        "hindi": "\u0928\u092f\u093e\u0917\u0902\u091c",
        "ll": [
          80.348,
          26.459
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Kanpur Central",
        "hindi": "\u0915\u093e\u0928\u092a\u0941\u0930 \u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          80.352,
          26.454
        ],
        "l": [
          "knp-orange"
        ],
        "interchange": true
      },
      {
        "n": "Jhakarkati Bus Terminal",
        "hindi": "\u091d\u0915\u0930\u0915\u091f\u0940 \u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          80.354,
          26.446
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Transport Nagar KNP",
        "hindi": "\u091f\u094d\u0930\u093e\u0902\u0938\u092a\u094b\u0930\u094d\u091f \u0928\u0917\u0930 \u0915\u093e\u0928\u092a\u0941\u0930",
        "ll": [
          80.355,
          26.438
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Baradevi",
        "hindi": "\u092c\u093e\u0930\u093e\u0926\u0947\u0935\u0940",
        "ll": [
          80.354,
          26.43
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Kidwai Nagar",
        "hindi": "\u0915\u093f\u0926\u0935\u0908 \u0928\u0917\u0930",
        "ll": [
          80.352,
          26.422
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Vasant Vihar",
        "hindi": "\u0935\u0938\u0902\u0924 \u0935\u093f\u0939\u093e\u0930",
        "ll": [
          80.35,
          26.415
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Baudh Nagar",
        "hindi": "\u092c\u094c\u0926\u094d\u0927 \u0928\u0917\u0930",
        "ll": [
          80.348,
          26.408
        ],
        "l": [
          "knp-orange"
        ]
      },
      {
        "n": "Naubasta",
        "hindi": "\u0928\u094c\u092c\u0938\u094d\u0924\u093e",
        "ll": [
          80.345,
          26.401
        ],
        "l": [
          "knp-orange"
        ]
      }
    ],
    "links": []
  },
  "agra": {
    "name": "Agra Metro (UPMRC)",
    "hindi": "\u0906\u0917\u0930\u093e \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                77.92,
                27.12
              ],
              [
                77.94,
                27.24
              ],
              [
                78.08,
                27.24
              ],
              [
                78.1,
                27.12
              ],
              [
                77.92,
                27.12
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              78.0,
              27.23
            ],
            [
              78.015,
              27.2
            ],
            [
              78.02,
              27.18
            ],
            [
              78.042,
              27.175
            ],
            [
              78.06,
              27.165
            ],
            [
              78.09,
              27.16
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              77.96,
              27.22
            ],
            [
              77.99,
              27.195
            ],
            [
              78.01,
              27.17
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              78.03,
              27.165
            ],
            [
              78.06,
              27.155
            ],
            [
              78.1,
              27.14
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              77.98,
              27.22
            ],
            [
              77.99,
              27.195
            ],
            [
              78.005,
              27.16
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Taj Mahal (UNESCO World Wonder)",
          "ll": [
            78.042,
            27.175
          ],
          "r": 5
        },
        {
          "n": "Agra Fort World Heritage",
          "ll": [
            78.021,
            27.179
          ],
          "r": 5
        },
        {
          "n": "Mankameshwar Mandir Core",
          "ll": [
            78.015,
            27.185
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "agr-yellow",
        "nm": "Yellow Line (Taj East Gate - Sikandra)",
        "c": "#eab308",
        "seq": [
          "Taj East Gate",
          "Captain Shubham Gupta",
          "Taj Mahal",
          "Agra Fort",
          "Jama Masjid Agra",
          "SN Medical College",
          "Agra College",
          "Raja Ki Mandi",
          "RBS College",
          "Sikandra"
        ],
        "segs": [
          [
            [
              78.062,
              27.162
            ],
            [
              78.05,
              27.165
            ],
            [
              78.04,
              27.171
            ],
            [
              78.024,
              27.178
            ],
            [
              78.016,
              27.184
            ],
            [
              78.008,
              27.188
            ],
            [
              78.001,
              27.192
            ],
            [
              77.992,
              27.199
            ],
            [
              77.982,
              27.206
            ],
            [
              77.954,
              27.221
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Taj East Gate",
        "hindi": "\u0924\u093e\u091c \u0908\u0938\u094d\u091f \u0917\u0947\u091f",
        "ll": [
          78.062,
          27.162
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Captain Shubham Gupta",
        "hindi": "\u0915\u0948\u092a\u094d\u091f\u0928 \u0936\u0941\u092d\u092e \u0917\u0941\u092a\u094d\u0924\u093e (\u092b\u0924\u0947\u0939\u093e\u092c\u093e\u0926 \u0930\u094b\u0921)",
        "ll": [
          78.05,
          27.165
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Taj Mahal",
        "hindi": "\u0924\u093e\u091c \u092e\u0939\u0932 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          78.04,
          27.171
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Agra Fort",
        "hindi": "\u0906\u0917\u0930\u093e \u092b\u094b\u0930\u094d\u091f",
        "ll": [
          78.024,
          27.178
        ],
        "l": [
          "agr-yellow"
        ],
        "interchange": true
      },
      {
        "n": "Jama Masjid Agra",
        "hindi": "\u091c\u093e\u092e\u093e \u092e\u0938\u094d\u091c\u093f\u0926 (\u092e\u0928\u0915\u093e\u092e\u0947\u0936\u094d\u0935\u0930)",
        "ll": [
          78.016,
          27.184
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "SN Medical College",
        "hindi": "\u090f\u0938\u090f\u0928 \u092e\u0947\u0921\u093f\u0915\u0932 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          78.008,
          27.188
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Agra College",
        "hindi": "\u0906\u0917\u0930\u093e \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          78.001,
          27.192
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Raja Ki Mandi",
        "hindi": "\u0930\u093e\u091c\u093e \u0915\u0940 \u092e\u0902\u0921\u0940 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          77.992,
          27.199
        ],
        "l": [
          "agr-yellow"
        ],
        "interchange": true
      },
      {
        "n": "RBS College",
        "hindi": "\u0906\u0930\u092c\u0940\u090f\u0938 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          77.982,
          27.206
        ],
        "l": [
          "agr-yellow"
        ]
      },
      {
        "n": "Sikandra",
        "hindi": "\u0938\u093f\u0915\u0902\u0926\u0930\u093e (\u0905\u0915\u092c\u0930 \u0915\u093e \u092e\u0915\u092c\u0930\u093e)",
        "ll": [
          77.954,
          27.221
        ],
        "l": [
          "agr-yellow"
        ]
      }
    ],
    "links": []
  },
  "jaipur": {
    "name": "Jaipur Metro (JMRC)",
    "hindi": "\u091c\u092f\u092a\u0941\u0930 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                75.7,
                26.82
              ],
              [
                75.72,
                26.98
              ],
              [
                75.88,
                26.98
              ],
              [
                75.88,
                26.82
              ],
              [
                75.7,
                26.82
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              75.75,
              26.84
            ],
            [
              75.77,
              26.88
            ],
            [
              75.81,
              26.93
            ],
            [
              75.83,
              26.97
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              75.835,
              26.95
            ],
            [
              75.845,
              26.96
            ],
            [
              75.84,
              26.955
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              75.74,
              26.87
            ],
            [
              75.77,
              26.9
            ],
            [
              75.8,
              26.915
            ],
            [
              75.83,
              26.92
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              75.8,
              26.85
            ],
            [
              75.805,
              26.89
            ],
            [
              75.815,
              26.915
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              75.76,
              26.9
            ],
            [
              75.789,
              26.92
            ],
            [
              75.82,
              26.93
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Hawa Mahal & City Palace (Walled City)",
          "ll": [
            75.826,
            26.924
          ],
          "r": 5
        },
        {
          "n": "Jaipur Junction Railway",
          "ll": [
            75.789,
            26.92
          ],
          "r": 5
        },
        {
          "n": "Albert Hall State Museum",
          "ll": [
            75.819,
            26.911
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "jai-pink",
        "nm": "Pink Line (Phase 1: Mansarovar - Badi Chaupar)",
        "c": "#ec4899",
        "seq": [
          "Mansarovar",
          "New Aatish Market",
          "Vivek Vihar",
          "Shyam Nagar",
          "Ram Nagar",
          "Civil Lines Jaipur",
          "Railway Station Jaipur",
          "Sindhi Camp",
          "Chandpole",
          "Chhoti Chaupar",
          "Badi Chaupar"
        ],
        "segs": [
          [
            [
              75.752,
              26.879
            ],
            [
              75.761,
              26.886
            ],
            [
              75.768,
              26.893
            ],
            [
              75.772,
              26.899
            ],
            [
              75.776,
              26.906
            ],
            [
              75.781,
              26.912
            ],
            [
              75.789,
              26.92
            ],
            [
              75.798,
              26.923
            ],
            [
              75.811,
              26.924
            ],
            [
              75.82,
              26.924
            ],
            [
              75.828,
              26.924
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Mansarovar",
        "hindi": "\u092e\u093e\u0928\u0938\u0930\u094b\u0935\u0930",
        "ll": [
          75.752,
          26.879
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "New Aatish Market",
        "hindi": "\u0928\u094d\u092f\u0942 \u0906\u0924\u093f\u0936 \u092e\u093e\u0930\u094d\u0915\u0947\u091f",
        "ll": [
          75.761,
          26.886
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Vivek Vihar",
        "hindi": "\u0935\u093f\u0935\u0947\u0915 \u0935\u093f\u0939\u093e\u0930",
        "ll": [
          75.768,
          26.893
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Shyam Nagar",
        "hindi": "\u0936\u094d\u092f\u093e\u092e \u0928\u0917\u0930",
        "ll": [
          75.772,
          26.899
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Ram Nagar",
        "hindi": "\u0930\u093e\u092e \u0928\u0917\u0930",
        "ll": [
          75.776,
          26.906
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Civil Lines Jaipur",
        "hindi": "\u0938\u093f\u0935\u093f\u0932 \u0932\u093e\u0907\u0902\u0938",
        "ll": [
          75.781,
          26.912
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Railway Station Jaipur",
        "hindi": "\u091c\u092f\u092a\u0941\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          75.789,
          26.92
        ],
        "l": [
          "jai-pink"
        ],
        "interchange": true
      },
      {
        "n": "Sindhi Camp",
        "hindi": "\u0938\u093f\u0902\u0927\u0940 \u0915\u0948\u0902\u092a \u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          75.798,
          26.923
        ],
        "l": [
          "jai-pink"
        ],
        "interchange": true
      },
      {
        "n": "Chandpole",
        "hindi": "\u091a\u093e\u0902\u0926\u092a\u094b\u0932 (\u0939\u0947\u0930\u093f\u091f\u0947\u091c \u0917\u0947\u091f)",
        "ll": [
          75.811,
          26.924
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Chhoti Chaupar",
        "hindi": "\u091b\u094b\u091f\u0940 \u091a\u094c\u092a\u0921\u093c",
        "ll": [
          75.82,
          26.924
        ],
        "l": [
          "jai-pink"
        ]
      },
      {
        "n": "Badi Chaupar",
        "hindi": "\u092c\u0921\u093c\u0940 \u091a\u094c\u092a\u0921\u093c (\u0939\u0935\u093e \u092e\u0939\u0932)",
        "ll": [
          75.828,
          26.924
        ],
        "l": [
          "jai-pink"
        ]
      }
    ],
    "links": []
  },
  "nagpur": {
    "name": "Nagpur Metro (Maha Metro)",
    "hindi": "\u0928\u093e\u0917\u092a\u0942\u0930 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                78.96,
                21.02
              ],
              [
                78.98,
                21.22
              ],
              [
                79.18,
                21.22
              ],
              [
                79.18,
                21.02
              ],
              [
                78.96,
                21.02
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              79.03,
              21.125
            ],
            [
              79.06,
              21.135
            ],
            [
              79.085,
              21.145
            ],
            [
              79.13,
              21.15
            ]
          ]
        },
        {
          "t": "canal",
          "g": [
            [
              79.05,
              21.19
            ],
            [
              79.1,
              21.185
            ],
            [
              79.15,
              21.17
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              79.055,
              21.06
            ],
            [
              79.07,
              21.11
            ],
            [
              79.084,
              21.146
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              79.084,
              21.146
            ],
            [
              79.12,
              21.15
            ],
            [
              79.16,
              21.155
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              79.075,
              21.1
            ],
            [
              79.088,
              21.153
            ],
            [
              79.095,
              21.2
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Zero Mile Stone (Geographical Center of India)",
          "ll": [
            79.082,
            21.148
          ],
          "r": 5
        },
        {
          "n": "Sitabuldi Interchange Hub",
          "ll": [
            79.084,
            21.146
          ],
          "r": 5
        },
        {
          "n": "Deekshabhoomi Sacred Monument",
          "ll": [
            79.068,
            21.128
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "nag-orange",
        "nm": "Orange Line (North-South: Automotive Square - Khapri)",
        "c": "#ea580c",
        "seq": [
          "Automotive Square",
          "Nari Road",
          "Indora Square",
          "Kadvi Chowk",
          "GaddiGodam Square",
          "Kasturchand Park",
          "Zero Mile Freedom Park",
          "Sitabuldi Nagpur",
          "Congress Nagar",
          "Rahate Colony",
          "Ajni Square",
          "Chhatrapati Square",
          "Jaiprakash Nagar",
          "Ujjwal Nagar",
          "Airport Nagpur",
          "Airport South",
          "New Airport",
          "Khapri"
        ],
        "segs": [
          [
            [
              79.086,
              21.196
            ],
            [
              79.086,
              21.187
            ],
            [
              79.085,
              21.178
            ],
            [
              79.085,
              21.169
            ],
            [
              79.084,
              21.16
            ],
            [
              79.083,
              21.154
            ],
            [
              79.082,
              21.148
            ],
            [
              79.084,
              21.146
            ],
            [
              79.082,
              21.137
            ],
            [
              79.08,
              21.129
            ],
            [
              79.078,
              21.12
            ],
            [
              79.076,
              21.111
            ],
            [
              79.074,
              21.102
            ],
            [
              79.072,
              21.093
            ],
            [
              79.07,
              21.084
            ],
            [
              79.068,
              21.074
            ],
            [
              79.066,
              21.064
            ],
            [
              79.064,
              21.054
            ]
          ]
        ]
      },
      {
        "id": "nag-aqua",
        "nm": "Aqua Line (East-West: Prajapati Nagar - Lokmanya Nagar)",
        "c": "#06b6d4",
        "seq": [
          "Prajapati Nagar",
          "Vaishno Devi Square",
          "Ambedkar Square",
          "Telephone Exchange",
          "Chittar Oli Square",
          "Agrasen Square",
          "Dosar Vaisya Square",
          "Nagpur Railway Station",
          "Cotton Market",
          "Sitabuldi Nagpur",
          "Jhansi Rani Square",
          "Institute of Engineers",
          "Shankar Nagar Square",
          "LAD Square",
          "Dharampeth College",
          "Subhash Nagar Nagpur",
          "Rachana Ring Road",
          "Vasudev Nagar",
          "Bansi Nagar",
          "Lokmanya Nagar"
        ],
        "segs": [
          [
            [
              79.155,
              21.152
            ],
            [
              79.145,
              21.151
            ],
            [
              79.135,
              21.15
            ],
            [
              79.125,
              21.149
            ],
            [
              79.115,
              21.148
            ],
            [
              79.105,
              21.147
            ],
            [
              79.096,
              21.146
            ],
            [
              79.09,
              21.146
            ],
            [
              79.087,
              21.146
            ],
            [
              79.084,
              21.146
            ],
            [
              79.076,
              21.144
            ],
            [
              79.068,
              21.142
            ],
            [
              79.059,
              21.14
            ],
            [
              79.051,
              21.138
            ],
            [
              79.043,
              21.136
            ],
            [
              79.035,
              21.134
            ],
            [
              79.027,
              21.132
            ],
            [
              79.019,
              21.13
            ],
            [
              79.011,
              21.128
            ],
            [
              79.003,
              21.126
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Automotive Square",
        "hindi": "\u0911\u091f\u094b\u092e\u094b\u091f\u093f\u0935 \u091a\u094c\u0915",
        "ll": [
          79.086,
          21.196
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Nari Road",
        "hindi": "\u0928\u093e\u0930\u0940 \u0930\u094b\u0921",
        "ll": [
          79.086,
          21.187
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Indora Square",
        "hindi": "\u0907\u0902\u0926\u094b\u0930\u093e \u091a\u094c\u0915",
        "ll": [
          79.085,
          21.178
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Kadvi Chowk",
        "hindi": "\u0915\u0921\u093c\u0935\u0940 \u091a\u094c\u0915",
        "ll": [
          79.085,
          21.169
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "GaddiGodam Square",
        "hindi": "\u0917\u0921\u094d\u0921\u0940\u0917\u094b\u0926\u093e\u092e \u091a\u094c\u0915",
        "ll": [
          79.084,
          21.16
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Kasturchand Park",
        "hindi": "\u0915\u0938\u094d\u0924\u0942\u0930\u091a\u0902\u0926 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          79.083,
          21.154
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Zero Mile Freedom Park",
        "hindi": "\u091c\u0940\u0930\u094b \u092e\u093e\u0907\u0932 \u092b\u094d\u0930\u0940\u0921\u092e \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          79.082,
          21.148
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Sitabuldi Nagpur",
        "hindi": "\u0938\u0940\u0924\u093e\u092c\u0930\u094d\u0921\u0940 (\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u0907\u0902\u091f\u0930\u091a\u0947\u0902\u091c)",
        "ll": [
          79.084,
          21.146
        ],
        "l": [
          "nag-orange",
          "nag-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Congress Nagar",
        "hindi": "\u0915\u093e\u0902\u0917\u094d\u0930\u0947\u0938 \u0928\u0917\u0930",
        "ll": [
          79.082,
          21.137
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Rahate Colony",
        "hindi": "\u0930\u093e\u0939\u093e\u091f\u0947 \u0915\u0949\u0932\u094b\u0928\u0940",
        "ll": [
          79.08,
          21.129
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Ajni Square",
        "hindi": "\u0905\u091c\u0928\u0940 \u091a\u094c\u0915",
        "ll": [
          79.078,
          21.12
        ],
        "l": [
          "nag-orange"
        ],
        "interchange": true
      },
      {
        "n": "Chhatrapati Square",
        "hindi": "\u091b\u0924\u094d\u0930\u092a\u0924\u0940 \u091a\u094c\u0915",
        "ll": [
          79.076,
          21.111
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Jaiprakash Nagar",
        "hindi": "\u091c\u092f\u092a\u094d\u0930\u0915\u093e\u0936 \u0928\u0917\u0930",
        "ll": [
          79.074,
          21.102
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Ujjwal Nagar",
        "hindi": "\u0909\u091c\u094d\u091c\u094d\u0935\u0932 \u0928\u0917\u0930",
        "ll": [
          79.072,
          21.093
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Airport Nagpur",
        "hindi": "\u0928\u093e\u0917\u092a\u0941\u0930 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          79.07,
          21.084
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Airport South",
        "hindi": "\u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f \u0938\u093e\u0909\u0925",
        "ll": [
          79.068,
          21.074
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "New Airport",
        "hindi": "\u0928\u094d\u092f\u0942 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          79.066,
          21.064
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Khapri",
        "hindi": "\u0916\u093e\u092a\u0930\u0940",
        "ll": [
          79.064,
          21.054
        ],
        "l": [
          "nag-orange"
        ]
      },
      {
        "n": "Prajapati Nagar",
        "hindi": "\u092a\u094d\u0930\u091c\u093e\u092a\u0924\u093f \u0928\u0917\u0930",
        "ll": [
          79.155,
          21.152
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Vaishno Devi Square",
        "hindi": "\u0935\u0948\u0937\u094d\u0923\u094b \u0926\u0947\u0935\u0940 \u091a\u094c\u0915",
        "ll": [
          79.145,
          21.151
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Ambedkar Square",
        "hindi": "\u0906\u0902\u092c\u0947\u0921\u0915\u0930 \u091a\u094c\u0915",
        "ll": [
          79.135,
          21.15
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Telephone Exchange",
        "hindi": "\u091f\u0947\u0932\u0940\u092b\u094b\u0928 \u090f\u0915\u094d\u0938\u091a\u0947\u0902\u091c",
        "ll": [
          79.125,
          21.149
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Chittar Oli Square",
        "hindi": "\u091a\u093f\u0924\u094d\u0924\u093e\u0930 \u0913\u0932\u0940 \u091a\u094c\u0915",
        "ll": [
          79.115,
          21.148
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Agrasen Square",
        "hindi": "\u0905\u0917\u094d\u0930\u0938\u0947\u0928 \u091a\u094c\u0915",
        "ll": [
          79.105,
          21.147
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Dosar Vaisya Square",
        "hindi": "\u0926\u094b\u0938\u0930 \u0935\u0948\u0936\u094d\u092f \u091a\u094c\u0915",
        "ll": [
          79.096,
          21.146
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Nagpur Railway Station",
        "hindi": "\u0928\u093e\u0917\u092a\u0941\u0930 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          79.09,
          21.146
        ],
        "l": [
          "nag-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Cotton Market",
        "hindi": "\u0915\u0949\u091f\u0928 \u092e\u093e\u0930\u094d\u0915\u0947\u091f",
        "ll": [
          79.087,
          21.146
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Jhansi Rani Square",
        "hindi": "\u091d\u093e\u0902\u0938\u0940 \u0930\u093e\u0928\u0940 \u091a\u094c\u0915",
        "ll": [
          79.076,
          21.144
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Institute of Engineers",
        "hindi": "\u0907\u0902\u0938\u094d\u091f\u0940\u091f\u094d\u092f\u0942\u091f \u0911\u092b \u0907\u0902\u091c\u0940\u0928\u093f\u092f\u0930\u094d\u0938",
        "ll": [
          79.068,
          21.142
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Shankar Nagar Square",
        "hindi": "\u0936\u0902\u0915\u0930 \u0928\u0917\u0930 \u091a\u094c\u0915",
        "ll": [
          79.059,
          21.14
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "LAD Square",
        "hindi": "\u090f\u0932\u090f\u0921\u0940 \u091a\u094c\u0915",
        "ll": [
          79.051,
          21.138
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Dharampeth College",
        "hindi": "\u0927\u0930\u092e\u092a\u0947\u0920 \u0915\u0949\u0932\u0947\u091c",
        "ll": [
          79.043,
          21.136
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Subhash Nagar Nagpur",
        "hindi": "\u0938\u0941\u092d\u093e\u0937 \u0928\u0917\u0930",
        "ll": [
          79.035,
          21.134
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Rachana Ring Road",
        "hindi": "\u0930\u091a\u0928\u093e \u0930\u093f\u0902\u0917 \u0930\u094b\u0921",
        "ll": [
          79.027,
          21.132
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Vasudev Nagar",
        "hindi": "\u0935\u093e\u0938\u0941\u0926\u0947\u0935 \u0928\u0917\u0930",
        "ll": [
          79.019,
          21.13
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Bansi Nagar",
        "hindi": "\u092c\u0902\u0938\u0940 \u0928\u0917\u0930",
        "ll": [
          79.011,
          21.128
        ],
        "l": [
          "nag-aqua"
        ]
      },
      {
        "n": "Lokmanya Nagar",
        "hindi": "\u0932\u094b\u0915\u092e\u093e\u0928\u094d\u092f \u0928\u0917\u0930",
        "ll": [
          79.003,
          21.126
        ],
        "l": [
          "nag-aqua"
        ]
      }
    ],
    "links": []
  },
  "noida": {
    "name": "Noida & Greater Noida Metro (NMRC Aqua Line)",
    "hindi": "\u0928\u094b\u090f\u0921\u093e \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                77.3,
                28.4
              ],
              [
                77.32,
                28.62
              ],
              [
                77.56,
                28.62
              ],
              [
                77.56,
                28.4
              ],
              [
                77.3,
                28.4
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              77.3,
              28.58
            ],
            [
              77.33,
              28.52
            ],
            [
              77.36,
              28.46
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              77.41,
              28.61
            ],
            [
              77.43,
              28.53
            ],
            [
              77.46,
              28.44
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              77.33,
              28.55
            ],
            [
              77.38,
              28.51
            ],
            [
              77.43,
              28.48
            ],
            [
              77.502,
              28.463
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              77.502,
              28.463
            ],
            [
              77.53,
              28.43
            ],
            [
              77.56,
              28.38
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              77.45,
              28.56
            ],
            [
              77.48,
              28.5
            ],
            [
              77.52,
              28.45
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "Pari Chowk Landmark Hub",
          "ll": [
            77.502,
            28.463
          ],
          "r": 5
        },
        {
          "n": "Knowledge Park Institutional Hub",
          "ll": [
            77.485,
            28.466
          ],
          "r": 4
        },
        {
          "n": "Noida Special Economic Zone (NSEZ)",
          "ll": [
            77.404,
            28.532
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "noi-aqua",
        "nm": "Aqua Line (Noida Sector 51 - Depot Greater Noida)",
        "c": "#06b6d4",
        "seq": [
          "Noida Sector 51",
          "Sector 50",
          "Sector 76",
          "Sector 101",
          "Sector 81",
          "NSEZ",
          "Sector 83",
          "Sector 137",
          "Sector 142",
          "Sector 143",
          "Sector 144",
          "Sector 145",
          "Sector 146",
          "Sector 147",
          "Sector 148",
          "Knowledge Park II",
          "Pari Chowk",
          "Alpha 1",
          "Delta 1",
          "GNIDA Office",
          "Depot Greater Noida"
        ],
        "segs": [
          [
            [
              77.368,
              28.578
            ],
            [
              77.373,
              28.571
            ],
            [
              77.38,
              28.562
            ],
            [
              77.387,
              28.552
            ],
            [
              77.394,
              28.542
            ],
            [
              77.404,
              28.532
            ],
            [
              77.411,
              28.522
            ],
            [
              77.42,
              28.512
            ],
            [
              77.428,
              28.502
            ],
            [
              77.436,
              28.494
            ],
            [
              77.444,
              28.487
            ],
            [
              77.452,
              28.481
            ],
            [
              77.461,
              28.475
            ],
            [
              77.47,
              28.47
            ],
            [
              77.478,
              28.467
            ],
            [
              77.485,
              28.466
            ],
            [
              77.502,
              28.463
            ],
            [
              77.512,
              28.46
            ],
            [
              77.52,
              28.452
            ],
            [
              77.525,
              28.444
            ],
            [
              77.527,
              28.435
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Noida Sector 51",
        "hindi": "\u0928\u094b\u090f\u0921\u093e \u0938\u0947\u0915\u094d\u091f\u0930 51",
        "ll": [
          77.368,
          28.578
        ],
        "l": [
          "noi-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Sector 50",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 50",
        "ll": [
          77.373,
          28.571
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 76",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 76",
        "ll": [
          77.38,
          28.562
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 101",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 101",
        "ll": [
          77.387,
          28.552
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 81",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 81",
        "ll": [
          77.394,
          28.542
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "NSEZ",
        "hindi": "\u090f\u0928\u090f\u0938\u0908\u091c\u0947\u0921 \u0938\u094d\u092a\u0947\u0936\u0932 \u0907\u0915\u094b\u0928\u0949\u092e\u093f\u0915 \u091c\u094b\u0928",
        "ll": [
          77.404,
          28.532
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 83",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 83",
        "ll": [
          77.411,
          28.522
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 137",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 137",
        "ll": [
          77.42,
          28.512
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 142",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 142",
        "ll": [
          77.428,
          28.502
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 143",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 143",
        "ll": [
          77.436,
          28.494
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 144",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 144",
        "ll": [
          77.444,
          28.487
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 145",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 145",
        "ll": [
          77.452,
          28.481
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 146",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 146",
        "ll": [
          77.461,
          28.475
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 147",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 147",
        "ll": [
          77.47,
          28.47
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Sector 148",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 148",
        "ll": [
          77.478,
          28.467
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Knowledge Park II",
        "hindi": "\u0928\u0949\u0932\u0947\u091c \u092a\u093e\u0930\u094d\u0915 2",
        "ll": [
          77.485,
          28.466
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Pari Chowk",
        "hindi": "\u092a\u0930\u0940 \u091a\u094c\u0915 \u0917\u094d\u0930\u0947\u091f\u0930 \u0928\u094b\u090f\u0921\u093e",
        "ll": [
          77.502,
          28.463
        ],
        "l": [
          "noi-aqua"
        ],
        "interchange": true
      },
      {
        "n": "Alpha 1",
        "hindi": "\u0905\u0932\u094d\u092b\u093e 1",
        "ll": [
          77.512,
          28.46
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Delta 1",
        "hindi": "\u0921\u0947\u0932\u094d\u091f\u093e 1",
        "ll": [
          77.52,
          28.452
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "GNIDA Office",
        "hindi": "\u0917\u094d\u0930\u0947\u0928\u094b \u092a\u094d\u0930\u093e\u0927\u093f\u0915\u0930\u0923 \u0915\u093e\u0930\u094d\u092f\u093e\u0932\u092f",
        "ll": [
          77.525,
          28.444
        ],
        "l": [
          "noi-aqua"
        ]
      },
      {
        "n": "Depot Greater Noida",
        "hindi": "\u0921\u093f\u092a\u094b \u0917\u094d\u0930\u0947\u091f\u0930 \u0928\u094b\u090f\u0921\u093e",
        "ll": [
          77.527,
          28.435
        ],
        "l": [
          "noi-aqua"
        ]
      }
    ],
    "links": []
  },
  "navi-mumbai": {
    "name": "Navi Mumbai Metro (CIDCO Line 1)",
    "hindi": "\u0928\u0935\u0940 \u092e\u0941\u0902\u092c\u0908 \u092e\u0947\u091f\u094d\u0930\u094b",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                72.98,
                18.98
              ],
              [
                73.0,
                19.12
              ],
              [
                73.12,
                19.12
              ],
              [
                73.14,
                18.98
              ],
              [
                72.98,
                18.98
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              72.98,
              19.0
            ],
            [
              72.99,
              19.06
            ],
            [
              73.0,
              19.12
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              73.02,
              18.99
            ],
            [
              73.06,
              19.01
            ],
            [
              73.11,
              19.03
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              73.0,
              19.06
            ],
            [
              73.03,
              19.03
            ],
            [
              73.06,
              19.035
            ],
            [
              73.1,
              19.02
            ]
          ]
        },
        {
          "c": 2,
          "g": [
            [
              73.005,
              19.07
            ],
            [
              73.015,
              19.04
            ],
            [
              73.038,
              19.018
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              73.0,
              19.06
            ],
            [
              73.02,
              19.04
            ],
            [
              73.038,
              19.018
            ],
            [
              73.07,
              19.03
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "CBD Belapur Financial Hub",
          "ll": [
            73.038,
            19.018
          ],
          "r": 5
        },
        {
          "n": "Central Park Kharghar Valley",
          "ll": [
            73.066,
            19.052
          ],
          "r": 4
        },
        {
          "n": "Utsav Chowk Architectural Gateway",
          "ll": [
            73.054,
            19.038
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "nm-l1",
        "nm": "Line 1 (CBD Belapur - Pendhar)",
        "c": "#0284c7",
        "seq": [
          "Belapur Terminal",
          "Sector 7 Belapur",
          "CIDCO Science Park",
          "Utsav Chowk",
          "Sector 11 Kharghar",
          "Sector 14 Kharghar",
          "Central Park Kharghar",
          "Pethpada",
          "Sector 34 Kharghar",
          "Panchanand",
          "Pendhar"
        ],
        "segs": [
          [
            [
              73.038,
              19.018
            ],
            [
              73.042,
              19.023
            ],
            [
              73.047,
              19.03
            ],
            [
              73.054,
              19.038
            ],
            [
              73.058,
              19.043
            ],
            [
              73.062,
              19.048
            ],
            [
              73.066,
              19.052
            ],
            [
              73.072,
              19.058
            ],
            [
              73.078,
              19.064
            ],
            [
              73.084,
              19.07
            ],
            [
              73.091,
              19.076
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Belapur Terminal",
        "hindi": "\u0938\u0940\u092c\u0940\u0921\u0940 \u092c\u0947\u0932\u093e\u092a\u0941\u0930 \u091f\u0930\u094d\u092e\u093f\u0928\u0932",
        "ll": [
          73.038,
          19.018
        ],
        "l": [
          "nm-l1"
        ],
        "interchange": true
      },
      {
        "n": "Sector 7 Belapur",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 7 \u092c\u0947\u0932\u093e\u092a\u0941\u0930",
        "ll": [
          73.042,
          19.023
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "CIDCO Science Park",
        "hindi": "\u0938\u093f\u0921\u0915\u094b \u0938\u093e\u0907\u0902\u0938 \u092a\u093e\u0930\u094d\u0915",
        "ll": [
          73.047,
          19.03
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Utsav Chowk",
        "hindi": "\u0909\u0924\u094d\u0938\u0935 \u091a\u094c\u0915",
        "ll": [
          73.054,
          19.038
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Sector 11 Kharghar",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 11 \u0916\u093e\u0930\u0918\u0930",
        "ll": [
          73.058,
          19.043
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Sector 14 Kharghar",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 14 \u0916\u093e\u0930\u0918\u0930",
        "ll": [
          73.062,
          19.048
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Central Park Kharghar",
        "hindi": "\u0938\u0947\u0902\u091f\u094d\u0930\u0932 \u092a\u093e\u0930\u094d\u0915 \u0916\u093e\u0930\u0918\u0930",
        "ll": [
          73.066,
          19.052
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Pethpada",
        "hindi": "\u092a\u0947\u0920\u092a\u093e\u0921\u093c\u093e",
        "ll": [
          73.072,
          19.058
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Sector 34 Kharghar",
        "hindi": "\u0938\u0947\u0915\u094d\u091f\u0930 34 \u0916\u093e\u0930\u0918\u0930",
        "ll": [
          73.078,
          19.064
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Panchanand",
        "hindi": "\u092a\u0902\u091a\u093e\u0928\u0902\u0926",
        "ll": [
          73.084,
          19.07
        ],
        "l": [
          "nm-l1"
        ]
      },
      {
        "n": "Pendhar",
        "hindi": "\u092a\u0947\u0902\u0927\u0930",
        "ll": [
          73.091,
          19.076
        ],
        "l": [
          "nm-l1"
        ]
      }
    ],
    "links": []
  },
  "bhopal-indore": {
    "name": "Madhya Pradesh Metro (Bhopal & Indore - MPMRCL)",
    "hindi": "\u092e\u0927\u094d\u092f \u092a\u094d\u0930\u0926\u0947\u0936 \u092e\u0947\u091f\u094d\u0930\u094b (\u092d\u094b\u092a\u093e\u0932 \u090f\u0935\u0902 \u0907\u0902\u0926\u094c\u0930)",
    "base": {
      "bd": [
        {
          "lvl": "4",
          "r": [
            [
              [
                75.74,
                22.65
              ],
              [
                75.76,
                23.35
              ],
              [
                77.55,
                23.35
              ],
              [
                77.55,
                22.65
              ],
              [
                75.74,
                22.65
              ]
            ]
          ]
        }
      ],
      "water": [
        {
          "t": "river",
          "g": [
            [
              77.3,
              23.25
            ],
            [
              77.34,
              23.245
            ],
            [
              77.38,
              23.25
            ],
            [
              77.35,
              23.23
            ]
          ]
        },
        {
          "t": "river",
          "g": [
            [
              75.84,
              22.7
            ],
            [
              75.86,
              22.72
            ],
            [
              75.88,
              22.75
            ]
          ]
        }
      ],
      "roads": [
        {
          "c": 3,
          "g": [
            [
              77.42,
              23.25
            ],
            [
              77.44,
              23.22
            ],
            [
              77.46,
              23.18
            ]
          ]
        },
        {
          "c": 3,
          "g": [
            [
              75.81,
              22.74
            ],
            [
              75.84,
              22.76
            ],
            [
              75.88,
              22.765
            ]
          ]
        }
      ],
      "rail": [
        {
          "g": [
            [
              77.4,
              23.27
            ],
            [
              77.41,
              23.25
            ],
            [
              77.441,
              23.22
            ]
          ]
        },
        {
          "g": [
            [
              75.85,
              22.7
            ],
            [
              75.867,
              22.717
            ],
            [
              75.89,
              22.74
            ]
          ]
        }
      ],
      "places": [
        {
          "n": "AIIMS Bhopal Premier Medical Campus",
          "ll": [
            77.456,
            23.204
          ],
          "r": 5
        },
        {
          "n": "Rani Kamlapati World Class Terminal",
          "ll": [
            77.441,
            23.22
          ],
          "r": 5
        },
        {
          "n": "Rajwada Historic Royal Palace Indore",
          "ll": [
            75.856,
            22.718
          ],
          "r": 4
        },
        {
          "n": "Indore Super Corridor Tech Zone",
          "ll": [
            75.82,
            22.75
          ],
          "r": 4
        }
      ]
    },
    "lines": [
      {
        "id": "bhp-orange",
        "nm": "Bhopal Orange Line (Karond - AIIMS Bhopal)",
        "c": "#ea580c",
        "seq": [
          "Karond",
          "Bhopal Railway Station",
          "Nadra Bus Stand",
          "Subhash Nagar Bhopal",
          "Kendriya Vidyalaya Bhopal",
          "DB City Mall",
          "MP Nagar Zone 1",
          "Rani Kamlapati",
          "Alkapuri Bhopal",
          "AIIMS Bhopal"
        ],
        "segs": [
          [
            [
              77.398,
              23.305
            ],
            [
              77.411,
              23.268
            ],
            [
              77.415,
              23.261
            ],
            [
              77.425,
              23.248
            ],
            [
              77.431,
              23.241
            ],
            [
              77.435,
              23.235
            ],
            [
              77.438,
              23.228
            ],
            [
              77.441,
              23.22
            ],
            [
              77.449,
              23.211
            ],
            [
              77.456,
              23.204
            ]
          ]
        ]
      },
      {
        "id": "ind-yellow",
        "nm": "Indore Yellow Line (Indore Ring: Railway Station - Airport - Palasia)",
        "c": "#eab308",
        "seq": [
          "Indore Railway Station",
          "Rajwada",
          "Bada Ganpati",
          "Airport Indore",
          "Gandhi Nagar Indore",
          "Super Corridor 3",
          "Super Corridor 1",
          "MR 10 Road",
          "Vijay Nagar Indore",
          "Bengali Square",
          "Palasia"
        ],
        "segs": [
          [
            [
              75.867,
              22.716
            ],
            [
              75.856,
              22.718
            ],
            [
              75.845,
              22.721
            ],
            [
              75.805,
              22.724
            ],
            [
              75.808,
              22.741
            ],
            [
              75.819,
              22.753
            ],
            [
              75.832,
              22.762
            ],
            [
              75.852,
              22.766
            ],
            [
              75.885,
              22.754
            ],
            [
              75.901,
              22.728
            ],
            [
              75.885,
              22.721
            ]
          ]
        ]
      }
    ],
    "stations": [
      {
        "n": "Karond",
        "hindi": "\u0915\u0930\u094b\u0902\u0926 \u091a\u094c\u0930\u093e\u0939\u093e",
        "ll": [
          77.398,
          23.305
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "Bhopal Railway Station",
        "hindi": "\u092d\u094b\u092a\u093e\u0932 \u091c\u0902\u0915\u094d\u0936\u0928 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          77.411,
          23.268
        ],
        "l": [
          "bhp-orange"
        ],
        "interchange": true
      },
      {
        "n": "Nadra Bus Stand",
        "hindi": "\u0928\u093e\u0926\u0930\u093e \u092c\u0938 \u0938\u094d\u091f\u0948\u0902\u0921",
        "ll": [
          77.415,
          23.261
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "Subhash Nagar Bhopal",
        "hindi": "\u0938\u0941\u092d\u093e\u0937 \u0928\u0917\u0930",
        "ll": [
          77.425,
          23.248
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "Kendriya Vidyalaya Bhopal",
        "hindi": "\u0915\u0947\u0902\u0926\u094d\u0930\u0940\u092f \u0935\u093f\u0926\u094d\u092f\u093e\u0932\u092f",
        "ll": [
          77.431,
          23.241
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "DB City Mall",
        "hindi": "\u0921\u0940\u092c\u0940 \u0938\u093f\u091f\u0940 \u092e\u0949\u0932",
        "ll": [
          77.435,
          23.235
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "MP Nagar Zone 1",
        "hindi": "\u090f\u092e\u092a\u0940 \u0928\u0917\u0930 \u091c\u094b\u0928 1",
        "ll": [
          77.438,
          23.228
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "Rani Kamlapati",
        "hindi": "\u0930\u093e\u0928\u0940 \u0915\u092e\u0932\u093e\u092a\u0924\u093f (\u0939\u092c\u0940\u092c\u0917\u0902\u091c)",
        "ll": [
          77.441,
          23.22
        ],
        "l": [
          "bhp-orange"
        ],
        "interchange": true
      },
      {
        "n": "Alkapuri Bhopal",
        "hindi": "\u0905\u0932\u0915\u093e\u092a\u0941\u0930\u0940",
        "ll": [
          77.449,
          23.211
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "AIIMS Bhopal",
        "hindi": "\u090f\u092e\u094d\u0938 \u092d\u094b\u092a\u093e\u0932",
        "ll": [
          77.456,
          23.204
        ],
        "l": [
          "bhp-orange"
        ]
      },
      {
        "n": "Indore Railway Station",
        "hindi": "\u0907\u0902\u0926\u094c\u0930 \u091c\u0902\u0915\u094d\u0936\u0928 \u0930\u0947\u0932\u0935\u0947 \u0938\u094d\u091f\u0947\u0936\u0928",
        "ll": [
          75.867,
          22.716
        ],
        "l": [
          "ind-yellow"
        ],
        "interchange": true
      },
      {
        "n": "Rajwada",
        "hindi": "\u0930\u093e\u091c\u0935\u093e\u0921\u093c\u093e \u092a\u0948\u0932\u0947\u0938",
        "ll": [
          75.856,
          22.718
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Bada Ganpati",
        "hindi": "\u092c\u0921\u093c\u093e \u0917\u0923\u092a\u0924\u093f",
        "ll": [
          75.845,
          22.721
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Airport Indore",
        "hindi": "\u0926\u0947\u0935\u0940 \u0905\u0939\u093f\u0932\u094d\u092f\u093e\u092c\u093e\u0908 \u0939\u094b\u0932\u094d\u0915\u0930 \u090f\u092f\u0930\u092a\u094b\u0930\u094d\u091f",
        "ll": [
          75.805,
          22.724
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Gandhi Nagar Indore",
        "hindi": "\u0917\u093e\u0902\u0927\u0940 \u0928\u0917\u0930",
        "ll": [
          75.808,
          22.741
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Super Corridor 3",
        "hindi": "\u0938\u0941\u092a\u0930 \u0915\u0949\u0930\u093f\u0921\u094b\u0930 3",
        "ll": [
          75.819,
          22.753
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Super Corridor 1",
        "hindi": "\u0938\u0941\u092a\u0930 \u0915\u0949\u0930\u093f\u0921\u094b\u0930 1",
        "ll": [
          75.832,
          22.762
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "MR 10 Road",
        "hindi": "\u090f\u092e\u0906\u0930 10 \u0930\u094b\u0921",
        "ll": [
          75.852,
          22.766
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Vijay Nagar Indore",
        "hindi": "\u0935\u093f\u091c\u092f \u0928\u0917\u0930",
        "ll": [
          75.885,
          22.754
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Bengali Square",
        "hindi": "\u092c\u0902\u0917\u093e\u0932\u0940 \u091a\u094c\u0930\u093e\u0939\u093e",
        "ll": [
          75.901,
          22.728
        ],
        "l": [
          "ind-yellow"
        ]
      },
      {
        "n": "Palasia",
        "hindi": "\u092a\u0932\u093e\u0938\u093f\u092f\u093e",
        "ll": [
          75.885,
          22.721
        ],
        "l": [
          "ind-yellow"
        ]
      }
    ],
    "links": []
  }
};

export const PREPARED_PACKS = {
  'delhi-ncr': preparePack(packDataDelhi),
};

for (const [cid, raw] of Object.entries(CITY_RAW_DATA)) {
  PREPARED_PACKS[cid] = preparePack(raw);
}

export function getCityPack(cityId) {
  return PREPARED_PACKS[cityId] || PREPARED_PACKS['delhi-ncr'];
}
