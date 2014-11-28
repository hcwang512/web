#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#使用数据库sqlite3
import sqlite3
import time
#日期和时间
import datetime

reload(sys)

sys.setdefaultencoding('utf-8')


#构建类，并且设置UI框架
class LibManager:
    #以元组来定义书籍、读者信息
    bookColumName = (u"书本号", u"书名", u"作者", u"出版社",
                    u"价格", u"购入日期", u"分类", u"简介",   u"馆藏数")

    readerColumName = (u"读者号", u"读者姓名", u"读者身份", u"备注")

    adminColumName = (u"ID", u"密码", u"姓名", u"联系方式")

    



    def __init__(self):
        #连接数据库
        self.dbconn = sqlite3.connect('sqlitefile.db')
        #创建游标，以游标来控制数据库操作
        self.cursor = self.dbconn.cursor()

        self.nowDate = time.strftime("%Y-%m-%d")
        self.time_now = time.strftime('%Y-%m-%d',time.localtime(time.time()))



    def book_input(self):
        #print "ok , function"
        while(True):
            book_choice = int (raw_input("数字选择:\n1.单本入库\t2.批量入库\t3.退出\n"))
            if book_choice == 1:
                print "请按照书号,书名,作者,出版社,价格,购入日期,分类,简介,馆藏数的顺序输入\n"
                data_raw = []
                for book_colum in range(len(self.bookColumName)):
                    data_raw.append(raw_input("请输入:\t"))
                self.cursor.execute(u"INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",\
                                    data_raw)
                print "输入成功\n"
            elif book_choice == 2:
                your_doc = raw_input(u"输入文件地址:\t")
                for line in open(your_doc):
                    
                    self.cursor.execute(u"INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",\
                                    line.split(',', 8))
            elif book_choice == 3:
                print "退出至主页面\n"
                return 1
            else:
                print "错误输入,请再次尝试\n"
            self.dbconn.commit()

    def book_search(self):
        while(True):
            search_order = 2
            book_index = ["BookID", "BookName", "BookAuthor", "BookPublish", "BookPrice", "BookDate", "BookType"]
            search_choice = input("你想搜什么?请选择数字\n1.类别\t2.书名\t3.出版社\t4.作者\t5.年份\t6.价格\t7.所有书\t8.退出\n")
            search_order = input("你想按什么排序?请选择数字\n1.书号\t2.书名\t3.作者\t4.出版社\t5.价格\t6.时间\t7.类型\n")
            if(search_choice == 1):
                your_search = unicode(raw_input("输入书籍类别\n"))
                self.cursor.execute(u"SELECT * FROM books WHERE BookType = %s ORDER BY %s" % (your_search.encode('utf-8'), book_index[search_order - 1]))

            elif(search_choice == 2):
                your_search = (raw_input("输入书名\n"))
                self.cursor.execute(u"SELECT * FROM books WHERE BookName = %s ORDER BY %s" % (your_search, book_index[search_order - 1]))
            elif(search_choice == 3):
                your_search = (raw_input("输入出版社名字\n"))
                self.cursor.execute(u"SELECT * FROM books WHERE BookPublish = %s ORDER BY %s" % (your_search, book_index[search_order - 1]))
            elif(search_choice == 4):
                your_search = raw_input(u"输入作者名字\n")
                self.cursor.execute(u"SELECT * FROM books WHERE BookAuthor = %s ORDER BY %s" % (your_search.decode('utf-8'), book_index[search_order - 1]))
            elif(search_choice == 5):
                year_min = input("输入起始年份\n")
                year_max = input("输入最大年份\n")
                self.cursor.execute(u"SELECT * FROM books WHERE BookDate >= %s AND BookDate <= %s ORDER BY %s" % (year_min, year_max, book_index[search_order - 1]))
            elif(search_choice == 6):
                price_min = input("输入最低价格\n")
                price_max = input("输入最高价格\n")
                self.cursor.execute(u"SELECT * FROM books WHERE BookPrice >= %s AND BookPrice <= %s ORDER BY %s" % (price_min, price_max, book_index[search_order - 1]))
            elif search_choice == 7:
                self.cursor.execute(u"SELECT * FROM books ORDER BY %s" %  book_index[search_order - 1])
            elif search_choice == 8:
                return 1
            else:
                print "错误输入,请再次尝试\n"
            #查询结果输出
            search_result = self.cursor.fetchall()
            for every in search_result:
                for one in every:
                    if one.__class__ == str:
                        print one.decode('utf-8') ,
                    else:
                        print one,
                print "\n"
            print "搜索成功\n"

    def book_borrow(self):
        while(True):
            borrow_choice = input("输入你的选择:\t1.输入借书证卡号\t2.输入书号\t3.退出\n")
            if borrow_choice == 1:
                borrow_ID = input("输入你的借书证卡号\n")
                self.cursor.execute(u"SELECT * FROM borrows WHERE ReaderID = %d " % borrow_ID)
                borrow_result = self.cursor.fetchall()
                for every in borrow_result:
                    for one in every:
                        if one.__class__ == str:
                            print one.decode('utf-8') ,
                        else:
                            print one,
                    print "\n"
            elif borrow_choice == 2:
                book_ID = input("输入书号\n")
                borrow_ID_2 = input("输入借书证卡号\n")
                self.cursor.execute(u"SELECT BookState FROM books WHERE BookID = %d" % book_ID)
                book_state = self.cursor.fetchone()
                for book_num in book_state:
                    if(int(book_num) == 0):
                        print "库存中没有书,借书失败\n"
                    elif(int(book_num) > 0):
                        print "借书成功\n"
                        self.cursor.execute(u"UPDATE books SET BookState = BookState - 1 WHERE BookID = %d" % book_ID)
                        print "库存减少1\n"
                        self.cursor.execute(u"SELECT BookName FROM books WHERE BookID = %d" % book_ID)
                        book_na = self.cursor.fetchone()
                        book_name = book_na[0].decode('utf-8')
                        self.time_now_uni = unicode(self.time_now)
                        no = u'None'
                        borrow_data = [borrow_ID_2, book_ID, book_name, self.time_now_uni, no]
                        
                        self.cursor.execute("INSERT INTO borrows VALUES  (NULL, ?, ?, ?, ?, ?)",  [r for r in borrow_data])
                        self.dbconn.commit()
                    else:
                        print "请再次尝试\n"
            else:
                return 1

    def book_return(self):
        while(True):
            return_choice = input("输入数字选择:\t1.借书证卡号\t2.书号\t3.退出至主页面\n")
            if return_choice == 1:
                borrow_ID_1 = input("输入你的借书证卡号\n")
                self.cursor.execute(u"SELECT * FROM borrows WHERE ReaderID = %d " % borrow_ID_1)
                borrow_result = self.cursor.fetchall()
                for every in borrow_result:
                    for one in every:
                        if one.__class__ == str:
                            print one.decode('utf-8') ,
                        else:
                            print one,
                    print "\n"
            elif return_choice == 2:
                return_book_ID = input("输入你要还的书号\n")
                return_reader_ID = input("输入借书证卡号\n")
                self.cursor.execute(u"SELECT BookID FROM books WHERE BookID = %d" % return_book_ID)
                book_ID = [tuple[0] for tuple in self.cursor.description]
                if (book_ID):
                    print "还书成功\n"
                    self.cursor.execute(u"UPDATE books SET BookState = Bookstate + 1 WHERE BookID = %d" % return_book_ID)
                    print "库存增加1\n"
                    self.cursor.execute(u"SELECT BorrowID FROM borrows WHERE ReaderID = %d" % return_reader_ID)
                    borrow_ID = self.cursor.fetchall()
                    for one in borrow_ID:
                        print one,
                        print "\t",
                    print "\n"
                    your_bor_ID = input("输入你要还的书的借书号,从上选择\n")
                    self.cursor.execute(u"DELETE  FROM borrows WHERE BorrowID = %d" % your_bor_ID)


                    self.dbconn.commit()
                else:
                    print "还书失败,请再试\n"
            else:
                return 0

    def card_info(self):
        while(True):
            
            card_choice = input("数字选择:\n1.删除借书证\t2.增加借书证\t3.所有借书证\t4.退出\n")
            if card_choice == 1:
                card_number = input("输入你的证借书证号\n")
                self.cursor.execute(u"DELETE FROM reader WHERE ReaderID = %d" % card_number)
                self.cursor.execute(u"DELETE FROM borrows WHERE ReaderID = %d" % card_number)
                self.dbconn.commit()
                print "删除成功\n"

            elif card_choice == 2:
                print "请按照借书证卡号,姓名,学校,个人信息的顺序输入\n"
                reader_raw = []
                for reader_colum in range(4):
                    reader_raw.append(raw_input("请输入:\t"))
                self.cursor.execute(u"INSERT INTO reader VALUES (?, ?, ?, ?)", reader_raw)
                print "增加成功\n"
                self.dbconn.commit()
            elif card_choice == 3:
                self.cursor.execute(u"SELECT * FROM reader ")
                card_result = self.cursor.fetchall()
                for every in card_result:
                    for one in every:
                        if one.__class__ == str:
                            print one.decode('utf-8') ,
                        else:
                            print one,
                    print "\n"
            else:
                print "请重新输入\n"
                return 1
    def reader_info(self):
        borrow_ID = input("输入你的借书证卡号\n")
        self.cursor.execute(u"SELECT * FROM borrows WHERE ReaderID = %d " % borrow_ID)
        reader_result = self.cursor.fetchall()
        for every in reader_result:
                    for one in every:
                        if one.__class__ == str:
                            print one.decode('utf-8') ,
                        else:
                            print one,
                    print "\n"
                   


    def main(self):
        time_now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        #time_return = 
        admin_list = []
        admin_diction = {}
        app.cursor.execute(u"SELECT AdminID, AdminPassword FROM admin")
        admin_result = app.cursor.fetchall()
        for everyadmin in admin_result:
            admin_diction[everyadmin[0]] = everyadmin[1]
            admin_list.append(everyadmin[0])
        #print admin_list
        #print admin_diction
        reader_list = []
        app.cursor.execute(u"SELECT ReaderID FROM reader")
        reader_result = app.cursor.fetchall()
        for everyreader in reader_result:
            reader_list.append(everyreader[0])
        #print reader_list
        your_ID = input("Enter your ID :\t")
        
        if your_ID in admin_list:
            your_password = input("Enter your password:\t")
            if your_password == admin_diction[your_ID]:
                print "欢迎,管理员\n"
                while(True):
                    your_choice = int(raw_input("输入数字,选择功能:\n1.图书入库\t2.图书查询\t3.借书\t4.还书\t5.借书证管理\t6.退出\n"))
                    #print your_choice
                    if your_choice == 1:
                        #print "ok 1"
                        app.book_input()
                    elif your_choice == 2:
                        app.book_search()
                    elif your_choice == 3:
                        app.book_borrow()
                    elif your_choice == 4:
                        app.book_return()
                    elif your_choice == 5:
                        app.card_info()
                    else:
                        return 1
            else:
                print "密码错误\n"

        elif your_ID in reader_list:
            print "欢迎,普通用户\n"
            while(True):
                reader_choice = input("输入你的选择\n1.搜索\t2.借书\t3.还书\t4.个人信息\t5.退出\n")
                if reader_choice == 1:
                    app.book_search()
                elif  reader_choice == 2:
                    app.book_borrow()
                elif reader_choice == 3:
                    app.book_return()
                elif reader_choice == 4:
                    app.reader_info()
                else:
                    return 1
            
        else:
            print "你未注册\n"


if __name__ == "__main__":
    app = LibManager()
    print app.nowDate
    app.main()
