import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy import text

from db import engine
from predict_dead_product import predict_dead_product
from predict_combo import predict_combo
from explain_dead_product import explain_product


root = tk.Tk()
root.title("Shopping AI Dashboard")
root.geometry("1200x750+150+20")
root.configure(bg="#F4F6F9")

style = ttk.Style()

style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="black",
    fieldbackground="white",
    rowheight=20,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#2563EB",
    foreground="white",
    font=("Segoe UI", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#60A5FA")]
)

header = tk.Frame(
    root,
    bg="#2563EB",
    height=70
)

header.pack(fill="x")

title = tk.Label(
    header,
    text="🛒 Shopping AI Recommendation",
    bg="#2563EB",
    fg="white",
    font=("Segoe UI", 22, "bold")
)

title.pack(pady=15)
# ==================================================
# Predict
# ==================================================
def predict():

    try:

        predict_dead_product()
        predict_combo()

        load_data()

        messagebox.showinfo(
            "Thông báo",
            "AI đã phân tích xong!"
        )

    except Exception as e:

        messagebox.showerror(
            "Lỗi",
            str(e)
        )


# ==================================================
# Load Recommendation
# ==================================================
def load_data():

    for item in tree.get_children():
        tree.delete(item)

    txtExplain.config(state="normal")
    txtExplain.delete("1.0", tk.END)
    txtExplain.config(state="disabled")

    sql = """

    SELECT

        r.id,

        p.id product_id,

        p.name product_name,

        r.type,

        r.message,

        r.status,

        r.confidence

    FROM recommendations r

    LEFT JOIN products p
        ON r.product_id=p.id

    ORDER BY r.created_at DESC

    """

    df = pd.read_sql(sql, engine)

    for index, (_, row) in enumerate(df.iterrows()):

        if row["status"] == "DONE":
            tag = "done"
        elif row["status"] == "PENDING":
            tag = "pending"
        else:
            tag = "even" if index % 2 == 0 else "odd"

        tree.insert(
            "",
            "end",
            values=(
                row["id"],
                row["product_id"],
                row["product_name"],
                row["type"],
                row["message"],
                row["status"],
                f"{row['confidence']:.2f}%"
            ),
            tags=(tag,)
        )


# ==================================================
# Confirm
# ==================================================
def confirm():

    item = tree.focus()

    if not item:
        return

    values = tree.item(item)["values"]

    recommend_id = values[0]

    sql = """
    UPDATE recommendations
    SET status='DONE'
    WHERE id=:id
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            {"id": recommend_id}
        )

    load_data()

    messagebox.showinfo(
        "Thông báo",
        "Đã xác nhận!"
    )


# ==================================================
# SHAP Explain
# ==================================================
def show_explain(event=None):

    txtExplain.config(state="normal")
    txtExplain.delete("1.0", tk.END)

    item = tree.focus()

    if not item:
        return

    values = tree.item(item)["values"]

    product_id = values[1]
    rec_type = values[3]

    if rec_type != "DEAD_PRODUCT":

        txtExplain.insert(
            tk.END,
            "Recommendation này không sử dụng SHAP.\n"
        )
        return

    sql = """

    SELECT

        p.price,

        p.quantity AS current_stock,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW()-INTERVAL 7 DAY
                    THEN oi.quantity
                    ELSE 0
                END
            ),0
        ) AS sales_7_days,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW()-INTERVAL 30 DAY
                    THEN oi.quantity
                    ELSE 0
                END
            ),0
        ) AS sales_30_days,

        COALESCE(
            SUM(
                CASE
                    WHEN o.created_at >= NOW()-INTERVAL 30 DAY
                    THEN oi.subtotal
                    ELSE 0
                END
            ),0
        ) AS revenue_30_days,

        COUNT(
            DISTINCT
            CASE
                WHEN o.created_at >= NOW()-INTERVAL 30 DAY
                THEN o.id
            END
        ) AS order_count_30_days,

        COALESCE(
            SUM(oi.quantity) /
            NULLIF(COUNT(DISTINCT o.id),0),
            0
        ) AS average_quantity_per_order,

        DATEDIFF(
            NOW(),
            MAX(o.created_at)
        ) AS days_since_last_sale

    FROM products p

    LEFT JOIN order_items oi
        ON p.id=oi.product_id

    LEFT JOIN orders o
        ON oi.order_id=o.id
        AND o.status='COMPLETED'

    WHERE p.id=:id

    GROUP BY p.id

    """

    df = pd.read_sql(
        text(sql),
        engine,
        params={"id": product_id}
    )

    if df.empty:
        return

    df["days_since_last_sale"] = df[
        "days_since_last_sale"
    ].fillna(120)

    reasons = explain_product(df)

    txtExplain.insert(
        tk.END,
        "===== GIẢI THÍCH AI (SHAP) =====\n\n"
    )

    for i, r in enumerate(reasons, start=1):

        txtExplain.insert(
            tk.END,
            f"{i}. {r['feature']}\n"
        )

        txtExplain.insert(
            tk.END,
            f"   impact : {r['shap_value']:.4f}\n"
        )
    txtExplain.config(state="disabled")


# ==================================================
# TreeView
# ==================================================

columns = (
    "ID",
    "ProductID",
    "Tên sản phẩm",
    "Loại",
    "Ghi chú",
    "Trạng thái",
    "Độ tin cậy"
)

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=15
)
tree.tag_configure("odd", background="#FFFFFF")
tree.tag_configure("even", background="#F8FAFC")
tree.tag_configure("done", background="#DCFCE7")
tree.tag_configure("pending", background="#FEF3C7")
for col in columns:
    tree.heading(col, text=col)

tree.column("ID", width=40)
tree.column("ProductID", width=70)
tree.column("Tên sản phẩm", width=180)
tree.column("Loại", width=120)
tree.column("Ghi chú", width=430)
tree.column("Trạng thái", width=80)
tree.column("Độ tin cậy", width=100)

tree.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

tree.bind(
    "<<TreeviewSelect>>",
    show_explain
)


# ==================================================
# SHAP BOX
# ==================================================
label = tk.Label(
    root,
    text="🤖 Giải thích AI (SHAP)",
    bg="#F4F6F9",
    fg="#1E3A8A",
    font=("Segoe UI", 12, "bold")
)

label.pack(anchor="w", padx=10)

txtExplain = tk.Text(
    root,
    height=12,
    bg="white",
    fg="#374151",
    font=("Consolas",11),
    wrap="word",
    relief="solid",
    bd=1,
    padx=10,
    pady=10,
    state="disabled"
)

txtExplain.pack(
    fill="both",
    padx=10,
    pady=5
)


# ==================================================
# Buttons
# ==================================================

frame = tk.Frame(root)

frame.pack(
    pady=10
)

btnPredict = tk.Button(
    frame,
    text="Predict AI",
    bg="green",
    fg="white",
    width=20,
    command=predict
)

btnPredict.grid(
    row=0,
    column=0,
    padx=10
)

btnConfirm = tk.Button(
    frame,
    text="Xác nhận",
    bg="orange",
    fg="white",
    width=20,
    command=confirm
)

btnConfirm.grid(
    row=0,
    column=1,
    padx=10
)


# ==================================================
# Start
# ==================================================

load_data()

root.mainloop()