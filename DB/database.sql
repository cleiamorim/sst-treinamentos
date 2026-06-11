-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: inf07sst
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dimfuncionarios`
--

DROP TABLE IF EXISTS `dimfuncionarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dimfuncionarios` (
  `id_funcionario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `cpf` varchar(14) NOT NULL,
  `cargo` varchar(50) DEFAULT NULL,
  `setor` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `whatsapp` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_funcionario`),
  UNIQUE KEY `cpf` (`cpf`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dimfuncionarios`
--

/*!40000 ALTER TABLE `dimfuncionarios` DISABLE KEYS */;
INSERT INTO `dimfuncionarios` VALUES (12,'Ricardo Amorim','123.416.789-00','Consultor dados','DBA',NULL,NULL,NULL),(13,'Cleidson Amorim','000.000.111-00','Especialista em dados Fullstack','Data Science',NULL,NULL,NULL);
/*!40000 ALTER TABLE `dimfuncionarios` ENABLE KEYS */;

--
-- Table structure for table `dimtreinamentos`
--

DROP TABLE IF EXISTS `dimtreinamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dimtreinamentos` (
  `id_treinamento` int NOT NULL AUTO_INCREMENT,
  `nome_treinamento` varchar(100) NOT NULL,
  `validade_meses` int NOT NULL,
  PRIMARY KEY (`id_treinamento`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dimtreinamentos`
--

/*!40000 ALTER TABLE `dimtreinamentos` DISABLE KEYS */;
INSERT INTO `dimtreinamentos` VALUES (6,'NR-35 Trabalho em Altura',36),(7,'NR-06 - Treinamento de EPIs',12);
/*!40000 ALTER TABLE `dimtreinamentos` ENABLE KEYS */;

--
-- Table structure for table `factregistros`
--

DROP TABLE IF EXISTS `factregistros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factregistros` (
  `id_registro` int NOT NULL AUTO_INCREMENT,
  `id_funcionario` int NOT NULL,
  `id_treinamento` int NOT NULL,
  `data_realizacao` date NOT NULL,
  `status` varchar(20) DEFAULT 'Ativo',
  `data_vencimento` date DEFAULT NULL,
  PRIMARY KEY (`id_registro`),
  KEY `id_funcionario` (`id_funcionario`),
  KEY `id_treinamento` (`id_treinamento`),
  CONSTRAINT `factregistros_ibfk_1` FOREIGN KEY (`id_funcionario`) REFERENCES `dimfuncionarios` (`id_funcionario`) ON DELETE CASCADE,
  CONSTRAINT `factregistros_ibfk_2` FOREIGN KEY (`id_treinamento`) REFERENCES `dimtreinamentos` (`id_treinamento`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factregistros`
--

/*!40000 ALTER TABLE `factregistros` DISABLE KEYS */;
INSERT INTO `factregistros` VALUES (1,13,6,'2026-06-11','Ativo','2027-06-11'),(5,12,6,'2026-06-11','Ativo','2027-06-11'),(7,12,6,'2026-06-11','Concluído','2027-06-11');
/*!40000 ALTER TABLE `factregistros` ENABLE KEYS */;

--
-- Dumping routines for database 'inf07sst'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-11 17:48:30
