"""
Unit & Integration Tests for PriceWatch-scraper
Validates JSON-LD schema parsing, OpenGraph extraction, SSRF blocking,
and historical alert triggers.
"""

import os
import pytest
from scraper import PriceScraper
from database import init_db, record_price_observation, get_tracked_products

TEST_DB = "test_pricewatch.db"

@pytest.fixture(autouse=True)
def setup_teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

SAMPLE_JSON_LD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Sony WH-1000XM5 Noise Canceling Headphones</title>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": "Sony WH-1000XM5 Wireless Headphones",
    "offers": {
      "@type": "Offer",
      "priceCurrency": "USD",
      "price": "348.00",
      "availability": "https://schema.org/InStock"
    }
  }
  </script>
</head>
<body><h1>Sony Headphones</h1></body>
</html>
"""

SAMPLE_OPENGRAPH_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta property="og:title" content="Apple MacBook Air 15-inch M3" />
  <meta property="og:price:amount" content="1199.00" />
  <meta property="og:price:currency" content="USD" />
</head>
<body><h1>MacBook Air</h1></body>
</html>
"""

def test_json_ld_extraction():
    scraper = PriceScraper()
    res = scraper.parse_html(SAMPLE_JSON_LD_HTML, "https://sony.com/wh1000xm5")
    
    assert res["title"] == "Sony WH-1000XM5 Wireless Headphones"
    assert res["price"] == 348.00
    assert res["currency"] == "USD"
    assert res["in_stock"] is True
    assert "JSON-LD" in res["strategy"]
    assert res["confidence"] >= 0.95

def test_opengraph_extraction():
    scraper = PriceScraper()
    res = scraper.parse_html(SAMPLE_OPENGRAPH_HTML, "https://apple.com/macbook-air")
    
    assert res["title"] == "Apple MacBook Air 15-inch M3"
    assert res["price"] == 1199.00
    assert "OpenGraph" in res["strategy"]
    assert res["confidence"] >= 0.90

def test_ssrf_blocking():
    scraper = PriceScraper()
    assert scraper.is_safe_url("http://127.0.0.1:8080/admin") is False
    assert scraper.is_safe_url("http://localhost/secret") is False
    assert scraper.is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert scraper.is_safe_url("https://www.dell.com/products") is True

def test_price_history_and_alert_trigger():
    # Target is $400, price drops to $380 -> Alert should trigger
    res = record_price_observation(
        url="https://dell.com/monitor",
        title="Dell 4K Monitor",
        price=380.00,
        target_price=400.00,
        db_path=TEST_DB
    )
    assert res["alert_triggered"] is True
    assert "PRICE DROP ALERT" in res["alert_message"]

    prods = get_tracked_products(db_path=TEST_DB)
    assert len(prods) == 1
    assert prods[0]["current_price"] == 380.00
    assert prods[0]["lowest_price"] == 380.00
