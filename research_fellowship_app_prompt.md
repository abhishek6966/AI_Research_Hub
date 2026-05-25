# Prompt: Research Fellowship Data Collection & Automation Web App

---

## CONTEXT (read fully before building anything)

I am a first-year MS Business Analytics & AI student at Stevens Institute of Technology completing a **Summer Research Fellowship** on *"Professionalism in the AI Era."* My task is to collect **8 specific corporate documents** for each of **100 assigned companies** across 6 continents over 2 weeks, track progress in an Excel sheet, and upload files to a shared OneDrive.

The research studies how companies are updating professional norms in response to AI — examining their ethics policies, AI guidelines, governance reports, and financial disclosures.

Build me a **single-file full-stack web application** (React frontend + in-browser logic, no backend required) that serves as my personal command center for this entire data collection task. It should maximize automation, minimize manual steps, and let me track every company and document in real time.

---

## THE 100 COMPANIES (exact names, must be hardcoded)

```js
const COMPANIES = [
  { id: 1,  name: "John Deere",                    sector: "Industrials",               industry: "Capital Goods",                                    country: "United States",       continent: "North America" },
  { id: 2,  name: "Nike",                           sector: "Consumer Discretionary",    industry: "Consumer Durables & Apparel",                       country: "United States",       continent: "North America" },
  { id: 3,  name: "Banco Bradesco",                 sector: "Financials",                industry: "Banks",                                             country: "Brazil",              continent: "South America" },
  { id: 4,  name: "Deutsche Bahn",                  sector: "Industrials",               industry: "Transportation",                                    country: "Germany",             continent: "Europe" },
  { id: 5,  name: "Crédit Mutuel",                  sector: "Financials",                industry: "Banks",                                             country: "France",              continent: "Europe" },
  { id: 6,  name: "Bayer",                          sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "Germany",             continent: "Europe" },
  { id: 7,  name: "Saint-Gobain",                   sector: "Materials",                 industry: "Construction Materials",                            country: "France",              continent: "Europe" },
  { id: 8,  name: "Volvo Group",                    sector: "Industrials",               industry: "Capital Goods",                                     country: "Sweden",              continent: "Europe" },
  { id: 9,  name: "Iberdrola",                      sector: "Utilities",                 industry: "Utilities",                                         country: "Spain",               continent: "Europe" },
  { id: 10, name: "Veolia Environnement",           sector: "Utilities",                 industry: "Utilities",                                         country: "France",              continent: "Europe" },
  { id: 11, name: "Bristol Myers Squibb",           sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "United States",       continent: "North America" },
  { id: 12, name: "Landesbank Baden-Wuerttemberg",  sector: "Financials",                industry: "Banks",                                             country: "Germany",             continent: "Europe" },
  { id: 13, name: "General Dynamics",               sector: "Industrials",               industry: "Capital Goods",                                     country: "United States",       continent: "North America" },
  { id: 14, name: "L'Oréal",                        sector: "Consumer Staples",          industry: "Household & Personal Products",                     country: "France",              continent: "Europe" },
  { id: 15, name: "Travelers",                      sector: "Financials",                industry: "Insurance",                                         country: "United States",       continent: "North America" },
  { id: 16, name: "Swiss Re",                       sector: "Financials",                industry: "Insurance",                                         country: "Switzerland",         continent: "Europe" },
  { id: 17, name: "Eli Lilly",                      sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "United States",       continent: "North America" },
  { id: 18, name: "Orange",                         sector: "Communication Services",    industry: "Telecommunication Services",                        country: "France",              continent: "Europe" },
  { id: 19, name: "Telefónica",                     sector: "Communication Services",    industry: "Telecommunication Services",                        country: "Spain",               continent: "Europe" },
  { id: 20, name: "Woolworths",                     sector: "Consumer Staples",          industry: "Consumer Staples Distribution & Retail",            country: "Australia",           continent: "Oceania" },
  { id: 21, name: "Vodafone",                       sector: "Communication Services",    industry: "Telecommunication Services",                        country: "United Kingdom",      continent: "Europe" },
  { id: 22, name: "DZ Bank",                        sector: "Financials",                industry: "Banks",                                             country: "Germany",             continent: "Europe" },
  { id: 23, name: "Dow",                            sector: "Materials",                 industry: "Chemicals",                                         country: "United States",       continent: "North America" },
  { id: 24, name: "ANZ Group Holdings",             sector: "Financials",                industry: "Banks",                                             country: "Australia",           continent: "Oceania" },
  { id: 25, name: "Commonwealth Bank",              sector: "Financials",                industry: "Banks",                                             country: "Australia",           continent: "Oceania" },
  { id: 26, name: "Thermo Fisher Scientific",       sector: "Health Care",               industry: "Health Care Equipment & Services",                  country: "United States",       continent: "North America" },
  { id: 27, name: "Novo Nordisk",                   sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "Denmark",             continent: "Europe" },
  { id: 28, name: "Abbott Laboratories",            sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "United States",       continent: "North America" },
  { id: 29, name: "Standard Chartered",             sector: "Financials",                industry: "Banks",                                             country: "United Kingdom",      continent: "Europe" },
  { id: 30, name: "Inditex",                        sector: "Consumer Discretionary",    industry: "Consumer Durables & Apparel",                       country: "Spain",               continent: "Europe" },
  { id: 31, name: "Best Buy",                       sector: "Consumer Discretionary",    industry: "Consumer Discretionary Distribution & Retail",      country: "United States",       continent: "North America" },
  { id: 32, name: "Schneider Electric",             sector: "Industrials",               industry: "Capital Goods",                                     country: "France",              continent: "Europe" },
  { id: 33, name: "KB Financial Group",             sector: "Financials",                industry: "Financial Services",                                country: "South Korea",         continent: "Asia" },
  { id: 34, name: "Northrop Grumman",               sector: "Industrials",               industry: "Automobiles & Components",                          country: "United States",       continent: "North America" },
  { id: 35, name: "NAB - National Australia Bank",  sector: "Financials",                industry: "Banks",                                             country: "Australia",           continent: "Oceania" },
  { id: 36, name: "LyondellBasell",                 sector: "Materials",                 industry: "Chemicals",                                         country: "United States",       continent: "North America" },
  { id: 37, name: "GSK",                            sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "United Kingdom",      continent: "Europe" },
  { id: 38, name: "Cenovus Energy",                 sector: "Energy",                    industry: "Oil, Gas & Consumable Fuels",                       country: "Canada",              continent: "North America" },
  { id: 39, name: "Warner Bros. Discovery",         sector: "Communication Services",    industry: "Media & Entertainment",                             country: "United States",       continent: "North America" },
  { id: 40, name: "Netflix",                        sector: "Communication Services",    industry: "Media & Entertainment",                             country: "United States",       continent: "North America" },
  { id: 41, name: "Qualcomm",                       sector: "Information Technology",    industry: "Semiconductors & Semiconductor Equipment",          country: "United States",       continent: "North America" },
  { id: 42, name: "Honeywell International",        sector: "Industrials",               industry: "Capital Goods",                                     country: "United States",       continent: "North America" },
  { id: 43, name: "Vale",                           sector: "Materials",                 industry: "Metals & Mining",                                   country: "Brazil",              continent: "South America" },
  { id: 44, name: "Salesforce",                     sector: "Information Technology",    industry: "Software & Services",                               country: "United States",       continent: "North America" },
  { id: 45, name: "Philip Morris International",    sector: "Consumer Staples",          industry: "Food, Beverage & Tobacco",                          country: "United States",       continent: "North America" },
  { id: 46, name: "Westpac Banking Group",          sector: "Financials",                industry: "Banks",                                             country: "Australia",           continent: "Oceania" },
  { id: 47, name: "AIA Group",                      sector: "Financials",                industry: "Insurance",                                         country: "Hong Kong",           continent: "Asia" },
  { id: 48, name: "SAP",                            sector: "Information Technology",    industry: "Software & Services",                               country: "Germany",             continent: "Europe" },
  { id: 49, name: "Mondelez International",         sector: "Consumer Staples",          industry: "Food, Beverage & Tobacco",                          country: "United States",       continent: "North America" },
  { id: 50, name: "Starbucks",                      sector: "Consumer Discretionary",    industry: "Consumer Services",                                 country: "United States",       continent: "North America" },
  { id: 51, name: "Visa",                           sector: "Financials",                industry: "Financial Services",                                country: "United States",       continent: "North America" },
  { id: 52, name: "CBRE Group",                     sector: "Real Estate",               industry: "Real Estate Management & Development",              country: "United States",       continent: "North America" },
  { id: 53, name: "ICICI Bank",                     sector: "Financials",                industry: "Banks",                                             country: "India",               continent: "Asia" },
  { id: 54, name: "International Airlines Group",   sector: "Industrials",               industry: "Transportation",                                    country: "United Kingdom",      continent: "Europe" },
  { id: 55, name: "PNC Financial Services",         sector: "Financials",                industry: "Banks",                                             country: "United States",       continent: "North America" },
  { id: 56, name: "Emirates",                       sector: "Consumer Discretionary",    industry: "Transportation",                                    country: "United Arab Emirates", continent: "Asia" },
  { id: 57, name: "Cummins",                        sector: "Industrials",               industry: "Capital Goods",                                     country: "United States",       continent: "North America" },
  { id: 58, name: "Air France-KLM",                 sector: "Industrials",               industry: "Transportation",                                    country: "France",              continent: "Europe" },
  { id: 59, name: "Paccar",                         sector: "Industrials",               industry: "Automobiles & Components",                          country: "United States",       continent: "North America" },
  { id: 60, name: "Metro Group",                    sector: "Consumer Staples",          industry: "Consumer Staples Distribution & Retail",            country: "Germany",             continent: "Europe" },
  { id: 61, name: "BAE Systems",                    sector: "Industrials",               industry: "Automobiles & Components",                          country: "United Kingdom",      continent: "Europe" },
  { id: 62, name: "Amgen",                          sector: "Health Care",               industry: "Pharmaceuticals, Biotechnology & Life Sciences",    country: "United States",       continent: "North America" },
  { id: 63, name: "Linde",                          sector: "Materials",                 industry: "Chemicals",                                         country: "Germany",             continent: "Europe" },
  { id: 64, name: "ABB",                            sector: "Industrials",               industry: "Capital Goods",                                     country: "Switzerland",         continent: "Europe" },
  { id: 65, name: "Ecopetrol",                      sector: "Energy",                    industry: "Oil, Gas & Consumable Fuels",                       country: "Colombia",            continent: "South America" },
  { id: 66, name: "Medtronic",                      sector: "Health Care",               industry: "Health Care Equipment & Services",                  country: "United States",       continent: "North America" },
  { id: 67, name: "Heineken",                       sector: "Consumer Staples",          industry: "Food, Beverage & Tobacco",                          country: "Netherlands",         continent: "Europe" },
  { id: 68, name: "JBS",                            sector: "Consumer Staples",          industry: "Food, Beverage & Tobacco",                          country: "Brazil",              continent: "South America" },
  { id: 69, name: "Uniper",                         sector: "Utilities",                 industry: "Utilities",                                         country: "Germany",             continent: "Europe" },
  { id: 70, name: "Korea Electric Power",           sector: "Utilities",                 industry: "Utilities",                                         country: "South Korea",         continent: "Asia" },
  { id: 71, name: "Itau Unibanco Holding",          sector: "Financials",                industry: "Banks",                                             country: "Brazil",              continent: "South America" },
  { id: 72, name: "Raizen",                         sector: "Energy",                    industry: "Oil, Gas & Consumable Fuels",                       country: "Brazil",              continent: "South America" },
  { id: 73, name: "Energie Baden-Württemberg",      sector: "Utilities",                 industry: "Utilities",                                         country: "Germany",             continent: "Europe" },
  { id: 74, name: "CFE",                            sector: "Utilities",                 industry: "Utilities",                                         country: "Mexico",              continent: "North America" },
  { id: 75, name: "Standard Bank Group",            sector: "Financials",                industry: "Banks",                                             country: "South Africa",        continent: "Africa" },
  { id: 76, name: "Nedbank",                        sector: "Financials",                industry: "Banks",                                             country: "South Africa",        continent: "Africa" },
  { id: 77, name: "Absa Group",                     sector: "Financials",                industry: "Banks",                                             country: "South Africa",        continent: "Africa" },
  { id: 78, name: "Atlassian",                      sector: "Information Technology",    industry: "Software & Services",                               country: "Australia",           continent: "Oceania" },
  { id: 79, name: "ENBW",                           sector: "Utilities",                 industry: "Utilities",                                         country: "Germany",             continent: "Europe" },
  { id: 80, name: "MTN Group",                      sector: "Communication Services",    industry: "Telecommunication Services",                        country: "South Africa",        continent: "Africa" },
  { id: 81, name: "RWE",                            sector: "Utilities",                 industry: "Utilities",                                         country: "Germany",             continent: "Europe" },
  { id: 82, name: "KEPCO",                          sector: "Utilities",                 industry: "Utilities",                                         country: "South Korea",         continent: "Asia" },
  { id: 83, name: "Duke Energy",                    sector: "Utilities",                 industry: "Utilities",                                         country: "United States",       continent: "North America" },
  { id: 84, name: "Air New Zealand",                sector: "Industrials",               industry: "Transportation",                                    country: "New Zealand",         continent: "Oceania" },
  { id: 85, name: "MercadoLibre",                   sector: "Consumer Discretionary",    industry: "Consumer Discretionary Distribution & Retail",      country: "Argentina",           continent: "South America" },
  { id: 86, name: "Embraer",                        sector: "Industrials",               industry: "Capital Goods",                                     country: "Brazil",              continent: "South America" },
  { id: 87, name: "Wesfarmers",                     sector: "Consumer Discretionary",    industry: "Consumer Staples Distribution & Retail",            country: "Australia",           continent: "Oceania" },
  { id: 88, name: "Sappi",                          sector: "Materials",                 industry: "Paper & Forest Products",                           country: "South Africa",        continent: "Africa" },
  { id: 89, name: "Fortis (Canada)",                sector: "Utilities",                 industry: "Utilities",                                         country: "Canada",              continent: "North America" },
  { id: 90, name: "James Hardie Industries",        sector: "Materials",                 industry: "Construction Materials",                            country: "Australia",           continent: "Oceania" },
  { id: 91, name: "Metalurgica Gerdau",             sector: "Materials",                 industry: "Metals & Mining",                                   country: "Brazil",              continent: "South America" },
  { id: 92, name: "Anywhere Real Estate Inc.",      sector: "Real Estate",               industry: "Real Estate Management & Development",              country: "United States",       continent: "North America" },
  { id: 93, name: "Sasol",                          sector: "Energy",                    industry: "Oil, Gas & Consumable Fuels",                       country: "South Africa",        continent: "Africa" },
  { id: 94, name: "Colliers International",         sector: "Real Estate",               industry: "Real Estate Management & Development",              country: "Canada",              continent: "North America" },
  { id: 95, name: "Suncorp",                        sector: "Financials",                industry: "Insurance",                                         country: "Australia",           continent: "Oceania" },
  { id: 96, name: "Grupo Argos",                    sector: "Materials",                 industry: "Construction Materials",                            country: "Colombia",            continent: "South America" },
  { id: 97, name: "Adcorp",                         sector: "Industrials",               industry: "Commercial & Professional Services",                country: "South Africa",        continent: "Africa" },
  { id: 98, name: "Warehouse Group",                sector: "Consumer Discretionary",    industry: "Consumer Discretionary Distribution & Retail",      country: "New Zealand",         continent: "Oceania" },
  { id: 99, name: "Nubank",                         sector: "Financials",                industry: "Financial Services",                                country: "Brazil",              continent: "South America" },
  { id: 100,name: "Natura & Co.",                   sector: "Consumer Staples",          industry: "Household & Personal Products",                     country: "Brazil",              continent: "South America" },
];
```

