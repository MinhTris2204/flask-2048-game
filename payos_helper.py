"""
PayOS Helper - Simplified version
Xử lý API calls cho PayOS
"""

import hmac
import hashlib
import requests
from typing import Dict, Any


class PayOS:
    def __init__(self, client_id: str, api_key: str, checksum_key: str):
        self.client_id = client_id
        self.api_key = api_key
        self.checksum_key = checksum_key
        self.api_url = "https://api-merchant.payos.vn/v2/payment-requests"

    def create_payment_link(
        self,
        order_code: int,
        amount: int,
        description: str,
        return_url: str,
        cancel_url: str,
        buyer_name: str = None,
        buyer_email: str = None,
    ) -> Dict[str, Any]:
        """
        Tạo link thanh toán PayOS
        """
        payload = {
            "orderCode": order_code,
            "amount": amount,
            "description": description,
            "returnUrl": return_url,
            "cancelUrl": cancel_url,
        }
        
        if buyer_name:
            payload["buyerName"] = buyer_name
        if buyer_email:
            payload["buyerEmail"] = buyer_email
        
        # Tạo signature
        payload["signature"] = self._create_signature(payload)
        
        headers = {
            "x-client-id": self.client_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"PayOS API Error: {e}")
            return {"error": str(e), "code": "API_ERROR"}

    def _create_signature(self, data: Dict[str, Any]) -> str:
        """
        Tạo signature cho request
        """
        # Sort data theo key alphabet
        sorted_data = dict(sorted(data.items()))
        
        # Tạo query string
        query_parts = []
        for key, value in sorted_data.items():
            if key == "signature":  # Skip signature field
                continue
            
            # Convert value to string
            if isinstance(value, (int, float)):
                value_str = str(value)
            elif value is None:
                value_str = ""
            else:
                value_str = str(value)
            
            query_parts.append(f"{key}={value_str}")
        
        query_string = "&".join(query_parts)
        
        # Create HMAC SHA256
        signature = hmac.new(
            self.checksum_key.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return signature
