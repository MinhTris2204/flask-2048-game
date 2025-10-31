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
            print(f">>> PayOS API Request: {self.api_url}")
            print(f">>> Payload: orderCode={payload.get('orderCode')}, amount={payload.get('amount')}")
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            print(f">>> PayOS API Status: {response.status_code}")
            print(f">>> PayOS API Response: {response.text[:500]}")
            
            response.raise_for_status()
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f">>> PayOS API Error: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f">>> Response status: {e.response.status_code}")
                print(f">>> Response body: {e.response.text[:500]}")
            return {"error": str(e), "code": "API_ERROR"}
            
        except Exception as e:
            print(f">>> PayOS Unexpected Error: {type(e).__name__}: {e}")
            return {"error": str(e), "code": "UNKNOWN_ERROR"}

    def _create_signature(self, data: Dict[str, Any]) -> str:
        """
        Tạo signature cho request theo chuẩn PayOS
        """
        # Loại bỏ các field không cần thiết
        filtered_data = {}
        for key, value in data.items():
            if key == "signature":  # Skip signature field
                continue
            if value is None or value == "":  # Skip empty values
                continue
            filtered_data[key] = value
        
        # Sort theo key alphabet
        sorted_data = dict(sorted(filtered_data.items()))
        
        # Tạo query string
        query_parts = []
        for key, value in sorted_data.items():
            # Convert value to string
            if isinstance(value, (int, float)):
                value_str = str(int(value))  # Convert to int string (no decimals)
            else:
                value_str = str(value)
            
            query_parts.append(f"{key}={value_str}")
        
        query_string = "&".join(query_parts)
        
        print(f">>> Signature data string: {query_string}")
        
        # Create HMAC SHA256
        signature = hmac.new(
            self.checksum_key.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        print(f">>> Generated signature: {signature}")
        
        return signature
    
    def verify_webhook_signature(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Verify webhook signature từ PayOS
        """
        try:
            # Lấy signature từ webhook data
            received_signature = webhook_data.get("signature", "")
            if not received_signature:
                print(">>> PayOS Webhook: No signature in data")
                return False
            
            # Lấy data để verify
            data = webhook_data.get("data", {})
            code = webhook_data.get("code")
            
            # Tạo data dict để verify
            verify_data = {"code": code, **data}
            
            # Tạo signature từ data
            expected_signature = self._create_signature(verify_data)
            
            # So sánh signature
            is_valid = received_signature.lower() == expected_signature.lower()
            
            if not is_valid:
                print(f">>> PayOS Webhook: Signature mismatch")
                print(f">>> Received: {received_signature}")
                print(f">>> Expected: {expected_signature}")
            
            return is_valid
            
        except Exception as e:
            print(f">>> PayOS Webhook Verification Error: {type(e).__name__}: {e}")
            return False