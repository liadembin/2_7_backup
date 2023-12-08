-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS PythonSocketServer;

-- Switch to the PythonSocketServer database
USE PythonSocketServer;

-- Create the Users table
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    sessid VARCHAR(255),
    public_key_N BIGINT UNSIGNED
);

-- Create the Messages table
CREATE TABLE IF NOT EXISTS Messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    sendingtime DATETIME,
    content VARCHAR(1024),
    message_type ENUM('Received', 'Sent'), -- Indicates whether it's a received or sent message
    FOREIGN KEY (sender_id) REFERENCES Users(id),
    FOREIGN KEY (receiver_id) REFERENCES Users(id)
);

