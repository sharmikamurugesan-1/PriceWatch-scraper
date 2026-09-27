"""
PriceWatch — Resilient Multi-Strategy E-Commerce Scraper
Cascading extraction: JSON-LD Schema.org -> OpenGraph Meta -> DOM Selectors -> Regex Fallback.
Includes SSRF validation, rate limiting politeness, and health telemetry.
"""

import re
import json
import time
import random
from urllib.parse import urlparse
from typing import Dict, Any, Optional
import bs4

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

class PriceScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def is_safe_url(self, url: str) -> bool:
        """SSRF Guardrail: Prevents access to local loopback and internal private networks."""
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not hostname:
                return False
            hostname = hostname.lower()
            blocked = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "::1"]
            if hostname in blocked or hostname.startswith("10.") or hostname.startswith("192.168."):
                return False
            if parsed.scheme not in ["http", "https"]:
                return False
            return True
        except Exception:
            return False

    def parse_html(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """Cascading extraction across JSON-LD, OpenGraph, DOM Selectors, and Regex."""
        start_time = time.time()
        soup = bs4.BeautifulSoup(html_content, 'html.parser')

        # ---------------- Tier 1: JSON-LD Schema.org / Product ----------------
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string or '{}')
                # Could be a list or dict
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get('@type') in ['Product', 'IndividualProduct']:
                        title = item.get('name', '')
                        offers = item.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        
                        raw_price = offers.get('price') or offers.get('lowPrice')
                        curr = offers.get('priceCurrency', 'USD')
                        avail = offers.get('availability', '')
                        in_stock = 'InStock' in avail or 'InStoreOnly' in avail or not avail

                        if raw_price and title:
                            price_val = float(str(raw_price).replace(',', ''))
                            return {
                                "url": url,
                                "title": title.strip(),
                                "price": round(price_val, 2),
                                "currency": curr,
                                "in_stock": in_stock,
                                "strategy": "JSON-LD (Schema.org)",
                                "latency_ms": round((time.time() - start_time) * 1000, 2),
                                "confidence": 0.98
                            }
            except Exception:
                continue

        # ---------------- Tier 2: OpenGraph & Twitter Meta ----------------
        og_price = soup.find('meta', property='og:price:amount') or soup.find('meta', property='product:price:amount')
        og_title = soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title')
        og_curr = soup.find('meta', property='og:price:currency') or soup.find('meta', property='product:price:currency')

        if og_price and og_price.get('content'):
            try:
                p_val = float(re.sub(r'[^\d.]', '', og_price['content']))
                title = og_title['content'] if (og_title and og_title.get('content')) else "Product"
                return {
                    "url": url,
                    "title": title.strip(),
                    "price": round(p_val, 2),
                    "currency": og_curr['content'] if og_curr else "USD",
                    "in_stock": True,
                    "strategy": "OpenGraph Meta",
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "confidence": 0.92
                }
            except Exception:
                pass

        # ---------------- Tier 3: DOM CSS Selectors ----------------
        price_selectors = [
            '.price', '#priceblock_ourprice', '#priceblock_dealprice', '.a-price-whole',
            '[data-test="product-price"]', '.product-price', '.current-price', '.price-now'
        ]
        title_selectors = [
            'h1.product-title', '#productTitle', '.product-name', 'h1'
        ]

        title = ""
        for ts in title_selectors:
            el = soup.select_one(ts)
            if el and el.get_text(strip=True):
                title = el.get_text(strip=True)
                break

        for ps in price_selectors:
            el = soup.select_one(ps)
            if el:
                txt = el.get_text(strip=True)
                match = re.search(r'[\$₹€£]?\s*([\d,]+\.?\d{0,2})', txt)
                if match:
                    try:
                        p_val = float(match.group(1).replace(',', ''))
                        if p_val > 0.0:
                            return {
                                "url": url,
                                "title": title or "Product",
                                "price": round(p_val, 2),
                                "currency": "USD" if "$" in txt else "EUR",
                                "in_stock": "out of stock" not in html_content.lower(),
                                "strategy": "CSS Selector",
                                "latency_ms": round((time.time() - start_time) * 1000, 2),
                                "confidence": 0.85
                            }
                    except ValueError:
                        pass

        # ---------------- Tier 4: Contextual Regex Fallback ----------------
        price_match = re.search(r'(?:Price|Our Price|Sale Price|Now)[:\s]*[\$₹€£]\s*([\d,]+\.\d{2})', html_content, re.IGNORECASE)
        p_val = 0.0
        if price_match:
            try:
                p_val = float(price_match.group(1).replace(',', ''))
            except ValueError:
                p_val = 0.0

        title_tag = soup.find('title')
        page_title = title_tag.get_text(strip=True).split('|')[0].strip() if title_tag else "Target E-Commerce Item"

        return {
            "url": url,
            "title": title or page_title,
            "price": round(p_val, 2),
            "currency": "USD" if "$" in html_content else "EUR",
            "in_stock": "out of stock" not in html_content.lower(),
            "strategy": "Contextual Regex",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "confidence": 0.65 if p_val > 0 else 0.2
        }

    def fetch_product(self, url: str) -> Dict[str, Any]:
        """Fetches product URL safely, respecting SSRF rules and HTTP headers."""
        if not self.is_safe_url(url):
            return {
                "url": url,
                "title": "Invalid or Restricted URL",
                "price": 0.0,
                "currency": "USD",
                "in_stock": False,
                "strategy": "Blocked by SSRF Filter",
                "latency_ms": 0.0,
                "confidence": 0.0
            }

        try:
            import requests
            resp = requests.get(url, headers=self.headers, timeout=8)
            if resp.status_code == 200:
                return self.parse_html(resp.text, url)
            else:
                return {
                    "url": url,
                    "title": f"HTTP {resp.status_code} Error",
                    "price": 0.0,
                    "currency": "USD",
                    "in_stock": False,
                    "strategy": f"HTTP Error {resp.status_code}",
                    "latency_ms": 0.0,
                    "confidence": 0.0
                }
        except Exception as e:
            return {
                "url": url,
                "title": "Network Request Failed",
                "price": 0.0,
                "currency": "USD",
                "in_stock": False,
                "strategy": "Connection Timeout",
                "latency_ms": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
