-- MySQL dump 10.13  Distrib 8.4.10, for Linux (x86_64)
--
-- Host: localhost    Database: takeout
-- ------------------------------------------------------
-- Server version	8.4.10

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
-- Dumping data for table `t_user`
--

LOCK TABLES `t_user` WRITE;
/*!40000 ALTER TABLE `t_user` DISABLE KEYS */;
INSERT INTO `t_user` VALUES (1,'13800000001','管理员',NULL,0,'ADMIN',1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(2,'13800000002','测试商家',NULL,0,'MERCHANT',1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(3,'13800000003','测试用户',NULL,0,'CUSTOMER',1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(4,'13800000004','快乐汉堡商家',NULL,0,'MERCHANT',1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0);
/*!40000 ALTER TABLE `t_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `t_merchant`
--

LOCK TABLES `t_merchant` WRITE;
/*!40000 ALTER TABLE `t_merchant` DISABLE KEYS */;
INSERT INTO `t_merchant` VALUES (1,2,'香辣料理','/images/merchants/spicy-cuisine-logo.jpg','招牌川菜，麻辣鲜香','13900000001','北京市','北京市','朝阳区','朝阳区建国路88号',116.4630000,39.9210000,3.00,20.00,30,1,NULL,NULL,1256,5.0,'2026-07-18 07:39:52','2026-07-22 16:18:55',0),(2,4,'快乐汉堡','/images/merchants/happy-burger-logo.jpg','美式快餐，现做现卖','13900000002','北京市','北京市','海淀区','海淀区中关村大街1号',116.3170000,39.9830000,0.00,15.00,20,1,NULL,NULL,890,4.6,'2026-07-18 07:39:52','2026-07-18 07:39:52',0);
/*!40000 ALTER TABLE `t_merchant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `t_category`
--

LOCK TABLES `t_category` WRITE;
/*!40000 ALTER TABLE `t_category` DISABLE KEYS */;
INSERT INTO `t_category` VALUES (1,1,'主食',1,1,'2026-07-18 07:39:52','2026-07-18 07:39:52'),(2,1,'小炒',2,1,'2026-07-18 07:39:52','2026-07-18 07:39:52'),(3,1,'饮品',3,1,'2026-07-18 07:39:52','2026-07-18 07:39:52'),(4,2,'汉堡套餐',1,1,'2026-07-18 07:39:52','2026-07-18 07:39:52'),(5,2,'炸鸡',2,1,'2026-07-18 07:39:52','2026-07-18 07:39:52');
/*!40000 ALTER TABLE `t_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `t_dish`
--

LOCK TABLES `t_dish` WRITE;
/*!40000 ALTER TABLE `t_dish` DISABLE KEYS */;
INSERT INTO `t_dish` VALUES (1,1,1,'更新后的菜品','/images/dishes/braised-pork-rice.jpg','软糯入味，米饭香浓',29.90,92,364,1,1,'2026-07-18 07:39:52','2026-07-22 16:20:55',0),(2,1,1,'麻婆豆腐饭','/images/dishes/mapo-tofu-rice.jpg','麻辣鲜香，豆腐嫩滑',18.00,100,289,1,2,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(3,1,2,'宫保鸡丁','/images/dishes/kung-pao-chicken.jpg','酸甜微辣，经典川菜',28.00,50,178,1,1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(4,1,3,'冰镇柠檬茶','/images/dishes/iced-lemon-tea.jpg','清爽解腻',8.00,200,445,1,1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0),(5,2,4,'经典双层牛肉堡套餐','/images/dishes/beef-burger.jpg','含薯条+可乐',35.00,50,235,1,1,'2026-07-18 07:39:52','2026-07-18 07:47:50',0),(6,2,5,'香辣炸鸡腿','/images/dishes/fried-chicken.jpg','外酥里嫩，香辣过瘾',16.00,80,568,1,1,'2026-07-18 07:39:52','2026-07-18 07:47:50',0),(2079964410336972802,1,1,'新菜品',NULL,NULL,19.90,999,0,0,0,'2026-07-22 16:18:54','2026-07-22 16:18:54',0);
/*!40000 ALTER TABLE `t_dish` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `t_coupon`
--

LOCK TABLES `t_coupon` WRITE;
/*!40000 ALTER TABLE `t_coupon` DISABLE KEYS */;
INSERT INTO `t_coupon` VALUES (1,'新人专享券',1,20.00,5.00,1000,1,'2026-07-18 07:39:52','2026-08-17 07:39:52',1,'2026-07-18 07:39:52',0),(2,'满30减8',1,30.00,8.00,500,0,'2026-07-18 07:39:52','2026-08-17 07:39:52',1,'2026-07-18 07:39:52',0),(3,'无门槛2元券',1,0.00,2.00,2000,0,'2026-07-18 07:39:52','2026-07-25 07:39:52',1,'2026-07-18 07:39:52',0);
/*!40000 ALTER TABLE `t_coupon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `t_user_address`
--

LOCK TABLES `t_user_address` WRITE;
/*!40000 ALTER TABLE `t_user_address` DISABLE KEYS */;
INSERT INTO `t_user_address` VALUES (1,3,'张三','13800000003','北京市','北京市','朝阳区','朝阳区建国路100号1单元101',116.4650000,39.9200000,1,'2026-07-18 07:39:52','2026-07-18 07:39:52',0);
/*!40000 ALTER TABLE `t_user_address` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-22 16:46:36
