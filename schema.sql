CREATE DATABASE IF NOT EXISTS crop_health_db;
USE crop_health_db;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(30) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crops (
    crop_id INT PRIMARY KEY AUTO_INCREMENT,
    crop_name VARCHAR(80) NOT NULL UNIQUE,
    species VARCHAR(120) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    farm_size DECIMAL(10,2) NOT NULL,
    crop_focus VARCHAR(150),
    joined_date DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE IF NOT EXISTS images (
    image_id INT PRIMARY KEY AUTO_INCREMENT,
    crop_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    uploaded_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    image_id INT NOT NULL,
    health_status VARCHAR(40) NOT NULL,
    health_score DECIMAL(5,2) NOT NULL,
    green_percentage DECIMAL(5,2) NOT NULL,
    disease_area_percentage DECIMAL(5,2) NOT NULL,
    edge_density DECIMAL(5,2) DEFAULT 0,
    advice TEXT,
    notes VARCHAR(255),
    analyzed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(image_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT IGNORE INTO users (username, password_hash, full_name, role)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'System Administrator', 'admin');

INSERT IGNORE INTO crops (crop_name, species) VALUES
('Rice', 'Oryza sativa'),
('Wheat', 'Triticum aestivum'),
('Tomato', 'Solanum lycopersicum'),
('Maize', 'Zea mays'),
('Cotton', 'Gossypium hirsutum'),
('Sugarcane', 'Saccharum officinarum'),
('Potato', 'Solanum tuberosum'),
('Banana', 'Musa acuminata');
