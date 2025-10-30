import hashlib
import hmac
import urllib.parse
from datetime import datetime
import uuid

class VNPay:
    def __init__(self, tmn_code, hash_secret, url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.url = url

    def create_payment_url(self, amount, order_id, order_info, return_url, ip_addr, 
                          locale="vn", order_type="other", bank_code=None, expire_date=None):
        """
        Tạo URL thanh toán VNPay
        """
        # Tạo thời gian hiện tại
        create_date = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Tạo thời gian hết hạn (mặc định 15 phút)
        if not expire_date:
            from datetime import timedelta
            expire_date = (datetime.now() + timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')
        
        # Chuẩn bị dữ liệu
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.tmn_code,
            'vnp_Amount': str(int(amount * 100)),  # Nhân 100 để loại bỏ phần thập phân
            'vnp_CreateDate': create_date,
            'vnp_CurrCode': 'VND',
            'vnp_IpAddr': ip_addr,
            'vnp_Locale': locale,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': order_type,
            'vnp_ReturnUrl': return_url,
            'vnp_TxnRef': str(order_id),
            'vnp_ExpireDate': expire_date
        }
        
        # Thêm bank_code nếu có
        if bank_code:
            vnp_params['vnp_BankCode'] = bank_code
        
        # Sắp xếp tham số theo thứ tự alphabet
        vnp_params = dict(sorted(vnp_params.items()))
        
        # Tạo query string
        query_string = urllib.parse.urlencode(vnp_params)
        
        # Tạo hash
        hash_data = query_string
        secure_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Tạo URL thanh toán
        payment_url = f"{self.url}?{query_string}&vnp_SecureHash={secure_hash}"
        
        return payment_url

    def verify_return(self, vnp_params):
        """
        Xác thực dữ liệu trả về từ VNPay
        """
        vnp_secure_hash = vnp_params.get('vnp_SecureHash')
        if not vnp_secure_hash:
            return False
        
        # Loại bỏ vnp_SecureHash khỏi params
        vnp_params = {k: v for k, v in vnp_params.items() if k != 'vnp_SecureHash'}
        
        # Sắp xếp tham số
        vnp_params = dict(sorted(vnp_params.items()))
        
        # Tạo query string
        query_string = urllib.parse.urlencode(vnp_params)
        
        # Tạo hash
        hash_data = query_string
        secure_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return secure_hash == vnp_secure_hash

    def parse_response(self, vnp_params):
        """
        Parse dữ liệu phản hồi từ VNPay
        """
        return {
            'txn_ref': vnp_params.get('vnp_TxnRef'),
            'amount': int(vnp_params.get('vnp_Amount', 0)) / 100,
            'bank_code': vnp_params.get('vnp_BankCode'),
            'bank_tran_no': vnp_params.get('vnp_BankTranNo'),
            'card_type': vnp_params.get('vnp_CardType'),
            'order_info': vnp_params.get('vnp_OrderInfo'),
            'pay_date': vnp_params.get('vnp_PayDate'),
            'response_code': vnp_params.get('vnp_ResponseCode'),
            'transaction_no': vnp_params.get('vnp_TransactionNo'),
            'transaction_status': vnp_params.get('vnp_TransactionStatus'),
            'tmn_code': vnp_params.get('vnp_TmnCode')
        }