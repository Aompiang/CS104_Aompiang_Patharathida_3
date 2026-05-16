import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.executescript('''
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
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
''')

categories = [
    ('Dogs', 'สุนัขหลากสายพันธุ์'),
    ('Cats', 'แมวหลากสายพันธุ์'),
    ('Birds', 'นกสวยงาม'),
    ('Fish', 'ปลาตู้ปลา'),
    ('Rabbits', 'กระต่ายน่ารัก'),
    ('Reptiles', 'สัตว์เลื้อยคลาน'),
    ('Small Pets', 'สัตว์เลี้ยงขนาดเล็ก'),
    ('Horses', 'ม้าและสัตว์ฟาร์ม'),
    ('Exotic', 'สัตว์แปลกใหม่'),
    ('Rodents', 'หนูและสัตว์ฟันแทะ'),
    ('Amphibians', 'สัตว์ครึ่งบกครึ่งน้ำ'),
    ('Farm', 'สัตว์ฟาร์มขนาดเล็ก'),
    ('Ferrets', 'เฟอร์เรท')
]
cur.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', categories)

suppliers = [
    ('PetHouse Co.', 'contact@pethouse.co', '0812345678', '123 Pet Street', 'Bangkok'),
    ('Happy Paws', 'sales@happypaws.com', '0821112223', '456 Animal Ave', 'Chiang Mai'),
    ('Bird World', 'info@birdworld.net', '0832223344', '789 Sky Road', 'Nakhon Pathom'),
    ('AquaFarm', 'service@aquafarm.com', '0843334455', '101 Water Lane', 'Phuket'),
    ('Rabbit House', 'hello@rabbithouse.com', '0854445566', '202 Soft Road', 'Khon Kaen'),
    ('Reptile Center', 'contact@reptilecenter.com', '0865556677', '303 Scale Blvd', 'Rayong'),
    ('Tiny Friends', 'support@tinyfriends.com', '0876667788', '404 Small Street', 'Ayutthaya'),
    ('Farm Fresh', 'orders@farmfresh.co', '0887778899', '505 Green Way', 'Ratchaburi'),
    ('Exotic Pets', 'exotic@pets.com', '0898889900', '606 Rare Rd', 'Chonburi'),
    ('Rodent Trader', 'rodents@trader.com', '0909990011', '707 Quiet Ave', 'Saraburi'),
    ('Amphibia Shop', 'amphibia@shop.com', '0910001122', '808 Wet St', 'Surat Thani'),
    ('Barnyard', 'barnyard@farm.com', '0921112233', '909 Field Rd', 'Lampang'),
    ('Ferret House', 'ferret@house.com', '0932223344', '1010 Furry Ln', 'Nakhon Si Thammarat')
]
cur.executemany('INSERT INTO suppliers (name, email, phone, address, city) VALUES (?, ?, ?, ?, ?)', suppliers)

pets = [
    ('Lucky', 1, 1, 12, 4500.00, 'Available', 'Brown', 'สุนัขสายพันธุ์ไทยหลังอาน', 'https://loremflickr.com/320/240/dog?lock=1'),
    ('Milo', 1, 2, 8, 6500.00, 'Sold', 'White', 'สุนัขพันธุ์ชิวาวา', 'https://loremflickr.com/320/240/dog?lock=2'),
    ('Luna', 2, 2, 6, 5200.00, 'Available', 'Black', 'แมวเปอร์เซียขนนุ่ม', 'https://loremflickr.com/320/240/cat?lock=3'),
    ('Mochi', 2, 3, 10, 4200.00, 'Reserved', 'Grey', 'แมวไทยโบราณ', 'https://loremflickr.com/320/240/cat?lock=4'),
    ('Sunny', 3, 3, 4, 1200.00, 'Available', 'Yellow', 'นกแก้วคอสีน้ำเงิน', 'https://loremflickr.com/320/240/bird?lock=5'),
    ('Fin', 4, 4, 3, 900.00, 'Available', 'Silver', 'ปลาทองสวยงาม', 'https://via.placeholder.com/320x240.png?text=Goldfish'),
    ('Bunny', 5, 5, 5, 3000.00, 'Available', 'White', 'กระต่ายฮอลแลนด์ลอป', 'https://loremflickr.com/320/240/rabbit?lock=7'),
    ('Stripe', 6, 6, 18, 7500.00, 'Available', 'Green', 'งูหลามเขียว', 'https://via.placeholder.com/320x240.png?text=Reptile'),
    ('Peanut', 7, 7, 7, 850.00, 'Available', 'Brown', 'หนูตะเภา', 'https://via.placeholder.com/320x240.png?text=Rodent'),
    ('Star', 4, 4, 2, 600.00, 'Sold', 'Orange', 'ปลาเบต้า', 'https://via.placeholder.com/320x240.png?text=Betta'),
    ('Bella', 2, 1, 9, 4800.00, 'Available', 'Calico', 'แมวสก๊อตติชโฟลด์', 'https://loremflickr.com/320/240/cat?lock=9'),
    ('Coco', 3, 3, 5, 1400.00, 'Reserved', 'Green', 'นกฟินซ์', 'https://loremflickr.com/320/240/bird?lock=10'),
    ('Nemo', 4, 4, 1, 200.00, 'Available', 'Orange', 'ปลานีโม่', 'https://via.placeholder.com/320x240.png?text=Nemo')
]
cur.executemany('INSERT INTO pets (name, category_id, supplier_id, age_months, price, status, color, description, photo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', pets)

