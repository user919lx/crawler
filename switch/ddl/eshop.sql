CREATE TABLE `eshop` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country` varchar(100),
  `alpha2` varchar(10),
  `currency` varchar(10),
  `region` varchar(10),
  `is_active` tinyint,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alpha2` (`alpha2`),
  KEY `ix_country_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;