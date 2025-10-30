
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import db, app, User, Score, Order, PremiumPlan

load_dotenv()

def migrate():
    """Chạy migration để tạo tất cả các bảng."""
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (chú ý: xóa dữ liệu cũ)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Created table: users")
        print("Created table: scores")
        print("Created table: premium_plans")
        print("Created table: orders")
        
        # Seed premium plans
        plans = [
            PremiumPlan(
                name="Premium 1 tháng",
                duration_days=30,
                price=99000.00,
                description="Trải nghiệm đầy đủ tính năng Premium trong 30 ngày. Bao gồm: Trợ giúp trò chơi, Xáo trộn bàn cờ, Hoàn tác nước đi không giới hạn.",
                is_active=True
            ),
            PremiumPlan(
                name="Premium 3 tháng",
                duration_days=90,
                price=249000.00,
                description="Tiết kiệm 16% so với gói 1 tháng! Hưởng trọn vẹn tính năng Premium trong 90 ngày. Gói phổ biến nhất cho game thủ thường xuyên.",
                is_active=True
            ),
            PremiumPlan(
                name="Premium 1 năm",
                duration_days=365,
                price=599000.00,
                description="Tiết kiệm 50% - Gói tốt nhất! Sử dụng không giới hạn trong 365 ngày. Tất cả tính năng Premium cao cấp nhất, không giới hạn thời gian chơi.",
                is_active=True
            )
        ]
        
        for plan in plans:
            db.session.add(plan)
        
        db.session.commit()
        print("Seeded premium plans")
        
        print("\nMigration completed successfully!")
        print("\nTo run migration on MySQL, ensure:")
        print("1. SQLALCHEMY_DATABASE_URI configured in .env")
        print("2. Database created")
        print("3. User has CREATE TABLE permission")

if __name__ == "__main__":
    migrate()

