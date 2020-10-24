
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `aggregate_WR_Daten_hourly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aggregate_WR_Daten_hourly` (
  `time_sec` int(11) NOT NULL,
  `TIMESTAMP` timestamp NULL DEFAULT NULL,
  `ChargeCycles` int(4) unsigned DEFAULT NULL,
  `BatTemperature` decimal(11,6) DEFAULT NULL,
  `HomeConsumptionSolar_kWh` decimal(17,14) DEFAULT NULL,
  `HomeConsumptionBat_kWh` decimal(17,14) DEFAULT NULL,
  `HomeConsumptionGrid_kWh` decimal(17,14) DEFAULT NULL,
  `HomeConsumption_kWh` decimal(17,14) DEFAULT NULL,
  `Autarkie` decimal(4,3) DEFAULT NULL,
  `PV_kWh` decimal(17,14) DEFAULT NULL,
  `ac_kWh` decimal(17,14) DEFAULT NULL,
  `BatLaden_kWh` decimal(17,14) DEFAULT NULL,
  `BatLaden_Frei_kWh` decimal(17,14) DEFAULT NULL,
  `BatEntladen_kWh` decimal(17,14) DEFAULT NULL,
  `Einspeisen_kWh` decimal(17,14) DEFAULT NULL,
  PRIMARY KEY (`time_sec`),
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

