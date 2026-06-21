"""AeroVia – shared constants (2026 data)."""

# ── Airports ──────────────────────────────────────────────────────────────────
# All domestic airports operated by at least one airline in the directory
INDIAN_AIRPORTS = {
    # Metro
    "DEL": {"name": "Indira Gandhi International",    "city": "Delhi",              "lat": 28.5562, "lon": 77.1000},
    "BOM": {"name": "Chhatrapati Shivaji Maharaj",    "city": "Mumbai",             "lat": 19.0896, "lon": 72.8656},
    "BLR": {"name": "Kempegowda International",       "city": "Bengaluru",          "lat": 13.1986, "lon": 77.7066},
    "MAA": {"name": "Chennai International",           "city": "Chennai",            "lat": 12.9900, "lon": 80.1693},
    "HYD": {"name": "Rajiv Gandhi International",     "city": "Hyderabad",          "lat": 17.2403, "lon": 78.4294},
    "CCU": {"name": "Netaji Subhas Chandra Bose",     "city": "Kolkata",            "lat": 22.6520, "lon": 88.4463},
    # Tier 2
    "PNQ": {"name": "Pune Airport",                   "city": "Pune",               "lat": 18.5822, "lon": 73.9197},
    "GOI": {"name": "Goa International (Dabolim)",    "city": "Goa",                "lat": 15.3808, "lon": 73.8314},
    "GOX": {"name": "Mopa International",             "city": "Goa (Mopa)",         "lat": 15.7120, "lon": 73.9120},
    "AMD": {"name": "Sardar Vallabhbhai Patel",       "city": "Ahmedabad",          "lat": 23.0772, "lon": 72.6347},
    "COK": {"name": "Cochin International",           "city": "Kochi",              "lat": 10.1520, "lon": 76.3919},
    "IXC": {"name": "Chandigarh Airport",             "city": "Chandigarh",         "lat": 30.6735, "lon": 76.7885},
    "JAI": {"name": "Jaipur International",           "city": "Jaipur",             "lat": 26.8242, "lon": 75.8122},
    "LKO": {"name": "Chaudhary Charan Singh",         "city": "Lucknow",            "lat": 26.7606, "lon": 80.8893},
    "PAT": {"name": "Jay Prakash Narayan",            "city": "Patna",              "lat": 25.5913, "lon": 85.0880},
    "BBI": {"name": "Biju Patnaik International",     "city": "Bhubaneswar",        "lat": 20.2444, "lon": 85.8178},
    "GAU": {"name": "Lokpriya Gopinath Bordoloi",     "city": "Guwahati",           "lat": 26.1061, "lon": 91.5859},
    "TRV": {"name": "Trivandrum International",       "city": "Thiruvananthapuram", "lat":  8.4821, "lon": 76.9201},
    "IXB": {"name": "Bagdogra Airport",               "city": "Bagdogra",           "lat": 26.6812, "lon": 88.3286},
    "VTZ": {"name": "Visakhapatnam Airport",          "city": "Visakhapatnam",      "lat": 17.7212, "lon": 83.2245},
    "SXR": {"name": "Sheikh ul-Alam International",   "city": "Srinagar",           "lat": 33.9871, "lon": 74.7742},
    "IXJ": {"name": "Jammu Airport",                  "city": "Jammu",              "lat": 32.6891, "lon": 74.8374},
    "DED": {"name": "Jolly Grant Airport",            "city": "Dehradun",           "lat": 30.1897, "lon": 78.1803},
    "RPR": {"name": "Swami Vivekananda Airport",      "city": "Raipur",             "lat": 21.1804, "lon": 81.7388},
    "NAG": {"name": "Dr. Babasaheb Ambedkar",         "city": "Nagpur",             "lat": 21.0922, "lon": 79.0472},
    # Additional from PDF
    "AGR": {"name": "Agra Airport",                   "city": "Agra",               "lat": 27.1558, "lon": 77.9608},
    "IXA": {"name": "Agartala Airport",               "city": "Agartala",           "lat": 23.8870, "lon": 91.2404},
    "AJL": {"name": "Lengpui Airport",                "city": "Aizawl",             "lat": 23.8406, "lon": 92.6196},
    "ATQ": {"name": "Sri Guru Ram Dass Jee Intl",     "city": "Amritsar",           "lat": 31.7096, "lon": 74.7973},
    "IXU": {"name": "Aurangabad Airport",             "city": "Aurangabad",         "lat": 19.8627, "lon": 75.3981},
    "AYJ": {"name": "Maryada Purushottam Shriram",    "city": "Ayodhya",            "lat": 26.7609, "lon": 82.1954},
    "BEK": {"name": "Bareilly Airport",               "city": "Bareilly",           "lat": 28.4221, "lon": 79.4513},
    "BEP": {"name": "Belagavi Airport",               "city": "Belagavi",           "lat": 15.8593, "lon": 74.6183},
    "BHO": {"name": "Raja Bhoj Airport",              "city": "Bhopal",             "lat": 23.2875, "lon": 77.3374},
    "BKB": {"name": "Nal Airport",                    "city": "Bikaner",            "lat": 28.0706, "lon": 73.2072},
    "IXR": {"name": "Birsa Munda Airport",            "city": "Ranchi",             "lat": 23.3143, "lon": 85.3217},
    "CBD": {"name": "Coimbatore International",       "city": "Coimbatore",         "lat": 11.0300, "lon": 77.0434},
    "DBR": {"name": "Darbhanga Airport",              "city": "Darbhanga",          "lat": 26.1912, "lon": 85.9168},
    "DIB": {"name": "Dibrugarh Airport",              "city": "Dibrugarh",          "lat": 27.4839, "lon": 95.0169},
    "DMU": {"name": "Dimapur Airport",                "city": "Dimapur",            "lat": 25.8839, "lon": 93.7711},
    "RDP": {"name": "Kazi Nazrul Islam Airport",      "city": "Durgapur",           "lat": 23.6225, "lon": 87.2430},
    "GAY": {"name": "Gaya Airport",                   "city": "Gaya",               "lat": 24.7443, "lon": 84.9512},
    "GOP": {"name": "Gorakhpur Airport",              "city": "Gorakhpur",          "lat": 26.7397, "lon": 83.4497},
    "GWL": {"name": "Gwalior Airport",                "city": "Gwalior",            "lat": 26.2933, "lon": 78.2278},
    "HBX": {"name": "Hubli Airport",                  "city": "Hubballi",           "lat": 15.3617, "lon": 75.0849},
    "IMF": {"name": "Tulihal Airport",                "city": "Imphal",             "lat": 24.7600, "lon": 93.8967},
    "IDR": {"name": "Devi Ahilya Bai Holkar",         "city": "Indore",             "lat": 22.7218, "lon": 75.8011},
    "IXI": {"name": "North Lakhimpur Airport",        "city": "Itanagar",           "lat": 27.2950, "lon": 94.1760},
    "JLR": {"name": "Jabalpur Airport",               "city": "Jabalpur",           "lat": 23.1778, "lon": 80.0520},
    "JSA": {"name": "Jaisalmer Airport",              "city": "Jaisalmer",          "lat": 26.8889, "lon": 70.8650},
    "JDH": {"name": "Jodhpur Airport",                "city": "Jodhpur",            "lat": 26.2511, "lon": 73.0489},
    "JRH": {"name": "Jorhat Airport",                 "city": "Jorhat",             "lat": 26.7315, "lon": 94.1755},
    "CNN": {"name": "Kannur International",           "city": "Kannur",             "lat": 11.9186, "lon": 75.5477},
    "KNU": {"name": "Kanpur Airport",                 "city": "Kanpur",             "lat": 26.4044, "lon": 80.3648},
    "IXZ": {"name": "Veer Savarkar International",   "city": "Port Blair",         "lat": 11.6412, "lon": 92.7297},
    "IXD": {"name": "Bamrauli Airport",               "city": "Prayagraj",          "lat": 25.4401, "lon": 81.7339},
    "RJA": {"name": "Rajahmundry Airport",            "city": "Rajahmundry",        "lat": 17.1104, "lon": 81.8182},
    "SHL": {"name": "Shillong Airport",               "city": "Shillong",           "lat": 25.7036, "lon": 91.9787},
    "SLV": {"name": "Shimla Airport",                 "city": "Shimla",             "lat": 31.0818, "lon": 77.0674},
    "SAG": {"name": "Shirdi Airport",                 "city": "Shirdi",             "lat": 19.6886, "lon": 74.3788},
    "IXS": {"name": "Silchar Airport",                "city": "Silchar",            "lat": 24.9129, "lon": 92.9787},
    "STV": {"name": "Surat Airport",                  "city": "Surat",              "lat": 21.1141, "lon": 72.7418},
    "TRZ": {"name": "Tiruchirappalli International",  "city": "Tiruchirappalli",    "lat": 10.7654, "lon": 78.7097},
    "TIR": {"name": "Tirupati Airport",               "city": "Tirupati",           "lat": 13.6325, "lon": 79.5433},
    "UDR": {"name": "Maharana Pratap Airport",        "city": "Udaipur",            "lat": 24.6177, "lon": 73.8961},
    "BDQ": {"name": "Vadodara Airport",               "city": "Vadodara",           "lat": 22.3362, "lon": 73.2263},
    "VNS": {"name": "Lal Bahadur Shastri Airport",    "city": "Varanasi",           "lat": 25.4524, "lon": 82.8593},
    "VGA": {"name": "Vijayawada Airport",             "city": "Vijayawada",         "lat": 16.5304, "lon": 80.7979},
    "IXE": {"name": "Mangaluru International",        "city": "Mangaluru",          "lat": 12.9613, "lon": 74.8900},
    "IXM": {"name": "Madurai Airport",                "city": "Madurai",            "lat":  9.8345, "lon": 78.0934},
    "CCJ": {"name": "Calicut International",          "city": "Kozhikode",          "lat": 11.1368, "lon": 75.9553},
    "IXL": {"name": "Kushok Bakula Rimpochee",        "city": "Leh",                "lat": 34.1359, "lon": 77.5465},
    "SLM": {"name": "Salem Airport",                  "city": "Salem",              "lat":  11.7833, "lon": 78.0656},
    "TCR": {"name": "Thoothukudi Airport",            "city": "Thoothukudi",        "lat":   8.7242, "lon": 78.0258},
    "GAY": {"name": "Gaya Airport",                   "city": "Gaya",               "lat":  24.7443, "lon": 84.9512},
    "DHM": {"name": "Gaggal Airport",                 "city": "Dharamshala",        "lat":  32.1651, "lon": 76.2634},
    "IXK": {"name": "Keshod Airport",                 "city": "Rajkot",             "lat":  21.3171, "lon": 70.2795},
    "GBD": {"name": "North Maharashtra Airport",      "city": "Nashik",             "lat":  19.9663, "lon": 73.9128},
    "MYQ": {"name": "Mysore Airport",                 "city": "Mysuru",             "lat":  12.2310, "lon": 76.6496},
}