customers = [
    ('Anna', 'anna@example.com', '0912345678', '123 Sukhumvit', 'Bangkok'),
    ('Bank', 'bank@example.com', '0923456789', '456 Nimman', 'Chiang Mai'),
    ('Chompoo', 'chompoo@example.com', '0934567890', '789 Boat Rd', 'Bangkok'),
    ('Deck', 'deck@example.com', '0945678901', '101 Beach', 'Phuket'),
    ('Fah', 'fah@example.com', '0956789012', '202 Lake', 'Khon Kaen'),
    ('Gift', 'gift@example.com', '0967890123', '303 Hill', 'Rayong'),
    ('Ice', 'ice@example.com', '0978901234', '404 Garden', 'Ayutthaya'),
    ('Joy', 'joy@example.com', '0989012345', '505 Village', 'Ratchaburi'),
    ('Kwang', 'kwang@example.com', '0990123456', '606 Market', 'Chonburi'),
    ('Luk', 'luk@example.com', '0901234567', '707 Park', 'Saraburi'),
    ('May', 'may@example.com', '0912340012', '808 School', 'Surat Thani'),
    ('Nok', 'nok@example.com', '0923451123', '909 Farm', 'Lampang'),
    ('Off', 'off@example.com', '0934562234', '1010 Road', 'Nakhon Si Thammarat')
]
cur.executemany('INSERT INTO customers (name, email, phone, address, city) VALUES (?, ?, ?, ?, ?)', customers)

sales = [
    (1, 1, '2026-05-01', 1, 4500.00, 'Cash', 'ซื้อให้เพื่อน'),
    (2, 2, '2026-05-03', 1, 6500.00, 'Credit Card', 'ลูกค้าซื้อออนไลน์'),
    (3, 3, '2026-05-04', 1, 5200.00, 'Cash', 'มอบเป็นของขวัญ'),
    (4, 4, '2026-05-05', 1, 4200.00, 'Bank Transfer', 'ลูกค้าจองล่วงหน้า'),
    (10, 5, '2026-05-06', 1, 1200.00, 'Cash', 'ซื้อปลาตู้'),
    (6, 6, '2026-05-07', 1, 900.00, 'Mobile Pay', 'ซื้อปลาทอง'),
    (7, 7, '2026-05-08', 1, 3000.00, 'Cash', 'ซื้อกระต่าย'),
    (8, 8, '2026-05-09', 1, 7500.00, 'Credit Card', 'ซื้อสัตว์เลื้อยคลาน'),
    (9, 9, '2026-05-10', 1, 850.00, 'Cash', 'ซื้อหนูนำเข้าจากต่างประเทศ'),
    (11, 10, '2026-05-11', 1, 600.00, 'Credit Card', 'ซื้อปลาสวยงาม'),
    (12, 11, '2026-05-12', 1, 4800.00, 'Cash', 'ซื้อแมวเปอร์เซีย'),
    (13, 12, '2026-05-13', 1, 1400.00, 'Bank Transfer', 'จัดส่งนกฟินซ์'),
    (5, 13, '2026-05-14', 1, 200.00, 'Cash', 'ซื้อปลานีโม่')
]
cur.executemany('INSERT INTO sales (pet_id, customer_id, sale_date, quantity, total_price, payment_method, notes) VALUES (?, ?, ?, ?, ?, ?, ?)', sales)

conn.commit()
conn.close()
print('Created', DB_PATH)
