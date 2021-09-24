CREATE TABLE `fixtures` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fixtureType` int DEFAULT NULL,
  `startTime` datetime DEFAULT NULL,
  `marketEndTime` datetime DEFAULT NULL,
  `endTime` datetime DEFAULT NULL,
  `price` double DEFAULT NULL,
  `status` varchar(45) DEFAULT 'NOT CREATED',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5116 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;