# ── Airlines ──────────────────────────────────────────────────────────────────
AIRLINES = {
    "6E": {"name": "IndiGo",          "type": "LCC", "color": "#1a56db"},
    "IX": {"name": "Air India Express","type": "LCC", "color": "#e63946"},
    "AI": {"name": "Air India",        "type": "FSC", "color": "#c8102e"},
    "QP": {"name": "Akasa Air",        "type": "LCC", "color": "#f97316"},
    "SG": {"name": "SpiceJet",         "type": "LCC", "color": "#e63946"},
}

# ── Airline-specific domestic destination lists (IATA codes) ─────────────────
# Source: Comprehensive Indian Airlines Destinations Directory (2026)

AIRLINE_DESTINATIONS = {
    "6E": {  # IndiGo — 74 domestic
        "domestic": [
            "IXA","AGR","AMD","AJL","ATQ","IXU","AYJ","IXB","BEK","BEP",
            "BLR","BHO","BBI","BKB","IXC","MAA","CBD","DBR","DED","DEL",
            "DIB","DMU","RDP","GAY","GOI","GOX","GOP","CCU","GWL","HBX",
            "HYD","IMF","IDR","IXI","JLR","JAI","JSA","IXJ","JDH","JRH",
            "CNN","KNU","COK","CCU","CCJ","IXL","LKO","IXM","IXE","BOM",
            "MYQ","NAG","GBD","PAT","IXZ","IXD","PNQ","RPR","RJA","IXR",
            "SHL","SLV","SAG","IXS","SXR","STV","TRV","TRZ","TIR","UDR",
            "BDQ","VNS","VGA","VTZ",
        ],
    },
    "AI": {  # Air India — 42 domestic
        "domestic": [
            "AMD","ATQ","AYJ","IXB","BLR","BHO","BBI","IXC","MAA","DED",
            "DEL","DIB","GAY","GOI","GAU","HYD","IDR","JAI","JSA","IXJ",
            "JDH","COK","CCU","CCJ","IXL","LKO","IXM","BOM","NAG","PAT",
            "IXZ","PNQ","RPR","IXR","SXR","TRV","TRZ","TIR","UDR","VNS",
            "VGA","VTZ",
        ],
    },
    "IX": {  # Air India Express — 49 domestic
        "domestic": [
            "IXA","AGR","AMD","ATQ","AYJ","IXB","BLR","BBI","IXC","MAA",
            "CBD","DED","DEL","DIB","DMU","GOI","GOP","GWL","HYD","IMF",
            "IDR","JAI","IXJ","JDH","CNN","KNU","COK","CCU","CCJ","IXL",
            "LKO","IXM","IXE","BOM","NAG","PAT","IXZ","IXD","PNQ","SLM",
            "SXR","STV","TRV","TCR","TRZ","TIR","UDR","VNS","VGA",
        ],
    },
    "QP": {  # Akasa Air — 24 domestic
        "domestic": [
            "IXA","AMD","AYJ","IXB","BLR","BBI","IXC","MAA","DEL","GOI",
            "GOP","GAU","GWL","HYD","JAI","COK","CCU","LKO","BOM","PAT",
            "PNQ","SXR","VNS","VTZ",
        ],
    },
    "SG": {  # SpiceJet — 33 domestic
        "domestic": [
            "AMD","ATQ","AYJ","IXB","BLR","MAA","DBR","DEL","DHM","GOI",
            "GOP","GAU","HYD","JAI","JSA","IXJ","JDH","COK","CCU","CCJ",
            "IXL","IXM","BOM","PAT","IXZ","PNQ","IXK","SHL","SXR","TCR",
            "UDR","VNS",
        ],
    },
}

