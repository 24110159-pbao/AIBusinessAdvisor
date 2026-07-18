import pandas as pd
import joblib
import shap

# ==========================
# Load model
# ==========================
model = joblib.load("model/dead_product.pkl")
explainer = shap.TreeExplainer(model)

# ==========================
# Feature
# ==========================
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

# ==========================
# Mapping tên tiếng Việt
# ==========================
feature_name = {
    "price": "Giá sản phẩm",
    "current_stock": "Tồn kho hiện tại",
    "sales_7_days": "Số lượng bán 7 ngày gần đây",
    "sales_30_days": "Số lượng bán 30 ngày gần đây",
    "revenue_30_days": "Doanh thu 30 ngày gần đây",
    "order_count_30_days": "Số đơn hàng 30 ngày gần đây",
    "average_quantity_per_order": "Số lượng trung bình mỗi đơn",
    "days_since_last_sale": "Số ngày kể từ lần bán cuối"
}


def reason_text(feature, actual_value):

    if feature == "days_since_last_sale":
        return f"Đã {int(actual_value)} ngày chưa phát sinh bán."

    elif feature == "sales_7_days":
        return f"Chỉ bán {int(actual_value)} sản phẩm trong 7 ngày."

    elif feature == "sales_30_days":
        return f"Chỉ bán {int(actual_value)} sản phẩm trong 30 ngày."

    elif feature == "revenue_30_days":
        return f"Doanh thu 30 ngày chỉ còn {actual_value:,.0f} VNĐ."

    elif feature == "current_stock":
        return f"Tồn kho còn {int(actual_value)} sản phẩm."

    elif feature == "price":
        return f"Giá bán {actual_value:,.0f} VNĐ."

    elif feature == "order_count_30_days":
        return f"Chỉ có {int(actual_value)} đơn hàng trong 30 ngày."

    elif feature == "average_quantity_per_order":
        return f"Trung bình mỗi đơn mua {actual_value:.1f} sản phẩm."

    return feature_name.get(feature, feature)


def explain_product(data):
    """
    data: DataFrame chỉ gồm 1 dòng
    """

    X = data[features]

    # ==========================
    # SHAP
    # ==========================
    shap_values = explainer(X)

    # Hỗ trợ nhiều version SHAP
    if len(shap_values.values.shape) == 3:
        # shape = (1, n_features, n_classes)
        values = shap_values.values[0, :, 1]
    else:
        # shape = (1, n_features)
        values = shap_values.values[0]

    result = []

    for feature, shap_value in zip(features, values):

        actual_value = X.iloc[0][feature]

        result.append({
            "feature": reason_text(feature, actual_value),
            "impact": abs(float(shap_value)),
            "shap_value": float(shap_value)
        })

    result = sorted(
        result,
        key=lambda x: x["impact"],
        reverse=True
    )

    return result[:3]


