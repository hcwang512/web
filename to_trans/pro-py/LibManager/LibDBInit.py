#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3

def LibDbInit(con):
    c = con.cursor()

    c.execute("""
    CREATE TABLE `books` (
    `BookID` INTEGER PRIMARY KEY,
    `BookName` TEXT ,
    `BookAuthor` TEXT ,
    `BookPublish` TEXT ,
    `BookPrice` FLOAT ,
    `BookDate` TEXT ,
    `BookType` TEXT ,
    `BookContent` TEXT ,
    `BookState` INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE `reader` (
    `ReaderID` INTEGER PRIMARY KEY,
    `ReaderName` TEXT ,
    `ReaderSchool` TEXT ,
    `ReaderInfo` TEXT
    )
    """)

    c.execute("""
    CREATE TABLE `borrows` (
    `BorrowID` INTEGER PRIMARY KEY,
    `ReaderID` INTEGER ,
    `BookID` INTEGER ,
    `BookName` TEXT,
    `BorrowDate` TEXT,
    `AdminName` TEXT
    )
    """)

    c.execute("""
        CREATE TABLE `admin`(
        `AdminID` INTEGER PRIMARY KEY,
        `AdminPassword` INTEGER,
        `AdminName` TEXT,
        `AdminAdd` TEXT
        )
        """)

    books = ((1, u"C语言程序设计", u"谭浩强", u"教育出版社", 29.90, u"2009-04-30", u"计算机", u"", 5),
    (2, u"数据结构", u"谭浩强", u"教育出版社", 29.90, u"2009-04-30", u"计算机", u"", 5),
    (3, u"数据库原理", u"tanhaoqiang", u"教育出版社", 29.90, u"2009-04-30", u"计算机", u"", 5),
    (4, u"汇编语言", u"谭浩强", u"教育出版社", 29.90, u"2009-04-30", u"计算机", u"", 5),
    (5, u"大学国文", u"国立", u"教育出版社", 19.90, u"2009-04-30", u"文学", u"", 5),
    (6, u"古代诗词", u"国立", u"教育出版社", 19.90, u"2009-04-30", u"文学", u"", 5),
    (7, u"广州地图", u"工作", u"广州出版社", 9.90, u"2009-04-30", u"工具书", u"", 5),
    (8, u"牛津词典", u"词典", u"广州出版社", 9.90, u"2009-04-30", u"工具书", u"", 5))

    for r in books:
        c.execute("INSERT INTO books VALUES (?,?,?,?,?,?,?,?,?)", r)

    readers = ((1001, u"陈一", u"浙江大学计算机学院", u"B15"),
    (1002, u"王二", u"浙江大学计算机学院", u"B15"),
    (1003, u"刘三", u"浙江大学美术学院", u"B12"),
    (1004, u"陈一明", u"浙江大学人文学院", u"B10"),
    (1005, u"张三", u"浙江大学人文学院", u"B5"),
    (1006, u"何明", u"浙江大学土木工程学院", u"B22"),
    (1007, u"陈中", u"浙江大学数学学院", u"B24"),
    (1008, u"黄六", u"浙江大学体育学院", u"B25"))

    for r in readers:
        c.execute("INSERT INTO reader VALUES (?,?,?,?)", r)

    borrows = ((1, 1001, 1, u"c语言程序设计",u"2009-04-20",  u"chenhua"),
    (2, 1001, 2, u"数据结构", u"2009-04-20", u"chenhua"),
    (3, 1002, 3, u"数据库原理", u"2009-04-20", u"chenhua"),
    (4, 1003, 5, u"大学国文", u"2009-04-20", u"chenhua"),
    (5, 1004, 4, u"汇编语言", u"2009-04-20", u"chenhua"),
    (6, 1004, 2, u"数据结构", u"2009-04-20", u"chenhua"),
    (7, 1003, 7, u"广州地图", u"2009-04-20", u"chenhua"),
    (8, 1006, 8, u"牛津词典", u"2009-04-20", u"chenhua"),
    (9, 1007, 2, u"数据结构", u"2009-04-20", u"chenhua"),
    (10, 1008, 8, u"牛津词典", u"2009-04-20", u"chenhua"))

    for r in borrows:
        c.execute(u"INSERT INTO borrows VALUES (?,?,?,?,?,?)", r)

    admins = ((123, 123, u"chenhua", u"8377839"), (234, 234, u"lijing", u"3875894"))

    for ad in admins:
        c.execute(u"INSERT INTO admin VALUES (?, ?, ?, ?)", ad)

     Save (commit) the changes
    con.commit()

if __name__ == "__main__":
    LibDbInit(sqlite3.connect('sqlitefile.db'))


