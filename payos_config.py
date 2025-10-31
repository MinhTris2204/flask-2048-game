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

# Return URL và Cancel URL (tự động detect Railway domain)
BASE_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if BASE_URL:
    # Railway deployment
    BASE_URL = f"https://{BASE_URL}"
else:
    # Local development
    BASE_URL = "http://localhost:5000"

PAYOS_RETURN_URL = f"{BASE_URL}/payos/return"
PAYOS_CANCEL_URL = f"{BASE_URL}/payos/cancel"
PAYOS_WEBHOOK_URL = f"{BASE_URL}/payos/webhook"

# Debug log
print(f">>> PayOS Client ID: {PAYOS_CLIENT_ID[:8]}***" if PAYOS_CLIENT_ID else ">>> PayOS: No credentials (using demo mode)")
print(f">>> PayOS API Key: {PAYOS_API_KEY[:8]}***" if PAYOS_API_KEY else ">>> PayOS: No API Key")
print(f">>> PayOS Checksum Key length: {len(PAYOS_CHECKSUM_KEY) if PAYOS_CHECKSUM_KEY else 0} chars")
print(f">>> PayOS Checksum Key (first 16): {PAYOS_CHECKSUM_KEY[:16]}***" if PAYOS_CHECKSUM_KEY and len(PAYOS_CHECKSUM_KEY) >= 16 else ">>> PayOS: No Checksum Key")
print(f">>> PayOS Return URL: {PAYOS_RETURN_URL}")
print(f">>> PayOS Webhook URL: {PAYOS_WEBHOOK_URL}")
