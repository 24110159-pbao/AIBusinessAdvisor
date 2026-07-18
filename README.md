# Shopping AI Recommendation System

## Giới thiệu

Shopping AI Recommendation System là hệ thống phân tích dữ liệu bán hàng nhằm hỗ trợ quản lý cửa hàng bằng AI với hai chức năng chính:

* **Dead Product Prediction:** Dự đoán sản phẩm có nguy cơ bán chậm hoặc ngừng tiêu thụ.
* **Product Combo Recommendation:** Gợi ý các sản phẩm thường được mua cùng nhau.

Ngoài ra, hệ thống sử dụng **SHAP** để giải thích lý do mô hình dự đoán, giúp tăng tính minh bạch.

---

## Công nghệ

* Python
* MySQL
* Pandas
* SQLAlchemy
* Scikit-learn
* SHAP
* mlxtend (FP-Growth)

---

## Cài đặt

Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

Cấu hình kết nối MySQL trong `db.py`:

```python
engine = create_engine(
    "mysql+pymysql://username:password@localhost:3306/SHOPPINGAI"
)
```

Huấn luyện mô hình:

```bash
python train_dead_product.py
```

Chạy hệ thống:

```bash
python gui.py
```

---

## Ý tưởng

### 1. Dead Product Prediction

Hệ thống tổng hợp dữ liệu bán hàng (doanh thu, số lượng bán, tồn kho, số ngày từ lần bán cuối...) và sử dụng **Decision Tree** để dự đoán sản phẩm có nguy cơ trở thành *Dead Product*. Kết quả được giải thích bằng **SHAP** để xác định các yếu tố ảnh hưởng lớn nhất.

**Chọn Decision Tree vì:**

* Dễ giải thích kết quả.
* Không cần chuẩn hóa dữ liệu.
* Huấn luyện và dự đoán nhanh.
* Tương thích tốt với SHAP.

### 2. Product Combo Recommendation

Từ lịch sử đơn hàng, hệ thống sử dụng **FP-Growth** để tìm các sản phẩm thường xuất hiện cùng nhau và sinh các luật kết hợp (Association Rules) nhằm đề xuất combo.

**Chọn FP-Growth vì:**

* Tốc độ nhanh hơn Apriori.
* Không sinh nhiều candidate itemsets.
* Phù hợp với dữ liệu giao dịch có nhiều sản phẩm.

---

## Quy trình hoạt động

```
Database
   │
   ├── Dead Product Prediction (Decision Tree + SHAP)
   │
   └── Product Combo Recommendation (FP-Growth)
            │
            ▼
     Recommendation
            │
            ▼
      Lưu vào Database
```
