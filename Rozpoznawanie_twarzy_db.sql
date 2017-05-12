-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Czas generowania: 12 Maj 2017, 23:15
-- Wersja serwera: 5.5.54-0+deb8u1
-- Wersja PHP: 5.6.30-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Baza danych: `Rozpoznawanie_twarzy_db`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `Osoby`
--

CREATE TABLE IF NOT EXISTS `Osoby` (
  `LABEL` int(11) NOT NULL,
  `NAME` varchar(40) CHARACTER SET utf8 COLLATE utf8_polish_ci NOT NULL,
  `SURNAME` varchar(50) CHARACTER SET utf8 COLLATE utf8_polish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Zrzut danych tabeli `Osoby`
--

INSERT INTO `Osoby` (`LABEL`, `NAME`, `SURNAME`) VALUES
(1, 'Damian', 'Filipowicz'),
(2, 'Maciej', 'Marciniak'),
(3, 'Ktoś', 'Tam');

--
-- Indeksy dla zrzutów tabel
--

--
-- Indexes for table `Osoby`
--
ALTER TABLE `Osoby`
 ADD PRIMARY KEY (`LABEL`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
