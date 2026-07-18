import pandas as pd
import joblib

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# đọc dataset đã sinh
df = pd.read_csv("dataset/dead_product.csv")


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

y = df["dead_product"]


# chia dữ liệu
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# train
model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)


model.fit(X_train, y_train)


# test độ chính xác
y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("Accuracy:", accuracy)


# lưu model
joblib.dump(
    model,
    "model/dead_product.pkl"
)

print("Đã lưu model")