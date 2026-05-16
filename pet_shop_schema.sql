-- =====================================
-- PET SHOP MANAGEMENT SYSTEM
-- Database Schema Design
-- =====================================

-- 1. CATEGORIES TABLE (ประเภทสัตว์เลี้ยง)
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. SUPPLIERS TABLE (ผู้จัดหาสัตว์เลี้ยง)
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. PETS TABLE ⭐ (สัตว์เลี้ยง - MAIN TABLE FOR CRUD)
CREATE TABLE pets (
    pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    age_months INTEGER NOT NULL CHECK(age_months >= 0),
    price DECIMAL(10, 2) NOT NULL CHECK(price > 0),
    status VARCHAR(20) DEFAULT 'Available',
    color VARCHAR(50),
    description TEXT,
    photo_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 4. CUSTOMERS TABLE (ลูกค้า)
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    member_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. SALES TABLE (บันทึกการขาย)
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
    total_price DECIMAL(10, 2) NOT NULL CHECK(total_price > 0),
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- =====================================
-- INDEX OPTIMIZATION
-- =====================================
CREATE INDEX idx_pets_category ON pets(category_id);
CREATE INDEX idx_pets_supplier ON pets(supplier_id);
CREATE INDEX idx_pets_status ON pets(status);
CREATE INDEX idx_sales_pet ON sales(pet_id);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_date ON sales(sale_date);

-- =====================================
-- RELATIONSHIPS DIAGRAM
-- =====================================
-- categories (1) ──→ (N) pets
-- suppliers (1) ──→ (N) pets
-- pets (1) ──→ (N) sales
-- customers (1) ──→ (N) sales
-- 
-- NO M2N (Many-to-Many) Relationships ✓
-- =====================================
