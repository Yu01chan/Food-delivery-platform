-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-12-24 14:55:14
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
-- 資料庫： `restaurant_platform`
--

-- --------------------------------------------------------

--
-- 資料表結構 `customers`
--

CREATE TABLE `customers` (
  `id` int(100) NOT NULL,
  `c_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `customers`
--

INSERT INTO `customers` (`id`, `c_id`, `password`, `created_at`) VALUES
(4, 'Rd', 'scrypt:32768:8:1$NPbOeXZU00yQwW9x$5faccd077517044662ceb9d1f1a853bf76bf055e60d85c573ac56195c5dae729e69550ab1e0306a0622d56d731ff4cd1b07bf464569212fe2a5d6ea7730fc561', '2024-12-24 06:09:34'),
(5, 'Ds', 'scrypt:32768:8:1$9KEWRHOt603Pn54x$9a19bf462a2aa2e8096131213703cf743c09d4c2ee11553e07b1073e6fc5138d519d85ab989c6928f8eaa8a0dbb72d39cfc24d5bc2d7b64aef24d0923bf15ec3', '2024-12-24 06:10:25');

-- --------------------------------------------------------

--
-- 資料表結構 `menu_items`
--

CREATE TABLE `menu_items` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `restaurant_id` varchar(11) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `menu_items`
--

INSERT INTO `menu_items` (`id`, `name`, `description`, `price`, `restaurant_id`, `image_path`, `created_at`) VALUES
(1, '紅燒肉', '肉口即化，好下飯', 100.00, '7', 'static/images\\c6900d0f6b9b45d0a4450ff56caaf7d4_7.jpg', '2024-12-23 08:37:25'),
(2, '燙青菜', '營養均衡', 30.00, '7', 'static/images\\cdb78db4c6d44a23ae3438fca2092ad5_8.jpg', '2024-12-23 08:39:27'),
(3, '鰻魚飯套餐', '日本口味，彷彿到達日本', 220.00, 'TR', 'static/images\\01bf586387a04b34bf2055bd14a481cd_0.png', '2024-12-24 07:14:59'),
(4, '鰻魚飯(大)', '不吃可惜', 250.00, 'TR', 'static/images\\dc2b0f9b7fc440b382a85369a7d07c17_1.jpg', '2024-12-24 07:16:23');

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `status` enum('Pending','Ready for Pickup','Completed','Cancelled') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `menu_item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `restaurants`
--

CREATE TABLE `restaurants` (
  `id` int(11) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `restaurants`
--

INSERT INTO `restaurants` (`id`, `user_id`, `password`, `created_at`) VALUES
(1, '7', 'scrypt:32768:8:1$L3lNQQekUWk6muWx$d32d7ea9eb88271698d4e805c375e733a30489d2b126a3b664364ac9ef60a10c8ab138788b2d7467378beaf25b7e3e8708814620329a0f94a6cd7617f43a07cc', '2024-12-23 08:36:19'),
(2, 'Ew', 'scrypt:32768:8:1$VfZ0GhCImF0ABOru$c3e34817057c11396316600843355eb5aa1995af5b023cab0d309e8e67cfac1ab36d4286b436e10f9c359c6eac505258489f19b6827548468fe7b8d057dea9e5', '2024-12-24 05:57:56'),
(3, 'TR', 'scrypt:32768:8:1$ktPLD0GJKwdS46fI$b663e551d3ec54d0d10af9eabbc349b90a3beeef3896fea43402e493c20f334645c42dcfba7672300832194d4c0f5a742d9905ff01f1bcdfe12ee9d2b76edd54', '2024-12-24 07:13:17');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `menu_items`
--
ALTER TABLE `menu_items`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `restaurants`
--
ALTER TABLE `restaurants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `menu_items`
--
ALTER TABLE `menu_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `restaurants`
--
ALTER TABLE `restaurants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
