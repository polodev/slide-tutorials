"""The 'Rahim Mobile' shop database shared by MySQL 102, 103 and MySQL for Laravel.
Fictional names and numbers. One customer has no purchase, one category and one product were never sold,
so LEFT JOIN / anti-join lessons have something to find."""

SCHEMA = '''
CREATE TABLE branches (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE customers (
    id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    phone    VARCHAR(15)  NOT NULL UNIQUE,
    district VARCHAR(50)
);

CREATE TABLE categories (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id INT UNSIGNED NOT NULL,
    name        VARCHAR(100) NOT NULL,
    brand       VARCHAR(50)  NOT NULL,
    cost        DECIMAL(10,2) NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    stock       INT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE employees (
    id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    branch_id INT UNSIGNED NOT NULL,
    name      VARCHAR(100) NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branches (id)
);

CREATE TABLE sales (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    invoice_no  VARCHAR(20) NOT NULL UNIQUE,
    branch_id   INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    customer_id INT UNSIGNED NULL,            -- walk-in হলে NULL
    sold_at     DATETIME NOT NULL,
    total       DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (branch_id)   REFERENCES branches (id),
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

CREATE TABLE sale_items (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sale_id    INT UNSIGNED NOT NULL,
    product_id INT UNSIGNED NOT NULL,
    qty        INT UNSIGNED NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id)    REFERENCES sales (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id)
);
'''

SEED = '''
INSERT INTO branches (name) VALUES ('Mirpur'), ('Uttara'), ('Gulshan');

INSERT INTO customers (name, phone, district) VALUES
    ('Karim Uddin',  '01711000001', 'Dhaka'),
    ('Nusrat Jahan', '01811000002', 'Sylhet'),
    ('Rahim Mia',    '01911000003', 'Khulna'),
    ('Sadia Islam',  '01611000004', 'Dhaka'),
    ('Tanvir Hasan', '01511000005', 'Gazipur'),
    ('Mitu Akter',   '01311000006', 'Dhaka');

INSERT INTO categories (name) VALUES ('Smartphone'), ('Feature phone'), ('Accessories'), ('Tablet');

INSERT INTO products (category_id, name, brand, cost, price, stock) VALUES
    (1, 'Redmi 13',       'Xiaomi',  15800, 17500, 5),
    (1, 'Redmi Note 13',  'Xiaomi',  21500, 23500, 2),
    (1, 'Galaxy A15',     'Samsung', 19000, 21000, 3),
    (1, 'iPhone 12',      'Apple',   44000, 48000, 1),
    (1, 'Vivo Y28',       'Vivo',    16300, 18000, 4),
    (2, 'Nokia 105',      'Nokia',    1750,  2100, 12),
    (2, 'Walton Olvio',   'Walton',   1400,  1750, 9),
    (3, 'Charger 20W',    'Anker',     480,   650, 30),
    (3, 'Earbuds Q20i',   'Soundcore', 2600, 3300, 8),
    (3, 'Glass Protector','Generic',    60,   150, 50),
    (1, 'Realme C67',     'Realme',  16500, 18500, 3);

INSERT INTO employees (branch_id, name) VALUES (1, 'Sabbir'), (1, 'Lima'), (2, 'Fahim'), (3, 'Riya');

INSERT INTO sales (invoice_no, branch_id, employee_id, customer_id, sold_at, total) VALUES
    ('INV-1001', 1, 1, 1,    '2026-10-15 11:20:00', 18150),
    ('INV-1002', 1, 2, NULL, '2026-10-15 16:05:00',  2100),
    ('INV-1003', 2, 3, 2,    '2026-10-16 12:40:00', 24150),
    ('INV-1004', 3, 4, 3,    '2026-10-16 18:10:00', 48000),
    ('INV-1005', 1, 1, 4,    '2026-10-17 10:30:00', 21300),
    ('INV-1006', 2, 3, NULL, '2026-10-17 19:45:00',  3450),
    ('INV-1007', 1, 2, 1,    '2026-10-18 13:15:00', 18000),
    ('INV-1008', 3, 4, 5,    '2026-10-18 17:30:00', 21650),
    ('INV-1009', 2, 3, 2,    '2026-10-19 11:00:00',  1750),
    ('INV-1010', 1, 1, NULL, '2026-10-19 20:10:00',  1300);

INSERT INTO sale_items (sale_id, product_id, qty, unit_price) VALUES
    (1, 1, 1, 17500), (1, 8, 1, 650),
    (2, 6, 1, 2100),
    (3, 2, 1, 23500), (3, 8, 1, 650),
    (4, 4, 1, 48000),
    (5, 3, 1, 21000), (5, 10, 2, 150),
    (6, 9, 1, 3300), (6, 10, 1, 150),
    (7, 5, 1, 18000),
    (8, 3, 1, 21000), (8, 8, 1, 650),
    (9, 7, 1, 1750),
    (10, 8, 2, 650);
'''
