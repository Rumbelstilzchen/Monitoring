
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
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

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

