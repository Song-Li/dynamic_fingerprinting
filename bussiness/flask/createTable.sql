-- MySQL dump 10.13  Distrib 5.7.20, for Linux (x86_64)
--
-- Host: localhost    Database: uniquemachine
-- ------------------------------------------------------
-- Server version	5.7.20-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cookies`
--

DROP TABLE IF EXISTS `cookies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cookies` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `cookie` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cookies`
--

LOCK TABLES `cookies` WRITE;
/*!40000 ALTER TABLE `cookies` DISABLE KEYS */;
/*!40000 ALTER TABLE `cookies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `features`
--

DROP TABLE IF EXISTS `features`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `features` (
  `IP` varchar(32) DEFAULT NULL,
  `inc` text,
  `httpheaders` text,
  `gpu` text,
  `timezone` int(11) DEFAULT NULL,
  `resolution` text,
  `plugins` text,
  `cookie` text,
  `localstorage` text,
  `gpuimgs` text,
  `adblock` text,
  `cpucores` int(11) DEFAULT NULL,
  `canvastest` text,
  `audio` text,
  `langsdetected` text,
  `agent` text,
  `accept` text,
  `encoding` text,
  `language` text,
  `jsFonts` text,
  `WebGL` text,
  `browserfingerprint` text,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `label` text,
  `ccaudio` text,
  `hybridaudio` text,
  `clientid` text,
  `touchSupport` text,
  `doNotTrack` text,
  `uniquelabel` varchar(64) DEFAULT NULL,
  `fp2_colordepth` text,
  `fp2_sessionstorage` text,
  `fp2_indexdb` text,
  `fp2_addbehavior` text,
  `fp2_opendatabase` text,
  `fp2_cpuclass` text,
  `fp2_pixelratio` text,
  `fp2_liedlanguages` text,
  `fp2_liedresolution` text,
  `fp2_liedos` text,
  `fp2_liedbrowser` text,
  `fp2_webgl` text,
  `fp2_webglvendoe` text,
  `fp2_platform` text,
  `iplocation` text,
  KEY `uniquelabel` (`uniquelabel`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `features`
--

LOCK TABLES `features` WRITE;
/*!40000 ALTER TABLE `features` DISABLE KEYS */;
/*!40000 ALTER TABLE `features` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pictures`
--

DROP TABLE IF EXISTS `pictures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pictures` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `dataurl` longblob NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pictures`
--

LOCK TABLES `pictures` WRITE;
/*!40000 ALTER TABLE `pictures` DISABLE KEYS */;
/*!40000 ALTER TABLE `pictures` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-28 17:44:42
