
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `WR_Daten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WR_Daten` (
  `ID` int(8) unsigned NOT NULL AUTO_INCREMENT,
  `TIMESTAMP` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `time_sec` int(11) unsigned NOT NULL,
  `BatVoltage` decimal(11,6) DEFAULT NULL,
  `BatCurrent` decimal(11,6) DEFAULT NULL,
  `BatCurrentDir` int(1) DEFAULT NULL,
  `ChargeCycles` int(4) unsigned DEFAULT NULL,
  `BatTemperature` decimal(11,6) DEFAULT NULL,
  `BatStateOfCharge` int(3) unsigned DEFAULT NULL,
  `GridLimitation` decimal(11,6) DEFAULT NULL,
  `GridFreq` decimal(11,6) DEFAULT NULL,
  `GridCosPhi` decimal(11,6) DEFAULT NULL,
  `GridVoltageL1` decimal(11,6) DEFAULT NULL,
  `GridVoltageL2` decimal(11,6) DEFAULT NULL,
  `GridVoltageL3` decimal(11,6) DEFAULT NULL,
  `AktHomeConsumptionSolar` decimal(11,6) DEFAULT NULL,
  `AktHomeConsumptionBat` decimal(11,6) DEFAULT NULL,
  `AktHomeConsumptionGrid` decimal(11,6) DEFAULT NULL,
  `AktHomeConsumption` decimal(11,6) DEFAULT NULL,
  `dc1Voltage` decimal(11,6) NOT NULL,
  `dc1Current` decimal(11,6) NOT NULL,
  `dc1Power` decimal(11,6) DEFAULT NULL,
  `dc2Voltage` decimal(11,6) NOT NULL,
  `dc2Current` decimal(11,6) NOT NULL,
  `dc2Power` decimal(11,6) DEFAULT NULL,
  `dcPowerPV` decimal(11,6) DEFAULT NULL,
  `acPower` decimal(11,6) DEFAULT NULL,
  `operatingStatus` int(1) unsigned DEFAULT NULL,
  `BatPowerLaden` decimal(11,6) DEFAULT NULL,
  `BatLaden_Frei` decimal(11,6) NOT NULL,
  `BatPowerEntLaden` decimal(11,6) DEFAULT NULL,
  `EinspeisenPower` decimal(11,6) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `time_sec` (`time_sec`),
  UNIQUE KEY `ID` (`ID`) USING BTREE,
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB AUTO_INCREMENT=904608 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