---

## THE 8 DOCUMENT TYPES (exact names and metadata)

```js
const DOCUMENT_TYPES = [
  {
    id: "doc1",
    label: "Code of Conduct",
    shortLabel: "CoC",
    pillar: "Normative & Ethical",
    source: "ir",         // ir = company IR page, edgar = SEC EDGAR, mixed = both
    required: true,
    filingType: null,     // SEC filing form type if applicable
    notes: "Code of Business Conduct / Code of Ethics. Almost always on IR/Governance page."
  },
  {
    id: "doc2",
    label: "Ethics & Compliance Policy",
    shortLabel: "Ethics",
    pillar: "Normative & Ethical",
    source: "ir",
    required: true,
    filingType: null,
    notes: "Often bundled with CoC. If same doc, save in both folders."
  },
  {
    id: "doc3",
    label: "Responsible AI / AI Ethics Guidelines",
    shortLabel: "AI Ethics",
    pillar: "Normative & Ethical",
    source: "ir",
    required: true,
    filingType: null,
    notes: "Hardest to find. ~40% of companies have standalone policy. Check ESG report if absent."
  },
  {
    id: "doc4",
    label: "ESG / SDG Sustainability Report",
    shortLabel: "ESG",
    pillar: "Governance & Stakeholder",
    source: "ir",
    required: true,
    filingType: null,
    notes: "Must be 2022 or later. Save PDF version, not web version."
  },
  {
    id: "doc5",
    label: "Annual Report",
    shortLabel: "Annual",
    pillar: "Strategic & Financial",
    source: "edgar",
    required: true,
    filingType: "10-K",   // or 20-F for foreign private issuers
    notes: "10-K for US companies. 20-F for foreign private issuers on US exchanges. FY2023 or FY2024."
  },
  {
    id: "doc6",
    label: "Earnings Call Transcript (Q4/FY only)",
    shortLabel: "Transcript",
    pillar: "Strategic & Financial",
    source: "mixed",
    required: true,
    filingType: "8-K",
    notes: "Q4 / Full Year wrap-up call ONLY. Seeking Alpha is primary source. Save as .txt or .pdf."
  },
  {
    id: "doc7",
    label: "Proxy Statement / Corporate Governance Report",
    shortLabel: "Proxy",
    pillar: "Governance & Stakeholder",
    source: "edgar",
    required: true,
    filingType: "DEF 14A",
    notes: "DEF 14A for US. AGM Notice / Corp Governance Report for non-US. Filed annually."
  },
  {
    id: "doc8",
    label: "Supplier Code of Conduct",
    shortLabel: "Supplier CoC",
    pillar: "Governance & Stakeholder",
    source: "ir",
    required: false,
    filingType: null,
    notes: "Mark N/A if not available — expected for ~40% of companies. Check procurement/sustainability pages."
  }
];
```

