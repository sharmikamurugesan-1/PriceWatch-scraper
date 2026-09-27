# 🕸️ PriceWatch — 24/7 E-Commerce Price Tracker & Alert System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Automation](https://img.shields.io/badge/Automation-Cron%20Scheduled-brightgreen.svg)]()

> **Impact:** ⚡ Monitors hundreds of product pages 24/7 and alerts on price drops with zero manual intervention.

**PriceWatch** is an automated web scraping system that tracks product prices across e-commerce platforms, logs historical price trends into an SQLite database, and triggers instant alerts via Email (SMTP) or Webhooks when prices drop below user-configured target thresholds.

---

## 📌 Architecture

```
[Target Product URLs]
          │
          ▼
[User-Agent Rotating Scraper] ──► Extracts live price, stock status & title
          │
          ▼
[SQLite Historical Database]   ──► Logs timestamps & price fluctuations
          │
          ▼
[Threshold Comparison Logic]   ──► Checks if Price < Target Threshold
          │
          ▼
[Alert Dispatcher (SMTP/Webhook)] ──► Dispatches instant notifications
```

---

## ✨ Features

- **Multi-Site Scraping Support:** Configurable parser engine with rotating User-Agents to prevent anti-bot blocking.
- **Historical Price Logging:** Stores long-term price history in SQLite for trend analysis.
- **Configurable Threshold Rules:** Set target price limits per product individually.
- **Automated Alerts:** Dispatches instant notifications on verified price drops.
- **Cron Scheduling:** Runs silently in the background on periodic schedules.

---

## 🚀 Quickstart

### 1. Installation
```bash
git clone https://github.com/sharmika-murugesan/PriceWatch-scraper.git
cd PriceWatch-scraper
pip install -r requirements.txt
```

### 2. Run Immediate Price Check
```bash
python app.py
```

### 3. Check Tracked Database
All logged prices and product items are saved in `pricewatch.db`.

---

## 🛠️ Tech Stack

- **Scraping:** BeautifulSoup, Requests, Python 3.10+
- **Database:** SQLite
- **Automation & Alerts:** Schedule, SMTP

---

## 📄 License
MIT License. Developed by **Sharmika Murugesan** — Available for freelance web scraping & automation projects.
