CREATE TABLE `price_raw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alpha2` varchar(10),
  `nsuid` varchar(100) COLLATE utf8mb4_unicode_ci,
  `raw_data` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_country_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;