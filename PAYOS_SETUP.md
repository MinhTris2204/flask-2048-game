# HƯỚNG DẪN TÍCH HỢP PAYOS

## ✅ TẠI SAO CHỌN PAYOS?

**Dành cho sinh viên / cá nhân:**
- ✅ **Đăng ký dễ** - Chỉ cần CMND + tài khoản ngân hàng cá nhân
- ✅ **Phí thấp** - 1.5% / giao dịch
- ✅ **Không phí setup** - Miễn phí hoàn toàn
- ✅ **Không phí duy trì** - Không tốn phí hàng tháng
- ✅ **API tốt** - Docs rõ ràng, dễ tích hợp
- ✅ **Rút tiền dễ** - Về tài khoản ngân hàng miễn phí

---

## BƯỚC 1: ĐĂNG KÝ TÀI KHOẢN PAYOS

### 1.1. Tạo tài khoản

1. Truy cập: https://my.payos.vn/register
2. Đăng ký với:
   - Email
   - Số điện thoại
   - Mật khẩu

### 1.2. Xác thực thông tin

1. Đăng nhập vào https://my.payos.vn
2. Click **"Xác thực"**
3. Upload:
   - **CMND/CCCD** (ảnh rõ nét 2 mặt)
   - **Thông tin ngân hàng** (nhận tiền)
4. Chờ duyệt: **1-2 ngày làm việc**

### 1.3. Tạo kênh thanh toán

1. Sau khi tài khoản được duyệt
2. Vào **"Kênh thanh toán"** > **"Tạo kênh mới"**
3. Điền thông tin:
   - **Tên kênh:** Game 2048
   - **Website:** `https://game2048.up.railway.app`
   - **Loại hình:** Gaming / Digital Content
   - **Webhook URL:** `https://game2048.up.railway.app/payos/webhook`
4. Click **"Tạo kênh"**

### 1.4. Lấy credentials

Sau khi tạo kênh thành công, bạn sẽ thấy 3 keys:

```
Client ID:      xxx-xxx-xxx-xxx
API Key:        xxx-xxx-xxx-xxx
Checksum Key:   xxx-xxx-xxx-xxx
```

**⚠️ Quan trọng:** Copy và lưu lại 3 keys này!

---

## BƯỚC 2: CẬP NHẬT RAILWAY ENVIRONMENT VARIABLES

1. Vào Railway Dashboard
2. Click vào **Flask service** (web app)
3. Tab **"Variables"**
4. Thêm 3 biến:

### Variables cần thêm:

#### 1. PAYOS_CLIENT_ID
```
Variable: PAYOS_CLIENT_ID
Value: <CLIENT_ID_CỦA_BẠN>
```

#### 2. PAYOS_API_KEY
```
Variable: PAYOS_API_KEY
Value: <API_KEY_CỦA_BẠN>
```

#### 3. PAYOS_CHECKSUM_KEY
```
Variable: PAYOS_CHECKSUM_KEY
Value: <CHECKSUM_KEY_CỦA_BẠN>
```

5. Railway sẽ tự động redeploy

---

## BƯỚC 3: PUSH CODE LÊN RAILWAY

```bash
cd "d:\GAME 2048 Py"

git add .
git commit -m "feat: Replace VNPay with PayOS payment gateway"
git push
```

---

## BƯỚC 4: KIỂM TRA SAU KHI DEPLOY

### 4.1. Xem logs

Railway > Flask service > Tab "Deployments" > Click deployment mới

**Phải thấy:**
```
>>> PayOS Client ID: xxx-xxx-...
>>> PayOS Return URL: https://game2048.up.railway.app/payos/return
>>> PayOS Webhook URL: https://game2048.up.railway.app/payos/webhook
```

### 4.2. Seed Premium Plans (nếu chưa có)

Truy cập 1 lần:
```
https://game2048.up.railway.app/admin/seed-premium-plans
```

### 4.3. Test thanh toán

1. Truy cập: `https://game2048.up.railway.app/premium/manage`
2. Click **"Mua ngay"** gói nào đó
3. Chọn **"Thanh toán qua PayOS"**
4. Redirect đến PayOS → Thanh toán bằng:
   - **QR Code** (quét bằng app ngân hàng)
   - **Internet Banking**
   - **Ví điện tử** (Momo, ZaloPay, v.v.)

5. Sau khi thanh toán thành công:
   - Redirect về website
   - Premium được kích hoạt
   - Thời hạn hiển thị đúng

---

