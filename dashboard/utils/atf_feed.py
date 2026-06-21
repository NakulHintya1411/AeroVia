"""Live ATF price fetcher with fallback."""
import requests, re, datetime

FALLBACK_PRICE = 104.93  # IOCL Delhi April 2026 (₹1,04,927/KL)
_cache = {"price": None, "fetched_at": None}

def _stale():
    if not _cache["fetched_at"]: return True
    return (datetime.datetime.now() - _cache["fetched_at"]).seconds / 60 > 60

def fetch_atf_price() -> tuple:
    """Returns (price_inr_per_litre, source_str)."""
    if not _stale() and _cache["price"]:
        return _cache["price"], "IOCL (cached)"
    try:
        r = requests.get("https://www.iocl.com/aviation-fuel-prices",
                         timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            for m in re.findall(r'[\d,]+\.\d{2}', r.text):
                val = float(m.replace(",", ""))
                if 70 < val < 150:
                    _cache.update({"price": val, "fetched_at": datetime.datetime.now()})
                    return val, "IOCL (live)"
    except Exception:
        pass
    price = _cache["price"] or FALLBACK_PRICE
    return price, f"Benchmark ₹{price}/L (live unavailable)"
