// Sanskrit accents shown beside English headings. Decorative only: never used for data or labels that carry meaning.
export const MOTTO = 'सत्यमेव जयते';
export const HOME_KICKER = 'भारतस्य यात्रा';
export const EXPLORE_KICKER = 'अन्वेषणम्';
export const GROUPS_KICKER = 'समूहाः';
export const ANALYSIS_KICKER = 'विश्लेषणम्';

export const GROUP_SANSKRIT = {
  'economy-markets': 'अर्थव्यवस्था',
  'public-finance-states': 'राजकोषः',
  'industry-energy-technology': 'उद्योगः ऊर्जा प्रौद्योगिकी',
  'infrastructure-mobility': 'आधारसंरचना',
  'people-health-society': 'जनाः स्वास्थ्यं समाजः',
  'environment-agriculture-food': 'पर्यावरणं कृषिः',
  'security-justice-defence': 'सुरक्षा न्यायः',
  'elections-democracy': 'निर्वाचनं लोकतन्त्रम्',
  'culture-heritage-sport': 'संस्कृतिः परम्परा',
  'epics-faiths-journeys': 'इतिहासः धर्मयात्रा',
  'india-in-maps': 'भारतस्य मानचित्रम्',
};

export const groupSanskrit = slug => GROUP_SANSKRIT[slug] || '';
