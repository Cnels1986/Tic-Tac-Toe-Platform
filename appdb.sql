CREATE DATABASE appdb;
USE appdb;
DROP TABLE IF EXISTS `login`;
DROP TABLE IF EXISTS `stats`;


-- table that will store the login information (username and password)
CREATE TABLE `Users` (
  `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
  `userName` varchar(45) NOT NULL UNIQUE,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;


-- table that will store all of the stat information, and be linked to the login table through the id
CREATE TABLE `Stats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL UNIQUE,
  `name` varchar(45) NOT NULL,
  `wins` int(11) NOT NULL,
  `losses` int(11) NOT NULL,
  `winStreak` int(11) NOT NULL,
  `lossStreak` int(11) NOT NULL,
  PRIMARY KEY(`id`),
  FOREIGN KEY (`user_id`) REFERENCES Users(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
