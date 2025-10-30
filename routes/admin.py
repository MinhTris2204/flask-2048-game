"""
Admin routes for seeding database and management tasks.
"""

from flask import jsonify
from config import app, db
from models import PremiumPlan


@app.route("/admin/seed-premium-plans", methods=["GET"])
def seed_premium_plans():
    """Seed premium plans into database. Run once after deployment."""
    try:
        # Check if plans already exist
        existing_plans = PremiumPlan.query.count()
        if existing_plans > 0:
            return jsonify({
                "status": "info",
                "message": f"Premium plans already exist ({existing_plans} plans found). Skipping seed.",
                "plans_count": existing_plans
            }), 200
        
        # Create premium plans
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
        
        return jsonify({
            "status": "success",
            "message": "Premium plans seeded successfully!",
            "plans_count": len(plans),
            "plans": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": float(p.price),
                    "duration_days": p.duration_days
                } for p in plans
            ]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error seeding premium plans: {str(e)}"
        }), 500


@app.route("/admin/update-prices", methods=["GET"])
def update_premium_prices():
    """Update giá các gói premium xuống dưới 20,000 VND"""
    try:
        plans_config = [
            {
                'duration_days': 30,
                'new_price': 9000,
                'name': 'Premium 1 tháng',
                'description': 'Trải nghiệm Premium 1 tháng với giá ưu đãi'
            },
            {
                'duration_days': 90,
                'new_price': 15000,
                'name': 'Premium 3 tháng',
                'description': 'Tiết kiệm hơn với gói 3 tháng'
            },
            {
                'duration_days': 365,
                'new_price': 19000,
                'name': 'Premium 1 năm',
                'description': 'Ưu đãi cực khủng - Chỉ 19k/năm ⭐'
            }
        ]
        
        updated_plans = []
        for config in plans_config:
            plan = PremiumPlan.query.filter_by(
                duration_days=config['duration_days']
            ).first()
            
            if plan:
                old_price = float(plan.price)
                plan.price = config['new_price']
                plan.name = config['name']
                plan.description = config['description']
                
                updated_plans.append({
                    'id': plan.id,
                    'name': plan.name,
                    'old_price': old_price,
                    'new_price': config['new_price'],
                    'duration_days': plan.duration_days
                })
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Prices updated successfully!",
            "updated_count": len(updated_plans),
            "plans": updated_plans
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error updating prices: {str(e)}"
        }), 500
