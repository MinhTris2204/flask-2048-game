"""
PayOS Helper
Xử lý API calls và signature verification cho PayOS
"""

import hmac
import hashlib
import json
import requests
from typing import Dict, Any, Optional


class PayOS:
    def __init__(self, client_id: str, api_key: str, checksum_key: str, api_url: str):
        self.client_id = client_id
        self.api_key = api_key
        self.checksum_key = checksum_key
        self.api_url = api_url

    def create_payment_link(
        self,
        order_code: int,
        amount: int,
        description: str,
        return_url: str,
        cancel_url: str,
        buyer_name: Optional[str] = None,
        buyer_email: Optional[str] = None,
        buyer_phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Tạo link thanh toán PayOS
        
        Args:
            order_code: Mã đơn hàng (unique)
            amount: Số tiền (VND)
            description: Mô tả giao dịch
            return_url: URL redirect sau khi thanh toán thành công
            cancel_url: URL redirect khi hủy thanh toán
            buyer_name: Tên người mua (optional)
            buyer_email: Email người mua (optional)
            buyer_phone: SĐT người mua (optional)
            
        Returns:
            dict: Response từ PayOS API
        """
        payload = {
            "orderCode": order_code,
            "amount": amount,
            "description": description,
            "returnUrl": return_url,
            "cancelUrl": cancel_url,
        }
        
        # Thêm thông tin buyer nếu có
        if buyer_name:
            payload["buyerName"] = buyer_name
        if buyer_email:
            payload["buyerEmail"] = buyer_email
        if buyer_phone:
            payload["buyerPhone"] = buyer_phone
        
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

    def verify_webhook_signature(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Verify signature từ webhook
        
        Args:
            webhook_data: Dữ liệu từ webhook (bao gồm signature)
            
        Returns:
            bool: True nếu signature hợp lệ
        """
        received_signature = webhook_data.get("signature", "")
        data = webhook_data.get("data", {})
        
        if not received_signature or not data:
            return False
        
        # Sort data theo key alphabet
        sorted_data = self._sort_dict_recursive(data)
        
        # Tạo query string
        query_string = self._dict_to_query_string(sorted_data)
        
        # Tạo signature để so sánh
        computed_signature = hmac.new(
            self.checksum_key.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return computed_signature == received_signature

    def _sort_dict_recursive(self, obj: Any) -> Any:
        """
        Sort dictionary recursively
        """
        if isinstance(obj, dict):
            return dict(sorted((k, self._sort_dict_recursive(v)) for k, v in obj.items()))
        elif isinstance(obj, list):
            return [self._sort_dict_recursive(item) for item in obj]
        else:
            return obj

    def _dict_to_query_string(self, obj: Dict[str, Any]) -> str:
        """
        Convert dict to query string for signature
        """
        query_parts = []
        
        for key, value in obj.items():
            if isinstance(value, (int, float, bool)):
                value_str = str(value).lower() if isinstance(value, bool) else str(value)
            elif value is None or value == "null" or value == "NULL":
                value_str = ""
            elif isinstance(value, list):
                value_str = json.dumps(value, separators=(',', ':'))
            elif isinstance(value, dict):
                value_str = json.dumps(value, separators=(',', ':'))
            else:
                value_str = str(value)
            
            query_parts.append(f"{key}={value_str}")
        
        return "&".join(query_parts)

    def get_payment_info(self, order_code: int) -> Dict[str, Any]:
        """
        Lấy thông tin thanh toán
        
        Args:
            order_code: Mã đơn hàng
            
        Returns:
            dict: Thông tin thanh toán
        """
        url = f"{self.api_url}/{order_code}"
        headers = {
            "x-client-id": self.client_id,
            "x-api-key": self.api_key,
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"PayOS Get Payment Info Error: {e}")
            return {"error": str(e), "code": "API_ERROR"}

    def cancel_payment(self, order_code: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Hủy thanh toán
        
        Args:
            order_code: Mã đơn hàng
            reason: Lý do hủy (optional)
            
        Returns:
            dict: Response từ PayOS
        """
        url = f"{self.api_url}/{order_code}/cancel"
        headers = {
            "x-client-id": self.client_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {}
        if reason:
            payload["cancellationReason"] = reason
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"PayOS Cancel Payment Error: {e}")
            return {"error": str(e), "code": "API_ERROR"}