## BƯỚC 5: CẤU HÌNH WEBHOOK (QUAN TRỌNG!)

### 5.1. Đăng nhập PayOS Portal

1. Truy cập: https://my.payos.vn
2. Vào **"Kênh thanh toán"** > Click kênh vừa tạo

### 5.2. Cập nhật Webhook URL

1. Tìm mục **"Webhook URL"**
2. Nhập: `https://game2048.up.railway.app/payos/webhook`
3. Click **"Lưu"**

**⚠️ Lưu ý:**
- URL phải dùng **HTTPS**
- URL phải accessible từ internet
- PayOS sẽ gửi webhook đến URL này khi có giao dịch

---

## BƯỚC 6: TEST WEBHOOK (TÙY CHỌN)

Để test webhook hoạt động:

1. Thực hiện 1 giao dịch test (gói rẻ nhất)
2. Xem Railway logs:
   ```
   >>> PayOS Webhook: Order 123 completed successfully
   ```
3. Kiểm tra Premium đã được kích hoạt

---

## 📊 FLOW THANH TOÁN PAYOS

```
User click "Mua Premium"
    ↓
Flask tạo Order (pending)
    ↓
Gọi PayOS API tạo payment link
    ↓
Redirect user đến PayOS checkout
    ↓
User thanh toán (QR/Banking/Wallet)
    ↓
┌─────────────────┬──────────────────┐
│ PayOS Webhook   │ User redirect về │
│ (server-side)   │ Return URL       │
│ ✅ Xử lý chính   │ ✅ Hiển thị UI   │
└─────────────────┴──────────────────┘
    ↓                      ↓
Update Order status    Show success page
Activate Premium       Update UI
```

---

## 💰 PHÍ PAYOS

### Phí giao dịch: 1.5%

**Ví dụ:**
```
Gói Premium 1 tháng:
- Giá bán:          99,000 VND
- Phí PayOS (1.5%):  1,485 VND
- Bạn nhận:         97,515 VND
```

```
Gói Premium 1 năm:
- Giá bán:           599,000 VND
- Phí PayOS (1.5%):    8,985 VND
- Bạn nhận:          590,015 VND
```

### Phí rút tiền: MIỄN PHÍ

- Rút về ngân hàng bất cứ lúc nào
- Không phí chuyển khoản
- Không giới hạn số lần rút

---

## 🔒 BẢO MẬT

**Quan trọng:**

1. ❌ **KHÔNG BAO GIỜ** commit credentials vào Git
2. ❌ **KHÔNG** share API Key / Checksum Key
3. ✅ Chỉ lưu trong Railway Environment Variables
4. ✅ Kiểm tra webhook signature luôn
5. ✅ Nếu bị lộ → Regenerate keys trên PayOS portal

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Không thể tạo link thanh toán"

**Nguyên nhân:**
- Thiếu credentials trong Railway
- Client ID/API Key sai
- Kênh thanh toán chưa được duyệt

**Fix:**
1. Kiểm tra Railway Variables đã add đủ 3 keys chưa
2. Kiểm tra keys copy đúng không (không có space thừa)
3. Kiểm tra kênh thanh toán trên PayOS đã active chưa

### Webhook không hoạt động

**Nguyên nhân:**
- Webhook URL chưa cấu hình
- Webhook URL không accessible
- Signature verification failed

**Fix:**
1. Vào PayOS portal cấu hình Webhook URL
2. Test URL bằng curl:
   ```bash
   curl https://game2048.up.railway.app/payos/webhook
   ```
3. Xem Railway logs để debug

### Premium không được kích hoạt

**Nguyên nhân:**
- Webhook chưa nhận được
- Order status chưa được update

**Fix:**
1. Kiểm tra Railway logs có log webhook không
2. Check database xem order status là gì
3. Test lại với order mới

---

## 📞 HỖ TRỢ

### PayOS Support:
- **Email:** support@payos.vn
- **Website:** https://payos.vn
- **Docs:** https://payos.vn/docs/api

### Facebook Group:
- Tìm "PayOS Developer Community" trên Facebook

---

## 🎉 HOÀN THÀNH!

Sau khi hoàn tất tất cả các bước:

✅ Website đã tích hợp PayOS
✅ Chấp nhận thanh toán QR/Banking/Wallet
✅ Tự động kích hoạt Premium
✅ Tiền về tài khoản ngân hàng cá nhân
✅ Phí chỉ 1.5% - thấp nhất thị trường!

**Chúc mừng! Game của bạn đã sẵn sàng kiếm tiền! 🚀💰**
