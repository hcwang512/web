#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
#来自pygtk，是用户界面模块
import gtk
import sys
import gobject
#使用数据库sqlite3
import sqlite3
import time
#日期和时间
import datetime


#构建类，并且设置UI框架
class LibManager:
    #以元组来定义书籍、读者信息
    bookColumName = (u"书本号", u"书名", u"作者", u"出版社",
                    u"价格", u"购入日期", u"分类", u"简介",   u"馆藏数")

    readerColumName = (u"读者号", u"读者姓名", u"读者身份", u"备注")

    def __init__(self):
        #连接数据库
        self.dbconn = sqlite3.connect('sqlitefile.db')
        #创建游标，以游标来控制数据库操作
        self.cursor = self.dbconn.cursor()

        self.nowDate = time.strftime("%Y-%m-%d")
        #输入书籍信息的起始状态
        inputBookInitData = (u"书名", u"作者", u"出版社",
                    0.0, self.nowDate, u"分类", u"简介", 0)

        try:
            builder = gtk.Builder()
            builder.add_from_file("ui.glade")
        except BaseException, e:
            self.errorMessage("Fail to load UI file.")
            print e
            sys.exit(1)

        builder.connect_signals(self)
        #以下为UI界面
        self.window = builder.get_object("mainWindow")

        self.borrowView = builder.get_object("borrowView")
        self.borrowViewModel = builder.get_object("borrowViewModel")
        self.borrowViewInit()

        self.returnView = builder.get_object("returnView")
        self.returnViewModel = builder.get_object("returnViewModel")
        self.returnEntryReaderID = builder.get_object("returnReaderID")
        self.returnEntryBookID = builder.get_object("returnBookID")
        self.returnViewInit()

        self.queryView = builder.get_object("queryView")
        self.queryViewReaderModel = builder.get_object("queryViewReaderModel")
        self.queryViewBookModel = builder.get_object("queryViewBookModel")

        self.inputView = builder.get_object("inputView")
        self.inputViewBookModel = builder.get_object("inputViewBookModel")
        self.inputViewReaderModel = builder.get_object("inputViewReaderModel")
        self.inputViewModel = None

    #借书界面的起始状态
    def borrowViewInit(self):
        columName = (u"读者号", u"书号", u"借出日期")
        columEditAttr = (True, True, False)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_data("column", columnNum)
            renderer.set_property("editable", columEditAttr[columnNum])
            if columEditAttr[columnNum]:
                renderer.connect("edited", self.on_borrow_cell_edited)
            column = gtk.TreeViewColumn(columName[columnNum], renderer,
                                        text=columnNum)
            column.set_resizable(True)
            self.borrowView.append_column(column)

    #归还界面的起始状态
    def returnViewInit(self):
        columName = (u"借书记录", u"书本", u"读者姓名", u"读者资料", u"借出日期")
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(columName[columnNum], renderer,
                                        text=columnNum)
            column.set_resizable(True)
            self.returnView.append_column(column)

    # 搜索界面
    def queryViewSetColumn(self, columName):
        self.queryRecord = 0
        columns = self.queryView.get_columns()
        for c in columns:
            self.queryView.remove_column(c)

        self.queryViewModel.clear()
        self.queryView.set_model(self.queryViewModel)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_property("editable", True)
            column = gtk.TreeViewColumn(columName[columnNum], renderer,
                                        text=columnNum)
            column.set_resizable(True)
            self.queryView.append_column(column)

    #搜索读者
    def queryReader(self):
        self.queryViewModel = self.queryViewReaderModel
        self.queryViewSetColumn(self.readerColumName)
        self.cursor.execute("SELECT COUNT(*) FROM reader")
        self.maxRecords = self.cursor.fetchone()[0]
        print self.maxRecords

    #搜索书籍
    def queryBook(self):
        self.queryViewModel = self.queryViewBookModel
        self.queryViewSetColumn(self.bookColumName)
        self.cursor.execute("SELECT COUNT(*) FROM books")
        self.maxRecords = self.cursor.fetchone()[0]
        print self.maxRecords

    #输入界面
    def inputViewSetColumn(self, columName):
        columns = self.inputView.get_columns()
        for c in columns:
            self.inputView.remove_column(c)

        self.inputViewModel.clear()
        self.inputView.set_model(self.inputViewModel)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_property("editable", True)
            renderer.set_data("column", columnNum)
            renderer.connect("edited", self.on_input_cell_edited)

            column = gtk.TreeViewColumn(columName[columnNum], renderer,
                                        text=columnNum)
            column.set_resizable(True)
            self.inputView.append_column(column)

    #输入读者信息
    def inputReader(self):
        self.inputViewModel = self.inputViewReaderModel
        self.inputViewSetColumn(self.readerColumName[1:])

    #输入书籍信息
    def inputBook(self):
        self.inputViewModel = self.inputViewBookModel
        self.inputViewSetColumn(self.bookColumName[1:])

    #删除函数
    def on_mainWindow_delete_event(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    #添加借书记录
    def on_borrowAdd_clicked(self, button, data = None):
        self.borrowViewModel.append((1001, 1, self.nowDate))

    #删除借书记录
    def on_borrowDel_clicked(self, button, data = None):
        selection = self.borrowView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)

    #清空借书记录
    def on_borrowClear_clicked(self, button, data = None):
        self.borrowViewModel.clear()

    #向数据库添加借书记录
    def on_borrowSubmit_clicked(self, button, data = None):
        for row in self.borrowViewModel:
            self.cursor.execute("INSERT INTO borrow VALUES (NULL, ?, ?, ?)", row)
        self.dbconn.commit()
        self.infoMessage(u"借书记录已经成功提交。")
        self.borrowViewModel.clear()

    def on_borrow_cell_edited(self, cell, path_string, new_text):
        model = self.borrowViewModel
        iter = model.get_iter_from_string(path_string)
        column = cell.get_data("column")
        try:
            id = int(new_text)
        except ValueError, e:
            print e
            self.errorMessage(u"请输入纯数字记录。")
            return

        if column == 0:
            self.cursor.execute("SELECT * FROM reader where ReaderID = ?", [new_text])
            if self.cursor.fetchone():
                model.set(iter, column, id)
            else:
                self.errorMessage(u"不存在该读者号: %d。" % id)

        if column == 1:
            self.cursor.execute("SELECT * FROM books where BookID = ?", [new_text])
            if self.cursor.fetchone():
                model.set(iter, column, id)
            else:
                self.errorMessage(u"不存在该书本号: %d。" % id)

    #书籍搜索界面
    def on_queryBooks_clicked(self, button, data = None):
        self.queryBook()
        self.cursor.execute("SELECT * FROM books LIMIT ? OFFSET ?", [15, 0])
        for row in self.cursor:
            self.queryViewModel.append(row)

    #读者搜索界面
    def on_queryReaders_clicked(self, button, data = None):
        self.queryReader()
        self.cursor.execute("SELECT * FROM reader LIMIT ? OFFSET ?", [15, 0])
        for row in self.cursor:
            self.queryViewModel.append(row)

    #搜索界面前一页
    def on_queryPrev_clicked(self, button, data = None):
        if self.queryRecord == 0:
            self.errorMessage(u"已到最前页。")
            return
        self.queryRecord -= 15
        self.queryViewModel.clear()

        if self.queryViewModel.get_n_columns() == 9:
            self.cursor.execute("SELECT * FROM books LIMIT ? OFFSET ?",[15, self.queryRecord])

        elif self.queryViewModel.get_n_columns() == 4:
            self.cursor.execute("SELECT * FROM reader LIMIT ? OFFSET ?",[15, self.queryRecord])

        for row in self.cursor:
            self.queryViewModel.append(row)

    #搜索界面后一页
    def on_queryNext_clicked(self, button, data = None):
        if self.queryRecord + 15 > self.maxRecords:
            self.errorMessage(u"已到最后页。")
            return

        self.queryRecord += 15
        self.queryViewModel.clear()

        if self.queryViewModel.get_n_columns() == 9:
            self.cursor.execute("SELECT * FROM books LIMIT ? OFFSET ?",[15, self.queryRecord])

        elif self.queryViewModel.get_n_columns() == 4:
            self.cursor.execute("SELECT * FROM reader LIMIT ? OFFSET ?",[15, self.queryRecord])

        for row in self.cursor:
            self.queryViewModel.append(row)

    #返回查询结果，分为按读者ID和书籍ID查询两种方式
    def on_returnQuery_clicked(self, button, data = None):
        readerid = self.returnEntryReaderID.get_text()
        bookid = self.returnEntryBookID.get_text()

        if len(readerid) and len(bookid):
            self.cursor.execute("SELECT borrow.BorrowID, books.BookName, reader.ReaderName,\
                                reader.ReaderSchool, borrow.BorrowDate FROM borrow,books,reader\
                                WHERE books.BookID = borrow.BookID AND \
                                reader.ReaderID = borrow.ReaderID AND\
                                borrow.ReaderID = ? AND borrow.BookID = ?", [readerid, bookid])
        elif len(readerid):
            self.cursor.execute("SELECT borrow.BorrowID, books.BookName, reader.ReaderName,\
                                reader.ReaderSchool, borrow.BorrowDate FROM borrow,books,reader\
                                WHERE books.BookID = borrow.BookID AND \
                                reader.ReaderID = borrow.ReaderID AND\
                                borrow.ReaderID = ?", [readerid])
        elif len(bookid):
            self.cursor.execute("SELECT borrow.BorrowID, books.BookName, reader.ReaderName,\
                                reader.ReaderSchool, borrow.BorrowDate FROM borrow,books,reader\
                                WHERE books.BookID = borrow.BookID AND \
                                reader.ReaderID = borrow.ReaderID AND\
                                borrow.BookID = ?", [bookid])
        else:
            self.errorMessage(u"请输入查询条件。")
            return

        self.returnViewModel.clear()

        for row in self.cursor:
            self.returnViewModel.append(row)

    #归还图书，将记录从数据库中删除
    def on_returnCommit_clicked(self, button, data = None):
        selection = self.returnView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            borrowDate = time.strptime(model.get_value(iter, 4), "%Y-%m-%d")
            timeDelta = datetime.date.today() - datetime.date(*borrowDate[0:3])
            borrowDays = timeDelta.days

            borrowID = model.get_value(iter, 0)
            self.cursor.execute("DELETE FROM borrow WHERE BorrowID = ?", [borrowID])
            self.dbconn.commit()
            readerName = model.get_value(iter, 2)
            bookName = model.get_value(iter, 1)
            self.infoMessage(u"读者  %s  所借书《%s》归还成功。 借出%d天" % (readerName, bookName, borrowDays))
            model.remove(iter)

    #UI输入界面，调用之前的函数
    def on_inputReader_clicked(self, button, data = None):
        self.inputReader()

    def on_inputBooks_clicked(self, button, data = None):
        self.inputBook()

    def on_inputAdd_clicked(self, button, data = None):
        if not self.inputViewModel:
            self.errorMessage(u"请先选择录入类型。")
            return
        count = self.inputViewModel.get_n_columns()
        if count == 3:
            inputReaderInitData = (u"姓名", u"身份", u"备注")
            self.inputViewModel.append(inputReaderInitData)
        elif count == 8:
            inputBookInitData = (u"书名", u"作者", u"出版社",
                                0.0, self.nowDate, u"分类", u"简介", 0)
            self.inputViewModel.append(inputBookInitData)

    def on_inputDel_clicked(self, button, data = None):
        selection = self.inputView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)

    def on_inputSubmit_clicked(self, button, data = None):
        count = self.inputViewModel.get_n_columns()
        for row in self.inputViewModel:
            #录入读者
            if count == 3:
                self.cursor.execute(u"INSERT INTO reader VALUES (NULL, ?, ?, ?)",
                                    [s for s in row])

            #录入书目
            elif count == 8:
                dataRow = []
                for obj in row:
                    if isinstance(obj, str):
                        dataRow.append(obj)
                    else:
                        dataRow.append(obj)
                print dataRow
                self.cursor.execute(u"INSERT INTO books VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",\
                                    dataRow)
        self.dbconn.commit()
        self.infoMessage(u"记录已经成功提交。")
        self.inputViewModel.clear()

    def on_input_cell_edited(self, cell, path_string, new_text):
        iter = self.inputViewModel.get_iter_from_string(path_string)
        column = cell.get_data("column")
        columnCount = self.inputViewModel.get_n_columns()
        if columnCount == 3:
            self.inputViewModel.set(iter, column, new_text)
        elif columnCount == 8:
            if self.inputViewModel.get_column_type(column) == gobject.TYPE_FLOAT:
                try:
                    self.inputViewModel.set(iter, column, float(new_text))
                except ValueError, e:
                    self.errorMessage(u"请输入价格实数。")
                    return
            elif self.inputViewModel.get_column_type(column) == gobject.TYPE_UINT:
                try:
                    self.inputViewModel.set(iter, column, int(new_text))
                except ValueError, e:
                    self.errorMessage(u"请输入整数。")
                    return
            else:
                self.inputViewModel.set(iter, column, new_text)

    def errorMessage(self, message):
        print message
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()

    def infoMessage(self, message):
        print message
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()

    def main(self):
        your_ID = raw_input("Enter your ID :\t")
        your_password = raw_input("Enter your password:\t")
        if your_ID == "admin" and your_password == "123456":
            self.window.show()
            gtk.main()
        else:
            print "ID/密码错误"

if __name__ == "__main__":
    app = LibManager()
    print app.cursor.execute(u"SELECT * FROM books")
    app.main()
