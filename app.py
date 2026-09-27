"""
PriceWatch — Main CLI & Monitor Daemon
"""

import time
from scraper import PriceScraper
from database import PriceDatabase
from alerts import AlertDispatcher

def run_price_check():
    print("=" * 60)
    print("🕸️ PriceWatch — 24/7 E-Commerce Price Monitoring Daemon")
    print("=" * 60)

    db = PriceDatabase("pricewatch.db")
    scraper = PriceScraper()
    dispatcher = AlertDispatcher()

    # Seed default tracked products if none exist
    items = db.get_tracked_items()
    if not items:
        print("[*] Initializing default product monitor watchlist...")
        db.add_product("https://ecommerce-store.example/products/rtx-4070-ti-gpu", "NVIDIA GeForce RTX 4070 Ti", 720.00)
        db.add_product("https://ecommerce-store.example/products/dell-4k-monitor", "Dell UltraSharp 27 4K Monitor", 450.00)
        items = db.get_tracked_items()

    print(f"[*] Monitoring {len(items)} active product listings.")
    
    for item in items:
        url = item['url']
        threshold = item['target_threshold']
        
        data = scraper.fetch_product(url)
        current_price = data['price']
        db.record_price(url, current_price)
        
        print(f"  -> {data['title'][:32]}... | Price: ${current_price:,.2f} | Alert Threshold: ${threshold:,.2f}")
        
        if current_price < threshold:
            dispatcher.dispatch_alert(data, current_price, threshold)

    print("-" * 60)
    print("[✓] Price monitoring poll cycle completed.")
    print("=" * 60)

if __name__ == "__main__":
    run_price_check()
