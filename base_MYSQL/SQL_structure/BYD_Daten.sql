
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `BYD_Daten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `BYD_Daten` (
  `time_sec` int(11) unsigned NOT NULL,
  `TIMESTAMP` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `Laden_kWh` decimal(11,3) DEFAULT NULL,
  `EntLaden_kWh` decimal(11,3) DEFAULT NULL,
  `CycleCounts` int(6) DEFAULT NULL,
  `PackVoltage_V` decimal(7,3) DEFAULT NULL,
  `Current_A` decimal(7,3) DEFAULT NULL,
  `SOC` decimal(7,3) DEFAULT NULL,
  `SysTemp_C` decimal(7,3) DEFAULT NULL,
  `MaxCellTemp_C` decimal(7,3) DEFAULT NULL,
  `MinCellTemp_C` decimal(7,3) DEFAULT NULL,
  `MaxCellVol_V` decimal(7,3) DEFAULT NULL,
  `MinCellVol_V` decimal(7,3) DEFAULT NULL,
  `Power_kW` decimal(7,3) DEFAULT NULL,
  `MaxVolPos` int(1) DEFAULT NULL,
  `MinVolPos` int(1) DEFAULT NULL,
  `MaxTempPos` int(1) DEFAULT NULL,
  `MinTempPos` int(1) DEFAULT NULL,
  PRIMARY KEY (`time_sec`),
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`),
  UNIQUE KEY `time_sec` (`time_sec`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

