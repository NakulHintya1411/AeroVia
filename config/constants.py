"""AeroVia – shared constants."""

INDIAN_AIRPORTS = {
    "DEL": {"name": "Indira Gandhi International", "city": "Delhi", "lat": 28.5562, "lon": 77.1000},
    "BOM": {"name": "Chhatrapati Shivaji Maharaj", "city": "Mumbai", "lat": 19.0896, "lon": 72.8656},
    "BLR": {"name": "Kempegowda International", "city": "Bengaluru", "lat": 13.1986, "lon": 77.7066},
    "MAA": {"name": "Chennai International", "city": "Chennai", "lat": 12.9900, "lon": 80.1693},
    "HYD": {"name": "Rajiv Gandhi International", "city": "Hyderabad", "lat": 17.2403, "lon": 78.4294},
    "CCU": {"name": "Netaji Subhas Chandra Bose", "city": "Kolkata", "lat": 22.6520, "lon": 88.4463},
    "PNQ": {"name": "Pune Airport", "city": "Pune", "lat": 18.5822, "lon": 73.9197},
    "GOI": {"name": "Goa International (Dabolim)", "city": "Goa", "lat": 15.3808, "lon": 73.8314},
    "AMD": {"name": "Sardar Vallabhbhai Patel", "city": "Ahmedabad", "lat": 23.0772, "lon": 72.6347},
    "COK": {"name": "Cochin International", "city": "Kochi", "lat": 10.1520, "lon": 76.3919},
    "IXC": {"name": "Chandigarh Airport", "city": "Chandigarh", "lat": 30.6735, "lon": 76.7885},
    "JAI": {"name": "Jaipur International", "city": "Jaipur", "lat": 26.8242, "lon": 75.8122},
    "LKO": {"name": "Chaudhary Charan Singh", "city": "Lucknow", "lat": 26.7606, "lon": 80.8893},
    "PAT": {"name": "Jay Prakash Narayan", "city": "Patna", "lat": 25.5913, "lon": 85.0880},
    "BBI": {"name": "Biju Patnaik International", "city": "Bhubaneswar", "lat": 20.2444, "lon": 85.8178},
    "GAU": {"name": "Lokpriya Gopinath Bordoloi", "city": "Guwahati", "lat": 26.1061, "lon": 91.5859},
    "TRV": {"name": "Trivandrum International", "city": "Thiruvananthapuram", "lat": 8.4821, "lon": 76.9201},
    "IXB": {"name": "Bagdogra Airport", "city": "Siliguri", "lat": 26.6812, "lon": 88.3286},
    "VTZ": {"name": "Visakhapatnam Airport", "city": "Visakhapatnam", "lat": 17.7212, "lon": 83.2245},
    "SXR": {"name": "Sheikh ul-Alam International", "city": "Srinagar", "lat": 33.9871, "lon": 74.7742},
    "IXJ": {"name": "Jammu Airport", "city": "Jammu", "lat": 32.6891, "lon": 74.8374},
    "DED": {"name": "Jolly Grant Airport", "city": "Dehradun", "lat": 30.1897, "lon": 78.1803},
    "RPR": {"name": "Swami Vivekananda Airport", "city": "Raipur", "lat": 21.1804, "lon": 81.7388},
    "NAG": {"name": "Dr. Babasaheb Ambedkar", "city": "Nagpur", "lat": 21.0922, "lon": 79.0472},
}

AIRLINES = {
    "6E": {"name": "IndiGo", "type": "LCC"},
    "AI": {"name": "Air India", "type": "FSC"},
    "SG": {"name": "SpiceJet", "type": "LCC"},
    "UK": {"name": "Vistara", "type": "FSC"},
    "G8": {"name": "Go First", "type": "LCC"},
    "I5": {"name": "Air Asia India", "type": "LCC"},
    "QP": {"name": "Akasa Air", "type": "LCC"},
}

AIRCRAFT_TYPES = {
    "A320": {"seats": 180, "fuel_burn_kg_hr": 2600, "speed_kmh": 840, "ownership_cost_usd_hr": 1200},
    "A321": {"seats": 220, "fuel_burn_kg_hr": 2900, "speed_kmh": 840, "ownership_cost_usd_hr": 1400},
    "B737-800": {"seats": 189, "fuel_burn_kg_hr": 2500, "speed_kmh": 842, "ownership_cost_usd_hr": 1150},
    "B737 MAX 8": {"seats": 178, "fuel_burn_kg_hr": 2200, "speed_kmh": 839, "ownership_cost_usd_hr": 1300},
    "ATR 72": {"seats": 72, "fuel_burn_kg_hr": 620, "speed_kmh": 510, "ownership_cost_usd_hr": 500},
    "Q400": {"seats": 78, "fuel_burn_kg_hr": 680, "speed_kmh": 556, "ownership_cost_usd_hr": 550},
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
    "Peak": [11, 12, 1, 2],
    "Shoulder": [3, 4, 9, 10],
    "Lean": [5, 6, 7, 8],
}
