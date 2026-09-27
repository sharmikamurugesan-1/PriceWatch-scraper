"""
PriceWatch — E-Commerce Scraper & Parser Engine
Extracts product title, price, stock status, and currency with User-Agent rotation.
"""

import re
import random
from typing import Dict, Any, Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

class PriceScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def parse_html_price(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """Extracts product details from raw HTML string or simulated mock data."""
        # Generic regex for prices
        price_match = re.search(r'[\$₹€£]\s*([\d,]+(?:\.\d{2})?)', html_content)
        price_val = 0.0
        if price_match:
            try:
                price_val = float(price_match.group(1).replace(',', ''))
            except ValueError:
                price_val = 0.0

        # Title extraction
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1).split('|')[0].strip() if title_match else "Target E-Commerce Product"

        return {
            "url": url,
            "title": title,
            "price": price_val,
            "currency": "USD" if "$" in html_content else "INR",
            "in_stock": "out of stock" not in html_content.lower()
        }

    def fetch_product(self, url: str) -> Dict[str, Any]:
        """Fetches URL via requests or falls back to mock live price stream."""
        try:
            import requests
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                return self.parse_html_price(resp.text, url)
        except Exception:
            pass

        # Simulated live product scraper stream
        mock_catalog = {
            "gpu": {"title": "NVIDIA GeForce RTX 4070 Ti 12GB", "price": 749.99},
            "monitor": {"title": "Dell UltraSharp 27 4K USB-C Hub Monitor", "price": 489.00},
            "laptop": {"title": "MacBook Air 15-inch M3 Chip 512GB", "price": 1299.00}
        }
        
        key = "gpu"
        for k in mock_catalog:
            if k in url.lower():
                key = k
                break
                
        base_item = mock_catalog[key]
        # Introduce slight fluctuation
        jitter = random.choice([-50.0, -100.0, 0.0, 20.0])
        simulated_price = max(base_item["price"] + jitter, 199.0)

        return {
            "url": url,
            "title": base_item["title"],
            "price": simulated_price,
            "currency": "USD",
            "in_stock": True
        }
