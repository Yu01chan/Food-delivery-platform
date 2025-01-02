-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-01-02 05:14:14
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

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
(4, '鰻魚飯(大)', '不吃可惜，好吃', 250.00, 'TR', 'static/images/dc2b0f9b7fc440b382a85369a7d07c17_1.jpg', '2024-12-24 07:16:23'),
(8, '炒飯', '有三色豆不好吃！', 65.00, 'kj', 'static/images\\fa22e97d0cbe495481f2a972bc7cc9f5_726682a118b44a4d87ce554c77fe0428_9_FriedRice_L.png', '2025-01-01 17:12:10');

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `user_id` varchar(60) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `restaurant_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `order_items` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `customer_total` float NOT NULL,
  `status` varchar(255) NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `orders`
--

INSERT INTO `orders` (`id`, `user_id`, `restaurant_id`, `order_items`, `customer_total`, `status`, `created_at`) VALUES
(14, 'gg', 'kj', '炒飯&1', 65, 'Completed', '2025-01-02 03:13:16'),
(15, 'gg', 'TR', '鰻魚飯(大)&1', 250, 'Pending', '2025-01-02 03:21:33'),
(16, 'gg', 'kj', '炒飯&1', 65, 'Completed', '2025-01-02 04:11:03');

-- --------------------------------------------------------

--
-- 資料表結構 `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` varchar(60) NOT NULL,
  `menu_item_id` varchar(60) NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `order_reviews`
--

CREATE TABLE `order_reviews` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `order_reviews`
--

INSERT INTO `order_reviews` (`id`, `order_id`, `rating`, `comment`, `created_at`) VALUES
(1, 14, 3, '1', '2025-01-02 04:03:43');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('restaurant','delivery','customer') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`id`, `user_id`, `password`, `role`, `created_at`) VALUES
(1, '7', 'scrypt:32768:8:1$L3lNQQekUWk6muWx$d32d7ea9eb88271698d4e805c375e733a30489d2b126a3b664364ac9ef60a10c8ab138788b2d7467378beaf25b7e3e8708814620329a0f94a6cd7617f43a07cc', 'restaurant', '2024-12-23 08:36:19'),
(2, 'Ew', 'scrypt:32768:8:1$VfZ0GhCImF0ABOru$c3e34817057c11396316600843355eb5aa1995af5b023cab0d309e8e67cfac1ab36d4286b436e10f9c359c6eac505258489f19b6827548468fe7b8d057dea9e5', 'restaurant', '2024-12-24 05:57:56'),
(3, 'TR', 'scrypt:32768:8:1$ktPLD0GJKwdS46fI$b663e551d3ec54d0d10af9eabbc349b90a3beeef3896fea43402e493c20f334645c42dcfba7672300832194d4c0f5a742d9905ff01f1bcdfe12ee9d2b76edd54', 'restaurant', '2024-12-24 07:13:17'),
(4, 'Rd', 'scrypt:32768:8:1$NPbOeXZU00yQwW9x$5faccd077517044662ceb9d1f1a853bf76bf055e60d85c573ac56195c5dae729e69550ab1e0306a0622d56d731ff4cd1b07bf464569212fe2a5d6ea7730fc561', 'customer', '2024-12-24 06:09:34'),
(5, 'Ds', 'scrypt:32768:8:1$9KEWRHOt603Pn54x$9a19bf462a2aa2e8096131213703cf743c09d4c2ee11553e07b1073e6fc5138d519d85ab989c6928f8eaa8a0dbb72d39cfc24d5bc2d7b64aef24d0923bf15ec3', 'customer', '2024-12-24 06:10:25'),
(15, 'kj', 'scrypt:32768:8:1$2qDovp3RZE4HTldE$6c865524618f4995b1bf57fd9a2ce9beb8667815d75c6c7cebd7aa64caf40cf6d0c3630c5e0a44897d785c1aa90109a288bdca2b8271a7c94dc2d875fabac546', 'restaurant', '2025-01-01 17:09:49'),
(16, 'gg', 'scrypt:32768:8:1$eGDBl9oOZ9Nuz0u7$89f9359991ab312146f92137e6c2cf2279317850df2b7a30ce463c961beb624c54b02982533528404d92bbb1f470dfd4af1f92674ae200f41cba8bd7de9c9c8c', 'customer', '2025-01-01 17:28:36');

--
-- 已傾印資料表的索引
--

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
-- 資料表索引 `order_reviews`
--
ALTER TABLE `order_reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `menu_items`
--
ALTER TABLE `menu_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_reviews`
--
ALTER TABLE `order_reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `order_reviews`
--
ALTER TABLE `order_reviews`
  ADD CONSTRAINT `order_reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