---

## FILING PORTAL LOOKUP TABLE (hardcode this — used for smart link generation)

```js
const PORTAL_BY_COUNTRY = {
  "United States": {
    annualReport:    { label: "SEC EDGAR 10-K",    url: (name) => `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(name)}&type=10-K&action=getcompany` },
    proxy:           { label: "SEC EDGAR DEF 14A", url: (name) => `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(name)}&type=DEF+14A&action=getcompany` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/symbol/${name.replace(/\s+/g,'')}/earnings/transcripts` },
    general:         { label: "SEC EDGAR",         url: (name) => `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(name)}&action=getcompany` },
  },
  "Canada": {
    annualReport:    { label: "SEDAR+",            url: (name) => `https://www.sedarplus.ca/csa-party/pages/search.html?search=${encodeURIComponent(name)}` },
    proxy:           { label: "SEDAR+ Proxy",      url: (name) => `https://www.sedarplus.ca/csa-party/pages/search.html?search=${encodeURIComponent(name)}` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' earnings transcript')}` },
    general:         { label: "SEDAR+",            url: (name) => `https://www.sedarplus.ca` },
  },
  "Germany": {
    annualReport:    { label: "Bundesanzeiger",    url: (name) => `https://www.bundesanzeiger.de/pub/de/start?0-2.-top%7Econtent%7Epanel-left%7Ecard_panel%7Elink_to_login=&fulltext=${encodeURIComponent(name)}&btnSuche=Suchen` },
    proxy:           { label: "Boerse Frankfurt",  url: (name) => `https://www.boerse-frankfurt.de/suche?q=${encodeURIComponent(name)}` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year results')}` },
    general:         { label: "Bundesanzeiger",    url: (name) => `https://www.bundesanzeiger.de` },
  },
  "France": {
    annualReport:    { label: "AMF / Euronext",    url: (name) => `https://live.euronext.com/en/search_instruments/search-result?search%5Bquery%5D=${encodeURIComponent(name)}` },
    proxy:           { label: "AMF France",        url: (name) => `https://www.amf-france.org/fr/recherche-de-societes?query=${encodeURIComponent(name)}` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual results transcript')}` },
    general:         { label: "Euronext Paris",    url: (name) => `https://live.euronext.com/en/markets/paris` },
  },
  "Spain": {
    annualReport:    { label: "CNMV",              url: (name) => `https://www.cnmv.es/Portal/Consultas/BusquedaEntidades.aspx` },
    proxy:           { label: "CNMV Governance",   url: (name) => `https://www.cnmv.es/Portal/Consultas/BusquedaEntidades.aspx` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year earnings')}` },
    general:         { label: "CNMV",              url: (name) => `https://www.cnmv.es` },
  },
  "United Kingdom": {
    annualReport:    { label: "FCA NSM",           url: (name) => `https://data.fca.org.uk/artefacts/NSM/TCR/` },
    proxy:           { label: "FCA NSM / LSE",     url: (name) => `https://www.londonstockexchange.com/search?q=${encodeURIComponent(name)}` },
    transcript:      { label: "Seeking Alpha / LSE RNS", url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year results')}` },
    general:         { label: "London Stock Exchange", url: (name) => `https://www.londonstockexchange.com/search?q=${encodeURIComponent(name)}` },
  },
  "Switzerland": {
    annualReport:    { label: "SIX Exchange / IR", url: (name) => `https://www.six-group.com/en/products-services/the-swiss-stock-exchange.html` },
    proxy:           { label: "Company IR (AGM)", url: (name) => `https://www.google.com/search?q=${encodeURIComponent(name+' annual general meeting 2024 invitation')}` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual results')}` },
    general:         { label: "SIX Swiss Exchange",url: (name) => `https://www.six-group.com` },
  },
  "Sweden": {
    annualReport:    { label: "Nasdaq Nordic",     url: (name) => `https://www.nasdaqomxnordic.com/news/company?search=${encodeURIComponent(name)}` },
    proxy:           { label: "Nasdaq Nordic AGM", url: (name) => `https://www.nasdaqomxnordic.com` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year')}` },
    general:         { label: "Nasdaq Stockholm",  url: (name) => `https://www.nasdaqomxnordic.com` },
  },
  "Denmark": {
    annualReport:    { label: "Nasdaq Copenhagen", url: (name) => `https://www.nasdaqomxnordic.com` },
    proxy:           { label: "Nasdaq Copenhagen", url: (name) => `https://www.nasdaqomxnordic.com` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual results')}` },
    general:         { label: "Nasdaq Copenhagen", url: (name) => `https://www.nasdaqomxnordic.com` },
  },
  "Netherlands": {
    annualReport:    { label: "Euronext Amsterdam",url: (name) => `https://live.euronext.com/en/search_instruments/search-result?search%5Bquery%5D=${encodeURIComponent(name)}` },
    proxy:           { label: "Euronext Amsterdam",url: (name) => `https://live.euronext.com/en/markets/amsterdam` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year results')}` },
    general:         { label: "Euronext Amsterdam",url: (name) => `https://live.euronext.com/en/markets/amsterdam` },
  },
  "Australia": {
    annualReport:    { label: "ASX",               url: (name) => `https://www.asx.com.au/markets/company/${name.split(' ')[0].toUpperCase()}` },
    proxy:           { label: "ASX (Notice of AGM)",url: (name) => `https://www.asx.com.au/markets/company/${name.split(' ')[0].toUpperCase()}` },
    transcript:      { label: "ASX Full Year Results",url: (name) => `https://www.asx.com.au/markets/company/${name.split(' ')[0].toUpperCase()}` },
    general:         { label: "ASX",               url: (name) => `https://www.asx.com.au/markets/company` },
  },
  "New Zealand": {
    annualReport:    { label: "NZX",               url: (name) => `https://www.nzx.com/companies` },
    proxy:           { label: "NZX (Notice of AGM)",url: (name) => `https://www.nzx.com/companies` },
    transcript:      { label: "NZX Full Year",     url: (name) => `https://www.nzx.com/companies` },
    general:         { label: "NZX",               url: (name) => `https://www.nzx.com` },
  },
  "South Korea": {
    annualReport:    { label: "DART (Korean EDGAR)",url: (name) => `https://dart.fss.or.kr/dsab002/search.ax?textCrpNm=${encodeURIComponent(name)}` },
    proxy:           { label: "DART",              url: (name) => `https://dart.fss.or.kr` },
    transcript:      { label: "Company IR (English)",url: (name) => `https://www.google.com/search?q=${encodeURIComponent(name+' annual earnings call transcript 2024')}` },
    general:         { label: "DART",              url: (name) => `https://dart.fss.or.kr` },
  },
  "Hong Kong": {
    annualReport:    { label: "HKEX News",         url: (name) => `https://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main.aspx` },
    proxy:           { label: "HKEX Circular",     url: (name) => `https://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main.aspx` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual results')}` },
    general:         { label: "HKEX",              url: (name) => `https://www.hkexnews.hk` },
  },
  "India": {
    annualReport:    { label: "BSE India",         url: (name) => `https://www.bseindia.com/corporates/ann.html` },
    proxy:           { label: "BSE India (AGM)",   url: (name) => `https://www.bseindia.com/corporates/ann.html` },
    transcript:      { label: "NSE India",         url: (name) => `https://www.nseindia.com` },
    general:         { label: "BSE India",         url: (name) => `https://www.bseindia.com` },
  },
  "Brazil": {
    annualReport:    { label: "CVM (Brazilian SEC)",url: (name) => `https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx` },
    proxy:           { label: "CVM",               url: (name) => `https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx` },
    transcript:      { label: "Seeking Alpha / IR",url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual earnings')}` },
    general:         { label: "CVM Brazil",        url: (name) => `https://www.cvm.gov.br` },
  },
  "South Africa": {
    annualReport:    { label: "JSE SENS",          url: (name) => `https://senspdf.jse.co.za` },
    proxy:           { label: "JSE SENS",          url: (name) => `https://senspdf.jse.co.za` },
    transcript:      { label: "Seeking Alpha / IR",url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' full year results')}` },
    general:         { label: "JSE",               url: (name) => `https://www.jse.co.za` },
  },
  "United Arab Emirates": {
    annualReport:    { label: "Company IR only",   url: (name) => `https://www.emirates.com/english/about-us/annual-report/` },
    proxy:           { label: "N/A (state-owned)", url: (name) => `#` },
    transcript:      { label: "N/A (no public calls)", url: (name) => `#` },
    general:         { label: "Emirates IR",       url: (name) => `https://www.emirates.com/english/about-us/` },
  },
  "Mexico": {
    annualReport:    { label: "BMV / Company IR",  url: (name) => `https://www.bmv.com.mx` },
    proxy:           { label: "CNBV",              url: (name) => `https://www.cnbv.gob.mx` },
    transcript:      { label: "Company IR",        url: (name) => `https://www.google.com/search?q=${encodeURIComponent(name+' annual results earnings call')}` },
    general:         { label: "BMV Mexico",        url: (name) => `https://www.bmv.com.mx` },
  },
  "Colombia": {
    annualReport:    { label: "BVC / Company IR",  url: (name) => `https://www.bvc.com.co` },
    proxy:           { label: "Company IR",        url: (name) => `https://www.google.com/search?q=${encodeURIComponent(name+' corporate governance report 2024')}` },
    transcript:      { label: "Seeking Alpha / IR",url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual results')}` },
    general:         { label: "BVC Colombia",      url: (name) => `https://www.bvc.com.co` },
  },
  "Argentina": {
    annualReport:    { label: "CNV / SEC EDGAR",   url: (name) => `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(name)}&type=20-F&action=getcompany` },
    proxy:           { label: "SEC EDGAR (20-F)",  url: (name) => `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(name)}&type=20-F&action=getcompany` },
    transcript:      { label: "Seeking Alpha",     url: (name) => `https://seekingalpha.com/search?query=${encodeURIComponent(name+' annual earnings')}` },
    general:         { label: "SEC EDGAR / CNV",   url: (name) => `https://www.cnv.gob.ar` },
  },
};
```

---

## TRACKER DATA MODEL

Each company-document combination has this state:

```js
// Status options: "pending" | "found" | "not_found" | "na"
// "found"     → document exists, link saved
// "not_found" → document searched for, confirmed doesn't exist → log "No" in tracker
// "na"        → not applicable (e.g. Emirates proxy statement)
// "pending"   → not yet searched

const docState = {
  companyId: 1,
  docId: "doc5",
  status: "found",        // pending | found | not_found | na
  link: "https://...",    // URL where document was found
  fileName: "John_Deere_Annual_Report_10K_FY2024.pdf",
  notes: "",              // free-text notes
  dateCollected: "2025-05-27"
};
```

All state must be persisted in `localStorage` under the key `"fellowship_tracker_v1"` so progress survives page refresh.

---

## APPLICATION VIEWS — build all 5

### VIEW 1: Dashboard (default home screen)

A command-center overview with:

**KPI cards row (4 cards):**
- Companies completed (all 8 docs = done) / 100
- Documents collected / 800 total
- % complete (animated progress ring)
- Documents collected today

**Progress by continent (horizontal stacked bar or segmented bars):**
- North America, Europe, Oceania, South America, Africa, Asia
- Each bar shows: completed / in-progress / not started

**Progress by document type (grid of 8 tiles):**
- One tile per document type
- Shows: X/100 found, color-coded by completion %

**Daily target tracker:**
- Today's date, target = 10 companies
- How many companies fully worked on today
- A simple "you need X more today" message

**Recent activity feed:**
- Last 10 status updates (company name, doc type, status, timestamp)

---

### VIEW 2: Company List (filterable table)

A sortable, filterable table of all 100 companies with:

**Filters (top bar):**
- Continent (multi-select chips)
- Sector (dropdown)
- Status: All / Complete / In Progress / Not Started
- Search box (fuzzy search by company name)

**Table columns:**
- # | Company Name | Country + flag emoji | Sector | Progress bar (X/8 docs) | Status badge | Action button

**Status badges:**
- Complete (green) = all 8 docs resolved (found/not_found/na)
- In Progress (amber) = some docs done
- Not Started (gray) = no docs touched yet

**Clicking a company row** opens the Company Detail view (View 3).

**Batch actions bar** (appears when companies are multi-selected via checkboxes):
- "Mark selected as In Progress"
- "Open all portal links for selected"

---

### VIEW 3: Company Detail (the core work screen)

This is where the user spends most of their time. Opened by clicking a company in the list.

**Header:**
- Company name, sector badge, country + flag, continent
- Overall progress: X/8 documents collected
- Navigation arrows: ← Previous Company | Next Company → (so user can flow through companies without going back to list)

**Smart Portal Links section:**
- Auto-generated based on the company's country using `PORTAL_BY_COUNTRY`
- Show as clickable buttons: "Open EDGAR 10-K", "Open EDGAR DEF 14A", "Open Seeking Alpha", "Open Company IR" (Google search fallback)
- Each button opens in a new tab

**Document collection grid (8 rows, one per document type):**

Each row has:
- Document number + name + pillar badge
- Status toggle: 4 buttons → `Pending` | `✓ Found` | `✗ Not Found` | `N/A`
  - Clicking sets the status; only one can be active at a time
- Link input field: text box to paste the URL where the doc was found (enabled only when status = Found)
- Suggested search button: opens a pre-built Google/EDGAR search for this specific company + document type in a new tab (auto-generate the search URL using company name + document keywords)
- Notes field: small single-line text input for notes
- File name suggestion: auto-display the recommended file name e.g. `Nike_Annual_Report_10K_FY2024.pdf`

**Auto-save:** Every field change immediately saves to localStorage. Show "Saved" flash.

**Special rule alerts:**
- If country is "United Arab Emirates" and doc is Proxy or Transcript → auto-set to N/A and show a note: "Emirates is state-owned — no public AGM or earnings calls"
- If doc is Supplier CoC and status is "Not Found" → show note: "Expected for ~40% of companies — log as No in tracker"
- If doc is AI Ethics and status is "Not Found" → show note: "Absence is valid research data — note it clearly"

---

### VIEW 4: Smart Link Generator / Search Automation

A productivity panel — not a separate page, but accessible from a side panel or modal:

**One-click search URL generator:**
For any selected company + document type, generate and display ready-to-open search URLs for:
1. SEC EDGAR (if US company) — exact URL with company name pre-filled
2. Google filetype:pdf search — e.g. `"Nike" "code of conduct" filetype:pdf`
3. Seeking Alpha transcript search
4. Company IR page search (Google: `"Nike" site:nike.com investor relations`)
5. Filing portal (country-specific from PORTAL_BY_COUNTRY)

All links open in new tabs. Copy button next to each.

**Batch link opener:**
- User selects a company and clicks "Open all 8 source links"
- Opens all relevant portal links for that company at once (with a browser-permission note)

---

### VIEW 5: Export & Reporting

**Excel Tracker Export:**
Generate a downloadable `.csv` file that exactly matches the structure of the provided Excel tracker:

```
Sl no | Company | Sector | Code of Conduct report | Link | Notes | Ethics & Compliance Policy report | Link | Notes | Responsible AI /AI Ethics - Guidelines | Link | Notes | SDG/ESG Report | Link | Notes | Annual Report | Link | Notes | Earning Calls Transcript | Link | Notes | Proxy Statement (US Companies) / Corporate governance report to Investors | Link | Notes | Supplier Code of Conduct(If abailable) | Link | Notes
```

Column values:
- `[Document] report` column: "Yes" if status=found, "No" if status=not_found, "N/A" if status=na, "" if status=pending
- `Link` column: the URL entered by user
- `Notes` column: the notes text entered by user

**Weekly Progress Report Generator:**
A formatted text block the user can copy-paste into an email or Slack message:
```
Weekly Progress Report — [Date]
Researcher: Abhishek Mishra

Overall: [X]/100 companies fully documented, [Y]/800 documents collected ([Z]%)

By Region:
  North America: X/33 complete
  Europe: X/31 complete
  ...

By Document Type:
  Annual Reports: X/100 collected
  Proxy Statements: X/100 collected
  ...

Completed this week: [list of company names]
In progress: [list]
Not started: [list]
```

**Per-company checklist export:**
A printable/copy-paste checklist for any selected company showing which docs are done/pending.

---

## TECHNICAL REQUIREMENTS

**Stack:**
- Single HTML file — React (via CDN from esm.sh or unpkg), no build step required
- Tailwind CSS via CDN for styling
- `xlsx` or `papaparse` library for CSV export
- All state in `localStorage` — no backend, no server needed
- Must work by simply opening the HTML file in a browser

**Performance:**
- 100 companies × 8 docs = 800 state objects — all in localStorage, load on mount
- No lag on filter/search — use `useMemo` for filtered lists
- Debounce all input saves by 300ms

**Design:**
- Clean, minimal, professional dashboard aesthetic
- Dark/light mode toggle (persist preference in localStorage)
- Color coding: green = found, red = not_found, amber = pending, gray = na
- Mobile-friendly enough to use on a laptop — doesn't need to be phone-optimized
- Left sidebar navigation between the 5 views

**Data integrity:**
- On first load, initialize all 800 doc states as "pending"
- Never lose data — every state change writes to localStorage immediately
- Import/export full state as JSON (backup button) so user can transfer between computers

---

## AUTOMATION PRIORITIES (implement in this order)

1. Smart search URL generation (zero-effort, just string building)
2. Auto-set N/A for known impossible docs (Emirates proxy, state-owned companies)
3. Suggested file naming for every doc
4. Progress calculations and dashboard stats
5. CSV export matching tracker format
6. Weekly report text generator
7. "Open all portals" batch link opener

---

## WHAT NOT TO BUILD

- No file upload or file storage (this is a tracker, not a file manager)
- No authentication
- No backend or API calls
- No web scraping (browser restrictions make this impossible; links open externally)
- No drag-and-drop reordering (not needed)

---

## FILE NAMING CONVENTION

Auto-suggest this format in the UI for every document:
```
[CompanyName]_[DocType]_[Year].pdf
```
Examples:
- `Nike_Code_of_Conduct_2024.pdf`
- `Nike_Annual_Report_10K_FY2024.pdf`
- `Nike_Proxy_Statement_DEF14A_2024.pdf`
- `Bayer_ESG_Report_2023.pdf`
- `Novo_Nordisk_Earnings_Transcript_Q4_FY2024.txt`

Use underscores, no spaces. Strip special characters from company names (L'Oréal → LOreal, etc.)

---

## EDGE CASES TO HANDLE

| Company | Issue | Handling |
|---|---|---|
| Emirates | State-owned, no exchange listing, no earnings calls | Auto-set proxy + transcript to N/A |
| Crédit Mutuel | French cooperative, not publicly listed | Note: "Cooperative — limited public filings" |
| Deutsche Bahn | German state-owned | Note: "State-owned — use Bundesanzeiger" |
| DZ Bank | German cooperative bank | Note: "Cooperative bank — use Bundesanzeiger" |
| Atlassian | Australian company but NASDAQ-listed → files 20-F on EDGAR | Auto-use EDGAR links even though country = Australia |
| KB Financial Group | Korean company but SEC 20-F filer | Show both DART and EDGAR links |
| Novo Nordisk | Danish company but SEC 20-F filer | Show both Nasdaq Nordic and EDGAR links |
| CFE | Mexican state-owned utility | Note: "State-owned utility — limited public filings" |
| Landesbank BW / DZ Bank | Not exchange-listed | Note: "Use Bundesanzeiger — not exchange-listed" |

---

Build the complete single-file application. Prioritize working functionality over visual polish. All 100 companies and 8 document types must be hardcoded. All state must persist in localStorage. The export must match the exact tracker column structure.
