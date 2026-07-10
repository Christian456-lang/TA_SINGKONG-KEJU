CREATE TABLE IF NOT EXISTS menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    price INT NOT NULL,
    rating FLOAT DEFAULT 0.0,
    reviews INT DEFAULT 0,
    image VARCHAR(255) NOT NULL,
    `group` VARCHAR(50) NOT NULL,
    stock INT DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

TRUNCATE TABLE menu;

DROP TABLE IF EXISTS admin;
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin'
);

INSERT IGNORE INTO admin (username, password, role) VALUES ('admin', 'admin123', 'admin');
INSERT IGNORE INTO admin (username, password, role) VALUES ('kasir', 'kasir123', 'kasir');

CREATE TABLE IF NOT EXISTS payment_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT IGNORE INTO payment_method (name) VALUES ('Tunai'), ('QRIS'), ('Transfer');

CREATE TABLE IF NOT EXISTS `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100),
    payment_method_id INT,
    table_number VARCHAR(20) NOT NULL,
    table_category VARCHAR(50) NOT NULL,
    date DATETIME NOT NULL,
    total_amount INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    product_summary VARCHAR(255) NOT NULL,
    admin_id INT,
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS order_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_unit INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order`(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menu(id) ON DELETE CASCADE
);

INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Singkong Keju D9', 'OLAHAN SINGKONG', '', 25000, 5.0, 1244, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Keju', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Getuk D9 Pelangi', 'MANIS TRADISIONAL', '', 20000, 4.9, 982, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Getuk+Pelangi', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Kroket Singkong D9', 'CEMILAN GURIH', '', 22000, 4.8, 843, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Kroket+Singkong', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Prol Tape Keju D9', 'VARIAN TAPE', '', 35000, 4.9, 528, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Prol+Tape', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Timus Manis D9', 'KUDAPAN SORE', '', 18000, 4.7, 315, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Timus+Manis', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Gemblong Cotot D9', 'TRADISI SALATIGA', '', 20000, 4.8, 526, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Gemblong+Cotot', 'unggulan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Bakmi Jawa Godog (Rebus)', 'MAKANAN BERAT', 'Mie rebus tradisional dengan kuah kaldu kentol dan rempah pilihan.', 22000, 4.5, 320, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Bakmi+Godog', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Bakmi Jawa Goreng', 'MAKANAN BERAT', 'Mie goreng khas Jawa dengan aroma smokey dan cita rasa manis gurih.', 22000, 4.5, 285, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Bakmi+Goreng', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Nasi Goreng Spesial', 'FAVORIT', 'Nasi goreng dengan telur, ayam, dan sayuran segar khas D9.', 25000, 4.8, 510, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Nasgor+Spesial', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Nasi Goreng Babat', 'MAKANAN BERAT', 'Nasi goreng gurih dengan potongan babat empuk bumbu rempah.', 28000, 4.6, 198, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Nasgor+Babat', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Nasi Pecel', 'MENU TRADISIONAL', 'Sayuran segar dengan siraman bumbu kacang gurih dan rempeyek renyah.', 18000, 4.7, 425, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Pecel', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Nasi Ayam Goreng', 'MAKANAN BERAT', 'Ayam goreng bumbu lengkap dengan sambal kentol dan lalapan.', 25000, 4.8, 480, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Ayam+Goreng', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Nasi Ayam Bakar', 'MAKANAN BERAT', 'Ayam bakar bumbu kecap meresap dengan aroma bakaran yang menggoda.', 26000, 4.9, 390, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Ayam+Bakar', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Soto Ayam / Sop', 'MENU SEGAR', 'Soto ayam kuah bening segar dengan irisan dan rempah dan kuva gurih.', 20000, 4.6, 310, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Soto+Ayam', 'makanan_berat', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Singkong Keju Original', 'OLAHAN TERLARIS', 'Singkong goreng renyah dengan taburan keju yang melimpah.', 25000, 5.0, 1244, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Keju', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Singkong Keju Cokelat / Meises', 'MANIS TRADISIONAL', 'Perpaduan gurihnya singkong dengan manisnya cokelat meises.', 25000, 4.9, 982, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Cokelat', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Singkong Sambal Roa', 'CAMILAN GURIH', 'Singkong goreng khas D9 disajikan dengan sambal roa pedas mantap.', 22000, 4.8, 843, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Sambal', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Tahu Serasi Goreng', 'KHAS BANDUNGAN', 'Tahu goreng khas Bandungan yang lembut dan gurih.', 18000, 4.7, 315, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Tahu+Serasi', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Tempe Mendoan', 'GORENGAN FAVORIT', 'Tempe goreng tepung setengah matang dengan irisan daun bawang.', 15000, 4.6, 290, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Tempe+Mendoan', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Pisang Goreng', 'MANIS ALAMI', 'Pisang goreng manis dengan pilihan topping keju atau cokelat.', 18000, 4.7, 350, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Pisang+Goreng', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Kroket Singkong', 'CAMILAN GURIH', 'Kroket lembut berbahan dasar singkong pilihan.', 20000, 4.8, 526, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Kroket+Singkong', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Tape Goreng', 'MANIS LEGIT', 'Tape singkong goreng yang manis dan legit.', 15000, 4.5, 210, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Tape+Goreng', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Getuk Goreng', 'TRADISI SALATIGA', 'Getuk singkong manis yang digoreng hingga renyah di luar.', 18000, 4.8, 420, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Getuk+Goreng', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Roti Bakar (Aneka Topping)', 'CAMILAN POPULER', 'Roti bakar hangat dengan berbagai pilihan topping toast.', 20000, 4.6, 380, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Roti+Bakar', 'makanan_ringan', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Teh Poci', 'SEDUHAN TRADISIONAL', 'Teh poci tradisional yang harum dan menyegarkan.', 13000, 4.8, 860, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Teh+Poci', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Es Teh Kampul', 'SEGARNYA ALAMI', 'Es teh segar dengan sensasi kampul yang khas.', 8000, 4.7, 945, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Teh+Kampul', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Wedang Uwuh', 'SEDUHAN ALAMI', 'Wedang uwuh hangat dengan rempah-rempah tradisional.', 12000, 4.9, 990, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Uwuh', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Wedang Jahe', 'HANGAT MENYEHATKAN', 'Wedang jahe hangat yang menyehatkan tubuh.', 10000, 4.7, 710, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Jahe', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Wedang Ronde', 'LEGENDA HANGAT', 'Wedang ronde dengan isian kacang yang gurih.', 15000, 4.8, 850, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Ronde', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Kopi Hitam Tubruk', 'KOPI KLASIK', 'Kopi hitam tubruk khas yang kuat dan nikmat.', 12000, 4.6, 620, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Kopi+Tubruk', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Kopi Susu', 'LEMBUT & CREAMY', 'Kopi susu lembut yang creamy dan nikmat.', 18000, 4.9, 1050, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Kopi+Susu', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Es Campur', 'MINUMAN PALING SEGAR', 'Es campur segar dengan aneka buah dan sirup.', 22000, 4.8, 880, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Campur', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Es Teler', 'FAVORIT NUSANTARA', 'Es teler segar dengan alpukat, kelapa, dan nangka.', 25000, 4.9, 730, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Teler', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Aneka Jus Buah', 'FRESH & SEHAT', 'Jus buah segar pilihan yang menyehatkan.', 15000, 4.7, 480, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Jus+Buah', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Lemon Tea (Panas / Es)', 'SEGAR & SEHAT', 'Lemon tea yang segar dan menyehatkan.', 10000, 4.6, 390, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Lemon+Tea', 'minuman', 100);
INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ('Teh Manis / Tawar', 'MINUMAN SEPANJANG', 'Teh manis atau tawar hangat/dingin.', 5000, 4.5, 1200, 'https://placehold.co/300x250/fdfbf7/7a6353?text=Teh+Manis', 'minuman', 100);