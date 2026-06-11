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

# ── Aircraft ──────────────────────────────────────────────────────────────────
AIRCRAFT_TYPES = {
    "A320":       {"seats": 180, "fuel_burn_kg_hr": 2600, "speed_kmh": 840, "ownership_cost_usd_hr": 1200},
    "A321":       {"seats": 220, "fuel_burn_kg_hr": 2900, "speed_kmh": 840, "ownership_cost_usd_hr": 1400},
    "B737-800":   {"seats": 189, "fuel_burn_kg_hr": 2500, "speed_kmh": 842, "ownership_cost_usd_hr": 1150},
    "B737 MAX 8": {"seats": 178, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "ATR 72":     {"seats":  72, "fuel_burn_kg_hr":  620, "speed_kmh": 510, "ownership_cost_usd_hr":  500},
    "Q400":       {"seats":  78, "fuel_burn_kg_hr":  680, "speed_kmh": 556, "ownership_cost_usd_hr":  550},
}

# Preferred aircraft per airline (for defaults)
AIRLINE_AIRCRAFT = {
    "6E": "A320",
    "IX": "A320",
    "AI": "A321",
    "QP": "B737 MAX 8",
    "SG": "B737-800",
}

DEFAULT_COST_ASSUMPTIONS = {
    "atf_price_inr_per_litre": 95.0,
    "crew_cost_pct_of_revenue": 0.12,
    "maintenance_cost_per_flight_hour": 8000,
    "airport_charges_per_sector": 15000,
    "overhead_pct_of_revenue": 0.08,
    "usd_inr_rate": 83.5,
    "avg_yield_inr_per_km": 4.2,
}

SEASONS = {
    "Peak":     [11, 12, 1, 2],
    "Shoulder": [3, 4, 9, 10],
    "Lean":     [5, 6, 7, 8],
}
