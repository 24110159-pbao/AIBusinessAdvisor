DROP DATABASE IF EXISTS SHOPPINGAI;

CREATE DATABASE SHOPPINGAI;

USE SHOPPINGAI;

-- =====================================================
-- 1. USERS
-- =====================================================

CREATE TABLE users (
    id VARCHAR(36) NOT NULL PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE,

    role ENUM('ADMIN','CUSTOMER')
        DEFAULT 'CUSTOMER',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- =====================================================
-- 2. CATEGORY
-- =====================================================

CREATE TABLE categories (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE

);



-- =====================================================
-- 3. PRODUCTS
-- =====================================================

CREATE TABLE products (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,


    category_id BIGINT NOT NULL,


    name VARCHAR(150) NOT NULL,


    price DECIMAL(10,2) NOT NULL,


    quantity INT NOT NULL DEFAULT 0,


    image VARCHAR(255),


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,


    CONSTRAINT fk_product_category

        FOREIGN KEY(category_id)

        REFERENCES categories(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT

);



-- =====================================================
-- 4. ORDERS
-- =====================================================

CREATE TABLE orders (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,


    user_id VARCHAR(36) NOT NULL,


    total_price DECIMAL(10,2) NOT NULL,


    status ENUM(
        'PENDING',
        'SHIPPING',
        'COMPLETED',
        'CANCELLED'
    )
    DEFAULT 'PENDING',


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_order_user

        FOREIGN KEY(user_id)

        REFERENCES users(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT

);



-- =====================================================
-- 5. ORDER ITEMS
-- Bảng quan trọng nhất cho AI
-- =====================================================

CREATE TABLE order_items (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,


    order_id BIGINT NOT NULL,


    product_id BIGINT NOT NULL,


    quantity INT NOT NULL,


    unit_price DECIMAL(10,2) NOT NULL,


    subtotal DECIMAL(10,2)
        GENERATED ALWAYS AS
        (quantity * unit_price)
        STORED,


    CONSTRAINT fk_order_item_order

        FOREIGN KEY(order_id)

        REFERENCES orders(id)

        ON UPDATE CASCADE

        ON DELETE CASCADE,


    CONSTRAINT fk_order_item_product

        FOREIGN KEY(product_id)

        REFERENCES products(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT

);



-- =====================================================
-- 6. AI REPORTS
-- Lưu báo cáo phân tích tổng
-- =====================================================

CREATE TABLE ai_reports (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,


    title VARCHAR(150) NOT NULL,


    content TEXT NOT NULL,


    report_type VARCHAR(50),


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



-- =====================================================
-- 7. AI RECOMMENDATIONS
-- Lưu kết quả AI
-- =====================================================

CREATE TABLE recommendations (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,


    product_id BIGINT NULL,


    type VARCHAR(50) NOT NULL,


    message TEXT NOT NULL,


    ai_model VARCHAR(100),


    confidence DECIMAL(5,2),


    status ENUM(
        'NEW',
        'DONE'
    )
    DEFAULT 'NEW',


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_recommendation_product

        FOREIGN KEY(product_id)

        REFERENCES products(id)

        ON UPDATE CASCADE

        ON DELETE SET NULL

);

-- =====================================================
-- INDEX HỖ TRỢ AI PHÂN TÍCH NHANH
-- =====================================================


CREATE INDEX idx_order_created
ON orders(created_at);

CREATE INDEX idx_order_item_product
ON order_items(product_id);

CREATE INDEX idx_order_item_order
ON order_items(order_id);

CREATE INDEX idx_product_category
ON products(category_id);

INSERT INTO categories (name)
VALUES
('Laptop'),
('Smartphone'),
('Tablet'),
('Phu kien'),
('Tai nghe');

INSERT INTO users
(
    id,
    username,
    password,
    full_name,
    email,
    role
)
VALUES
(
'11111111-1111-1111-1111-111111111111',
'user01',
'123456',
'Nguyen Van A',
'a@gmail.com',
'CUSTOMER'
),

(
'22222222-2222-2222-2222-222222222222',
'user02',
'123456',
'Nguyen Van B',
'b@gmail.com',
'CUSTOMER'
),

(
'33333333-3333-3333-3333-333333333333',
'user03',
'123456',
'Nguyen Van C',
'c@gmail.com',
'CUSTOMER'
),

(
'44444444-4444-4444-4444-444444444444',
'user04',
'123456',
'Nguyen Van D',
'd@gmail.com',
'CUSTOMER'
),

(
'55555555-5555-5555-5555-555555555555',
'user05',
'123456',
'Nguyen Van E',
'e@gmail.com',
'CUSTOMER'
);

INSERT INTO products
(
category_id,
name,
price,
quantity
)
VALUES
(1,'Laptop Dell XPS',35000000,20),

(2,'iPhone 15',25000000,50),

(3,'Tablet Samsung',12000000,100),

(4,'Chuột Gaming',500000,200),

(5,'Tai nghe Bluetooth cũ',300000,150);

INSERT INTO orders
(
user_id,
total_price,
status,
created_at
)
VALUES

(
'11111111-1111-1111-1111-111111111111',
35000000,
'COMPLETED',
DATE_SUB(NOW(), INTERVAL 5 DAY)
),

(
'22222222-2222-2222-2222-222222222222',
25000000,
'COMPLETED',
DATE_SUB(NOW(), INTERVAL 10 DAY)
),

(
'33333333-3333-3333-3333-333333333333',
12000000,
'COMPLETED',
DATE_SUB(NOW(), INTERVAL 20 DAY)
),

(
'44444444-4444-4444-4444-444444444444',
500000,
'PENDING',
DATE_SUB(NOW(), INTERVAL 3 DAY)
),

(
'55555555-5555-5555-5555-555555555555',
300000,
'CANCELLED',
DATE_SUB(NOW(), INTERVAL 2 DAY)
);

INSERT INTO order_items
(
order_id,
product_id,
quantity,
unit_price
)
VALUES

(1,1,1,35000000),

(2,2,1,25000000),

(3,3,2,12000000),

(4,4,1,500000),

(5,5,5,300000);