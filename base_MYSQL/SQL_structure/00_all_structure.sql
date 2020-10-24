-- MySQL dump 10.17  Distrib 10.3.21-MariaDB, for Linux ()
--
-- Host: localhost    Database: SolarAnlage
-- ------------------------------------------------------
-- Server version	10.3.21-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `SolarAnlage`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `SolarAnlage` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `SolarAnlage`;

--
-- Table structure for table `BYD_Daten`
--

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
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DWD_Daten`
--

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

--
-- Table structure for table `DWD_Rad_factor`
--

DROP TABLE IF EXISTS `DWD_Rad_factor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DWD_Rad_factor` (
  `month` int(2) NOT NULL,
  `Faktor` decimal(38,22) DEFAULT NULL,
  `LeastSQR` decimal(65,27) DEFAULT NULL,
  PRIMARY KEY (`month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `DWD_SIM_Daten`
--

DROP TABLE IF EXISTS `DWD_SIM_Daten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DWD_SIM_Daten` (
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
  `Rad1wh` decimal(5,1) NOT NULL,
  `Rad1Energy` int(5) NOT NULL,
  `ACSim` int(4) DEFAULT NULL,
  `CellTempSim` int(4) DEFAULT NULL,
  `DCSim` int(4) DEFAULT NULL,
  `VmpSIM` int(3) NOT NULL,
  `ImpSIM` decimal(3,1) NOT NULL,
  PRIMARY KEY (`time_sec`),
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DWD_SIM_Rad_factor`
--

DROP TABLE IF EXISTS `DWD_SIM_Rad_factor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DWD_SIM_Rad_factor` (
  `month` int(2) NOT NULL,
  `Faktor` decimal(38,22) DEFAULT NULL,
  `LeastSQR` decimal(65,27) DEFAULT NULL,
  PRIMARY KEY (`month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `GeldwerterVorteil`
--

DROP TABLE IF EXISTS `GeldwerterVorteil`;
/*!50001 DROP VIEW IF EXISTS `GeldwerterVorteil`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `GeldwerterVorteil` (
  `jahr` tinyint NOT NULL,
  `cent_kWh` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Gewinne_Verlust`
--

DROP TABLE IF EXISTS `Gewinne_Verlust`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Gewinne_Verlust` (
  `time_sec` int(11) NOT NULL,
  `TIMESTAMP` date DEFAULT NULL,
  `Verkauf` decimal(34,5) DEFAULT NULL,
  `Ersparnis` decimal(35,5) DEFAULT NULL,
  `SteuerlGewinn` decimal(37,8) DEFAULT NULL,
  `MWST` decimal(49,5) DEFAULT NULL,
  `BezugKosten` decimal(34,5) DEFAULT NULL,
  `Abschreibung` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`time_sec`),
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Gewinne_Verlust_PVonly`
--

DROP TABLE IF EXISTS `Gewinne_Verlust_PVonly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Gewinne_Verlust_PVonly` (
  `time_sec` int(11) NOT NULL,
  `TIMESTAMP` date DEFAULT NULL,
  `Verkauf` decimal(36,5) DEFAULT NULL,
  `Ersparnis` decimal(34,5) DEFAULT NULL,
  `SteuerlGewinn` decimal(37,8) DEFAULT NULL,
  `MWST` decimal(49,5) DEFAULT NULL,
  `BezugKosten` decimal(35,5) DEFAULT NULL,
  `Abschreibung` decimal(9,5) DEFAULT NULL,
  PRIMARY KEY (`time_sec`),
  UNIQUE KEY `TIMESTAMP` (`TIMESTAMP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `SteuerlGewinnVerlust`
--

DROP TABLE IF EXISTS `SteuerlGewinnVerlust`;
/*!50001 DROP VIEW IF EXISTS `SteuerlGewinnVerlust`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `SteuerlGewinnVerlust` (
  `TIMESTAMP` tinyint NOT NULL,
  `time_sec` tinyint NOT NULL,
  `SteuerlEinnahmen` tinyint NOT NULL,
  `SteuerlAbschr` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `SteuerlGewinnVerlust_PV`
--

DROP TABLE IF EXISTS `SteuerlGewinnVerlust_PV`;
/*!50001 DROP VIEW IF EXISTS `SteuerlGewinnVerlust_PV`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `SteuerlGewinnVerlust_PV` (
  `TIMESTAMP` tinyint NOT NULL,
  `time_sec` tinyint NOT NULL,
  `SteuerlEinnahmen` tinyint NOT NULL,
  `SteuerlAbschr` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Stromkosten`
--

DROP TABLE IF EXISTS `Stromkosten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Stromkosten` (
  `ID` int(2) NOT NULL AUTO_INCREMENT,
  `DATE` date NOT NULL,
  `Valid_UNTIL` date NOT NULL,
  `TYPE` varchar(10) NOT NULL,
  `cent_kWh` decimal(5,2) NOT NULL,
  `Euro_Jahr` decimal(6,3) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WR_Daten`
--

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
) ENGINE=InnoDB AUTO_INCREMENT=903918 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `aggregate_WR_Daten_daily`
--

DROP TABLE IF EXISTS `aggregate_WR_Daten_daily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aggregate_WR_Daten_daily` (
  `time_sec` int(11) NOT NULL,
  `TIMESTAMP` date DEFAULT NULL,
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

--
-- Table structure for table `aggregate_WR_Daten_hourly`
--

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

--
-- Dumping events for database 'SolarAnlage'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `EV01_Aggregate_WR` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`127.0.0.1`*/ /*!50106 EVENT `EV01_Aggregate_WR` ON SCHEDULE EVERY 1 HOUR STARTS '2020-02-02 20:00:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL Agregate_WR() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `EV02_Gewinne_Verlust` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`127.0.0.1`*/ /*!50106 EVENT `EV02_Gewinne_Verlust` ON SCHEDULE EVERY 1 HOUR STARTS '2020-02-02 21:01:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL Gewinne_Verlust() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `EV02_Gewinne_Verluste_PVonly` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`127.0.0.1`*/ /*!50106 EVENT `EV02_Gewinne_Verluste_PVonly` ON SCHEDULE EVERY 1 HOUR STARTS '2020-02-02 21:02:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL Gewinne_Verlust_PVonly() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `EV04_DWD_RAD_FACTOR` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`127.0.0.1`*/ /*!50106 EVENT `EV04_DWD_RAD_FACTOR` ON SCHEDULE EVERY 1 DAY STARTS '2020-02-02 21:04:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL DWD_RAD_FACTOR() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'SolarAnlage'
--
/*!50003 DROP PROCEDURE IF EXISTS `Agregate_WR` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `Agregate_WR`()
    MODIFIES SQL DATA
BEGIN
	replace LOW_PRIORITY into aggregate_WR_Daten_hourly (time_sec,  TIMESTAMP, ChargeCycles, BatTemperature, HomeConsumptionSolar_kWh, HomeConsumptionBat_kWh, HomeConsumptionGrid_kWh, HomeConsumption_kWh, PV_kWh, ac_kWh, BatLaden_kWh, BatLaden_Frei_kWh, BatEntladen_kWh, Einspeisen_kWh, Autarkie)
    select
    round(min(time_sec),-1) as time_sec,
    FROM_UNIXTIME(round(min(time_sec),-1)) as TIMESTAMP,
    max(ChargeCycles) as ChargeCycles,
    round(avg(BatTemperature),6) as BatTemperature,
    round(avg(AktHomeConsumptionSolar)/1000,13) as HomeConsumptionSolar_kWh,
    round(avg(AktHomeConsumptionBat)/1000,13) as HomeConsumptionBat_kWh,
    round(avg(AktHomeConsumptionGrid)/1000,13) as HomeConsumptionGrid_kWh,
    round(avg(AktHomeConsumption)/1000,13) as HomeConsumption_kWh,
    round(avg(dcPowerPV)/1000,13) as PV_kWh,
    round(avg(acPower)/1000,13) as ac_kWh,
    round(avg(BatPowerLaden)/1000,13) as BatLaden_kWh,
    round(avg(BatLaden_Frei)/1000,13) as BatLaden_Frei_kWh,
    round(avg(BatPowerEntLaden)/1000,13) as BatEntladen_kWh,
    round(avg(EinspeisenPower)/1000,13) as Einspeisen_kWh,
    round(1-if(sum(AktHomeConsumption)>0,LEAST(sum(AktHomeConsumptionGrid)/sum(AktHomeConsumption),1),NULL),3) as Autarkie
    FROM WR_Daten
    WHERE DATE(TIMESTAMP) Between SUBDATE(CURRENT_DATE(), INTERVAL 1 DAY) AND CURRENT_DATE()
    Group By to_days(TIMESTAMP),hour(TIMESTAMP)
    Order BY time_sec;

	replace LOW_PRIORITY into aggregate_WR_Daten_daily (time_sec,  TIMESTAMP, ChargeCycles, BatTemperature, HomeConsumptionSolar_kWh, HomeConsumptionBat_kWh, HomeConsumptionGrid_kWh, HomeConsumption_kWh, PV_kWh, ac_kWh, BatLaden_kWh, BatLaden_Frei_kWh, BatEntladen_kWh, Einspeisen_kWh, Autarkie)
    select
    min(time_sec) as time_sec,
    DATE(min(TIMESTAMP)) as TIMESTAMP,
    max(ChargeCycles) as ChargeCycles,
    round(avg(BatTemperature),6) as BatTemperature,
    round(sum(HomeConsumptionSolar_kWh),13) as HomeConsumptionSolar_kWh,
    round(sum(HomeConsumptionBat_kWh),13) as HomeConsumptionBat_kWh,
    round(sum(HomeConsumptionGrid_kWh),13) as HomeConsumptionGrid_kWh,
    round(sum(HomeConsumption_kWh),13) as HomeConsumption_kWh,
    round(sum(PV_kWh),13) as PV_kWh,
    round(sum(ac_kWh),13) as ac_kWh,
    round(sum(BatLaden_kWh),13) as BatLaden_kWh,
    round(sum(BatLaden_Frei_kWh),13) as BatLaden_Frei_kWh,
    round(sum(BatEntladen_kWh),13) as BatEntladen_kWh,
    round(sum(Einspeisen_kWh),13) as Einspeisen_kWh,
    round(1-if(sum(HomeConsumption_kWh)>0,LEAST(sum(HomeConsumptionGrid_kWh)/sum(HomeConsumption_kWh),1),NULL),3) as Autarkie
    FROM aggregate_WR_Daten_hourly
    WHERE DATE(TIMESTAMP) Between SUBDATE(CURRENT_DATE(), INTERVAL 1 DAY) AND CURRENT_DATE()
    Group By to_days(TIMESTAMP)
    Order BY time_sec;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `DWD_RAD_FACTOR` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `DWD_RAD_FACTOR`()
    MODIFIES SQL DATA
BEGIN

    replace LOW_PRIORITY into DWD_Rad_factor (month, Faktor, LeastSQR) select 
    T2.month as month,
    T2.factor as Faktor,
    if (T2.N>15, (T2.N * T2.Sum_XY - T2.Sum_X * T2.Sum_Y)/(T2.N * T2.Sum_X2 - T2.Sum_X * T2.Sum_X),T2.factor) as LeastSQR
    from (
        select
        count(*) as N,
        sum(T1.value * T1.Rad) as SUM_XY,
        sum(T1.Rad) as SUM_X,
        sum(T1.value) as SUM_Y,
        sum(T1.Rad * T1.Rad) as SUM_X2,
        month(T1.time) AS month,
        avg(T1.value / T1.Rad) AS factor 
        from (
            select 
            aggregate_WR_Daten_hourly.TIMESTAMP AS time,
            'PV Power' AS metric,
            aggregate_WR_Daten_hourly.PV_kWh*1000 AS value,
            DWD_Daten.Rad1h / 3.6 * 37.65 * 0.187 AS Rad
            from (aggregate_WR_Daten_hourly
                join DWD_Daten on ( TIMESTAMPADD(HOUR,1,aggregate_WR_Daten_hourly.TIMESTAMP) = DWD_Daten.TIMESTAMP))
            where aggregate_WR_Daten_hourly.time_sec >= (select DWD_Daten.time_sec from DWD_Daten order by DWD_Daten.time_sec limit 1) - 3601 and month(aggregate_WR_Daten_hourly.TIMESTAMP) = month(CURRENT_DATE())) T1
        where T1.Rad > 0 AND T1.value > 0
        group by month(T1.time)) T2;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `DWD_SIM_FACTOR_Quality` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `DWD_SIM_FACTOR_Quality`()
    READS SQL DATA
select
T2.time_sec as time_sec,
T2.DCSim/T2.N as DCSim,
T2.LeastSQR/T2.N as LeastSQR,
T2.Faktor/T2.N as Faktor
from(
	select
	T1.time_sec as time_sec,
	count(*) as N,
	sum(pow(T1.DCPower - T1.DCSim,2)/T1.DCPower) as DCSim,
	sum(pow(T1.DCPower - T1.LeastSQR,2)/T1.DCPower) as LeastSQR,
	sum(pow(T1.DCPower - T1.Faktor,2)/T1.DCPower) as Faktor
	from (
		select 
		aggregate_WR_Daten_hourly.time_sec AS time_sec,
		aggregate_WR_Daten_hourly.PV_kWh*1000 AS DCPower,
		DWD_SIM_Daten.DCSim AS DCSim,
		DWD_SIM_Daten.Rad1Energy * DWD_Rad_factor.LeastSQR AS LeastSQR,
		DWD_SIM_Daten.Rad1Energy * DWD_Rad_factor.Faktor AS Faktor
		from (aggregate_WR_Daten_hourly
			join DWD_SIM_Daten on ( TIMESTAMPADD(HOUR,1,aggregate_WR_Daten_hourly.TIMESTAMP) = DWD_SIM_Daten.TIMESTAMP)
			join DWD_Rad_factor on ( DWD_Rad_factor.month = month(DWD_SIM_Daten.TIMESTAMP))
			)
		where DWD_SIM_Daten.Rad1wh > 0 and aggregate_WR_Daten_hourly.time_sec >= (select DWD_SIM_Daten.time_sec from DWD_SIM_Daten order by DWD_SIM_Daten.time_sec limit 1) - 3601) T1
	where T1.DCPower > 0
) T2 ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Gewinne_Verlust` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `Gewinne_Verlust`()
    MODIFIES SQL DATA
BEGIN

    drop table if exists Gewinne_Verlust;

    create table Gewinne_Verlust as select
    T1.time_sec AS time_sec,T1.TIMESTAMP AS TIMESTAMP,
    round(sum(T1.Einspeisen_kWh * T1.verkauf_cent_kWh) / 100,5) AS Verkauf,
    round(sum((T1.HomeConsumptionSolar_kWh + T1.HomeConsumptionBat_kWh) * Stromkosten.cent_kWh) / 100,5) AS Ersparnis,
    round(sum(T1.ac_kWh * T1.verkauf_cent_kWh) / 100,8) AS SteuerlGewinn,
    round(sum((T1.HomeConsumptionSolar_kWh + T1.HomeConsumptionBat_kWh) * T1.geldwv_cent_kWh) / 100 * 0.19,5) AS MWST,
    round(sum(T1.HomeConsumptionGrid_kWh * Stromkosten.cent_kWh) / 100,5) AS BezugKosten,
    SteuerlGewinnVerlust.SteuerlAbschr AS Abschreibung
    from (
        select
        aggregate_WR_Daten_daily.time_sec AS time_sec,
        aggregate_WR_Daten_daily.TIMESTAMP AS TIMESTAMP,
        aggregate_WR_Daten_daily.Einspeisen_kWh AS Einspeisen_kWh,
        aggregate_WR_Daten_daily.ac_kWh AS ac_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionSolar_kWh AS HomeConsumptionSolar_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionBat_kWh AS HomeConsumptionBat_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionGrid_kWh AS HomeConsumptionGrid_kWh,
        Stromkosten.cent_kWh AS verkauf_cent_kWh,
        GeldwerterVorteil.cent_kWh AS geldwv_cent_kWh
        from ((
            aggregate_WR_Daten_daily
            left join Stromkosten on(DATE(aggregate_WR_Daten_daily.TIMESTAMP) >= Stromkosten.DATE and DATE(aggregate_WR_Daten_daily.TIMESTAMP) <= Stromkosten.Valid_UNTIL))
            left join GeldwerterVorteil on (year(aggregate_WR_Daten_daily.TIMESTAMP) = GeldwerterVorteil.jahr))
        where Stromkosten.TYPE = 'Verkauf') T1
        left join Stromkosten on (DATE(T1.TIMESTAMP) >= Stromkosten.DATE and DATE(T1.TIMESTAMP) <= Stromkosten.Valid_UNTIL)
        left join SteuerlGewinnVerlust on T1.TIMESTAMP=date(SteuerlGewinnVerlust.TIMESTAMP)
    where Stromkosten.TYPE = 'Bezug'
    group by to_days(T1.TIMESTAMP);

ALTER TABLE Gewinne_Verlust ADD PRIMARY KEY (`time_sec`);
ALTER TABLE Gewinne_Verlust ADD UNIQUE(`TIMESTAMP`);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Gewinne_Verlust_PVonly` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `Gewinne_Verlust_PVonly`()
    MODIFIES SQL DATA
BEGIN

    drop table if exists Gewinne_Verlust_PVonly;
    create table Gewinne_Verlust_PVonly as select 
    T1.time_sec AS time_sec,T1.TIMESTAMP AS TIMESTAMP,
    round(sum((T1.Einspeisen_kWh + T1.HomeConsumptionBat_kWh - if(T1.BatLaden_Frei_kWh is not NULL,(T1.BatLaden_Frei_kWh)*0.90,0)) * T1.verkauf_cent_kWh) / 100,5) AS Verkauf,
    round(sum(T1.HomeConsumptionSolar_kWh * Stromkosten.cent_kWh) / 100,5) AS Ersparnis,
    round(sum(T1.ac_kWh * T1.verkauf_cent_kWh) / 100,8) AS SteuerlGewinn,
    round(sum(T1.HomeConsumptionSolar_kWh * T1.geldwv_cent_kWh) / 100 * 0.19,5) AS MWST,
    round(sum((T1.HomeConsumptionGrid_kWh + T1.HomeConsumptionBat_kWh) * Stromkosten.cent_kWh) / 100,5) AS BezugKosten,
    round(SteuerlGewinnVerlust_PV.SteuerlAbschr,5) AS Abschreibung
    from (
        select
        aggregate_WR_Daten_daily.time_sec AS time_sec,
        aggregate_WR_Daten_daily.TIMESTAMP AS TIMESTAMP,
        aggregate_WR_Daten_daily.Einspeisen_kWh AS Einspeisen_kWh,
        aggregate_WR_Daten_daily.ac_kWh AS ac_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionSolar_kWh AS HomeConsumptionSolar_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionBat_kWh AS HomeConsumptionBat_kWh,
        aggregate_WR_Daten_daily.HomeConsumptionGrid_kWh AS HomeConsumptionGrid_kWh,
        aggregate_WR_Daten_daily.BatLaden_Frei_kWh AS BatLaden_Frei_kWh,
        Stromkosten.cent_kWh AS verkauf_cent_kWh,
        GeldwerterVorteil.cent_kWh AS geldwv_cent_kWh
        from ((
            aggregate_WR_Daten_daily
            left join Stromkosten on(aggregate_WR_Daten_daily.TIMESTAMP >= Stromkosten.DATE and aggregate_WR_Daten_daily.TIMESTAMP <= Stromkosten.Valid_UNTIL))
            left join GeldwerterVorteil on (year(aggregate_WR_Daten_daily.TIMESTAMP) = GeldwerterVorteil.jahr))
        where Stromkosten.TYPE = 'Verkauf') T1
        left join Stromkosten on (T1.TIMESTAMP >= Stromkosten.DATE and T1.TIMESTAMP <= Stromkosten.Valid_UNTIL)
        left join SteuerlGewinnVerlust_PV on T1.TIMESTAMP=date(SteuerlGewinnVerlust_PV.TIMESTAMP)
    where Stromkosten.TYPE = 'Bezug'
    group by to_days(T1.TIMESTAMP)
    Order by TIMESTAMP ASC;
ALTER TABLE Gewinne_Verlust_PVonly ADD PRIMARY KEY (`time_sec`);
ALTER TABLE Gewinne_Verlust_PVonly ADD UNIQUE(`TIMESTAMP`);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `SolarAnlage`
--

USE `SolarAnlage`;

--
-- Final view structure for view `GeldwerterVorteil`
--

/*!50001 DROP TABLE IF EXISTS `GeldwerterVorteil`*/;
/*!50001 DROP VIEW IF EXISTS `GeldwerterVorteil`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`127.0.0.1` SQL SECURITY DEFINER */
/*!50001 VIEW `GeldwerterVorteil` AS select year(`aggregate_WR_Daten_daily`.`TIMESTAMP`) AS `jahr`,round(sum(`aggregate_WR_Daten_daily`.`HomeConsumption_kWh` * `Stromkosten`.`cent_kWh` + `Stromkosten`.`Euro_Jahr` / 3.65) / sum(`aggregate_WR_Daten_daily`.`HomeConsumption_kWh`) / 1.19,2) AS `cent_kWh` from (`aggregate_WR_Daten_daily` left join `Stromkosten` on(`aggregate_WR_Daten_daily`.`TIMESTAMP` >= `Stromkosten`.`DATE` and `aggregate_WR_Daten_daily`.`TIMESTAMP` <= `Stromkosten`.`Valid_UNTIL`)) where `Stromkosten`.`TYPE` = 'Bezug' group by year(`aggregate_WR_Daten_daily`.`TIMESTAMP`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `SteuerlGewinnVerlust`
--

/*!50001 DROP TABLE IF EXISTS `SteuerlGewinnVerlust`*/;
/*!50001 DROP VIEW IF EXISTS `SteuerlGewinnVerlust`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`127.0.0.1` SQL SECURITY DEFINER */
/*!50001 VIEW `SteuerlGewinnVerlust` AS select `T1`.`TIMESTAMP` AS `TIMESTAMP`,`T1`.`time_sec` AS `time_sec`,round(`T1`.`acPower` * `T1`.`verkauf_cent_kWh` / 100,8) AS `SteuerlEinnahmen`,round(`SolarAnlage`.`Stromkosten`.`Euro_Jahr` / 365,8) AS `SteuerlAbschr` from (((select `SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` AS `TIMESTAMP`,`SolarAnlage`.`aggregate_WR_Daten_daily`.`time_sec` AS `time_sec`,`SolarAnlage`.`aggregate_WR_Daten_daily`.`ac_kWh` AS `acPower`,`SolarAnlage`.`Stromkosten`.`cent_kWh` AS `verkauf_cent_kWh` from (`SolarAnlage`.`aggregate_WR_Daten_daily` left join `SolarAnlage`.`Stromkosten` on(`SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` >= `SolarAnlage`.`Stromkosten`.`DATE` and `SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` <= `SolarAnlage`.`Stromkosten`.`Valid_UNTIL`)) where `SolarAnlage`.`Stromkosten`.`TYPE` = 'Verkauf')) `T1` left join `SolarAnlage`.`Stromkosten` on(`T1`.`TIMESTAMP` >= `SolarAnlage`.`Stromkosten`.`DATE` and `T1`.`TIMESTAMP` <= `SolarAnlage`.`Stromkosten`.`Valid_UNTIL`)) where `SolarAnlage`.`Stromkosten`.`TYPE` = 'Abschreib' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `SteuerlGewinnVerlust_PV`
--

/*!50001 DROP TABLE IF EXISTS `SteuerlGewinnVerlust_PV`*/;
/*!50001 DROP VIEW IF EXISTS `SteuerlGewinnVerlust_PV`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`127.0.0.1` SQL SECURITY DEFINER */
/*!50001 VIEW `SteuerlGewinnVerlust_PV` AS select `T1`.`TIMESTAMP` AS `TIMESTAMP`,`T1`.`time_sec` AS `time_sec`,round(`T1`.`acPower` * `T1`.`verkauf_cent_kWh` / 100,8) AS `SteuerlEinnahmen`,round(`SolarAnlage`.`Stromkosten`.`Euro_Jahr` / 365,8) AS `SteuerlAbschr` from (((select `SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` AS `TIMESTAMP`,`SolarAnlage`.`aggregate_WR_Daten_daily`.`time_sec` AS `time_sec`,`SolarAnlage`.`aggregate_WR_Daten_daily`.`ac_kWh` AS `acPower`,`SolarAnlage`.`Stromkosten`.`cent_kWh` AS `verkauf_cent_kWh` from (`SolarAnlage`.`aggregate_WR_Daten_daily` left join `SolarAnlage`.`Stromkosten` on(`SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` >= `SolarAnlage`.`Stromkosten`.`DATE` and `SolarAnlage`.`aggregate_WR_Daten_daily`.`TIMESTAMP` <= `SolarAnlage`.`Stromkosten`.`Valid_UNTIL`)) where `SolarAnlage`.`Stromkosten`.`TYPE` = 'Verkauf')) `T1` left join `SolarAnlage`.`Stromkosten` on(`T1`.`TIMESTAMP` >= `SolarAnlage`.`Stromkosten`.`DATE` and `T1`.`TIMESTAMP` <= `SolarAnlage`.`Stromkosten`.`Valid_UNTIL`)) where `SolarAnlage`.`Stromkosten`.`TYPE` = 'AbschrPV' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-10-24  1:02:37
