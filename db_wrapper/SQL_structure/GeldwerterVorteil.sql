
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
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

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

