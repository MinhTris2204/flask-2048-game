"""
PayOS Configuration
Đọc từ environment variables
"""

import os

# PayOS Credentials - Lấy từ https://my.payos.vn
PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID", "")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY", "")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY", "")

# PayOS API URLs
PAYOS_API_URL = "https://api-merchant.payos.vn/v2/payment-requests"

# Return/Cancel/Webhook base URL
# Ưu tiên lấy từ APP_BASE_URL/BASE_URL; nếu không có thì dùng RAILWAY_PUBLIC_DOMAIN;
# cuối cùng mặc định theo domain mới: http://game2048.io.vn
_app_base = os.getenv("APP_BASE_URL") or os.getenv("BASE_URL")
if _app_base:
    if _app_base.startswith("http://") or _app_base.startswith("https://"):
        BASE_URL = _app_base
    else:
        BASE_URL = f"https://{_app_base}"
else:
    _railway = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if _railway:
        BASE_URL = f"https://{_railway}"
    else:
        BASE_URL = "http://game2048.io.vn"

PAYOS_RETURN_URL = f"{BASE_URL}/payos/return"
PAYOS_CANCEL_URL = f"{BASE_URL}/payos/cancel"
PAYOS_WEBHOOK_URL = f"{BASE_URL}/payos/webhook"

# Debug log
print(f">>> PayOS Client ID: {PAYOS_CLIENT_ID[:8]}***" if PAYOS_CLIENT_ID else ">>> PayOS: No credentials (using demo mode)")
print(f">>> PayOS Return URL: {PAYOS_RETURN_URL}")
print(f">>> PayOS Webhook URL: {PAYOS_WEBHOOK_URL}")
