# HƯỚNG DẪN DEPLOY LÊN RAILWAY - TỪNG BƯỚC CHI TIẾT

## PHẦN 1: CHUẨN BỊ VÀ ĐƯA CODE LÊN GITHUB

### Bước 1.1: Cài đặt Git (nếu chưa có)

1. Download Git từ: https://git-scm.com/download/win
2. Cài đặt với các option mặc định
3. Kiểm tra cài đặt thành công:
   ```bash
   git --version
   ```

### Bước 1.2: Tạo GitHub Account (nếu chưa có)

1. Truy cập: https://github.com/
2. Click **"Sign up"**
3. Điền thông tin và tạo account

### Bước 1.3: Tạo Repository mới trên GitHub

1. Đăng nhập GitHub
2. Click nút **"+"** góc trên bên phải > **"New repository"**
3. Điền thông tin:
   - **Repository name**: `flask-2048-game` (hoặc tên bạn thích)
   - **Description**: `2048 Game with Flask and MySQL`
   - **Visibility**: Chọn **Public** hoặc **Private**
   - **❌ KHÔNG** tick vào "Add a README file"
   - **❌ KHÔNG** tick vào ".gitignore" và "license"
4. Click **"Create repository"**
5. **GHI NHỚ** URL repository, ví dụ: `https://github.com/your-username/flask-2048-game.git`

### Bước 1.4: Khởi tạo Git trong project

Mở **PowerShell** hoặc **Command Prompt** trong folder project:

```bash
# Di chuyển vào folder project
cd "d:\GAME 2048 Py"

# Khởi tạo git repository
git init

# Kiểm tra status
git status
```

Bạn sẽ thấy danh sách files màu đỏ (chưa được track).

### Bước 1.5: Config Git (lần đầu tiên sử dụng)

```bash
# Set tên và email của bạn
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Bước 1.6: Add và Commit code

```bash
# Add tất cả files
git add .

# Kiểm tra lại
git status

# Commit với message
git commit -m "Initial commit: Flask 2048 game ready for Railway"
```

### Bước 1.7: Connect với GitHub và Push code

```bash
# Thay YOUR_USERNAME và YOUR_REPO bằng thông tin thực tế
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Đổi branch sang main
git branch -M main

# Push code lên GitHub
git push -u origin main
```

**Nếu gặp lỗi authentication:**
- GitHub không cho dùng password trực tiếp nữa
- Bạn cần tạo **Personal Access Token**:
  1. GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
  2. Click **"Generate new token (classic)"**
  3. Chọn scope: **repo** (full control)
  4. Copy token và dùng làm password khi git push

### Bước 1.8: Xác nhận code đã lên GitHub

1. Truy cập: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Refresh trang
3. Bạn sẽ thấy tất cả files đã được upload

---

## PHẦN 2: DEPLOY LÊN RAILWAY

### Bước 2.1: Tạo Railway Account

1. Truy cập: https://railway.app/
2. Click **"Login"** 
3. Chọn **"Login with GitHub"**
4. Authorize Railway truy cập GitHub của bạn

### Bước 2.2: Tạo Project mới

1. Sau khi login, click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Nếu lần đầu: Click **"Configure GitHub App"**
   - Chọn repositories bạn muốn Railway có quyền truy cập
   - Hoặc chọn **"All repositories"**
4. Chọn repository **`flask-2048-game`** (hoặc tên repo bạn đã tạo)
5. Railway sẽ bắt đầu deploy (sẽ fail vì chưa có database)

### Bước 2.3: Thêm MySQL Database

1. Trong project dashboard, click **"New"** (góc trên bên phải)
2. Chọn **"Database"**
3. Chọn **"Add MySQL"**
4. Railway sẽ tự động tạo MySQL instance
5. Đợi vài giây cho MySQL khởi động (có icon màu xanh là OK)

### Bước 2.4: Configure Environment Variables cho Flask App

1. Click vào service **Flask app** (không phải MySQL)
2. Chọn tab **"Variables"**
3. Click **"+ New Variable"** và thêm từng biến sau:

**Biến 1: FLASK_SECRET_KEY**
```
Variable: FLASK_SECRET_KEY
Value: your-random-secret-key-123456789-change-this
```
*(Thay bằng một chuỗi ngẫu nhiên dài và phức tạp)*

**Biến 2: DATABASE_URL**
```
Variable: DATABASE_URL
Value: Click vào "${{ MySQL.DATABASE_URL }}" để chọn
```
*(Railway sẽ tự động tạo reference link đến MySQL)*

**Biến 3: FLASK_ENV**
```
Variable: FLASK_ENV
Value: production
```

**Biến 4 & 5: Google OAuth (nếu dùng)**
```
Variable: GOOGLE_CLIENT_ID
Value: (copy từ file .env của bạn)

