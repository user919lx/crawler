CREATE TABLE `price_raw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alpha2` varchar(10),
  `nsuid` varchar(100),
  `sales_status` varchar(100),
  `raw_data` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_country_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;