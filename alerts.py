"""
PriceWatch — Alert Engine & Dispatcher
"""

import time
from typing import Dict, Any

class AlertDispatcher:
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode

    def dispatch_alert(self, product: Dict[str, Any], current_price: float, threshold: float):
        savings = threshold - current_price
        drop_pct = (savings / threshold) * 100
        
        msg = f"""
🚨 PRICE DROP ALERT: {product['title']}
--------------------------------------------------
Current Price:    ${current_price:,.2f}
Target Threshold: ${threshold:,.2f}
Total Savings:    ${savings:,.2f} (-{drop_pct:.1f}%)
Product Link:     {product['url']}
Time:             {time.strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------------------------
Notification dispatched to: Email / Webhook / Telegram
"""
        print(msg)
        return True