Variable: GOOGLE_CLIENT_SECRET
Value: (copy từ file .env của bạn)
```

4. Click **"Add"** cho mỗi biến

### Bước 2.5: Link MySQL với Flask App

1. Vẫn trong Flask app service
2. Tab **"Settings"**
3. Scroll xuống section **"Service"**
4. Click **"Connect"** hoặc **"New Variable"**
5. Chọn MySQL service
6. Railway sẽ tự động thêm `DATABASE_URL` variable

### Bước 2.6: Deploy lại

1. Tab **"Deployments"**
2. Click vào deployment mới nhất
3. Xem logs để kiểm tra
4. Đợi cho đến khi thấy **"Success"** hoặc **"Active"**

### Bước 2.7: Enable Public Access

1. Vẫn trong Flask app service
2. Tab **"Settings"**
3. Scroll xuống **"Networking"**
4. Click **"Generate Domain"**
5. Railway sẽ tạo một URL dạng: `https://flask-2048-game-production-xxxx.up.railway.app`
6. **Copy URL này!**

### Bước 2.8: Test App

1. Mở URL vừa copy trong trình duyệt
2. Đợi vài giây (lần đầu có thể hơi lâu)
3. Website của bạn sẽ xuất hiện!

---

## PHẦN 3: CẬP NHẬT GOOGLE OAUTH (NẾU DÙNG)

### Bước 3.1: Update Redirect URI

1. Truy cập: https://console.cloud.google.com/apis/credentials
2. Click vào OAuth 2.0 Client ID của bạn
3. Trong **"Authorized redirect URIs"**, click **"+ ADD URI"**
4. Thêm URI mới:
   ```
   https://YOUR-APP.up.railway.app/login/google/authorized
   ```
   *(Thay YOUR-APP bằng domain Railway của bạn)*
5. Click **"Save"**

### Bước 3.2: Test Google Login

1. Truy cập website Railway
2. Click "Login with Google"
3. Nếu thành công → Done! ✅

---

## PHẦN 4: CẬP NHẬT CODE SAU NÀY

Mỗi khi bạn thay đổi code:

```bash
# Kiểm tra files đã thay đổi
git status

# Add files đã thay đổi
git add .

# Commit với message mô tả
git commit -m "Fix bug ABC" 

# Push lên GitHub
git push

# Railway sẽ TỰ ĐỘNG deploy lại sau vài giây!
```

Không cần làm gì thêm trên Railway, nó sẽ tự động detect và deploy!

---

## TROUBLESHOOTING - KHẮC PHỤC LỖI

### ❌ Lỗi: "Application failed to respond"

**Nguyên nhân:** App không start được

**Cách fix:**
1. Vào Railway > Flask service > Tab "Deployments"
2. Click vào deployment > Xem logs
3. Tìm error message màu đỏ
4. Thường là thiếu environment variable hoặc database connection lỗi

### ❌ Lỗi: "502 Bad Gateway"

**Nguyên nhân:** Gunicorn không chạy đúng

**Cách fix:**
1. Kiểm tra file `Procfile` có đúng:
   ```
   web: gunicorn app:app
   ```
2. Kiểm tra file `requirements.txt` có `gunicorn==21.2.0`

### ❌ Lỗi: "Could not connect to database"

**Nguyên nhân:** DATABASE_URL chưa set hoặc sai

**Cách fix:**
1. Railway > Flask service > Variables
2. Kiểm tra `DATABASE_URL` có reference đến `${{ MySQL.DATABASE_URL }}`
3. Nếu không có, thêm mới và chọn reference

### ❌ Lỗi khi git push: "Authentication failed"

**Cách fix:**
1. Tạo Personal Access Token trên GitHub
2. GitHub > Settings > Developer settings > Personal access tokens
3. Generate new token (classic)
4. Chọn scope: `repo`
5. Copy token
6. Khi git push hỏi password, paste token vào

### ❌ Website load rất chậm

**Nguyên nhân:** Railway free tier sleep sau 20 phút không dùng

**Cách khắc phục:**
- Đợi 10-30 giây lần đầu truy cập (cold start)
- Hoặc upgrade Railway plan ($5/month)

---

## TỔNG KẾT

✅ **Đã làm:**
1. ✓ Code lên GitHub
2. ✓ MySQL database trên Railway
3. ✓ Flask app deploy trên Railway
4. ✓ Connect database với app
5. ✓ Public domain để truy cập

✅ **Chi phí:**
- Railway: $5 credit miễn phí/tháng
- Nếu hết: ~$5-10/tháng cho cả app + database

✅ **Auto-deploy:**
- Mỗi lần `git push` → Railway tự động deploy mới!

🎉 **DONE! Website của bạn đã online!**
