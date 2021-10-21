CREATE TABLE `bids` (
  `idbids` int NOT NULL AUTO_INCREMENT,
  `fixtureId` int DEFAULT NULL,
  `price` double DEFAULT NULL,
  `strike` double DEFAULT NULL,
  `probability` double DEFAULT NULL,
  `over` double DEFAULT NULL,
  `under` double DEFAULT NULL,
  `endPrice` double DEFAULT NULL,
  `bidAmount` double DEFAULT '100',
  `overPnl` double DEFAULT NULL,
  `underPnl` double DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `endTime` datetime DEFAULT NULL,
  PRIMARY KEY (`idbids`)
) ENGINE = InnoDB AUTO_INCREMENT = 436487 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE `expiries` (
  `idexpiries` int NOT NULL AUTO_INCREMENT,
  `expiry` bigint DEFAULT NULL,
  `btc_price` double DEFAULT NULL,
  `rake_over` double DEFAULT NULL,
  `rake_under` double DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idexpiries`)
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE `fixtures` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fixtureType` int DEFAULT NULL,
  `startTime` datetime DEFAULT NULL,
  `marketEndTime` datetime DEFAULT NULL,
  `endTime` datetime DEFAULT NULL,
  `price` double DEFAULT NULL,
  `status` varchar(45) DEFAULT 'NOT CREATED',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB AUTO_INCREMENT = 12316 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE `pnldata` (
  `idpnldata` int NOT NULL AUTO_INCREMENT,
  `fixtureId` int DEFAULT NULL,
  `price` double DEFAULT NULL,
  `strike` double DEFAULT NULL,
  `probability` double DEFAULT NULL,
  `over` double DEFAULT NULL,
  `under` double DEFAULT NULL,
  `endPrice` double DEFAULT NULL,
  `bidAmount` double DEFAULT '100',
  `overPnl` double DEFAULT NULL,
  `underPnl` double DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `endTime` datetime DEFAULT NULL,
  PRIMARY KEY (`idpnldata`)
) ENGINE = InnoDB AUTO_INCREMENT = 2555326 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE `probabilities` (
  `idprobabilities` int NOT NULL AUTO_INCREMENT,
  `idexpiries` int DEFAULT NULL,
  `odds_id` int DEFAULT NULL,
  `strike` double DEFAULT NULL,
  `over` double DEFAULT NULL,
  `under` double DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idprobabilities`)
) ENGINE = InnoDB AUTO_INCREMENT = 21 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;