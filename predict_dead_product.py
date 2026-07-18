import pandas as pd
import joblib
from sqlalchemy import text

from db import engine
from explain_dead_product import explain_product

def build_message(product):

    reasons = explain_product(product)

    msg = "⚠ AI đánh giá sản phẩm có nguy cơ trở thành Dead Product.\n\n"

    msg += "Nguyên nhân:\n"

    for r in reasons:
        msg += f"• {r['feature']}\n"

    return msg

def predict_dead_product():

    # =========================
    # 1. Load model
    # =========================
    model = joblib.load("model/dead_product.pkl")

    # =========================
    # 2. Lấy dữ liệu từ database
    # =========================
    sql = """
    SELECT

        p.id AS product_id,
        p.name AS product_name,
        p.price,
        p.quantity AS current_stock,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW() - INTERVAL 7 DAY
                    THEN oi.quantity
                    ELSE 0
                END
            ),0
        ) AS sales_7_days,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW() - INTERVAL 30 DAY
                    THEN oi.quantity
                    ELSE 0
                END
            ),0
        ) AS sales_30_days,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW() - INTERVAL 30 DAY
                    THEN oi.subtotal
                    ELSE 0
                END
            ),0
        ) AS revenue_30_days,

        COUNT(
            DISTINCT
            CASE
                WHEN o.created_at >= NOW() - INTERVAL 30 DAY
                THEN o.id
            END
        ) AS order_count_30_days,

        COALESCE(
            SUM(oi.quantity) /
            NULLIF(COUNT(DISTINCT o.id), 0),
            0
        ) AS average_quantity_per_order,

        DATEDIFF(
            NOW(),
            MAX(o.created_at)
        ) AS days_since_last_sale

    FROM products p

    LEFT JOIN order_items oi
        ON p.id = oi.product_id

    LEFT JOIN orders o
        ON oi.order_id = o.id
        AND o.status = 'COMPLETED'

    GROUP BY p.id
    """

    df = pd.read_sql(sql, engine)

    # Nếu chưa từng bán
    df["days_since_last_sale"] = df["days_since_last_sale"].fillna(120)

    # =========================
    # 3. Feature
    # =========================
    features = [
        "price",
        "current_stock",
        "sales_7_days",
        "sales_30_days",
        "revenue_30_days",
        "order_count_30_days",
        "average_quantity_per_order",
        "days_since_last_sale"
    ]

    X = df[features]

    # =========================
    # 4. Predict
    # =========================
    result = model.predict(X)
    prob = model.predict_proba(X)

    df["dead_product"] = result
    df["confidence"] = prob[:, 1] * 100

    # =========================
    # 5. Lọc sản phẩm nguy cơ
    # =========================
    dead_products = df[df["dead_product"] == 1]
    

    print(dead_products)

    sql_insert = """
    INSERT INTO recommendations
    (
        product_id,
        type,
        message,
        ai_model,
        confidence
    )
    VALUES
    (
        :product_id,
        'DEAD_PRODUCT',
        :message,
        'Decision Tree',
        :confidence
    )
    """

    # =========================
    # 6. Xóa recommendation cùng ngày và lưu mới
    # =========================
    with engine.begin() as conn:

        conn.execute(text("""
            DELETE FROM recommendations
            WHERE type = 'DEAD_PRODUCT'
            AND DATE(created_at) = CURDATE()
        """))

        for idx, row in dead_products.iterrows():

            product = df.loc[[idx]]

            message = build_message(product)

            conn.execute(
                text(sql_insert),
                {
                    "product_id": int(row["product_id"]),
                    "message": message,
                    "confidence": round(float(row["confidence"]), 2)
                }
            )

    print("Đã lưu recommendation Dead Product.")