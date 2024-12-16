-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-12-16 07:56:09
-- 伺服器版本： 10.4.28-MariaDB
-- PHP 版本： 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `delivery`
--

-- --------------------------------------------------------

--
-- 資料表結構 `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `customers`
--

INSERT INTO `customers` (`customer_id`, `user_id`, `name`, `phone`, `address`) VALUES
(1, 4, '陳大名', '0951521364', '台中市潭子區中山路100號'),
(2, 6, '張君雅', '09601456812', '台中市潭子區民族路100號');

-- --------------------------------------------------------

--
-- 資料表結構 `deliverypersons`
--

CREATE TABLE `deliverypersons` (
  `delivery_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `status` enum('available','busy') DEFAULT 'available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `deliverypersons`
--

INSERT INTO `deliverypersons` (`delivery_id`, `user_id`, `name`, `phone`, `status`) VALUES
(1, 3, '王小明', '09888741857', 'available'),
(2, 5, '郭好', '0966784574', 'available');

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `delivery_id` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `platform_fee` decimal(10,2) NOT NULL,
  `restaurant_income` decimal(10,2) NOT NULL,
  `delivery_fee` decimal(10,2) DEFAULT NULL,
  `status` enum('pending','completed','cancelled') DEFAULT 'pending',
  `order_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `orders`
--

INSERT INTO `orders` (`order_id`, `restaurant_id`, `customer_id`, `delivery_id`, `total_amount`, `platform_fee`, `restaurant_income`, `delivery_fee`, `status`, `order_time`) VALUES
(1, 1, 2, 1, 260.00, 10.00, 240.00, 10.00, 'completed', '2024-12-12 10:10:50'),
(2, 2, 1, 2, 810.00, 10.00, 790.00, 10.00, 'completed', '2024-12-12 10:10:50');

-- --------------------------------------------------------

--
-- 資料表結構 `restaurants`
--

CREATE TABLE `restaurants` (
  `restaurant_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `phone` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `restaurants`
--

INSERT INTO `restaurants` (`restaurant_id`, `user_id`, `name`, `address`, `phone`) VALUES
(1, 1, '好吃鰻魚飯', '台中市北屯區東山路12號', '0425876798'),
(2, 2, '火鍋大王', '台中市潭子區中山路一段120號', '098585477');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('restaurant','delivery','customer') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `username`, `password_hash`, `role`, `created_at`) VALUES
(1, '好吃鰻魚飯', '1234', 'restaurant', '2024-12-12 09:55:07'),
(2, '火鍋大王', '5678', 'restaurant', '2024-12-12 09:55:07'),
(3, '王小明', '7891', 'delivery', '2024-12-12 09:55:07'),
(4, '陳大名', '2121', 'customer', '2024-12-12 09:55:07'),
(5, '郭好', '0101', 'delivery', '2024-12-12 09:55:07'),
(6, '張君雅', '2525', 'customer', '2024-12-12 09:55:07');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `name` (`name`);

--
-- 資料表索引 `deliverypersons`
--
ALTER TABLE `deliverypersons`
  ADD PRIMARY KEY (`delivery_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `name` (`name`);

--
-- 資料表索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `restaurant_id` (`restaurant_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `delivery_id` (`delivery_id`);

--
-- 資料表索引 `restaurants`
--
ALTER TABLE `restaurants`
  ADD PRIMARY KEY (`restaurant_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `name` (`name`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `deliverypersons`
--
ALTER TABLE `deliverypersons`
  MODIFY `delivery_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `restaurants`
--
ALTER TABLE `restaurants`
  MODIFY `restaurant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `customers`
--
ALTER TABLE `customers`
  ADD CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `customers_ibfk_2` FOREIGN KEY (`name`) REFERENCES `users` (`username`);

--
-- 資料表的限制式 `deliverypersons`
--
ALTER TABLE `deliverypersons`
  ADD CONSTRAINT `deliverypersons_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `deliverypersons_ibfk_2` FOREIGN KEY (`name`) REFERENCES `users` (`username`);

--
-- 資料表的限制式 `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`delivery_id`) REFERENCES `deliverypersons` (`delivery_id`);

--
-- 資料表的限制式 `restaurants`
--
ALTER TABLE `restaurants`
  ADD CONSTRAINT `restaurants_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `restaurants_ibfk_2` FOREIGN KEY (`name`) REFERENCES `users` (`username`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
