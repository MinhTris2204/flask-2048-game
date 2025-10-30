"""
Script để update giá Premium Plans xuống dưới 20,000 VND
Chạy một lần để cập nhật giá
"""
from config import app, db
from models import PremiumPlan

def update_premium_prices():
    """Update giá các gói premium"""
    with app.app_context():
        # Tìm và update từng plan
        plans_config = [
            {
                'name': 'Premium 1 tháng',
                'duration_days': 30,
                'new_price': 9000,
                'description': 'Trải nghiệm Premium 1 tháng với giá ưu đãi'
            },
            {
                'name': 'Premium 3 tháng',
                'duration_days': 90,
                'new_price': 15000,
                'description': 'Tiết kiệm hơn với gói 3 tháng'
            },
            {
                'name': 'Premium 1 năm',
                'duration_days': 365,
                'new_price': 19000,
                'description': 'Ưu đãi cực khủng - Chỉ 19k/năm'
            }
        ]
        
        for config in plans_config:
            plan = PremiumPlan.query.filter_by(
                duration_days=config['duration_days']
            ).first()
            
            if plan:
                old_price = plan.price
                plan.price = config['new_price']
                plan.name = config['name']
                plan.description = config['description']
                print(f"✅ Updated {plan.name}: {old_price:,} VND → {config['new_price']:,} VND")
            else:
                print(f"⚠️  Plan with {config['duration_days']} days not found")
        
        db.session.commit()
        print("\n🎉 All prices updated successfully!")
        print("\nNew pricing:")
        
        all_plans = PremiumPlan.query.filter_by(is_active=True).order_by(PremiumPlan.price).all()
        for plan in all_plans:
            print(f"  - {plan.name}: {plan.price:,} VND ({plan.duration_days} ngày)")

if __name__ == "__main__":
    update_premium_prices()
