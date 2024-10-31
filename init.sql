CREATE DATABASE skripsi;
USE skripsi;
CREATE TABLE sales (
    no INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    name VARCHAR(255) NOT NULL,
    qty INT NOT NULL
);
CREATE TABLE predict (
    no INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    qty INT NOT NULL,
    month VARCHAR(255) NOT NULL
);
CREATE TABLE user (
    username VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);