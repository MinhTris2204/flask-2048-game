# Hướng dẫn Deploy Flask 2048 Game lên Railway

## Bước 1: Chuẩn bị Railway Account

1. Truy cập https://railway.app/
2. Đăng ký/Đăng nhập bằng GitHub account
3. Tạo project mới

## Bước 2: Push Code lên GitHub

```bash
# Khởi tạo git repository (nếu chưa có)
git init

# Add tất cả files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Tạo repository trên GitHub và push
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

## Bước 3: Deploy trên Railway

### 3.1. Tạo MySQL Database

1. Trong Railway dashboard, click **"New"** > **"Database"** > **"Add MySQL"**
2. Railway sẽ tự động tạo MySQL instance và cung cấp connection string

### 3.2. Deploy Flask App

1. Click **"New"** > **"GitHub Repo"**
2. Chọn repository của bạn
3. Railway sẽ tự động detect và deploy

### 3.3. Cấu hình Environment Variables

Trong Railway dashboard, vào tab **"Variables"** của Flask service, thêm các biến sau:

```
FLASK_SECRET_KEY=your-super-secret-random-key-here
DATABASE_URL=${{MySQL.DATABASE_URL}}
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FLASK_ENV=production
```

**Quan trọng:**
- `DATABASE_URL` sẽ tự động reference đến MySQL service bạn vừa tạo
- Click vào `${{MySQL.DATABASE_URL}}` để Railway tự động điền
- Thay `your-super-secret-random-key-here` bằng một string ngẫu nhiên phức tạp
- Cập nhật Google OAuth credentials với domain mới của Railway

## Bước 4: Cập nhật Google OAuth Redirect URI

1. Truy cập https://console.cloud.google.com/apis/credentials
2. Chọn OAuth 2.0 Client của bạn
3. Thêm **Authorized redirect URIs**:
   ```
   https://your-app-name.up.railway.app/login/google/authorized
   ```
4. Thay `your-app-name` bằng domain Railway cung cấp

## Bước 5: Initialize Database

Sau khi deploy thành công, database tables sẽ tự động được tạo khi app khởi động (do `db.create_all()` trong `app.py`).

Nếu cần chạy migration thủ công:

1. Trong Railway dashboard, vào tab **"Settings"**
2. Scroll xuống **"Deploy"** section
3. Có thể sử dụng Railway CLI để chạy commands:

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Chạy migration
railway run flask init-db
```

## Bước 6: Kiểm tra Deployment

1. Trong Railway dashboard, click vào **"Settings"** > **"Public Networking"**
2. Railway sẽ cung cấp một URL (ví dụ: `https://your-app.up.railway.app`)
3. Truy cập URL để test app

## Troubleshooting

### Lỗi Database Connection
- Kiểm tra biến `DATABASE_URL` đã được set đúng
- Đảm bảo MySQL service đang running

### Lỗi 502 Bad Gateway
- Kiểm tra logs trong Railway dashboard
- Đảm bảo `Procfile` có đúng command: `web: gunicorn app:app`

### App không start
- Xem logs trong Railway dashboard tab **"Deployments"**
- Kiểm tra `requirements.txt` có đầy đủ dependencies

## Chi phí

- Railway cung cấp $5 credit miễn phí mỗi tháng
- Nếu vượt quá, bạn cần thêm payment method
- Ước tính chi phí:
  - Flask app: ~$5-10/tháng
  - MySQL: ~$5-10/tháng (tùy usage)

## Auto-Deploy

Railway sẽ tự động deploy lại mỗi khi bạn push code mới lên GitHub!

```bash
# Mỗi lần thay đổi code
git add .
git commit -m "Update feature"
git push

# Railway sẽ tự động deploy!
```
