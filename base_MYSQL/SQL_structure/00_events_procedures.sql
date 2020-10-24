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
/*!50106 DROP EVENT IF EXISTS `EV04_DWD_SIM_RAD_FACTOR` */;;
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
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`127.0.0.1`*/ /*!50106 EVENT `EV04_DWD_SIM_RAD_FACTOR` ON SCHEDULE EVERY 1 DAY STARTS '2020-02-02 21:04:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL DWD_SIM_RAD_FACTOR() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;
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
    round(avg(AktHomeConsumptionSolar)/1000,14) as HomeConsumptionSolar_kWh,
    round(avg(AktHomeConsumptionBat)/1000,14) as HomeConsumptionBat_kWh,
    round(avg(AktHomeConsumptionGrid)/1000,14) as HomeConsumptionGrid_kWh,
    round(avg(AktHomeConsumption)/1000,14) as HomeConsumption_kWh,
    round(avg(dcPowerPV)/1000,14) as PV_kWh,
    round(avg(acPower)/1000,14) as ac_kWh,
    round(avg(BatPowerLaden)/1000,14) as BatLaden_kWh,
    round(avg(BatLaden_Frei)/1000,14) as BatLaden_Frei_kWh,
    round(avg(BatPowerEntLaden)/1000,14) as BatEntladen_kWh,
    round(avg(EinspeisenPower)/1000,14) as Einspeisen_kWh,
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
    round(sum(HomeConsumptionSolar_kWh),14) as HomeConsumptionSolar_kWh,
    round(sum(HomeConsumptionBat_kWh),14) as HomeConsumptionBat_kWh,
    round(sum(HomeConsumptionGrid_kWh),14) as HomeConsumptionGrid_kWh,
    round(sum(HomeConsumption_kWh),14) as HomeConsumption_kWh,
    round(sum(PV_kWh),14) as PV_kWh,
    round(sum(ac_kWh),14) as ac_kWh,
    round(sum(BatLaden_kWh),14) as BatLaden_kWh,
    round(sum(BatLaden_Frei_kWh),14) as BatLaden_Frei_kWh,
    round(sum(BatEntladen_kWh),14) as BatEntladen_kWh,
    round(sum(Einspeisen_kWh),14) as Einspeisen_kWh,
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
/*!50003 DROP PROCEDURE IF EXISTS `DWD_SIM_RAD_FACTOR` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE `DWD_SIM_RAD_FACTOR`()
    MODIFIES SQL DATA
BEGIN

	replace LOW_PRIORITY into DWD_SIM_Rad_factor (month, Faktor, LeastSQR) select 
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
			aggregate_WR_Daten_hourly.PV_kWh*1000 AS value,
			DWD_SIM_Daten.Rad1Energy AS Rad
			from (aggregate_WR_Daten_hourly
				join DWD_SIM_Daten on ( TIMESTAMPADD(HOUR,1,aggregate_WR_Daten_hourly.TIMESTAMP) = DWD_SIM_Daten.TIMESTAMP))
			where aggregate_WR_Daten_hourly.time_sec >= (select DWD_SIM_Daten.time_sec from DWD_SIM_Daten order by DWD_SIM_Daten.time_sec limit 1) - 3601 and month(aggregate_WR_Daten_hourly.TIMESTAMP) = month(CURRENT_DATE())) T1
		where T1.Rad > 0 AND T1.value > 0
		group by month(T1.time)) T2;

END ;;
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
