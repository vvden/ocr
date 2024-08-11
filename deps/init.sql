-- Create the database
DROP DATABASE IF  EXISTS ocr_db;

CREATE DATABASE IF NOT EXISTS ocr_db;

-- Use the database
USE ocr_db;

-- Create the 'images' table
DROP TABLE IF EXISTS images;

CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filepath VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the 'words' table
DROP TABLE IF EXISTS words;

CREATE TABLE IF NOT EXISTS words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    word VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS text_data;

CREATE TABLE text_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(255) NOT NULL,
    extracted_text TEXT DEFAULT NULL,
    text TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
