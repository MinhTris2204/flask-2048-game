# Hướng Dẫn Tạo Ảnh Preview Cho Social Media

## Yêu cầu
Để link web hiển thị đẹp khi share lên Facebook, Messenger, Zalo, cần tạo ảnh preview với:
- **Kích thước**: 1200 x 630 pixels (tỉ lệ 1.91:1)
- **Định dạng**: PNG hoặc JPG
- **Dung lượng**: < 8MB
- **Tên file**: `og-image.png`

## Nội dung ảnh nên có
1. **Logo game 2048** (to, nổi bật)
2. **Text chính**: "GAME 2048" hoặc "Chơi Game 2048 Online"
3. **Text phụ**: "Miễn phí - Có bảng xếp hạng"
4. **Background**: Màu gradient đẹp mắt (cyan/blue như theme hiện tại)
5. **Có thể thêm**: Hình ảnh bàn cờ 2048 hoặc các ô số

## Cách tạo ảnh

### Option 1: Dùng Canva (Khuyên dùng)
1. Truy cập: https://www.canva.com
2. Tạo custom size: 1200 x 630 px
3. Chọn template "Facebook Post" hoặc "Social Media"
4. Design với các yếu tố trên
5. Download dạng PNG

### Option 2: Dùng Photoshop/GIMP
1. Tạo file mới: 1200 x 630 px, 72 DPI
2. Design theo mô tả trên
3. Export dạng PNG

### Option 3: Dùng tool online
- https://www.opengraph.xyz/
- https://www.bannerbear.com/
- https://placid.app/

## Sau khi có ảnh
1. Đặt file `og-image.png` vào folder: `d:\GAME 2048 Py\static\`
2. Code đã được cập nhật tự động để dùng ảnh này

## Test Preview
Sau khi deploy, test xem preview có đẹp không tại:
- Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/
- LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/
- Twitter Card Validator: https://cards-dev.twitter.com/validator

## Ghi chú
- Hiện tại đang dùng `logo.png` (512x512) làm preview tạm
- Nếu tạo được `og-image.png` (1200x630) thì preview sẽ đẹp hơn rất nhiều
- Đừng quên cache-bust bằng cách thêm `?v=` vào URL ảnh