# ── Helper ────────────────────────────────────────────────────────────────────
def get_airline_airports(airline_code: str) -> dict:
    """Return dict of {IATA: airport_info} for a given airline's domestic network."""
    iata_list = AIRLINE_DESTINATIONS.get(airline_code, {}).get("domestic", [])
    return {
        code: INDIAN_AIRPORTS[code]
        for code in iata_list
        if code in INDIAN_AIRPORTS
    }

# ── Aircraft Types (2026 fleet data) ─────────────────────────────────────────
AIRCRAFT_TYPES = {
    # ── IndiGo ──────────────────────────────────────────────────────────────
    "ATR 72-600":           {"seats":  78, "fuel_burn_kg_hr":  620, "speed_kmh": 510, "ownership_cost_usd_hr":  480},
    "A320-200":             {"seats": 180, "fuel_burn_kg_hr": 2600, "speed_kmh": 840, "ownership_cost_usd_hr": 1200},
    "A320neo":              {"seats": 180, "fuel_burn_kg_hr": 2300, "speed_kmh": 840, "ownership_cost_usd_hr": 1250},
    "A320neo (HD)":         {"seats": 186, "fuel_burn_kg_hr": 2350, "speed_kmh": 840, "ownership_cost_usd_hr": 1250},
    "A321neo":              {"seats": 222, "fuel_burn_kg_hr": 2700, "speed_kmh": 840, "ownership_cost_usd_hr": 1450},
    "A321neo (HD)":         {"seats": 232, "fuel_burn_kg_hr": 2750, "speed_kmh": 840, "ownership_cost_usd_hr": 1450},
    "A321neo Stretch":      {"seats": 220, "fuel_burn_kg_hr": 2720, "speed_kmh": 840, "ownership_cost_usd_hr": 1500},
    "A321XLR":              {"seats": 195, "fuel_burn_kg_hr": 2500, "speed_kmh": 840, "ownership_cost_usd_hr": 1600},
    "B787-9":               {"seats": 338, "fuel_burn_kg_hr": 5800, "speed_kmh": 900, "ownership_cost_usd_hr": 3200},
    "B777-300ER (6E)":      {"seats": 531, "fuel_burn_kg_hr": 8200, "speed_kmh": 905, "ownership_cost_usd_hr": 4500},
    # ── Air India ────────────────────────────────────────────────────────────
    "A319-100":             {"seats": 144, "fuel_burn_kg_hr": 2200, "speed_kmh": 840, "ownership_cost_usd_hr": 1000},
    "A320-200 (AI)":        {"seats": 162, "fuel_burn_kg_hr": 2600, "speed_kmh": 840, "ownership_cost_usd_hr": 1200},
    "A320neo (AI)":         {"seats": 174, "fuel_burn_kg_hr": 2300, "speed_kmh": 840, "ownership_cost_usd_hr": 1250},
    "A321-200":             {"seats": 182, "fuel_burn_kg_hr": 2800, "speed_kmh": 840, "ownership_cost_usd_hr": 1350},
    "A321neo (AI)":         {"seats": 188, "fuel_burn_kg_hr": 2700, "speed_kmh": 840, "ownership_cost_usd_hr": 1450},
    "B737 MAX 8 (AI)":      {"seats": 178, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "B777-200LR":           {"seats": 273, "fuel_burn_kg_hr": 7200, "speed_kmh": 905, "ownership_cost_usd_hr": 4000},
    "B777-300ER (AI)":      {"seats": 342, "fuel_burn_kg_hr": 8200, "speed_kmh": 905, "ownership_cost_usd_hr": 4500},
    "B787-8":               {"seats": 256, "fuel_burn_kg_hr": 5200, "speed_kmh": 900, "ownership_cost_usd_hr": 2800},
    "B787-9 (AI)":          {"seats": 279, "fuel_burn_kg_hr": 5800, "speed_kmh": 900, "ownership_cost_usd_hr": 3200},
    "A350-900":             {"seats": 316, "fuel_burn_kg_hr": 5500, "speed_kmh": 910, "ownership_cost_usd_hr": 3500},
    # ── Air India Express ────────────────────────────────────────────────────
    "A320-200 (IX)":        {"seats": 180, "fuel_burn_kg_hr": 2600, "speed_kmh": 840, "ownership_cost_usd_hr": 1200},
    "A320neo (IX)":         {"seats": 186, "fuel_burn_kg_hr": 2300, "speed_kmh": 840, "ownership_cost_usd_hr": 1250},
    "A321neo (IX)":         {"seats": 192, "fuel_burn_kg_hr": 2700, "speed_kmh": 840, "ownership_cost_usd_hr": 1450},
    "A321neo HD (IX)":      {"seats": 232, "fuel_burn_kg_hr": 2750, "speed_kmh": 840, "ownership_cost_usd_hr": 1450},
    "B737-800 (IX)":        {"seats": 189, "fuel_burn_kg_hr": 2500, "speed_kmh": 842, "ownership_cost_usd_hr": 1150},
    "B737 MAX 8 (IX)":      {"seats": 180, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "B737 MAX 8 Std (IX)":  {"seats": 189, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    # ── Akasa Air ────────────────────────────────────────────────────────────
    "B737 MAX 8 (QP)":      {"seats": 174, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "B737 MAX 8-200 HD":    {"seats": 197, "fuel_burn_kg_hr": 2250, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    # ── SpiceJet ─────────────────────────────────────────────────────────────
    "B737-700":             {"seats": 149, "fuel_burn_kg_hr": 2100, "speed_kmh": 840, "ownership_cost_usd_hr": 1000},
    "B737-800 (SG)":        {"seats": 189, "fuel_burn_kg_hr": 2500, "speed_kmh": 842, "ownership_cost_usd_hr": 1150},
    "B737 MAX 8 (SG)":      {"seats": 197, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "Q400":                 {"seats":  78, "fuel_burn_kg_hr":  680, "speed_kmh": 556, "ownership_cost_usd_hr":  520},
    "Q400 HD":              {"seats":  90, "fuel_burn_kg_hr":  700, "speed_kmh": 556, "ownership_cost_usd_hr":  520},
}

# Fleet per airline — Route Builder shows only these when airline is selected
AIRLINE_FLEET = {
    "6E": ["ATR 72-600", "A320-200", "A320neo", "A320neo (HD)", "A321neo",
           "A321neo (HD)", "A321neo Stretch", "A321XLR", "B787-9", "B777-300ER (6E)"],
    "AI": ["A319-100", "A320-200 (AI)", "A320neo (AI)", "A321-200", "A321neo (AI)",
           "B737 MAX 8 (AI)", "B777-200LR", "B777-300ER (AI)", "B787-8", "B787-9 (AI)", "A350-900"],
    "IX": ["A320-200 (IX)", "A320neo (IX)", "A321neo (IX)", "A321neo HD (IX)",
           "B737-800 (IX)", "B737 MAX 8 (IX)", "B737 MAX 8 Std (IX)"],
    "QP": ["B737 MAX 8 (QP)", "B737 MAX 8-200 HD"],
    "SG": ["B737-700", "B737-800 (SG)", "B737 MAX 8 (SG)", "Q400", "Q400 HD"],
}

# Default (most common) aircraft per airline
AIRLINE_AIRCRAFT = {
    "6E": "A320neo",
    "IX": "A320neo (IX)",
    "AI": "A321neo (AI)",
    "QP": "B737 MAX 8 (QP)",
    "SG": "B737-800 (SG)",
}

# ── Default Cost Assumptions — calibrated to Indian aviation, May 2026 ─────────
# ATF: Govt capped at ₹75.6/L for domestic (April 2026); was ₹104/L before cap
# Crew: ~13-15% of revenue for LCCs (IndiGo), 16-18% for FSCs (Air India)
# Maintenance: ₹9,500-12,000/FH for narrowbody (A320neo family, 2026 rates)
# Airport charges: AAI revised upward in Jan 2026; metro ~₹18,000/sector
# Overhead: 7-9% for LCCs; includes sales, admin, distribution, insurance
# Yield: Domestic RPK yield ~₹4.8-5.2 (post-2025 fare recovery); intl higher
# USD/INR: RBI reference rate, June 2026
# ── Default Cost Assumptions ─────────────────────────────────────────────────
# Source: IATA Industry Data 2025 (network carrier economics, operating ratio 96.1%)
# Calibrated for Indian domestic aviation, June 2026
#
# IATA 2025 cost structure (% of total costs):
#   Fuel 31% | Crew 11% | Maintenance 12% | Ownership 9% | Airport 7%
#   Sales/Mktg 7% | Ground Handling 5% | Overflight 5% | Pax Services 4%
#   G&A 6% | Other 2% → Profit margin 3.9%
#
# ATF: IOCL Delhi April 1 2026 — ₹1,04,927/KL = ₹104.93/L
# Crew: IATA 11% of costs → ~10.6% of revenue; Indian avg ~12% (DGCA norms)
# Maintenance: IATA 12% of costs — includes line + heavy maint amortisation → ₹14,500/FH
# Airport+Ground: IATA (7%+5%) of costs → combined ₹40,000/sector (AAI + handling)
# Overhead: IATA (G&A 6% + Sales 7% + Pax 4% + Overflight 5% + Other 2%) → 14% of revenue
# USD/INR: 94.33 — actual rate, June 2026
# Yield: ₹4.9/RPK — domestic fare recovery 2025-26
DEFAULT_COST_ASSUMPTIONS = {
    "atf_price_inr_per_litre": 104.93,        # IOCL Delhi, April 1 2026 (₹1,04,927/KL)
    "crew_cost_pct_of_revenue": 0.12,          # IATA: 11% of costs → ~12% Indian avg
    "maintenance_cost_per_flight_hour": 14500, # IATA: 12% of costs incl. heavy maint
    "airport_charges_per_sector": 40000,       # IATA: airport(7%) + ground(5%) = 12% of costs
    "overhead_pct_of_revenue": 0.14,           # IATA: G&A+Sales+Pax+Overflight+Other = ~24% costs
    "usd_inr_rate": 94.33,                     # Actual rate, June 2026
    "avg_yield_inr_per_km": 4.9,               # Domestic RPK yield, post-2025 fare recovery
}

SEASONS = {
    "Peak":     [11, 12, 1, 2],
    "Shoulder": [3, 4, 9, 10],
    "Lean":     [5, 6, 7, 8],
}

# ── International Airports ────────────────────────────────────────────────────
INTERNATIONAL_AIRPORTS = {
    # Middle East
    "DXB": {"name": "Dubai International",          "city": "Dubai",          "country": "UAE",         "lat": 25.2532, "lon": 55.3657},
    "AUH": {"name": "Abu Dhabi International",      "city": "Abu Dhabi",      "country": "UAE",         "lat": 24.4330, "lon": 54.6511},
    "SHJ": {"name": "Sharjah International",        "city": "Sharjah",        "country": "UAE",         "lat": 25.3286, "lon": 55.5172},
    "RKT": {"name": "Ras Al Khaimah International", "city": "Ras Al Khaimah", "country": "UAE",         "lat": 25.6135, "lon": 55.9388},
    "AAN": {"name": "Al Ain International",         "city": "Al Ain",         "country": "UAE",         "lat": 24.2617, "lon": 55.6092},
    "FJR": {"name": "Fujairah International",       "city": "Fujairah",       "country": "UAE",         "lat": 25.1121, "lon": 56.3240},
    "DOH": {"name": "Hamad International",          "city": "Doha",           "country": "Qatar",       "lat": 25.2731, "lon": 51.6080},
    "BAH": {"name": "Bahrain International",        "city": "Bahrain",        "country": "Bahrain",     "lat": 26.2708, "lon": 50.6336},
    "KWI": {"name": "Kuwait International",         "city": "Kuwait City",    "country": "Kuwait",      "lat": 29.2267, "lon": 47.9689},
    "MCT": {"name": "Muscat International",         "city": "Muscat",         "country": "Oman",        "lat": 23.5933, "lon": 58.2844},
    "SLL": {"name": "Salalah Airport",              "city": "Salalah",        "country": "Oman",        "lat": 17.0387, "lon": 54.0913},
    "JED": {"name": "King Abdulaziz International", "city": "Jeddah",         "country": "Saudi Arabia","lat": 21.6796, "lon": 39.1565},
    "RUH": {"name": "King Khalid International",    "city": "Riyadh",         "country": "Saudi Arabia","lat": 24.9576, "lon": 46.6988},
    "DMM": {"name": "King Fahd International",      "city": "Dammam",         "country": "Saudi Arabia","lat": 26.4712, "lon": 49.7979},
    # Southeast Asia
    "SIN": {"name": "Changi International",         "city": "Singapore",      "country": "Singapore",   "lat":  1.3644, "lon": 103.9915},
    "KUL": {"name": "Kuala Lumpur International",   "city": "Kuala Lumpur",   "country": "Malaysia",    "lat":  2.7456, "lon": 101.7099},
    "PEN": {"name": "Penang International",         "city": "Penang",         "country": "Malaysia",    "lat":  5.2977, "lon": 100.2769},
    "LGK": {"name": "Langkawi International",       "city": "Langkawi",       "country": "Malaysia",    "lat":  6.3300, "lon": 99.7286},
    "BKK": {"name": "Suvarnabhumi Airport",         "city": "Bangkok",        "country": "Thailand",    "lat": 13.6811, "lon": 100.7474},
    "HKT": {"name": "Phuket International",         "city": "Phuket",         "country": "Thailand",    "lat":  8.1132, "lon": 98.3167},
    "REP": {"name": "Siem Reap International",      "city": "Siem Reap",      "country": "Cambodia",    "lat": 13.4107, "lon": 103.8127},
    "HAN": {"name": "Noi Bai International",        "city": "Hanoi",          "country": "Vietnam",     "lat": 21.2212, "lon": 105.8072},
    "SGN": {"name": "Tan Son Nhat International",   "city": "Ho Chi Minh City","country": "Vietnam",    "lat": 10.8188, "lon": 106.6520},
    "DPS": {"name": "Ngurah Rai International",     "city": "Bali",           "country": "Indonesia",   "lat": -8.7482, "lon": 115.1672},
    # South Asia
    "CMB": {"name": "Bandaranaike International",   "city": "Colombo",        "country": "Sri Lanka",   "lat":  7.1808, "lon": 79.8841},
    "KTM": {"name": "Tribhuvan International",      "city": "Kathmandu",      "country": "Nepal",       "lat": 27.6966, "lon": 85.3591},
    "DAC": {"name": "Hazrat Shahjalal International","city": "Dhaka",         "country": "Bangladesh",  "lat": 23.8433, "lon": 90.3978},
    "JAF": {"name": "Jaffna International",         "city": "Jaffna",         "country": "Sri Lanka",   "lat":  9.7924, "lon": 80.0701},
    # Europe
    "LHR": {"name": "London Heathrow",              "city": "London",         "country": "UK",          "lat": 51.4700, "lon": -0.4543},
    "MAN": {"name": "Manchester Airport",           "city": "Manchester",     "country": "UK",          "lat": 53.3537, "lon": -2.2750},
    "BHX": {"name": "Birmingham Airport",           "city": "Birmingham",     "country": "UK",          "lat": 52.4539, "lon": -1.7480},
    "AMS": {"name": "Amsterdam Schiphol",           "city": "Amsterdam",      "country": "Netherlands", "lat": 52.3086, "lon": 4.7639},
    "CDG": {"name": "Charles de Gaulle",            "city": "Paris",          "country": "France",      "lat": 49.0097, "lon": 2.5479},
    "FRA": {"name": "Frankfurt Airport",            "city": "Frankfurt",      "country": "Germany",     "lat": 50.0379, "lon": 8.5622},
    "FCO": {"name": "Leonardo da Vinci",            "city": "Rome",           "country": "Italy",       "lat": 41.8003, "lon": 12.2389},
    "MXP": {"name": "Milan Malpensa",               "city": "Milan",          "country": "Italy",       "lat": 45.6306, "lon": 8.7281},
    "VIE": {"name": "Vienna International",         "city": "Vienna",         "country": "Austria",     "lat": 48.1103, "lon": 16.5697},
    "CPH": {"name": "Copenhagen Airport",           "city": "Copenhagen",     "country": "Denmark",     "lat": 55.6180, "lon": 12.6508},
    "IST": {"name": "Istanbul Airport",             "city": "Istanbul",       "country": "Turkey",      "lat": 41.2608, "lon": 28.7418},
    "ATH": {"name": "Athens International",         "city": "Athens",         "country": "Greece",      "lat": 37.9364, "lon": 23.9445},
    "GYD": {"name": "Heydar Aliyev International",  "city": "Baku",           "country": "Azerbaijan",  "lat": 40.4675, "lon": 50.0467},
    "TBS": {"name": "Tbilisi International",        "city": "Tbilisi",        "country": "Georgia",     "lat": 41.6692, "lon": 44.9547},
    # North America
    "JFK": {"name": "John F Kennedy International", "city": "New York",       "country": "USA",         "lat": 40.6413, "lon": -73.7781},
    "EWR": {"name": "Newark Liberty International", "city": "Newark",         "country": "USA",         "lat": 40.6895, "lon": -74.1745},
    "ORD": {"name": "O'Hare International",         "city": "Chicago",        "country": "USA",         "lat": 41.9742, "lon": -87.9073},
    "SFO": {"name": "San Francisco International",  "city": "San Francisco",  "country": "USA",         "lat": 37.6213, "lon": -122.3790},
    "IAD": {"name": "Washington Dulles",            "city": "Washington DC",  "country": "USA",         "lat": 38.9531, "lon": -77.4565},
    "YYZ": {"name": "Toronto Pearson International","city": "Toronto",        "country": "Canada",      "lat": 43.6777, "lon": -79.6248},
    "YVR": {"name": "Vancouver International",      "city": "Vancouver",      "country": "Canada",      "lat": 49.1967, "lon": -123.1815},
    # East Asia & Pacific
    "NRT": {"name": "Narita International",         "city": "Tokyo",          "country": "Japan",       "lat": 35.7720, "lon": 140.3929},
    "HKG": {"name": "Hong Kong International",      "city": "Hong Kong",      "country": "China",       "lat": 22.3080, "lon": 113.9185},
    "PVG": {"name": "Shanghai Pudong International","city": "Shanghai",       "country": "China",       "lat": 31.1443, "lon": 121.8083},
    "CAN": {"name": "Guangzhou Baiyun",             "city": "Guangzhou",      "country": "China",       "lat": 23.3924, "lon": 113.2988},
    "MNL": {"name": "Ninoy Aquino International",   "city": "Manila",         "country": "Philippines", "lat": 14.5086, "lon": 121.0194},
    "MEL": {"name": "Melbourne Airport",            "city": "Melbourne",      "country": "Australia",   "lat": -37.6690, "lon": 144.8410},
    "SYD": {"name": "Sydney Kingsford Smith",       "city": "Sydney",         "country": "Australia",   "lat": -33.9399, "lon": 151.1753},
    # Central Asia
    "ALA": {"name": "Almaty International",         "city": "Almaty",         "country": "Kazakhstan",  "lat": 43.3521, "lon": 77.0405},
    "SKD": {"name": "Samarkand International",      "city": "Samarkand",      "country": "Uzbekistan",  "lat": 39.7005, "lon": 66.9838},
    "TAS": {"name": "Islam Karimov International",  "city": "Tashkent",       "country": "Uzbekistan",  "lat": 41.2579, "lon": 69.2812},
    # Africa
    "NBO": {"name": "Jomo Kenyatta International",  "city": "Nairobi",        "country": "Kenya",       "lat": -1.3192, "lon": 36.9275},
    # Indian Ocean
    "MLE": {"name": "Velana International",         "city": "Malé",           "country": "Maldives",    "lat":  4.1918, "lon": 73.5290},
    "MRU": {"name": "Sir Seewoosagur Ramgoolam",    "city": "Mauritius",      "country": "Mauritius",   "lat": -20.4302, "lon": 57.6836},
}

# International destinations per airline
AIRLINE_INTL_DESTINATIONS = {
    "6E": ["AUH","ALA","AMS","ATH","BAH","GYD","DPS","BKK","CMB","CPH",
           "DAC","DOH","DXB","FJR","CAN","HAN","SGN","IST","JAF","JED",
           "KTM","KUL","KWI","LGK","LHR","MLE","MAN","MRU","MCT","NBO",
           "PEN","HKT","RKT","RUH","SLL","SKD","SHJ","REP","SIN","TAS","TBS"],
    "AI": ["AUH","AMS","BAH","DPS","BKK","BHX","ORD","CMB","CPH","DAC",
           "DOH","DXB","FRA","HAN","HKG","JED","KTM","KUL","KWI","LHR",
           "MNL","MEL","MXP","MCT","JFK","EWR","CDG","HKT","RUH","FCO",
           "SFO","PVG","SHJ","SIN","SYD","NRT","YYZ","YVR","VIE","IAD"],
    "IX": ["AUH","AAN","BAH","BKK","DMM","DOH","DXB","JED","KUL","KWI",
           "MCT","PEN","HKT","RKT","RUH","SHJ","SIN"],
    "QP": ["AUH","DOH","HAN","JED","KWI","HKT","RUH"],
    "SG": ["BKK","DXB","FJR","JED","HKT","SHJ"],
}

def get_airline_intl_airports(airline_code: str) -> dict:
    """Return dict of {IATA: airport_info} for international destinations."""
    iata_list = AIRLINE_INTL_DESTINATIONS.get(airline_code, [])
    return {
        code: INTERNATIONAL_AIRPORTS[code]
        for code in iata_list
        if code in INTERNATIONAL_AIRPORTS
    }

# ── Yield Benchmarks by Route Category ───────────────────────────────────────
# Based on Indian aviation market data (2024)
# Yield = Revenue per RPK in ₹

YIELD_BENCHMARKS = {
    # Route category: (min_yield, max_yield, typical_yield, description)
    "metro_trunk":    (3.2, 4.8, 3.8, "High-competition metro routes (DEL-BOM, DEL-BLR etc.) — yield compressed by LCC pricing"),
    "regional":       (4.0, 6.0, 4.8, "Regional routes with moderate competition — balanced yield"),
    "leisure":        (4.5, 7.5, 5.5, "Leisure/holiday routes (GOA, SXR, COK) — strong seasonal yield"),
    "thin_tier2":     (3.5, 5.5, 4.2, "Thin tier-2 city routes — low demand but moderate yield"),
    "northeast_udan": (2.8, 4.5, 3.5, "Northeast/UDAN routes — subsidised, structurally low yield"),
    "gulf_intl":      (5.0, 8.0, 6.2, "Gulf international routes (DXB, AUH, DOH) — strong diaspora demand"),
    "se_asia_intl":   (4.5, 7.0, 5.5, "Southeast Asia international (SIN, KUL, BKK) — leisure + business mix"),
    "europe_intl":    (6.0, 12.0, 8.5, "Long-haul Europe routes — premium cabin heavy, high yield"),
    "us_intl":        (7.0, 14.0, 10.0,"Ultra long-haul USA routes — highest yield in network"),
}

# Auto-classify a route based on origin/destination
def classify_route(origin: str, destination: str) -> tuple:
    """Returns (category_key, yield_inr_per_rpk, description)."""
    intl_gulf = {"DXB","AUH","SHJ","DOH","BAH","KWI","MCT","JED","RUH","DMM","RKT","FJR","AAN","SLL"}
    intl_sea  = {"SIN","KUL","PEN","LGK","BKK","HKT","REP","HAN","SGN","DPS","CMB","KTM","DAC","JAF","MLE"}
    intl_eu   = {"LHR","MAN","BHX","AMS","CDG","FRA","FCO","MXP","VIE","CPH","IST","ATH","GYD","TBS"}
    intl_us   = {"JFK","EWR","ORD","SFO","IAD","YYZ","YVR"}
    intl_east = {"NRT","HKG","PVG","CAN","MNL","MEL","SYD","ALA","SKD","TAS","NBO","MRU"}

    metro = {"DEL","BOM","BLR","MAA","HYD","CCU"}
    leisure_ap = {"GOI","SXR","IXL","TRV","COK","IXZ"}
    northeast = {"GAU","IMF","DIB","DMU","IXA","AJL","IXS","IXB","JRH"}
    udan = {"RPR","IXJ","DED","BEK","GWL","BKB","IXK","SLV","GBD"}

    # International check
    all_intl = intl_gulf | intl_sea | intl_eu | intl_us | intl_east
    if origin in all_intl or destination in all_intl:
        if destination in intl_gulf or origin in intl_gulf:
            b = YIELD_BENCHMARKS["gulf_intl"]
            return "gulf_intl", b[2], b[3]
        if destination in intl_sea or origin in intl_sea:
            b = YIELD_BENCHMARKS["se_asia_intl"]
            return "se_asia_intl", b[2], b[3]
        if destination in intl_eu or origin in intl_eu:
            b = YIELD_BENCHMARKS["europe_intl"]
            return "europe_intl", b[2], b[3]
        if destination in intl_us or origin in intl_us:
            b = YIELD_BENCHMARKS["us_intl"]
            return "us_intl", b[2], b[3]
        b = YIELD_BENCHMARKS["se_asia_intl"]
        return "se_asia_intl", b[2], b[3]

    # Domestic
    both = {origin, destination}
    if both & northeast or both & udan:
        b = YIELD_BENCHMARKS["northeast_udan"]
        return "northeast_udan", b[2], b[3]
    if both & leisure_ap:
        b = YIELD_BENCHMARKS["leisure"]
        return "leisure", b[2], b[3]
    if origin in metro and destination in metro:
        b = YIELD_BENCHMARKS["metro_trunk"]
        return "metro_trunk", b[2], b[3]
    if origin in metro or destination in metro:
        b = YIELD_BENCHMARKS["regional"]
        return "regional", b[2], b[3]
    b = YIELD_BENCHMARKS["thin_tier2"]
    return "thin_tier2", b[2], b[3]
