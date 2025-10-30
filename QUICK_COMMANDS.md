# QUICK COMMANDS - COPY & PASTE

## 🚀 BƯỚC 1: ĐƯA CODE LÊN GITHUB

```bash
# Mở PowerShell/CMD trong folder "d:\GAME 2048 Py"

# 1. Khởi tạo git (chỉ làm 1 lần)
git init

# 2. Config thông tin (thay YOUR_NAME và YOUR_EMAIL)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 3. Add tất cả files
git add .

# 4. Commit
git commit -m "Initial commit: Ready for Railway deployment"

# 5. Connect với GitHub (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 6. Push lên GitHub
git branch -M main
git push -u origin main
```

**Nếu hỏi username/password:**
- Username: GitHub username của bạn
- Password: Dùng Personal Access Token (không phải password GitHub)
- Tạo token tại: https://github.com/settings/tokens

---

## 🎯 BƯỚC 2: RAILWAY - ENVIRONMENT VARIABLES

Copy và điền vào Railway Variables:

### Variable 1:
```
FLASK_SECRET_KEY
```
Value: `your-super-secret-random-string-12345678` (tự đổi thành string ngẫu nhiên)

### Variable 2:
```
DATABASE_URL
```
Value: Click chọn `${{ MySQL.DATABASE_URL }}` trong Railway

### Variable 3:
```
FLASK_ENV
```
Value: `production`

### Variable 4 (optional - nếu dùng Google Login):
```
GOOGLE_CLIENT_ID
```
Value: Copy từ file `.env` của bạn

### Variable 5 (optional - nếu dùng Google Login):
```
GOOGLE_CLIENT_SECRET
```
Value: Copy từ file `.env` của bạn

---

## 🔄 UPDATE CODE SAU NÀY

Mỗi khi thay đổi code:

```bash
git add .
git commit -m "Mô tả thay đổi của bạn"
git push
```

Railway sẽ TỰ ĐỘNG deploy lại!

---

## 📋 CHECKLIST

- [ ] Đã tạo GitHub account
- [ ] Đã tạo repository trên GitHub
- [ ] Đã push code lên GitHub
- [ ] Đã tạo Railway account (login bằng GitHub)
- [ ] Đã deploy GitHub repo trên Railway
- [ ] Đã thêm MySQL database
- [ ] Đã set tất cả Environment Variables
- [ ] Đã generate domain public
- [ ] Website đã chạy được!

---

## 🔗 LINKS QUAN TRỌNG

- GitHub: https://github.com/
- Railway: https://railway.app/
- Google Console: https://console.cloud.google.com/
- Generate Random Secret: https://randomkeygen.com/
