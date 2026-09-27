"""
PriceWatch — REST API Server
Provides endpoints for scraping target URLs, tracking product price histories,
configuring alert thresholds, and evaluating scraper health.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import PriceScraper
from database import init_db, record_price_observation, get_tracked_products, get_product_history

app = Flask(__name__)
CORS(app)

init_db()
scraper = PriceScraper()

# Seed default demo products if empty
if not get_tracked_products():
    record_price_observation(
        url="https://www.dell.com/en-us/shop/dell-ultrasharp-27-4k-usb-c-hub-monitor",
        title="Dell UltraSharp 27 4K USB-C Hub Monitor (U2723QE)",
        price=389.00,
        target_price=450.00
    )
    record_price_observation(
        url="https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4070-ti/",
        title="NVIDIA GeForce RTX 4070 Ti 12GB GDDR6X",
        price=749.99,
        target_price=720.00
    )

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "service": "PriceWatch Scraper Engine",
        "version": "2.0.0",
        "capabilities": ["cascading_extraction", "json_ld_parsing", "ssrf_protection", "price_alert_engine"]
    })

@app.route('/api/scrape', methods=['POST'])
def scrape_url():
    """Scrapes target URL or parses provided HTML directly (Sandbox Mode)."""
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url", "")
    html_content = data.get("html", "")

    if html_content:
        result = scraper.parse_html(html_content, url or "sandbox-html")
    elif url:
        result = scraper.fetch_product(url)
    else:
        return jsonify({"error": "Either 'url' or 'html' must be provided."}), 400

    return jsonify(result)

@app.route('/api/products', methods=['GET'])
def list_products():
    """Returns watchlist with historical low/high and alert states."""
    products = get_tracked_products()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Adds a new product to the watchlist with target alert threshold."""
    data = request.get_json(force=True) or {}
    url = data.get("url", "")
    title = data.get("title", "")
    price = float(data.get("price", 0.0))
    target_price = float(data.get("target_price", 0.0))

    if not url or not title:
        return jsonify({"error": "URL and Title are required."}), 400

    res = record_price_observation(url, title, price, target_price=target_price)
    return jsonify({"success": True, "data": res})

@app.route('/api/products/<int:prod_id>/history', methods=['GET'])
def product_history(prod_id: int):
    """Returns price timeline for Chart.js."""
    history = get_product_history(prod_id)
    return jsonify(history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
