
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `DWD_Daten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DWD_Daten` (
  `time_sec` int(11) unsigned NOT NULL,
  `TIMESTAMP` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `Temperature` int(4) DEFAULT NULL,
  `SS1` int(4) DEFAULT NULL,
  `Bewoelkung_H` int(4) DEFAULT NULL,
  `Bewoelkung_M` int(4) DEFAULT NULL,
  `Bewoelkung_L` int(4) DEFAULT NULL,
  `Wind_direction` int(4) DEFAULT NULL,
  `Windgeschw` int(4) DEFAULT NULL,
  `Boeen` int(4) DEFAULT NULL,
  `Luftdruck` int(4) DEFAULT NULL,
  `Td` int(4) DEFAULT NULL,
  `Rad1h` int(4) DEFAULT NULL,
  `Humidity` int(4) DEFAULT NULL,
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

