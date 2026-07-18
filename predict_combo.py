import pandas as pd

from db import engine

from sqlalchemy import text

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules


def predict_combo():

    # =============================
    # 1. Lấy dữ liệu đơn hàng
    # =============================

    sql = """
    SELECT
        o.id AS order_id,
        p.id AS product_id,
        p.name AS product_name
    FROM orders o
    JOIN order_items oi
        ON o.id = oi.order_id
    JOIN products p
        ON p.id = oi.product_id
    WHERE o.status='COMPLETED'
    ORDER BY o.id
    """

    df = pd.read_sql(sql, engine)

    if df.empty:
        print("Không có dữ liệu.")
        return

    # =============================
    # 2. Gom sản phẩm theo đơn hàng
    # =============================

    transactions = (
        df.groupby("order_id")["product_name"]
        .apply(list)
        .tolist()
    )

    # Phải có đơn có từ 2 sản phẩm trở lên

    valid_transactions = [
        t for t in transactions if len(t) >= 2
    ]

    if len(valid_transactions) == 0:
        print("Không có đơn hàng để tạo combo.")
        return

    # =============================
    # 3. One Hot Encoding
    # =============================

    te = TransactionEncoder()

    te_array = te.fit(valid_transactions).transform(valid_transactions)

    basket = pd.DataFrame(
        te_array,
        columns=te.columns_
    )

    # =============================
    # 4. FP Growth
    # =============================

    frequent_itemsets = fpgrowth(
        basket,
        min_support=0.2,
        use_colnames=True
    )

    if frequent_itemsets.empty:
        print("Không tìm thấy frequent itemsets.")
        return

    # =============================
    # 5. Association Rules
    # =============================

    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=0.6
    )

    if rules.empty:
        print("Không tìm thấy association rules.")
        return

    print(rules)

    # =============================
    # 6. ko ghi recommendation cũ cùng ngày
    # =============================

    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM recommendations
            WHERE type = 'PRODUCT_COMBO'
            AND DATE(created_at) = CURDATE()
        """))

    # =============================
    # 7. Lưu recommendation
    # =============================

    insert_sql = """
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
        'PRODUCT_COMBO',
        :message,
        'FP-Growth',
        :confidence
    )
    """

    with engine.begin() as conn:
        
        for _, row in rules.iterrows():

            antecedent = list(row["antecedents"])
            consequent = list(row["consequents"])

            # Chỉ lưu rule 1 -> 1
            if len(antecedent) != 1 or len(consequent) != 1:
                continue

            product_name = antecedent[0]
            combo_name = consequent[0]

            product = df[df["product_name"] == product_name]

            if product.empty:
                continue

            product_id = int(product.iloc[0]["product_id"])

            message = (
                f"Khách mua '{product_name}' "
                f"thường mua kèm '{combo_name}'."
            )

            conn.execute(
                text(insert_sql),
                {
                    "product_id": product_id,
                    "message": message,
                    "confidence": round(
                        row["confidence"] * 100,
                        2
                    )
                }
            )

    print("Đã lưu recommendation combo.")


