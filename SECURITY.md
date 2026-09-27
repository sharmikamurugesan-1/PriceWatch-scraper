# Security Policy: PriceWatch-scraper

## 1. Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## 2. Threat Model & Mitigations

### Server-Side Request Forgery (SSRF) Prevention
- **IP & Hostname Sanitization:** All target scraping URLs are validated against private IP ranges (RFC 1918) and local loopback addresses (`127.0.0.1`, `localhost`, `169.254.169.254`, `::1`). Requests to internal networks are rejected before making network calls.
- **Allowed Schemes:** Only standard `http://` and `https://` schemes are supported. Dangerous protocols (`file://`, `gopher://`, `ftp://`) are rejected.

### Politeness & Rate Limiting Compliance
- **Robots.txt & Delays:** Requests incorporate configurable delays and rotate standard browser User-Agents.
- **Response Size Quota:** Scraper downloads are capped at 5 MB per page to avoid memory inflation from binary or media streams.

## 3. Reporting a Vulnerability
To report a security vulnerability or bypass of SSRF filters, please contact `sharmika.murugesan@gmail.com`. Disclosures are acknowledged within 24 hours.
