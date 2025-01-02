CREATE DATABASE IF NOT EXISTS delivery_platform;

USE delivery_platform;

-- 建立 riders 資料表
CREATE TABLE IF NOT EXISTS riders (
    id INT AUTO_INCREMENT PRIMARY KEY,                -- 自動遞增的外送員ID
    user_id VARCHAR(50) NOT NULL UNIQUE,              -- 用戶ID，確保唯一
    password VARCHAR(255) NOT NULL,                   -- 密碼
    name VARCHAR(100) DEFAULT NULL                    -- 外送員名稱
);

-- 建立 orders 資料表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,                -- 自動遞增的訂單ID
    restaurant_name VARCHAR(100) NOT NULL,            -- 餐廳名稱
    total_amount DECIMAL(10, 2) NOT NULL,             -- 訂單金額
    status ENUM('Ready for Pickup', 'In Transit', 'Picked Up', 'Completed') NOT NULL DEFAULT 'Ready for Pickup',  -- 訂單狀態
    rider_id INT DEFAULT NULL,                        -- 外送員ID，預設為NULL，代表尚未指派
    delivered_at DATETIME DEFAULT NULL,               -- 送達時間，預設為NULL
    FOREIGN KEY (rider_id) REFERENCES riders(id)     -- 外送員ID與riders表建立關聯
);
